-- ===========================================
-- REVIEWS TABLE SCHEMA
-- ===========================================
-- Project: Graph-Assisted Hybrid RAG for Amazon Electronics Recommendations
-- Database: PostgreSQL 17.6 with pgvector 0.8.1
-- Purpose: Store filtered Amazon Electronics review data
-- Source: 10 Parquet files (15,615,410 reviews)
-- Created: 2025-10-07
-- ===========================================

-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- ===========================================
-- DROP TABLE (if needed for clean slate)
-- ===========================================
-- Uncomment to drop existing table:
-- DROP TABLE IF EXISTS reviews CASCADE;

-- ===========================================
-- CREATE REVIEWS TABLE
-- ===========================================

CREATE TABLE IF NOT EXISTS reviews (
    -- =====================================
    -- PRIMARY KEY
    -- =====================================
    review_id SERIAL PRIMARY KEY,
    
    -- =====================================
    -- CORE IDENTIFIERS
    -- =====================================
    user_id VARCHAR(100) NOT NULL,
    asin VARCHAR(20) NOT NULL,
    parent_asin VARCHAR(20) NOT NULL,
    
    -- =====================================
    -- REVIEW CONTENT
    -- =====================================
    rating REAL NOT NULL CHECK (rating >= 0 AND rating <= 5),
    title TEXT,
    text TEXT NOT NULL,
    
    -- =====================================
    -- METADATA
    -- =====================================
    timestamp BIGINT NOT NULL,
    helpful_vote INTEGER NOT NULL DEFAULT 0,
    verified_purchase BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- =====================================
    -- EMBEDDING VECTORS (for future use)
    -- =====================================
    -- BLAIR-RoBERTa generates 768-dimensional embeddings
    -- Will be populated in Phase 3 (Embedding Generation)
    blair_embedding VECTOR(768),
    
    -- =====================================
    -- TIMESTAMPS
    -- =====================================
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- INDEXES FOR PERFORMANCE
-- ===========================================

-- Index on user_id for user-based queries
CREATE INDEX IF NOT EXISTS idx_reviews_user_id 
ON reviews(user_id);

-- Index on parent_asin for product-based queries
CREATE INDEX IF NOT EXISTS idx_reviews_parent_asin 
ON reviews(parent_asin);

-- Index on asin for variant-level queries
CREATE INDEX IF NOT EXISTS idx_reviews_asin 
ON reviews(asin);

-- Index on rating for filtering by rating
CREATE INDEX IF NOT EXISTS idx_reviews_rating 
ON reviews(rating);

-- Index on timestamp for temporal queries
CREATE INDEX IF NOT EXISTS idx_reviews_timestamp 
ON reviews(timestamp);

-- Index on verified_purchase for filtering verified reviews
CREATE INDEX IF NOT EXISTS idx_reviews_verified_purchase 
ON reviews(verified_purchase);

-- Composite index for user-product pairs (common query pattern)
CREATE INDEX IF NOT EXISTS idx_reviews_user_product 
ON reviews(user_id, parent_asin);

-- Composite index for product-rating queries
CREATE INDEX IF NOT EXISTS idx_reviews_product_rating 
ON reviews(parent_asin, rating);

-- Full-text search index on review text (optional, for text search)
-- Uncomment if you need full-text search capability:
-- CREATE INDEX IF NOT EXISTS idx_reviews_text_fts 
-- ON reviews USING GIN(to_tsvector('english', text));

-- ===========================================
-- FOREIGN KEY CONSTRAINT
-- ===========================================

-- Link to products table
-- This ensures referential integrity between reviews and products
ALTER TABLE reviews 
ADD CONSTRAINT fk_reviews_parent_asin 
FOREIGN KEY (parent_asin) 
REFERENCES products(parent_asin) 
ON DELETE CASCADE;

-- ===========================================
-- TABLE COMMENTS (Documentation)
-- ===========================================

COMMENT ON TABLE reviews IS 
'Amazon Electronics reviews filtered by 5-core dataset. Contains 15.6M reviews where both user and product have at least 5 interactions.';

COMMENT ON COLUMN reviews.review_id IS 
'Auto-incrementing primary key for each review';

COMMENT ON COLUMN reviews.user_id IS 
'Amazon user ID (anonymized)';

COMMENT ON COLUMN reviews.asin IS 
'Product ASIN (variant-level identifier)';

COMMENT ON COLUMN reviews.parent_asin IS 
'Parent product ASIN (links to products table)';

COMMENT ON COLUMN reviews.rating IS 
'Product rating from 1.0 to 5.0';

COMMENT ON COLUMN reviews.title IS 
'Review title/headline';

COMMENT ON COLUMN reviews.text IS 
'Full review text content';

COMMENT ON COLUMN reviews.timestamp IS 
'Unix timestamp in milliseconds';

COMMENT ON COLUMN reviews.helpful_vote IS 
'Number of helpful votes this review received';

COMMENT ON COLUMN reviews.verified_purchase IS 
'Whether the purchase was verified by Amazon';

COMMENT ON COLUMN reviews.blair_embedding IS 
'768-dimensional BLAIR-RoBERTa embedding (to be populated in Phase 3)';

-- ===========================================
-- VACUUM AND ANALYZE
-- ===========================================

-- Run VACUUM and ANALYZE after bulk loading for optimal performance
-- These commands will be run automatically by the loading script

-- ===========================================
-- TABLE STATISTICS
-- ===========================================

-- Expected data:
-- - Total reviews: 15,615,410
-- - Date range: 1996-2024
-- - Average review length: ~500 characters
-- - Storage estimate: ~12-15 GB (with indexes)
-- - Vector storage (when populated): ~45 GB additional

-- ===========================================
-- USAGE EXAMPLES
-- ===========================================

-- Get all reviews for a product:
-- SELECT * FROM reviews WHERE parent_asin = 'B0XXXXX' ORDER BY timestamp DESC;

-- Get user's review history:
-- SELECT * FROM reviews WHERE user_id = 'AXXXXX' ORDER BY timestamp DESC;

-- Get highly-rated verified reviews:
-- SELECT * FROM reviews 
-- WHERE rating >= 4.0 AND verified_purchase = TRUE 
-- ORDER BY helpful_vote DESC LIMIT 100;

-- Get review count by product:
-- SELECT parent_asin, COUNT(*) as review_count, AVG(rating) as avg_rating
-- FROM reviews GROUP BY parent_asin ORDER BY review_count DESC;

-- Full-text search (if FTS index is created):
-- SELECT * FROM reviews 
-- WHERE to_tsvector('english', text) @@ to_tsquery('english', 'excellent & quality')
-- ORDER BY helpful_vote DESC LIMIT 50;

-- ===========================================
-- MAINTENANCE NOTES
-- ===========================================

-- 1. Run VACUUM ANALYZE after bulk loading
-- 2. Update table statistics regularly: ANALYZE reviews;
-- 3. Rebuild indexes if fragmented: REINDEX TABLE reviews;
-- 4. Monitor table size: SELECT pg_size_pretty(pg_total_relation_size('reviews'));
-- 5. Check index usage: SELECT * FROM pg_stat_user_indexes WHERE relname = 'reviews';

-- ===========================================
-- END OF SCHEMA
-- ===========================================

