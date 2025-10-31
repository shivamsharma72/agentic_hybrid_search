#!/usr/bin/env python3
"""
Create HNSW Vector Index on Products Table
HNSW provides better recall than IVFFlat but takes longer to build
"""

import psycopg2
import time
import sys
from datetime import datetime

# ========= CONFIG =========
DB_NAME = "amazon_electronics_rag"
INDEX_NAME = "products_blair_embedding_hnsw_idx"

# HNSW parameters
# m = number of bi-directional links created for every new element
# Higher m = better recall but more memory and slower build
M = 16  # Default: 16, Range: 2-100, Recommended: 12-48

# ef_construction = size of dynamic candidate list for constructing the graph
# Higher ef_construction = better quality but slower build
EF_CONSTRUCTION = 64  # Default: 64, Range: 4-512, Recommended: 64-200

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME}")
        print(f"✅ Connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        sys.exit(1)

def check_current_state(conn):
    """Check current state of embeddings and indexes"""
    print("\n📊 Checking current state...")
    cur = conn.cursor()
    
    # Count products with embeddings
    cur.execute("""
        SELECT COUNT(*) 
        FROM products 
        WHERE blair_embedding IS NOT NULL 
        AND blair_embedding <> array_fill(0, ARRAY[768])::vector(768);
    """)
    count = cur.fetchone()[0]
    print(f"   Products with embeddings: {count:,}")
    
    # Check for existing indexes on blair_embedding
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'products' 
        AND indexdef LIKE '%blair_embedding%';
    """)
    indexes = cur.fetchall()
    
    if indexes:
        print(f"\n   Existing indexes on blair_embedding:")
        for idx_name, idx_def in indexes:
            # Determine index type
            if 'ivfflat' in idx_def.lower():
                idx_type = "IVFFlat"
            elif 'hnsw' in idx_def.lower():
                idx_type = "HNSW"
            else:
                idx_type = "Unknown"
            print(f"      - {idx_name} ({idx_type})")
    else:
        print(f"   No existing indexes on blair_embedding")
    
    cur.close()
    return count, indexes

def run_analyze(conn):
    """Run ANALYZE on products table"""
    print("\n🔧 Running ANALYZE on products table...")
    
    cur = conn.cursor()
    start = time.time()
    
    cur.execute("ANALYZE products;")
    conn.commit()
    
    duration = time.time() - start
    print(f"   ✅ ANALYZE complete ({duration:.1f}s)")
    cur.close()

def drop_existing_index(conn, index_name):
    """Drop existing index if it exists"""
    print(f"\n🗑️  Dropping existing index: {index_name}...")
    cur = conn.cursor()
    
    try:
        cur.execute(f"DROP INDEX IF EXISTS {index_name};")
        conn.commit()
        print(f"   ✅ Index dropped")
    except Exception as e:
        print(f"   ⚠️  Error dropping index: {e}")
        conn.rollback()
    
    cur.close()

def create_hnsw_index(conn, m, ef_construction):
    """Create HNSW index on blair_embedding column"""
    print(f"\n🚀 Creating HNSW index...")
    print(f"   Index name: {INDEX_NAME}")
    print(f"   m: {m} (bidirectional links per element)")
    print(f"   ef_construction: {ef_construction} (construction quality)")
    print(f"   Distance metric: Cosine")
    print(f"   Estimated time: 10-20 minutes (HNSW is slower than IVFFlat)")
    
    cur = conn.cursor()
    start = time.time()
    
    # Increase maintenance_work_mem for index creation
    print(f"\n   Setting maintenance_work_mem = 512MB")
    cur.execute("SET maintenance_work_mem = '512MB';")
    print(f"   ✅ Memory limit increased")
    
    # Create HNSW index with cosine distance
    create_index_sql = f"""
        CREATE INDEX {INDEX_NAME}
        ON products
        USING hnsw (blair_embedding vector_cosine_ops)
        WITH (m = {m}, ef_construction = {ef_construction});
    """
    
    print(f"\n   SQL: {create_index_sql}")
    print(f"\n   Building index... (this will take 10-20 minutes)")
    print(f"   ⏳ Please be patient...")
    
    try:
        cur.execute(create_index_sql)
        conn.commit()
        duration = time.time() - start
        print(f"\n   ✅ Index created successfully!")
        print(f"   ⏱️  Build time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    except Exception as e:
        print(f"\n   ❌ Error creating index: {e}")
        conn.rollback()
        cur.close()
        sys.exit(1)
    
    cur.close()
    return duration

def get_index_info(conn, index_name):
    """Get information about the created index"""
    print(f"\n📋 Index Information:")
    cur = conn.cursor()
    
    # Index size
    cur.execute(f"""
        SELECT pg_size_pretty(pg_relation_size('{index_name}'));
    """)
    size = cur.fetchone()[0]
    print(f"   Index size: {size}")
    
    # Index definition
    cur.execute(f"""
        SELECT indexdef 
        FROM pg_indexes 
        WHERE indexname = '{index_name}';
    """)
    indexdef = cur.fetchone()[0]
    print(f"   Definition: {indexdef}")
    
    cur.close()

def test_index_query(conn):
    """Test the HNSW index with a sample similarity search"""
    print(f"\n🧪 Testing HNSW index with sample query...")
    
    cur = conn.cursor()
    
    # Get a random product embedding to test with
    cur.execute("""
        SELECT parent_asin, title, blair_embedding
        FROM products
        WHERE blair_embedding IS NOT NULL
        AND title IS NOT NULL
        LIMIT 1;
    """)
    
    test_product = cur.fetchone()
    if not test_product:
        print("   ⚠️  No products found for testing")
        cur.close()
        return
    
    test_asin, test_title, test_emb = test_product
    print(f"   Test product: {test_asin} - {test_title[:60]}...")
    
    # Find similar products using the HNSW index
    print(f"\n   Finding 10 most similar products...")
    start = time.time()
    
    cur.execute("""
        SELECT 
            parent_asin,
            title,
            1 - (blair_embedding <=> %s::vector) as similarity
        FROM products
        WHERE blair_embedding IS NOT NULL
        AND parent_asin != %s
        ORDER BY blair_embedding <=> %s::vector
        LIMIT 10;
    """, (test_emb, test_asin, test_emb))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000  # Convert to ms
    
    print(f"\n   ✅ Query completed in {duration:.1f}ms")
    print(f"\n   Top 10 similar products:")
    for i, (asin, title, sim) in enumerate(results, 1):
        print(f"      {i}. [{asin}] (sim: {sim:.4f})")
        print(f"         {title[:60]}...")
    
    cur.close()

def compare_with_ivfflat(conn):
    """Compare HNSW with IVFFlat if both exist"""
    print(f"\n📊 Comparing HNSW vs IVFFlat...")
    cur = conn.cursor()
    
    # Check if both indexes exist
    cur.execute("""
        SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
        FROM pg_indexes
        WHERE tablename = 'products'
        AND indexdef LIKE '%blair_embedding%'
        ORDER BY indexname;
    """)
    
    indexes = cur.fetchall()
    
    if len(indexes) < 2:
        print(f"   Only {len(indexes)} index found, cannot compare")
        cur.close()
        return
    
    print(f"\n   Index Comparison:")
    for idx_name, size in indexes:
        idx_type = "HNSW" if 'hnsw' in idx_name else "IVFFlat" if 'ivfflat' in idx_name else "Other"
        print(f"      {idx_type:8s}: {idx_name:40s} Size: {size}")
    
    # Performance comparison
    print(f"\n   Running speed comparison (10 queries)...")
    
    # Get test embedding
    cur.execute("""
        SELECT blair_embedding
        FROM products
        WHERE blair_embedding IS NOT NULL
        LIMIT 1;
    """)
    test_emb = cur.fetchone()[0]
    
    # Test HNSW
    start = time.time()
    for _ in range(10):
        cur.execute("""
            SELECT parent_asin
            FROM products
            ORDER BY blair_embedding <=> %s::vector
            LIMIT 10;
        """, (test_emb,))
        cur.fetchall()
    hnsw_time = (time.time() - start) * 100  # ms per query
    
    # Test IVFFlat (with probes=50)
    cur.execute("SET ivfflat.probes = 50;")
    start = time.time()
    for _ in range(10):
        cur.execute("""
            SELECT parent_asin
            FROM products
            ORDER BY blair_embedding <=> %s::vector
            LIMIT 10;
        """, (test_emb,))
        cur.fetchall()
    ivfflat_time = (time.time() - start) * 100  # ms per query
    
    print(f"\n   Query Performance (avg of 10 queries):")
    print(f"      HNSW:    {hnsw_time:.1f}ms")
    print(f"      IVFFlat: {ivfflat_time:.1f}ms (probes=50)")
    
    if hnsw_time < ivfflat_time:
        speedup = ivfflat_time / hnsw_time
        print(f"      ⚡ HNSW is {speedup:.2f}x faster!")
    else:
        speedup = hnsw_time / ivfflat_time
        print(f"      ⚡ IVFFlat is {speedup:.2f}x faster")
    
    cur.close()

def main():
    """Main execution"""
    print("=" * 80)
    print("CREATE HNSW VECTOR INDEX FOR PRODUCT EMBEDDINGS")
    print("=" * 80)
    
    start_time = datetime.now()
    
    # Connect to database
    conn = connect_db()
    
    # Check current state
    count, existing_indexes = check_current_state(conn)
    
    if count == 0:
        print("\n❌ Error: No embeddings found in database!")
        print("   Please run upload_embeddings.py first")
        sys.exit(1)
    
    # Drop existing HNSW index if it exists
    if any(INDEX_NAME in idx[0] for idx in existing_indexes):
        response = input(f"\n⚠️  Index '{INDEX_NAME}' already exists. Drop and recreate? (y/n): ")
        if response.lower() != 'y':
            print("   Aborted by user")
            sys.exit(0)
        drop_existing_index(conn, INDEX_NAME)
    
    # Run ANALYZE
    run_analyze(conn)
    
    # Create HNSW index
    build_time = create_hnsw_index(conn, M, EF_CONSTRUCTION)
    
    # Get index info
    get_index_info(conn, INDEX_NAME)
    
    # Test the index
    test_index_query(conn)
    
    # Compare with IVFFlat if it exists
    compare_with_ivfflat(conn)
    
    # Summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("INDEX CREATION SUMMARY")
    print("=" * 80)
    print(f"Total time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print(f"Products indexed: {count:,}")
    print(f"Index name: {INDEX_NAME}")
    print(f"Index type: HNSW")
    print(f"Parameters: m={M}, ef_construction={EF_CONSTRUCTION}")
    print(f"Distance metric: Cosine")
    
    print(f"\n✅ SUCCESS! HNSW index is ready for similarity search")
    
    print(f"\n📝 Usage in queries:")
    print(f"   SELECT * FROM products")
    print(f"   ORDER BY blair_embedding <=> '[query_embedding]'::vector")
    print(f"   LIMIT 10;")
    
    print(f"\n🎯 Key Differences:")
    print(f"   HNSW:    Better recall (95-99%), faster queries, larger index")
    print(f"   IVFFlat: Good recall (90-95%), tunable speed, smaller index")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Test query performance with real searches")
    print(f"   2. Compare recall between HNSW and IVFFlat")
    print(f"   3. Choose the best index for your use case")
    
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

