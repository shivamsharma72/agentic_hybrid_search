#!/usr/bin/env python3
"""
Compare IVFFlat vs HNSW Index Performance
Tests both indexes with various queries and measures speed/accuracy
"""

import psycopg2
import time
import numpy as np
from datetime import datetime

DB_NAME = "amazon_electronics_rag"
NUM_TEST_QUERIES = 50  # Number of random products to test
TOP_K = 10  # Number of results to retrieve

def connect_db():
    """Connect to database"""
    conn = psycopg2.connect(f"dbname={DB_NAME}")
    return conn

def check_indexes(conn):
    """Check which indexes exist"""
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE tablename = 'products'
        AND indexdef LIKE '%blair_embedding%';
    """)
    indexes = [row[0] for row in cur.fetchall()]
    cur.close()
    
    has_ivfflat = any('ivfflat' in idx.lower() for idx in indexes)
    has_hnsw = any('hnsw' in idx.lower() for idx in indexes)
    
    return has_ivfflat, has_hnsw, indexes

def get_random_embeddings(conn, n):
    """Get N random product embeddings for testing"""
    cur = conn.cursor()
    cur.execute(f"""
        SELECT parent_asin, title, blair_embedding
        FROM products
        WHERE blair_embedding IS NOT NULL
        ORDER BY RANDOM()
        LIMIT {n};
    """)
    results = cur.fetchall()
    cur.close()
    return results

def test_ivfflat(conn, test_embedding, probes=50):
    """Test IVFFlat search"""
    cur = conn.cursor()
    cur.execute(f"SET ivfflat.probes = {probes};")
    
    start = time.time()
    cur.execute("""
        SELECT parent_asin
        FROM products
        ORDER BY blair_embedding <=> %s::vector
        LIMIT %s;
    """, (test_embedding, TOP_K))
    results = [row[0] for row in cur.fetchall()]
    duration = (time.time() - start) * 1000
    
    cur.close()
    return results, duration

def test_hnsw(conn, test_embedding):
    """Test HNSW search"""
    cur = conn.cursor()
    
    start = time.time()
    cur.execute("""
        SELECT parent_asin
        FROM products
        ORDER BY blair_embedding <=> %s::vector
        LIMIT %s;
    """, (test_embedding, TOP_K))
    results = [row[0] for row in cur.fetchall()]
    duration = (time.time() - start) * 1000
    
    cur.close()
    return results, duration

def calculate_recall(results1, results2):
    """Calculate recall: how many results overlap"""
    set1 = set(results1)
    set2 = set(results2)
    intersection = len(set1 & set2)
    recall = intersection / len(set1) if set1 else 0
    return recall

def main():
    print("=" * 80)
    print("COMPARE IVFFLAT vs HNSW INDEX PERFORMANCE")
    print("=" * 80)
    
    # Connect
    conn = connect_db()
    
    # Check indexes
    has_ivfflat, has_hnsw, indexes = check_indexes(conn)
    
    print(f"\n📊 Available Indexes:")
    for idx in indexes:
        idx_type = "HNSW" if 'hnsw' in idx else "IVFFlat" if 'ivfflat' in idx else "Other"
        print(f"   {idx_type:8s}: {idx}")
    
    if not has_ivfflat and not has_hnsw:
        print(f"\n❌ No vector indexes found!")
        print(f"   Please create at least one index first")
        return
    
    if not has_ivfflat:
        print(f"\n⚠️  IVFFlat index not found, skipping comparison")
        return
    
    if not has_hnsw:
        print(f"\n⚠️  HNSW index not found, skipping comparison")
        return
    
    # Get test embeddings
    print(f"\n🔄 Loading {NUM_TEST_QUERIES} random products for testing...")
    test_data = get_random_embeddings(conn, NUM_TEST_QUERIES)
    print(f"   ✅ Loaded {len(test_data)} test products")
    
    # Run tests
    print(f"\n🧪 Running performance comparison...")
    print(f"   Testing {NUM_TEST_QUERIES} queries, retrieving top {TOP_K} results each")
    
    ivfflat_times = []
    hnsw_times = []
    recalls = []
    
    for i, (asin, title, embedding) in enumerate(test_data, 1):
        # Test IVFFlat
        ivfflat_results, ivfflat_time = test_ivfflat(conn, embedding)
        ivfflat_times.append(ivfflat_time)
        
        # Test HNSW
        hnsw_results, hnsw_time = test_hnsw(conn, embedding)
        hnsw_times.append(hnsw_time)
        
        # Calculate recall (how similar are the results?)
        recall = calculate_recall(ivfflat_results, hnsw_results)
        recalls.append(recall)
        
        if i % 10 == 0:
            print(f"   Progress: {i}/{NUM_TEST_QUERIES} queries tested")
    
    # Calculate statistics
    print(f"\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\n📊 Query Performance (ms):")
    print(f"   IVFFlat (probes=50):")
    print(f"      Mean:   {np.mean(ivfflat_times):.2f}ms")
    print(f"      Median: {np.median(ivfflat_times):.2f}ms")
    print(f"      Min:    {np.min(ivfflat_times):.2f}ms")
    print(f"      Max:    {np.max(ivfflat_times):.2f}ms")
    
    print(f"\n   HNSW:")
    print(f"      Mean:   {np.mean(hnsw_times):.2f}ms")
    print(f"      Median: {np.median(hnsw_times):.2f}ms")
    print(f"      Min:    {np.min(hnsw_times):.2f}ms")
    print(f"      Max:    {np.max(hnsw_times):.2f}ms")
    
    print(f"\n⚡ Speed Comparison:")
    speedup = np.mean(ivfflat_times) / np.mean(hnsw_times)
    if speedup > 1:
        print(f"   HNSW is {speedup:.2f}x FASTER than IVFFlat")
    else:
        print(f"   IVFFlat is {1/speedup:.2f}x FASTER than HNSW")
    
    print(f"\n🎯 Result Overlap (Recall):")
    print(f"   Mean overlap:   {np.mean(recalls)*100:.1f}%")
    print(f"   Median overlap: {np.median(recalls)*100:.1f}%")
    print(f"   Min overlap:    {np.min(recalls)*100:.1f}%")
    print(f"   Max overlap:    {np.max(recalls)*100:.1f}%")
    
    print(f"\n📈 Interpretation:")
    mean_recall = np.mean(recalls)
    if mean_recall > 0.95:
        print(f"   ✅ Excellent: Both indexes return very similar results")
    elif mean_recall > 0.85:
        print(f"   ✅ Good: Both indexes return similar results")
    elif mean_recall > 0.70:
        print(f"   ⚠️  Moderate: Some differences in results")
    else:
        print(f"   ⚠️  Low: Significant differences in results")
    
    print(f"\n💡 Recommendation:")
    if speedup > 1.2 and mean_recall > 0.85:
        print(f"   Use HNSW: {speedup:.1f}x faster with similar accuracy")
    elif speedup < 0.8 and mean_recall > 0.85:
        print(f"   Use IVFFlat: Faster with similar accuracy")
    elif mean_recall < 0.80:
        print(f"   Consider tuning: Low recall suggests index parameters need adjustment")
    else:
        print(f"   Both are good: Choose based on your speed/accuracy preference")
    
    print("\n" + "=" * 80)
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


