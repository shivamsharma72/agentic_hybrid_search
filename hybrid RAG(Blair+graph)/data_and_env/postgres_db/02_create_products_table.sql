-- =====================================================
-- Step 2: Create Products Table (Laptop Products)
-- =====================================================
-- Run after 01_create_database.sql
-- Usage: psql -U your_username -d amazon_electronics_rag -f 02_create_products_table.sql

\c amazon_electronics_rag

-- Drop table if exists (for clean reinstall)
-- CAUTION: This will delete all data!
-- DROP TABLE IF EXISTS products_laptop CASCADE;

-- Create products_laptop table
CREATE TABLE IF NOT EXISTS products_laptop (
    -- Primary identifiers
    parent_asin         VARCHAR(10) NOT NULL PRIMARY KEY,
    
    -- Basic product information
    title               TEXT NOT NULL,
    description         TEXT,
    features            TEXT,
    
    -- Rating and price information
    average_rating      REAL,
    rating_number       INTEGER,
    price               REAL,
    
    -- Category information
    main_category       VARCHAR(100),
    categories          TEXT[],
    store               VARCHAR(255),
    
    -- Complex data (JSON)
    details             JSONB,
    images              JSONB,
    videos              JSONB,
    
    -- Vector embedding (768-dimensional BLAIR-RoBERTa)
    blair_embedding     VECTOR(768),
    
    -- Metadata timestamps
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    -- Tokenized arrays for search
    description_array   TEXT[],
    features_array      TEXT[],
    
    -- Constraints
    CONSTRAINT products_average_rating_check CHECK (average_rating >= 0 AND average_rating <= 5),
    CONSTRAINT products_rating_number_check CHECK (rating_number >= 0),
    CONSTRAINT products_price_check CHECK (price >= 0)
);

-- Create indexes for performance
\echo '📋 Creating indexes...'

-- Primary key index (automatically created)
-- CREATE UNIQUE INDEX products_laptop_pkey ON products_laptop(parent_asin);

-- Rating and sorting indexes
CREATE INDEX IF NOT EXISTS products_laptop_average_rating_idx ON products_laptop(average_rating DESC);
CREATE INDEX IF NOT EXISTS products_laptop_rating_number_idx ON products_laptop(rating_number DESC);
CREATE INDEX IF NOT EXISTS products_laptop_price_idx ON products_laptop(price);

-- Category indexes
CREATE INDEX IF NOT EXISTS products_laptop_main_category_idx ON products_laptop(main_category);
CREATE INDEX IF NOT EXISTS products_laptop_categories_idx ON products_laptop USING GIN(categories);
CREATE INDEX IF NOT EXISTS products_laptop_store_idx ON products_laptop(store);

-- JSON indexes for complex queries
CREATE INDEX IF NOT EXISTS products_laptop_details_idx ON products_laptop USING GIN(details);

-- NOTE: Vector indexes will be created AFTER data is loaded
-- See 05_create_vector_indexes.sql

-- Show table structure
\d products_laptop

-- Show table size
SELECT 
    'products_laptop' as table_name,
    pg_size_pretty(pg_total_relation_size('products_laptop')) as total_size,
    pg_size_pretty(pg_relation_size('products_laptop')) as table_size,
    pg_size_pretty(pg_indexes_size('products_laptop')) as indexes_size;

\echo '✅ Products table created successfully!'
\echo '📋 Next step: Run 03_create_reviews_table.sql'

