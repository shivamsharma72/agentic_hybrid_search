-- =====================================================
-- Step 3: Create Reviews Table (Laptop Reviews)
-- =====================================================
-- Run after 02_create_products_table.sql
-- Usage: psql -U your_username -d amazon_electronics_rag -f 03_create_reviews_table.sql

\c amazon_electronics_rag

-- Drop table if exists (for clean reinstall)
-- CAUTION: This will delete all data!
-- DROP TABLE IF EXISTS reviews_laptop CASCADE;

-- Create sequence for review_id
CREATE SEQUENCE IF NOT EXISTS reviews_review_id_seq;

-- Create reviews_laptop table
CREATE TABLE IF NOT EXISTS reviews_laptop (
    -- Primary identifier
    review_id           INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('reviews_review_id_seq'),
    
    -- User and product identifiers
    user_id             VARCHAR(100) NOT NULL,
    asin                VARCHAR(20) NOT NULL,        -- Product variant ASIN
    parent_asin         VARCHAR(20) NOT NULL,        -- Parent product ASIN
    
    -- Review content
    rating              REAL NOT NULL,
    title               TEXT,
    text                TEXT NOT NULL,
    
    -- Review metadata
    timestamp           BIGINT NOT NULL,             -- Unix timestamp
    helpful_vote        INTEGER NOT NULL DEFAULT 0,
    verified_purchase   BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Vector embedding (768-dimensional BLAIR-RoBERTa)
    blair_embedding     VECTOR(768),
    
    -- System timestamps
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional metadata
    images              JSONB,
    
    -- Constraints
    CONSTRAINT reviews_rating_check CHECK (rating >= 0 AND rating <= 5)
);

-- Create indexes for performance
\echo '📋 Creating indexes...'

-- Primary key index (automatically created)
-- CREATE UNIQUE INDEX reviews_laptop_pkey ON reviews_laptop(review_id);

-- Product relationship indexes
CREATE INDEX IF NOT EXISTS reviews_laptop_asin_idx ON reviews_laptop(asin);
CREATE INDEX IF NOT EXISTS reviews_laptop_parent_asin_idx ON reviews_laptop(parent_asin);
CREATE INDEX IF NOT EXISTS reviews_laptop_parent_asin_rating_idx ON reviews_laptop(parent_asin, rating);

-- User indexes
CREATE INDEX IF NOT EXISTS reviews_laptop_user_id_idx ON reviews_laptop(user_id);
CREATE INDEX IF NOT EXISTS reviews_laptop_user_id_parent_asin_idx ON reviews_laptop(user_id, parent_asin);

-- Filtering and sorting indexes
CREATE INDEX IF NOT EXISTS reviews_laptop_rating_idx ON reviews_laptop(rating);
CREATE INDEX IF NOT EXISTS reviews_laptop_timestamp_idx ON reviews_laptop(timestamp);
CREATE INDEX IF NOT EXISTS reviews_laptop_verified_purchase_idx ON reviews_laptop(verified_purchase);

-- NOTE: Vector indexes will be created AFTER data is loaded
-- See 05_create_vector_indexes.sql

-- Show table structure
\d reviews_laptop

-- Show table size
SELECT 
    'reviews_laptop' as table_name,
    pg_size_pretty(pg_total_relation_size('reviews_laptop')) as total_size,
    pg_size_pretty(pg_relation_size('reviews_laptop')) as table_size,
    pg_size_pretty(pg_indexes_size('reviews_laptop')) as indexes_size;

\echo '✅ Reviews table created successfully!'
\echo '📋 Next step: Run 04_load_data_from_parquet.py'

