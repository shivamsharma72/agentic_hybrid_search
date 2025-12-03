"""
LangGraph-based Query Orchestrator
Analyzes and refines user queries for better laptop search
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os


# ============================================================================
# State Definitions
# ============================================================================

class QuerySpecs(BaseModel):
    """Detected specifications from user query"""
    price_min: float | None = Field(None, description="Minimum price detected")
    price_max: float | None = Field(None, description="Maximum price detected")
    ram: str | None = Field(None, description="RAM requirement (e.g., '8GB', '16GB')")
    storage: str | None = Field(None, description="Storage requirement (e.g., '256GB SSD', '512GB')")
    screen_size: str | None = Field(None, description="Screen size (e.g., '13-inch', '15.6-inch')")
    processor: str | None = Field(None, description="Processor type (e.g., 'i5', 'i7', 'Ryzen')")
    use_case: str | None = Field(None, description="Use case (e.g., 'gaming', 'work', 'student')")
    
    def count_specs(self) -> int:
        """Count how many specs are specified"""
        return sum([
            self.price_min is not None or self.price_max is not None,
            self.ram is not None,
            self.storage is not None,
            self.screen_size is not None,
            self.processor is not None,
            self.use_case is not None
        ])


class QueryQuality(BaseModel):
    """Assessment of query quality"""
    is_specific: bool = Field(description="Whether query is specific enough")
    confidence: float = Field(description="Confidence score 0-1")
    specs_count: int = Field(description="Number of specifications detected")
    missing_critical: list[str] = Field(description="Critical missing specifications")
    suggestions: list[str] = Field(description="Suggestions for refinement")


class OrchestratorState(TypedDict):
    """State for the orchestrator graph"""
    original_query: str
    refined_query: str
    detected_specs: QuerySpecs
    quality_assessment: QueryQuality
    needs_refinement: bool
    refinement_suggestions: list[str]
    final_query: str


# ============================================================================
# LangGraph Orchestrator
# ============================================================================

class QueryOrchestrator:
    """LangGraph-based query orchestrator for laptop search"""
    
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            api_key=self.api_key
        )
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define the graph
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("assess_quality", self._assess_quality)
        workflow.add_node("generate_suggestions", self._generate_suggestions)
        workflow.add_node("refine_query", self._refine_query)
        
        # Define edges
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "assess_quality")
        
        # Conditional edge: refine or finish
        workflow.add_conditional_edges(
            "assess_quality",
            self._should_refine,
            {
                "refine": "generate_suggestions",
                "proceed": END
            }
        )
        
        workflow.add_edge("generate_suggestions", "refine_query")
        workflow.add_edge("refine_query", END)
        
        return workflow.compile()
    
    # ========================================================================
    # Graph Nodes
    # ========================================================================
    
    def _analyze_query(self, state: OrchestratorState) -> OrchestratorState:
        """Node 1: Analyze user query to extract specifications"""
        
        parser = PydanticOutputParser(pydantic_object=QuerySpecs)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a laptop specification extractor. 
            Analyze the user's laptop search query and extract specific requirements.
            
            {format_instructions}"""),
            ("user", "Query: {query}")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "query": state["original_query"],
            "format_instructions": parser.get_format_instructions()
        })
        
        try:
            specs = parser.parse(response.content)
        except:
            # Fallback to empty specs
            specs = QuerySpecs()
        
        state["detected_specs"] = specs
        return state
    
    def _assess_quality(self, state: OrchestratorState) -> OrchestratorState:
        """Node 2: Assess query quality and determine if refinement needed"""
        
        specs = state["detected_specs"]
        specs_count = specs.count_specs()
        
        # Determine what's missing
        missing = []
        if specs.price_min is None and specs.price_max is None:
            missing.append("price_range")
        if specs.use_case is None:
            missing.append("use_case")
        if specs.ram is None:
            missing.append("ram")
        if specs.storage is None:
            missing.append("storage")
        
        # Quality assessment
        is_specific = specs_count >= 2  # Need at least 2 specs
        confidence = min(specs_count / 4.0, 1.0)  # 4 specs = 100% confidence
        
        quality = QueryQuality(
            is_specific=is_specific,
            confidence=confidence,
            specs_count=specs_count,
            missing_critical=missing[:2],  # Top 2 missing
            suggestions=[]
        )
        
        state["quality_assessment"] = quality
        state["needs_refinement"] = not is_specific
        
        return state
    
    def _should_refine(self, state: OrchestratorState) -> Literal["refine", "proceed"]:
        """Conditional edge: Determine if query needs refinement"""
        return "refine" if state["needs_refinement"] else "proceed"
    
    def _generate_suggestions(self, state: OrchestratorState) -> OrchestratorState:
        """Node 3: Generate refinement suggestions using LLM"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant helping users refine laptop search queries.
            Generate 3-4 specific, actionable suggestions to make the query more specific.
            Focus on the most important missing specifications.
            
            Return ONLY a JSON array of suggestion strings, nothing else."""),
            ("user", """Original query: {query}
            
            Detected specs: {specs}
            Missing: {missing}
            
            Generate suggestions as a JSON array:""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "query": state["original_query"],
            "specs": state["detected_specs"].model_dump_json(),
            "missing": ", ".join(state["quality_assessment"].missing_critical)
        })
        
        # Parse suggestions (simple JSON array)
        import json
        try:
            suggestions = json.loads(response.content)
        except:
            # Fallback suggestions
            suggestions = [
                "What's your budget? (e.g., under $500, $500-$1000)",
                "What will you use it for? (gaming, work, student)",
                "How much RAM do you need? (8GB, 16GB)",
                "Preferred screen size? (13-inch, 15-inch)"
            ]
        
        state["refinement_suggestions"] = suggestions
        state["quality_assessment"].suggestions = suggestions
        
        return state
    
    def _refine_query(self, state: OrchestratorState) -> OrchestratorState:
        """Node 4: Create a refined query suggestion"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query refinement expert. 
            Given the original query and detected specs, create a more specific refined query.
            Keep it natural and concise.
            Return ONLY the refined query text, nothing else."""),
            ("user", """Original: {query}
            Specs: {specs}
            
            Refined query:""")
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({
            "query": state["original_query"],
            "specs": state["detected_specs"].model_dump_json()
        })
        
        state["refined_query"] = response.content.strip('"')
        state["final_query"] = state["refined_query"]
        
        return state
    
    # ========================================================================
    # Public Interface
    # ========================================================================
    
    def analyze(self, query: str) -> dict:
        """
        Analyze a user query and provide refinement guidance
        
        Args:
            query: User's natural language search query
            
        Returns:
            Dictionary with analysis results
        """
        
        initial_state: OrchestratorState = {
            "original_query": query,
            "refined_query": "",
            "detected_specs": QuerySpecs(),
            "quality_assessment": QueryQuality(
                is_specific=False,
                confidence=0.0,
                specs_count=0,
                missing_critical=[],
                suggestions=[]
            ),
            "needs_refinement": True,
            "refinement_suggestions": [],
            "final_query": query
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        # Format output
        return {
            "original_query": result["original_query"],
            "is_specific": result["quality_assessment"].is_specific,
            "confidence": result["quality_assessment"].confidence,
            "detected_specs": result["detected_specs"].model_dump(),
            "specs_count": result["quality_assessment"].specs_count,
            "needs_refinement": result["needs_refinement"],
            "suggestions": result["refinement_suggestions"],
            "refined_query": result.get("refined_query", query),
            "missing_specs": result["quality_assessment"].missing_critical
        }


# ============================================================================
# Singleton Instance
# ============================================================================

_orchestrator_instance = None

def get_orchestrator() -> QueryOrchestrator:
    """Get or create the query orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = QueryOrchestrator()
    return _orchestrator_instance


# ============================================================================
# Test
# ============================================================================

if __name__ == "__main__":
    orchestrator = QueryOrchestrator()
    
    test_queries = [
        "laptop",
        "gaming laptop",
        "laptop under $800 for gaming with 16GB RAM"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")
        
        result = orchestrator.analyze(query)
        
        print(f"\nSpecific enough: {result['is_specific']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Specs detected: {result['specs_count']}")
        print(f"\nDetected:")
        for k, v in result['detected_specs'].items():
            if v:
                print(f"  - {k}: {v}")
        
        if result['needs_refinement']:
            print(f"\n💡 Suggestions:")
            for i, sug in enumerate(result['suggestions'], 1):
                print(f"  {i}. {sug}")
            print(f"\n✨ Refined query: {result['refined_query']}")

