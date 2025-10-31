#!/usr/bin/env python3
"""
RAG Chatbot for Electronics E-commerce
Combines query enhancement, hybrid search, and response generation
"""

from query_enhancer import QueryEnhancer
from hybrid_retriever import HybridRetriever
from bm25_retriever import BM25Retriever
from response_generator import ResponseGenerator
import config

class EcommerceChatbot:
    """Main chatbot orchestrator"""
    
    def __init__(self, search_mode: str = None):
        print("🤖 Initializing E-commerce RAG Chatbot...")
        
        # Initialize components
        self.query_enhancer = QueryEnhancer(model_name=config.QUERY_ENHANCER_MODEL)
        self.semantic_retriever = HybridRetriever(db_name=config.DB_NAME)
        self.bm25_retriever = BM25Retriever(db_name=config.DB_NAME)
        self.response_generator = ResponseGenerator(model_name=config.RESPONSE_GENERATOR_MODEL)
        
        # Search mode
        self.search_mode = search_mode or config.SEARCH_MODE
        print(f"   Search mode: {self.search_mode}")
        
        # Conversation state
        self.conversation_history = []
        
        print("✅ Chatbot ready!")
    
    def chat(self, user_query: str) -> str:
        """
        Process a user query and generate a response
        
        Args:
            user_query: User's natural language query
            
        Returns:
            Bot's response
        """
        print(f"\n{'='*80}")
        print(f"User: {user_query}")
        print(f"{'='*80}")
        
        # Step 1: Enhance query
        print("\n🔧 Enhancing query...")
        try:
            enhanced = self.query_enhancer.enhance_query(user_query)
            
            print(f"   Keywords: {enhanced.keywords}")
            print(f"   Category: {enhanced.main_category or 'Any'}")
            if enhanced.price_max:
                print(f"   Price: ${enhanced.price_min or 0:.0f} - ${enhanced.price_max:.0f}")
            if enhanced.min_rating:
                print(f"   Min Rating: {enhanced.min_rating}★")
            print(f"   Intent: {enhanced.intent}")
            print(f"   Reasoning: {enhanced.reasoning}")
            
        except Exception as e:
            print(f"   ⚠️  Query enhancement failed: {e}")
            # Fallback to basic keyword extraction
            enhanced = None
        
        # Step 2: Retrieve products (with search mode)
        print(f"\n🔍 Searching for products (mode: {self.search_mode})...")
        try:
            if self.search_mode == "bm25":
                # BM25 keyword search only
                products_list = self.bm25_retriever.search_bm25(
                    query=user_query,
                    category=enhanced.main_category if enhanced else None,
                    price_min=enhanced.price_min if enhanced else None,
                    price_max=enhanced.price_max if enhanced else None,
                    min_rating=enhanced.min_rating if enhanced else None,
                    limit=config.MAX_RESULTS
                )
                # Convert dicts to Product objects
                from hybrid_retriever import Product
                products = [
                    Product(
                        asin=p['asin'],
                        title=p['title'],
                        price=p['price'],
                        rating=p['rating'],
                        num_reviews=p['num_reviews'],
                        category=p['category'],
                        similarity=p['similarity'],
                        image_url=p['image_url']
                    )
                    for p in products_list
                ]
            
            elif self.search_mode == "semantic":
                # Semantic vector search only
                if enhanced:
                    products = self.semantic_retriever.search(
                        keywords=enhanced.keywords,
                        category=enhanced.main_category,
                        price_min=enhanced.price_min,
                        price_max=enhanced.price_max,
                        min_rating=enhanced.min_rating,
                        sort_by=enhanced.sort_by or "rating_number",
                        limit=config.MAX_RESULTS,
                        use_vector=config.USE_VECTOR_SEARCH
                    )
                else:
                    keywords = user_query.split()
                    products = self.semantic_retriever.search(
                        keywords=keywords,
                        limit=config.MAX_RESULTS
                    )
            
            elif self.search_mode == "hybrid":
                # Hybrid: Run both searches and merge results
                print("   Running BM25 search...")
                bm25_results = self.bm25_retriever.search_bm25(
                    query=user_query,
                    category=enhanced.main_category if enhanced else None,
                    price_min=enhanced.price_min if enhanced else None,
                    price_max=enhanced.price_max if enhanced else None,
                    min_rating=enhanced.min_rating if enhanced else None,
                    limit=config.MAX_RESULTS // 2
                )
                
                print("   Running semantic search...")
                if enhanced:
                    semantic_results = self.semantic_retriever.search(
                        keywords=enhanced.keywords,
                        category=enhanced.main_category,
                        price_min=enhanced.price_min,
                        price_max=enhanced.price_max,
                        min_rating=enhanced.min_rating,
                        sort_by=enhanced.sort_by or "rating_number",
                        limit=config.MAX_RESULTS // 2,
                        use_vector=config.USE_VECTOR_SEARCH
                    )
                else:
                    semantic_results = self.semantic_retriever.search(
                        keywords=user_query.split(),
                        limit=config.MAX_RESULTS // 2
                    )
                
                # Merge and deduplicate by ASIN
                products_dict = {}
                from hybrid_retriever import Product
                
                # Add BM25 results
                for p in bm25_results:
                    products_dict[p['asin']] = Product(
                        asin=p['asin'],
                        title=p['title'],
                        price=p['price'],
                        rating=p['rating'],
                        num_reviews=p['num_reviews'],
                        category=p['category'],
                        similarity=p['similarity'],
                        image_url=p['image_url']
                    )
                
                # Add semantic results (will overwrite if duplicate ASINs)
                for p in semantic_results:
                    if p.asin not in products_dict:
                        products_dict[p.asin] = p
                    else:
                        # Boost similarity score if product appears in both
                        products_dict[p.asin].similarity = (
                            products_dict[p.asin].similarity + p.similarity
                        ) / 2 if p.similarity else products_dict[p.asin].similarity
                
                products = list(products_dict.values())
                # Sort by similarity (or popularity if no similarity)
                products.sort(
                    key=lambda p: (p.similarity or 0, p.num_reviews or 0),
                    reverse=True
                )
                products = products[:config.MAX_RESULTS]
            
            else:
                raise ValueError(f"Unknown search mode: {self.search_mode}")
            
            print(f"   Found {len(products)} products")
            
        except Exception as e:
            print(f"   ⚠️  Search failed: {e}")
            import traceback
            traceback.print_exc()
            products = []
        
        # Step 3: Generate response
        print("\n💬 Generating response...")
        try:
            response = self.response_generator.generate_response(
                user_query=user_query,
                products=products,
                enhanced_query=enhanced.dict() if enhanced else None,
                conversation_history=self.conversation_history
            )
        except Exception as e:
            print(f"   ⚠️  Response generation failed: {e}")
            response = f"I found {len(products)} products, but encountered an error generating the response."
        
        # Update conversation history
        self.conversation_history.append({
            'user': user_query,
            'bot': response
        })
        
        return response
    
    def switch_mode(self, mode: str):
        """Switch search mode dynamically"""
        if mode not in ["semantic", "bm25", "hybrid"]:
            print(f"❌ Invalid mode: {mode}. Choose: semantic, bm25, or hybrid")
            return False
        self.search_mode = mode
        print(f"✅ Switched to {mode} search mode")
        return True
    
    def interactive_mode(self):
        """Run the chatbot in interactive mode"""
        print("\n" + "=" * 80)
        print("🤖 ELECTRONICS SHOPPING ASSISTANT")
        print("=" * 80)
        print(f"\n🔧 Current search mode: {self.search_mode}")
        print("\nI can help you find electronics products!")
        print("\n📝 Example queries:")
        print("  - 'I need a gaming laptop under $1000'")
        print("  - 'Show me the best wireless headphones'")
        print("  - 'I like bose for audio, suggest good products from other brands'")
        print("  - 'Headphones similar to sony but not sony'")
        print("\n⚙️  Commands:")
        print("  - '/mode semantic' - Switch to semantic search (vector embeddings)")
        print("  - '/mode bm25' - Switch to BM25 keyword search")
        print("  - '/mode hybrid' - Use both search methods")
        print("  - 'quit' or 'exit' - End conversation")
        print()
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith('/mode '):
                    mode = user_input.split()[1].lower()
                    self.switch_mode(mode)
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    print("\n🤖 Bot: Thank you for shopping with us! Goodbye! 👋")
                    break
                
                # Get bot response
                response = self.chat(user_input)
                
                print(f"\n🤖 Bot:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def close(self):
        """Cleanup resources"""
        self.semantic_retriever.close()
        self.bm25_retriever.close()


def main():
    """Main entry point"""
    chatbot = EcommerceChatbot()
    
    try:
        chatbot.interactive_mode()
    finally:
        chatbot.close()


if __name__ == "__main__":
    main()

