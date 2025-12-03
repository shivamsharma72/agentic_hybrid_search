from retriever import EnhancedHybridRetriever
from embedding_model import EmbeddingModel
import config

def test_retriever():
    print("="*50)
    print("TESTING ENHANCED HYBRID RETRIEVER")
    print("="*50)
    
    # Initialize
    try:
        print("Initializing models...")
        retriever = EnhancedHybridRetriever()
        embedding_model = EmbeddingModel()
        print("✅ Initialization successful")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # Test Query
    query = "Light 512GB SSD Windows 10 laptop"
    print(f"\n🔍 Testing Query: '{query}'")
    
    try:
        # 1. Embed
        print("Generating embedding...")
        query_embedding = embedding_model.encode_query(query)
        
        # 2. Search
        print("Executing search_unified...")
        products, search_log = retriever.search_unified(
            query_embedding=query_embedding,
            query_text=query,
            top_products=5
        )
        
        print(f"\n✅ Search successful! Found {len(products)} products.")
        print(f"📋 Search Log: {search_log}")
        
        for i, p in enumerate(products, 1):
            print(f"\n{i}. {p.title}")
            print(f"   ASIN: {p.asin}")
            print(f"   Confidence: {p.confidence_score:.2%}")
            if p.graph_insights:
                print(f"   🕸️ Graph Insights: {p.graph_insights}")
            
    except Exception as e:
        print(f"\n❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        retriever.close()

if __name__ == "__main__":
    test_retriever()
