#!/usr/bin/env python3
"""
Create IVFFlat Vector Index on Products Table
Enables fast similarity search for product embeddings
"""

import psycopg2
import time
import sys
from datetime import datetime

# ========= CONFIG =========
DB_NAME = "amazon_electronics_rag"
INDEX_NAME = "products_blair_embedding_ivfflat_idx"

# IVFFlat parameters
# lists = sqrt(rows) is a good starting point
# For 348K products: sqrt(348228) ≈ 590
# We'll use 500 for round number
LISTS = 500  # Number of clusters

# Probes for search (will set later)
# More probes = better accuracy but slower
# Good default: lists/10 = 50
PROBES = 50

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
        print(f"\n   ⚠️  Found {len(indexes)} existing index(es):")
        for idx_name, idx_def in indexes:
            print(f"      - {idx_name}")
            print(f"        {idx_def[:100]}...")
    else:
        print(f"   No existing indexes on blair_embedding")
    
    cur.close()
    return count, indexes

def run_analyze(conn):
    """Run ANALYZE on products table"""
    print("\n🔧 Running ANALYZE on products table...")
    print("   (This helps PostgreSQL optimize queries)")
    
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

def create_ivfflat_index(conn, lists):
    """Create IVFFlat index on blair_embedding column"""
    print(f"\n🚀 Creating IVFFlat index...")
    print(f"   Index name: {INDEX_NAME}")
    print(f"   Lists (clusters): {lists}")
    print(f"   Distance metric: Cosine (best for embeddings)")
    print(f"   Estimated time: 2-5 minutes")
    
    cur = conn.cursor()
    start = time.time()
    
    # Increase maintenance_work_mem for index creation
    print(f"\n   Setting maintenance_work_mem = 256MB (required: ~127 MB)")
    cur.execute("SET maintenance_work_mem = '256MB';")
    print(f"   ✅ Memory limit increased")
    
    # Create index with cosine distance (1 - cosine_similarity)
    # Using vector_cosine_ops for cosine distance
    create_index_sql = f"""
        CREATE INDEX {INDEX_NAME}
        ON products
        USING ivfflat (blair_embedding vector_cosine_ops)
        WITH (lists = {lists});
    """
    
    print(f"\n   SQL: {create_index_sql}")
    print(f"\n   Building index... (this will take a few minutes)")
    
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

def set_probes(conn, probes):
    """Set the number of probes for IVFFlat searches"""
    print(f"\n⚙️  Setting search parameters...")
    print(f"   Probes: {probes} (more probes = better accuracy, slower search)")
    
    cur = conn.cursor()
    
    # Set probes for this session
    cur.execute(f"SET ivfflat.probes = {probes};")
    
    print(f"   ✅ Search probes set to {probes}")
    print(f"   💡 Add 'SET ivfflat.probes = {probes};' to queries for optimal search")
    
    cur.close()

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

def test_index_query(conn, probes):
    """Test the index with a sample similarity search"""
    print(f"\n🧪 Testing index with sample query...")
    
    cur = conn.cursor()
    
    # Set probes
    cur.execute(f"SET ivfflat.probes = {probes};")
    
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
    
    # Find similar products using the index
    print(f"\n   Finding 5 most similar products...")
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
        LIMIT 5;
    """, (test_emb, test_asin, test_emb))
    
    results = cur.fetchall()
    duration = (time.time() - start) * 1000  # Convert to ms
    
    print(f"\n   ✅ Query completed in {duration:.1f}ms")
    print(f"\n   Top 5 similar products:")
    for i, (asin, title, sim) in enumerate(results, 1):
        print(f"      {i}. [{asin}] {title[:60]}...")
        print(f"         Similarity: {sim:.4f}")
    
    cur.close()

def main():
    """Main execution"""
    print("=" * 80)
    print("CREATE IVFFLAT VECTOR INDEX FOR PRODUCT EMBEDDINGS")
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
    
    # Drop existing index if it exists
    if any(INDEX_NAME in idx[0] for idx in existing_indexes):
        response = input(f"\n⚠️  Index '{INDEX_NAME}' already exists. Drop and recreate? (y/n): ")
        if response.lower() != 'y':
            print("   Aborted by user")
            sys.exit(0)
        drop_existing_index(conn, INDEX_NAME)
    
    # Run ANALYZE
    run_analyze(conn)
    
    # Create IVFFlat index
    build_time = create_ivfflat_index(conn, LISTS)
    
    # Set probes
    set_probes(conn, PROBES)
    
    # Get index info
    get_index_info(conn, INDEX_NAME)
    
    # Test the index
    test_index_query(conn, PROBES)
    
    # Summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print("INDEX CREATION SUMMARY")
    print("=" * 80)
    print(f"Total time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print(f"Products indexed: {count:,}")
    print(f"Index name: {INDEX_NAME}")
    print(f"Index type: IVFFlat")
    print(f"Lists: {LISTS}")
    print(f"Probes: {PROBES}")
    print(f"Distance metric: Cosine")
    
    print(f"\n✅ SUCCESS! Vector index is ready for similarity search")
    
    print(f"\n📝 Usage in queries:")
    print(f"   1. Set probes: SET ivfflat.probes = {PROBES};")
    print(f"   2. Search: SELECT * FROM products")
    print(f"      ORDER BY blair_embedding <=> '[query_embedding]'::vector")
    print(f"      LIMIT 10;")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Test similarity search with real queries")
    print(f"   2. Tune probes parameter (50-100 for better accuracy)")
    print(f"   3. Build HNSW index for comparison (optional)")
    
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

