"""
Response Generator using LangChain + OpenAI
Generates natural language responses with product recommendations
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import List, Dict, Any
import config

class ResponseGenerator:
    """Generate conversational responses with product recommendations"""
    
    def __init__(self, model_name=None, temperature=0.7):
        model_name = model_name or config.RESPONSE_GENERATOR_MODEL
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=config.OPENAI_API_KEY
        )
    
    def generate_response(self, 
                         user_query: str, 
                         products: List[Any],
                         reviews_by_product: Dict = None,
                         enhanced_query: Dict = None,
                         conversation_history: List[Dict] = None) -> str:
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

        # Build context from products
        if not products:
            context = "No products found matching the criteria."
        else:
            context = "Available products with customer reviews:\n\n"
            for i, product in enumerate(products[:5], 1):  # Top 5
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
    from hybrid_retriever import HybridRetriever, Product
    
    generator = ResponseGenerator()
    retriever = HybridRetriever()
    
    print("=" * 80)
    print("TESTING RESPONSE GENERATOR")
    print("=" * 80)
    
    # Test query
    user_query = "I need a gaming laptop under $1000"
    
    print(f"\nUser Query: '{user_query}'")
    print("\n🔍 Searching for products...")
    
    products = retriever.search(
        keywords=["gaming", "laptop"],
        category="Computers",
        price_max=1000,
        min_rating=4.0,
        limit=5
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

