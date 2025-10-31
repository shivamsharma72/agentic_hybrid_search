"""
Query Enhancement using LangChain + OpenAI
Extracts intent, keywords, filters from natural language queries
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
from dotenv import load_dotenv

load_dotenv()

# Categories from your database (top 20)
CATEGORIES = [
    "All Electronics",
    "Computers",
    "Camera & Photo",
    "Cell Phones & Accessories",
    "Home Audio & Theater",
    "Industrial & Scientific",
    "Car Electronics",
    "Tools & Home Improvement",
    "Office Products",
    "Amazon Home",
    "Amazon Devices",
    "Sports & Outdoors",
    "AMAZON FASHION",
    "Automotive",
    "Musical Instruments",
    "GPS & Navigation",
    "Portable Audio & Accessories",
    "Toys & Games",
    "Apple Products",
    "Health & Personal Care",
    "Video Games",
    "All Beauty",
]

# Define output structure
class EnhancedQuery(BaseModel):
    """Enhanced query with extracted intent and filters"""
    keywords: List[str] = Field(description="Expanded keywords for search (3-5 relevant terms)")
    main_category: Optional[str] = Field(default=None, description="Most relevant category from the provided list, or null")
    price_min: Optional[float] = Field(default=None, description="Minimum price in USD, or null")
    price_max: Optional[float] = Field(default=None, description="Maximum price in USD, or null")
    min_rating: Optional[float] = Field(default=None, description="Minimum rating (1-5), or null")
    sort_by: Optional[Literal["rating_number", "price", "average_rating"]] = Field(
        default=None,
        description="How to sort results: rating_number (popularity), price, or average_rating"
    )
    intent: Literal["browse", "compare", "specific_product", "question"] = Field(
        description="User's intent: browse (general search), compare (comparing products), specific_product (looking for exact item), question (asking about products)"
    )
    reasoning: str = Field(description="Brief explanation of why these filters were chosen")


class QueryEnhancer:
    """Enhance user queries using LLM"""
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.parser = PydanticOutputParser(pydantic_object=EnhancedQuery)
        self.prompt = self._create_prompt()
    
    def _create_prompt(self):
        """Create the prompt template"""
        template = """You are a query enhancement system for an electronics e-commerce search engine.

AVAILABLE CATEGORIES ({num_categories} total):
{categories}

PRODUCT TYPE TO CATEGORY MAPPING:
- Laptops, desktops, monitors, keyboards, mice, SSDs, RAM → "Computers"
- Headphones, earbuds, speakers, soundbars → "Home Audio & Theater" or "Portable Audio & Accessories"
- Cameras, lenses, tripods, drones, webcams → "Camera & Photo"
- Smartphones, phone cases, chargers → "Cell Phones & Accessories"
- TVs, projectors → "Home Audio & Theater"
- Gaming accessories (mouse, keyboard, controller, headset) → "Computers" or "Video Games"
- Cables, adapters, power banks → "All Electronics" or relevant category
- If unsure or multi-category, use null (no category filter is better than wrong category)

FILTERABLE FIELDS:
- price: float (USD)
- average_rating: 1.0-5.0
- rating_number: number of reviews (popularity)
- main_category: from the category list above

PRICE INTERPRETATION:
- "cheap", "budget", "affordable", "inexpensive" → price_max: 50
- "mid-range", "decent", "reasonable" → price_max: 200
- "good quality" → min_rating: 4.0, price_max: 500
- "expensive", "premium", "high-end" → price_max: 1000
- "luxury", "top-tier" → price_max: 2000
- "under X" → price_max: X
- "over X" → price_min: X
- "around X", "about X" → price_min: X*0.8, price_max: X*1.2

RATING INTERPRETATION:
- "good reviews", "well-reviewed" → min_rating: 4.0
- "highly rated", "best", "top rated", "excellent" → min_rating: 4.5
- "popular", "best-selling" → sort_by: "rating_number"

SORT PREFERENCE:
- "best", "top", "highest rated" → sort_by: "average_rating"
- "popular", "most reviewed", "best-selling" → sort_by: "rating_number"
- "cheapest", "lowest price" → sort_by: "price"
- Default → sort_by: "rating_number" (popularity)

KEYWORD EXPANSION RULES:
- Expand with synonyms and related terms
- Include brand names if mentioned
- For "laptop" → include "laptop", "notebook", "chromebook"
- For "Apple laptop" → include "MacBook", "MacBook Air", "MacBook Pro" (NOT just "laptop")
- For "gaming monitor" → include "monitor", "gaming", "144hz", "165hz" (refresh rates)
- For "wireless headphones" → include "wireless", "bluetooth", "headphones", "earbuds"
- Be smart: "apple laptops" should search for "MacBook" not "laptop"
- Keep keywords specific and relevant

YOUR TASK:
Extract structured query parameters from the user's natural language query.
Be smart about context - "gaming laptop under 1000" should extract both "gaming" and price constraint.

IMPORTANT RULES FOR CATEGORIES:
- For monitors/keyboards/mice → "Computers"
- For headphones/speakers → "Home Audio & Theater"
- If uncertain or doesn't fit perfectly → use null (better no filter than wrong filter!)

{format_instructions}

User Query: {query}

Enhanced Query (JSON):"""

        return ChatPromptTemplate.from_template(
            template=template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "categories": "\n".join([f"- {cat}" for cat in CATEGORIES]),
                "num_categories": len(CATEGORIES)
            }
        )
    
    def enhance_query(self, user_query: str) -> EnhancedQuery:
        """Enhance a user query"""
        chain = self.prompt | self.llm | self.parser
        result = chain.invoke({"query": user_query})
        return result
    
    def enhance_query_with_history(self, user_query: str, conversation_history: List[dict]) -> EnhancedQuery:
        """Enhance query with conversation context"""
        # Add conversation history to the query
        context = "\n".join([
            f"User: {turn['user']}\nBot: {turn['bot']}" 
            for turn in conversation_history[-3:]  # Last 3 turns
        ])
        
        enhanced_query = f"Conversation History:\n{context}\n\nCurrent Query: {user_query}"
        return self.enhance_query(enhanced_query)


# Test the enhancer
if __name__ == "__main__":
    enhancer = QueryEnhancer()
    
    test_queries = [
        "gaming laptop under $1000",
        "best wireless headphones",
        "cheap phone case",
        "4k tv under 500",
        "laptop for video editing",
        "noise cancelling earbuds rating 4.5",
        "affordable mechanical keyboard",
        "dashcam for my car",
        "webcam for video calls",
        "monitor around 300 dollars"
    ]
    
    print("=" * 80)
    print("TESTING QUERY ENHANCER")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"{'='*80}")
        
        try:
            result = enhancer.enhance_query(query)
            print(f"\nKeywords: {result.keywords}")
            print(f"Category: {result.main_category}")
            print(f"Price: ${result.price_min or 0:.0f} - ${result.price_max or '∞'}")
            print(f"Min Rating: {result.min_rating or 'Any'}")
            print(f"Sort By: {result.sort_by}")
            print(f"Intent: {result.intent}")
            print(f"Reasoning: {result.reasoning}")
        except Exception as e:
            print(f"❌ Error: {e}")

