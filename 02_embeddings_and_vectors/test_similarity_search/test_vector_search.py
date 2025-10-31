#!/usr/bin/env python3
"""
Test Vector Similarity Search
Compare vector search vs traditional text search
"""

import psycopg2
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
import time
from datetime import datetime

# ========= CONFIG =========
DB_NAME = "amazon_electronics_rag"
MODEL_NAME = "hyp1231/blair-roberta-base"  # Same model used for product embeddings
PROBES = 50  # IVFFlat search parameter
TOP_K = 10  # Number of results to return

# Test queries
TEST_QUERIES = [
    "wireless bluetooth headphones",
    "gaming laptop with RTX graphics card",
    "4K smart TV 55 inch",
    "USB-C charging cable for iPhone",
    "mechanical keyboard with RGB lighting",
    "portable power bank 20000mAh",
    "noise cancelling earbuds",
    "gaming mouse with high DPI",
    "external hard drive 2TB",
    "webcam for video conferencing"
]

def load_model():
    """Load BLAIR-RoBERTa model for query embedding"""
    print("\n📦 Loading BLAIR-RoBERTa model...")
    print(f"   Model: {MODEL_NAME}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    print(f"   Device: {device}")
    print(f"   ✅ Model loaded")
    
    return tokenizer, model, device

def embed_text(text, tokenizer, model, device):
    """Generate embedding for a text query"""
    # Tokenize
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)
    
    # Generate embedding
    with torch.no_grad():
        outputs = model(**inputs)
        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        # Normalize
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    
    return embeddings.cpu().numpy()[0]

def vector_search(conn, query_embedding, top_k=10):
    """Search using vector similarity"""
    cur = conn.cursor()
    
    # Set probes
    cur.execute(f"SET ivfflat.probes = {PROBES};")
    
    # Search query
    start = time.time()
    
    cur.execute("""
        SELECT 
            parent_asin,
            title,
            average_rating,
            rating_number,
            price,
            1 - (blair_embedding <=> %s::vector) as similarity
        FROM products
        WHERE blair_embedding IS NOT NULL
        ORDER BY blair_embedding <=> %s::vector
        LIMIT %s;
    """, (query_embedding.tolist(), query_embedding.tolist(), top_k))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000  # Convert to ms
    
    cur.close()
    return results, duration

def text_search(conn, query_text, top_k=10):
    """Traditional text search using PostgreSQL full-text search"""
    cur = conn.cursor()
    
    start = time.time()
    
    # Simple ILIKE search on title
    cur.execute("""
        SELECT 
            parent_asin,
            title,
            average_rating,
            rating_number,
            price
        FROM products
        WHERE title ILIKE %s
        LIMIT %s;
    """, (f"%{query_text}%", top_k))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000  # Convert to ms
    
    cur.close()
    return results, duration

def print_results(results, search_type, duration, show_similarity=False):
    """Pretty print search results"""
    print(f"\n   {search_type} ({duration:.1f}ms):")
    
    if not results:
        print(f"      ❌ No results found")
        return
    
    for i, row in enumerate(results, 1):
        if show_similarity:
            asin, title, rating, num_ratings, price, similarity = row
            print(f"      {i}. [{asin}] (sim: {similarity:.4f})")
        else:
            asin, title, rating, num_ratings, price = row
            print(f"      {i}. [{asin}]")
        
        # Title (truncate if too long)
        title_display = title[:70] + "..." if len(title) > 70 else title
        print(f"         {title_display}")
        
        # Rating and price
        rating_str = f"⭐ {rating:.1f}" if rating else "No rating"
        num_ratings_str = f"({num_ratings:,})" if num_ratings else "(0)"
        price_str = f"${price:.2f}" if price else "N/A"
        print(f"         {rating_str} {num_ratings_str} | {price_str}")

def test_single_query(conn, query_text, tokenizer, model, device):
    """Test a single query with both methods"""
    print(f"\n{'='*80}")
    print(f"Query: \"{query_text}\"")
    print(f"{'='*80}")
    
    # 1. Generate query embedding
    print(f"\n🔄 Generating query embedding...")
    start = time.time()
    query_embedding = embed_text(query_text, tokenizer, model, device)
    embed_time = (time.time() - start) * 1000
    print(f"   ✅ Embedding generated ({embed_time:.1f}ms)")
    print(f"   Embedding shape: {query_embedding.shape}")
    print(f"   First 5 values: {query_embedding[:5]}")
    
    # 2. Vector search
    print(f"\n🔍 Vector Similarity Search:")
    vector_results, vector_time = vector_search(conn, query_embedding, TOP_K)
    print_results(vector_results, "Vector Results", vector_time, show_similarity=True)
    
    # 3. Text search
    print(f"\n📝 Traditional Text Search:")
    text_results, text_time = text_search(conn, query_text, TOP_K)
    print_results(text_results, "Text Results", text_time, show_similarity=False)
    
    # 4. Comparison
    print(f"\n📊 Performance Comparison:")
    print(f"   Vector search: {vector_time:.1f}ms ({len(vector_results)} results)")
    print(f"   Text search:   {text_time:.1f}ms ({len(text_results)} results)")
    
    if vector_time < text_time:
        speedup = text_time / vector_time
        print(f"   ⚡ Vector is {speedup:.2f}x faster!")
    elif text_time < vector_time:
        speedup = vector_time / text_time
        print(f"   📝 Text is {speedup:.2f}x faster")
    else:
        print(f"   🤝 Same speed")

def interactive_mode(conn, tokenizer, model, device):
    """Interactive mode for custom queries"""
    print(f"\n{'='*80}")
    print(f"INTERACTIVE MODE")
    print(f"{'='*80}")
    print(f"\nEnter your search query (or 'quit' to exit):")
    
    while True:
        query = input("\n> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        test_single_query(conn, query, tokenizer, model, device)

def main():
    """Main execution"""
    print("=" * 80)
    print("TEST VECTOR SIMILARITY SEARCH")
    print("=" * 80)
    
    # Connect to database
    print(f"\n📊 Connecting to database: {DB_NAME}")
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME}")
        print(f"   ✅ Connected")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Load model
    tokenizer, model, device = load_model()
    
    # Run test queries
    print(f"\n{'='*80}")
    print(f"TESTING {len(TEST_QUERIES)} PREDEFINED QUERIES")
    print(f"{'='*80}")
    
    for query in TEST_QUERIES:
        test_single_query(conn, query, tokenizer, model, device)
        time.sleep(0.5)  # Small delay between queries
    
    # Interactive mode
    print(f"\n{'='*80}")
    response = input(f"\nTry custom queries in interactive mode? (y/n): ")
    if response.lower() == 'y':
        interactive_mode(conn, tokenizer, model, device)
    
    conn.close()
    
    print(f"\n{'='*80}")
    print(f"✅ Testing complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

