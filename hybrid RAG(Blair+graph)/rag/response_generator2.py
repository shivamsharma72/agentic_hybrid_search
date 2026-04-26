"""
Response Generator using LangChain + Local Llama 3.1 (Ollama)
Generates natural language responses with product recommendations
"""
# USE Llama 3.2
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any
import config

class ResponseGenerator:
    """Generate conversational responses with product recommendations using Local Llama 3.1"""
    
    def __init__(self, model_name="llama3.1", temperature=0.7):
        # Use local Ollama instance via OpenAI-compatible endpoint
        self.llm = ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # Required but ignored
            model=model_name,
            temperature=temperature
        )
    
    def generate_response(self, 
                         user_query: str, 
                         products: List[Any],
                         reviews_by_product: Dict = None,
                         enhanced_query: Dict = None,
                         conversation_history: List[Dict] = None,
                         additional_context: str = None) -> str:
        """
        Generate a natural language response with product recommendations
        
        Args:
            user_query: Original user query
            products: List of Product objects
            enhanced_query: Enhanced query information
            conversation_history: Previous conversation turns
        """
        # Build system prompt
        system_prompt = """You are a helpful e-commerce shopping assistant for an electronics store.

**CRITICAL RULE**: You MUST ONLY recommend products from the "Available products" list provided below. 
DO NOT make up product names, prices, or details. ONLY use the exact products, prices, and reviews given to you.

Your role:
- Recommend ONLY the products from the list provided
- Use EXACT product titles, prices, and ratings from the data
- Quote real customer reviews provided for each product
- Answer questions naturally and conversationally
- Be concise but informative

Guidelines:
- Start with a brief acknowledgment of what they're looking for
- Present the top 3-5 products FROM THE PROVIDED LIST (don't invent products)
- For each product, use: EXACT title from list, EXACT price, EXACT rating, and INCLUDE the ASIN
- Quote or reference the actual customer reviews provided
- Use bullet points or numbers for clarity
- Always include the product ASIN in your response (format: "ASIN: B07FT8ZBMR")
- If no products match well, say so honestly - don't make up better products
- Be enthusiastic but honest about product quality based on PROVIDED reviews
- NEVER fabricate product names like "Govee", "DAYBETTER", etc. unless they're in the list"""

        # Use additional context if provided (e.g., from enhanced retriever with reviews)
        if additional_context:
            context = additional_context
        # Otherwise build context from products
        elif not products:
            context = "No products found matching the criteria."
        else:
            context = "Available products with customer reviews:\n\n"
            for i, product in enumerate(products, 1):  # All products
                context += f"{i}. **{product.title}**\n"
                context += f"   - ASIN: {product.asin}\n"
                
                # Handle None price
                if product.price is not None:
                    context += f"   - Price: ${product.price:.2f}\n"
                else:
                    context += f"   - Price: Not available\n"
                
                # Handle None rating
                if product.rating is not None:
                    context += f"   - Rating: {product.rating:.1f}★ ({product.num_reviews or 0:,} reviews)\n"
                else:
                    context += f"   - Rating: Not yet rated\n"
                
                context += f"   - Category: {product.category}\n"
                
                if product.similarity:
                    context += f"   - Relevance: {product.similarity:.2%}\n"
                
                # Add reviews if available
                if reviews_by_product and product.asin in reviews_by_product:
                    reviews = reviews_by_product[product.asin]
                    context += f"\n   Customer Reviews ({len(reviews)} shown):\n"
                    for j, review in enumerate(reviews, 1):
                        context += f"   {j}. [{review['rating']}★] {review.get('title', 'No title')}\n"
                        context += f"      \"{review['text'][:200]}...\"\n"
                        if review.get('verified_purchase'):
                            context += f"      (Verified Purchase)\n"
                
                context += "\n"
        
        # Add enhanced query info
        if enhanced_query:
            context += f"\nSearch filters applied:\n"
            if enhanced_query.get('main_category'):
                context += f"- Category: {enhanced_query['main_category']}\n"
            if enhanced_query.get('price_max') is not None:
                context += f"- Max Price: ${enhanced_query['price_max']:.2f}\n"
            if enhanced_query.get('min_rating') is not None:
                context += f"- Min Rating: {enhanced_query['min_rating']}★\n"
        
        # Build messages
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        if conversation_history:
            for turn in conversation_history[-3:]:  # Last 3 turns
                messages.append(HumanMessage(content=turn['user']))
                messages.append(AIMessage(content=turn['bot']))
        
        # Add current query and context
        user_message = f"""User Query: {user_query}

{context}

⚠️ IMPORTANT: Only recommend products from the list above. Use their EXACT titles and prices.
DO NOT invent or make up any product names, brands, or details not in the list.

Please provide a helpful response with product recommendations."""
        
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        response = self.llm.invoke(messages)
        return response.content


# Test the response generator
if __name__ == "__main__":
    from retriever import EnhancedHybridRetriever as HybridRetriever, Product
    
    from embedding_model import EmbeddingModel
    
    generator = ResponseGenerator()
    retriever = HybridRetriever()
    embedding_model = EmbeddingModel()
    
    print("=" * 80)
    print("TESTING RESPONSE GENERATOR (LOCAL LLAMA 3.1)")
    print("=" * 80)
    
    # Test query
    user_query = "I need a gaming laptop under $1000"
    
    print(f"\nUser Query: '{user_query}'")
    print("\n🔍 Searching for products...")
    
    query_embedding = embedding_model.encode_query(user_query)
    
    products = retriever.search_unified(
        query_embedding=query_embedding,
        category="Computers",
        price_max=1000,
        min_rating=4.0,
        top_products=5
    )
    
    print(f"Found {len(products)} products\n")
    
    print("🤖 Generating response...")
    response = generator.generate_response(
        user_query=user_query,
        products=products,
        enhanced_query={
            'main_category': 'Computers',
            'price_max': 1000,
            'min_rating': 4.0
        }
    )
    
    print("\n" + "=" * 80)
    print("BOT RESPONSE:")
    print("=" * 80)
    print(response)
    
    retriever.close()
