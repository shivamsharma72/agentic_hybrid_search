-- ============================================================================
-- PRODUCTS TABLE SCHEMA
-- ============================================================================
-- Database: Amazon Electronics Hybrid RAG System
-- Table: products
-- Purpose: Store product metadata filtered from 5-core dataset
-- Total Expected Records: ~368,228 products
-- Source: Parquet files (filtered by Electronics_pureid_5core.csv)
-- Created: 2025-10-07
-- ============================================================================

-- Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop table if exists (for clean recreation)
DROP TABLE IF EXISTS products CASCADE;

-- Create products table
CREATE TABLE products (
    -- Primary Identifiers
    parent_asin         VARCHAR(10) PRIMARY KEY,
    
    -- Core Text Fields (for semantic search)
    title               TEXT NOT NULL,
    description         TEXT,                    -- Joined from array in parquet
    features            TEXT,                    -- Joined from array in parquet
    
    -- Rating & Review Metrics
    average_rating      REAL CHECK (average_rating >= 0 AND average_rating <= 5),
    rating_number       INTEGER CHECK (rating_number >= 0),
    
    -- Pricing
    price               REAL CHECK (price >= 0),  -- Converted from string/null
    
    -- Category Information
    main_category       VARCHAR(100),
    categories          TEXT[],                  -- PostgreSQL array for hierarchy
    
    -- Store/Brand
    store               VARCHAR(255),
    
    -- Flexible Structured Data (JSONB for efficient querying)
    details             JSONB,                   -- Product specifications
    images              JSONB,                   -- Image URLs (hi_res, large, thumb, variant)
    videos              JSONB,                   -- Video metadata (title, url, user_id)
    
    -- Vector Embeddings (for semantic search)
    blair_embedding     VECTOR(768),             -- BLAIR-RoBERTa embeddings (768 dimensions)
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Primary key index (automatically created)
-- CREATE UNIQUE INDEX idx_products_pkey ON products(parent_asin);

-- Indexes for filtering and sorting
CREATE INDEX idx_products_rating ON products(average_rating DESC);
CREATE INDEX idx_products_rating_count ON products(rating_number DESC);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_store ON products(store);
CREATE INDEX idx_products_main_category ON products(main_category);

-- GIN index for array operations on categories
CREATE INDEX idx_products_categories ON products USING GIN(categories);

-- GIN index for JSONB fields (for efficient JSON querying)
CREATE INDEX idx_products_details ON products USING GIN(details);

-- IVFFlat index for vector similarity search (pgvector)
-- Note: This should be created AFTER data is loaded for optimal performance
-- Uncomment after loading data:
-- CREATE INDEX idx_products_embedding ON products 
-- USING ivfflat (blair_embedding vector_cosine_ops) 
-- WITH (lists = 100);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE products IS 'Product metadata for electronics items with 5-core review coverage';
COMMENT ON COLUMN products.parent_asin IS 'Amazon Standard Identification Number (Primary Key)';
COMMENT ON COLUMN products.title IS 'Product title/name';
COMMENT ON COLUMN products.description IS 'Product description (joined from array)';
COMMENT ON COLUMN products.features IS 'Product features and highlights (joined from array)';
COMMENT ON COLUMN products.average_rating IS 'Average customer rating (1.0 to 5.0)';
COMMENT ON COLUMN products.rating_number IS 'Total number of ratings/reviews';
COMMENT ON COLUMN products.price IS 'Product price in USD';
COMMENT ON COLUMN products.main_category IS 'Top-level category';
COMMENT ON COLUMN products.categories IS 'Full category hierarchy path as array';
COMMENT ON COLUMN products.store IS 'Store or brand name';
COMMENT ON COLUMN products.details IS 'Product specifications and technical details (JSONB)';
COMMENT ON COLUMN products.images IS 'Product images with URLs for different sizes (JSONB)';
COMMENT ON COLUMN products.videos IS 'Product videos metadata (JSONB)';
COMMENT ON COLUMN products.blair_embedding IS 'BLAIR-RoBERTa semantic embeddings (768-dim vector)';
COMMENT ON COLUMN products.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN products.updated_at IS 'Timestamp when record was last updated';

-- ============================================================================
-- GRANT PERMISSIONS (adjust based on your database users)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON products TO app_user;

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

/*
-- Count total products
SELECT COUNT(*) FROM products;

-- Get products by category
SELECT parent_asin, title, average_rating 
FROM products 
WHERE 'Headphones' = ANY(categories)
ORDER BY rating_number DESC
LIMIT 10;

-- Price range query
SELECT parent_asin, title, price, average_rating
FROM products
WHERE price BETWEEN 50 AND 200
  AND average_rating >= 4.0
ORDER BY rating_number DESC
LIMIT 20;

-- Semantic search (after embeddings are populated)
SELECT parent_asin, title, average_rating,
       1 - (blair_embedding <=> '[query_vector]'::vector) as similarity
FROM products
WHERE blair_embedding IS NOT NULL
ORDER BY blair_embedding <=> '[query_vector]'::vector
LIMIT 10;

-- Category distribution
SELECT main_category, COUNT(*) as product_count
FROM products
GROUP BY main_category
ORDER BY product_count DESC;

-- Store analysis
SELECT store, COUNT(*) as products, AVG(average_rating) as avg_rating
FROM products
WHERE store IS NOT NULL
GROUP BY store
HAVING COUNT(*) >= 10
ORDER BY products DESC
LIMIT 20;
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

