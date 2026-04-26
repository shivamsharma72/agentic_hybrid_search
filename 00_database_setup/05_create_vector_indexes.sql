-- =====================================================
-- Step 5: Create Vector Similarity Indexes
-- =====================================================
-- Run AFTER data is loaded (after 04_load_data_from_parquet.py)
-- Usage: psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql

-- IMPORTANT: Vector indexes should be created AFTER data is loaded
-- for optimal performance and index quality

\c amazon_electronics_rag

\echo '==================================================================================='
\echo '🎯 CREATING VECTOR SIMILARITY INDEXES'
\echo '==================================================================================='
\echo ''
\echo 'This process will create HNSW indexes for fast vector similarity search.'
\echo 'HNSW (Hierarchical Navigable Small World) provides excellent query performance.'
\echo ''
\echo 'Expected time:'
\echo '  - Products (5,455 vectors):  ~30-60 seconds'
\echo '  - Reviews (350,105 vectors): ~10-20 minutes'
\echo ''
\echo 'Press Ctrl+C to cancel, or press Enter to continue...'
\pause

-- ===========================
-- Products Vector Index
-- ===========================
\echo ''
\echo '[1/2] Creating HNSW index for products_laptop...'
\echo '  Parameters: m=16, ef_construction=64'
\echo '  Vector dimension: 768'
\echo '  Distance metric: cosine'
\echo ''

-- Drop existing indexes if recreating
-- DROP INDEX IF EXISTS products_laptop_blair_embedding_idx;
-- DROP INDEX IF EXISTS products_laptop_blair_embedding_idx1;

-- Create HNSW index for products
-- m=16: number of connections per layer (higher = better recall, slower build)
-- ef_construction=64: size of dynamic candidate list (higher = better quality)
CREATE INDEX IF NOT EXISTS products_laptop_blair_embedding_idx1 
ON products_laptop 
USING hnsw (blair_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

\echo '  ✅ Products HNSW index created!'

-- Optional: Create IVFFlat index (alternative, faster build but slower queries)
-- Uncomment if you want both index types for comparison
-- \echo ''
-- \echo '  Creating IVFFlat index for products_laptop (optional)...'
-- CREATE INDEX IF NOT EXISTS products_laptop_blair_embedding_idx 
-- ON products_laptop 
-- USING ivfflat (blair_embedding vector_cosine_ops)
-- WITH (lists = 500);
-- \echo '  ✅ Products IVFFlat index created!'

-- ===========================
-- Reviews Vector Index
-- ===========================
\echo ''
\echo '[2/2] Creating HNSW index for reviews_laptop...'
\echo '  Parameters: m=16, ef_construction=64'
\echo '  Vector dimension: 768'
\echo '  Distance metric: cosine'
\echo '  ⏱️  This may take 10-20 minutes for 350K reviews...'
\echo ''

-- Drop existing index if recreating
-- DROP INDEX IF EXISTS reviews_laptop_blair_embedding_idx;

-- Create HNSW index for reviews
CREATE INDEX IF NOT EXISTS reviews_laptop_blair_embedding_idx 
ON reviews_laptop 
USING hnsw (blair_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

\echo '  ✅ Reviews HNSW index created!'

-- ===========================
-- Verify Indexes
-- ===========================
\echo ''
\echo '==================================================================================='
\echo '✅ VECTOR INDEXES CREATED SUCCESSFULLY!'
\echo '==================================================================================='
\echo ''
\echo '📋 Verifying indexes...'
\echo ''

-- Show all indexes on products_laptop
\echo '📦 Products Indexes:'
\di+ products_laptop_*

-- Show all indexes on reviews_laptop
\echo ''
\echo '💬 Reviews Indexes:'
\di+ reviews_laptop_*

-- Show table sizes with indexes
\echo ''
\echo '📊 Final Table Sizes:'
SELECT 
    'products_laptop' as table_name,
    (SELECT COUNT(*) FROM products_laptop) as rows,
    pg_size_pretty(pg_total_relation_size('products_laptop')) as total_size,
    pg_size_pretty(pg_relation_size('products_laptop')) as table_size,
    pg_size_pretty(pg_indexes_size('products_laptop')) as indexes_size
UNION ALL
SELECT 
    'reviews_laptop' as table_name,
    (SELECT COUNT(*) FROM reviews_laptop) as rows,
    pg_size_pretty(pg_total_relation_size('reviews_laptop')) as total_size,
    pg_size_pretty(pg_relation_size('reviews_laptop')) as table_size,
    pg_size_pretty(pg_indexes_size('reviews_laptop')) as indexes_size;

\echo ''
\echo '==================================================================================='
\echo '🎉 SETUP COMPLETE!'
\echo '==================================================================================='
\echo ''
\echo '📋 Next step: Run 06_verify_setup.py to test vector similarity search'
\echo ''

