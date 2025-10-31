#!/usr/bin/env python3
"""
Interactive Vector Index Testing
Test IVFFlat and HNSW indexes by finding products similar to existing products
No model loading required - uses existing embeddings
"""

import psycopg2
import time
from datetime import datetime

# ========= CONFIG =========
DB_NAME = "amazon_electronics_rag"
TOP_K = 10  # Number of results to return
IVFFLAT_PROBES = 50  # Probes for IVFFlat

def connect_db():
    """Connect to database"""
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def check_indexes(conn):
    """Check which indexes exist"""
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
        FROM pg_indexes
        WHERE tablename = 'products'
        AND indexdef LIKE '%blair_embedding%'
        ORDER BY indexname;
    """)
    indexes = cur.fetchall()
    cur.close()
    
    has_ivfflat = any('ivfflat' in idx[0].lower() for idx in indexes)
    has_hnsw = any('hnsw' in idx[0].lower() for idx in indexes)
    
    return has_ivfflat, has_hnsw, indexes

def search_products_by_keyword(conn, keyword, limit=20, max_price=None, min_rating=None):
    """Search products by title keyword with optional filters"""
    cur = conn.cursor()
    
    # Build query with filters
    query = """
        SELECT parent_asin, title, average_rating, rating_number, price
        FROM products
        WHERE title ILIKE %s
        AND blair_embedding IS NOT NULL
    """
    params = [f"%{keyword}%"]
    
    # Add price filter
    if max_price is not None:
        query += " AND price IS NOT NULL AND price <= %s"
        params.append(max_price)
    
    # Add rating filter
    if min_rating is not None:
        query += " AND average_rating IS NOT NULL AND average_rating >= %s"
        params.append(min_rating)
    
    query += " ORDER BY rating_number DESC NULLS LAST LIMIT %s;"
    params.append(limit)
    
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    return results

def get_product_by_asin(conn, asin):
    """Get product details and embedding by ASIN"""
    cur = conn.cursor()
    cur.execute("""
        SELECT parent_asin, title, average_rating, rating_number, price, blair_embedding
        FROM products
        WHERE parent_asin = %s
        AND blair_embedding IS NOT NULL;
    """, (asin,))
    result = cur.fetchone()
    cur.close()
    return result

def search_similar_ivfflat(conn, embedding, exclude_asin=None):
    """Search using IVFFlat index"""
    cur = conn.cursor()
    
    # Set probes
    cur.execute(f"SET ivfflat.probes = {IVFFLAT_PROBES};")
    
    start = time.time()
    
    if exclude_asin:
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
            AND parent_asin != %s
            ORDER BY blair_embedding <=> %s::vector
            LIMIT %s;
        """, (embedding, exclude_asin, embedding, TOP_K))
    else:
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
        """, (embedding, embedding, TOP_K))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000
    
    cur.close()
    return results, duration

def search_similar_hnsw(conn, embedding, exclude_asin=None):
    """Search using HNSW index"""
    cur = conn.cursor()
    
    start = time.time()
    
    if exclude_asin:
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
            AND parent_asin != %s
            ORDER BY blair_embedding <=> %s::vector
            LIMIT %s;
        """, (embedding, exclude_asin, embedding, TOP_K))
    else:
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
        """, (embedding, embedding, TOP_K))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000
    
    cur.close()
    return results, duration

def print_product(asin, title, rating, num_ratings, price, similarity=None, index=None):
    """Pretty print a single product"""
    if index:
        print(f"      {index}. [{asin}]", end="")
    else:
        print(f"      [{asin}]", end="")
    
    if similarity is not None:
        print(f" (similarity: {similarity:.4f})")
    else:
        print()
    
    # Title
    title_display = title[:70] + "..." if len(title) > 70 else title
    print(f"         {title_display}")
    
    # Rating and price
    rating_str = f"⭐ {rating:.1f}" if rating else "No rating"
    num_ratings_str = f"({num_ratings:,})" if num_ratings else "(0)"
    price_str = f"${price:.2f}" if price else "N/A"
    print(f"         {rating_str} {num_ratings_str} | {price_str}")

def print_results(results, search_type, duration):
    """Print search results"""
    print(f"\n   {search_type} ({duration:.1f}ms):")
    
    if not results:
        print(f"      ❌ No results found")
        return
    
    for i, row in enumerate(results, 1):
        asin, title, rating, num_ratings, price, similarity = row
        print_product(asin, title, rating, num_ratings, price, similarity, i)

def compare_results(ivfflat_results, hnsw_results):
    """Compare overlap between IVFFlat and HNSW results"""
    ivfflat_asins = set([row[0] for row in ivfflat_results])
    hnsw_asins = set([row[0] for row in hnsw_results])
    
    overlap = len(ivfflat_asins & hnsw_asins)
    total = len(ivfflat_asins)
    
    return overlap, total

def interactive_mode(conn, has_ivfflat, has_hnsw):
    """Interactive mode for testing indexes"""
    print(f"\n{'='*80}")
    print(f"INTERACTIVE INDEX TESTING")
    print(f"{'='*80}")
    print(f"\nHow to use:")
    print(f"  1. Search for a product by keyword (e.g., 'wireless headphones')")
    print(f"  2. Select a product by entering its number")
    print(f"  3. See similar products using the vector indexes")
    print(f"  4. Compare IVFFlat vs HNSW performance")
    print(f"\nCommands:")
    print(f"  '<keyword>'                  - Search for products (e.g., 'laptop')")
    print(f"  '<keyword> under <price>'    - Filter by max price (e.g., 'laptop under 1000')")
    print(f"  '<keyword> rating <rating>'  - Filter by min rating (e.g., 'headphones rating 4.5')")
    print(f"  'asin <ASIN>'                - Look up product by ASIN")
    print(f"  'quit' or 'exit'             - Exit the program")
    print(f"\nExamples:")
    print(f"  > laptop under 1000")
    print(f"  > wireless headphones rating 4.5")
    print(f"  > gaming mouse under 50")
    
    while True:
        print(f"\n{'='*80}")
        user_input = input("\n> ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        # Search by ASIN
        if user_input.lower().startswith('asin '):
            asin = user_input[5:].strip()
            if not asin:
                print("⚠️  Please provide an ASIN")
                continue
            
            test_product(conn, asin, has_ivfflat, has_hnsw)
            continue
        
        # Parse search query with filters
        keyword = user_input
        max_price = None
        min_rating = None
        
        # Check for "under <price>" filter
        if ' under ' in keyword.lower():
            parts = keyword.lower().split(' under ')
            keyword = parts[0].strip()
            try:
                max_price = float(parts[1].strip().replace('$', '').replace(',', ''))
                print(f"💰 Filtering by max price: ${max_price:.2f}")
            except:
                print(f"⚠️  Invalid price format, ignoring price filter")
        
        # Check for "rating <rating>" filter
        if ' rating ' in keyword.lower():
            parts = keyword.lower().split(' rating ')
            keyword = parts[0].strip()
            try:
                min_rating = float(parts[1].strip())
                print(f"⭐ Filtering by min rating: {min_rating}")
            except:
                print(f"⚠️  Invalid rating format, ignoring rating filter")
        
        if not keyword:
            print("⚠️  Please provide a search keyword")
            continue
        
        print(f"\n🔍 Searching for: '{keyword}'...")
        results = search_products_by_keyword(conn, keyword, max_price=max_price, min_rating=min_rating)
        
        if not results:
            print(f"   ❌ No products found")
            if max_price or min_rating:
                print(f"   💡 Tip: Try relaxing your filters or using a different keyword")
            continue
        
        print(f"\n   Found {len(results)} products:")
        for i, (asin, title, rating, num_ratings, price) in enumerate(results, 1):
            print(f"\n      {i}. ", end="")
            print_product(asin, title, rating, num_ratings, price)
        
        # Let user select a product
        print(f"\nEnter product number to find similar items (or press Enter to skip):")
        selection = input("> ").strip()
        
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(results):
                selected_asin = results[idx][0]
                test_product(conn, selected_asin, has_ivfflat, has_hnsw)
            else:
                print(f"⚠️  Invalid selection")

def test_product(conn, asin, has_ivfflat, has_hnsw):
    """Test similarity search for a specific product"""
    print(f"\n{'='*80}")
    print(f"Finding products similar to: {asin}")
    print(f"{'='*80}")
    
    # Get product details
    product = get_product_by_asin(conn, asin)
    
    if not product:
        print(f"❌ Product not found or has no embedding")
        return
    
    asin, title, rating, num_ratings, price, embedding = product
    
    print(f"\n📦 Selected Product:")
    print_product(asin, title, rating, num_ratings, price)
    
    # Test IVFFlat
    if has_ivfflat:
        print(f"\n🔍 Searching with IVFFlat index (probes={IVFFLAT_PROBES})...")
        ivfflat_results, ivfflat_time = search_similar_ivfflat(conn, embedding, exclude_asin=asin)
        print_results(ivfflat_results, "IVFFlat Results", ivfflat_time)
    
    # Test HNSW
    if has_hnsw:
        print(f"\n🚀 Searching with HNSW index...")
        hnsw_results, hnsw_time = search_similar_hnsw(conn, embedding, exclude_asin=asin)
        print_results(hnsw_results, "HNSW Results", hnsw_time)
    
    # Compare if both exist
    if has_ivfflat and has_hnsw:
        print(f"\n📊 Comparison:")
        print(f"   IVFFlat: {ivfflat_time:.1f}ms")
        print(f"   HNSW:    {hnsw_time:.1f}ms")
        
        if ivfflat_time < hnsw_time:
            speedup = hnsw_time / ivfflat_time
            print(f"   ⚡ IVFFlat is {speedup:.2f}x faster")
        else:
            speedup = ivfflat_time / hnsw_time
            print(f"   ⚡ HNSW is {speedup:.2f}x faster")
        
        overlap, total = compare_results(ivfflat_results, hnsw_results)
        print(f"\n   Result overlap: {overlap}/{total} ({overlap/total*100:.1f}%)")
        
        if overlap == total:
            print(f"   ✅ Perfect match: Both indexes returned the same results")
        elif overlap/total > 0.8:
            print(f"   ✅ Good: High overlap between results")
        else:
            print(f"   ⚠️  Moderate: Some differences in results")

def main():
    """Main execution"""
    print("=" * 80)
    print("INTERACTIVE VECTOR INDEX TESTING")
    print("=" * 80)
    
    # Connect
    conn = connect_db()
    if not conn:
        return
    
    print(f"\n✅ Connected to database: {DB_NAME}")
    
    # Check indexes
    has_ivfflat, has_hnsw, indexes = check_indexes(conn)
    
    print(f"\n📊 Available Indexes:")
    if indexes:
        for idx_name, size in indexes:
            idx_type = "HNSW" if 'hnsw' in idx_name else "IVFFlat" if 'ivfflat' in idx_name else "Other"
            print(f"   ✅ {idx_type:8s}: {idx_name} ({size})")
    else:
        print(f"   ❌ No vector indexes found")
        print(f"   Please create an index first using create_ivfflat_index.py or create_hnsw_index.py")
        conn.close()
        return
    
    if not has_ivfflat and not has_hnsw:
        print(f"\n❌ No vector indexes found!")
        conn.close()
        return
    
    # Start interactive mode
    interactive_mode(conn, has_ivfflat, has_hnsw)
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

