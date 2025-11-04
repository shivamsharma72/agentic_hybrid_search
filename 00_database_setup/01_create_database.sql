-- =====================================================
-- Step 1: Create Database and Enable pgvector Extension
-- =====================================================
-- Run this script first to set up the database
-- Usage: psql -U your_username -f 01_create_database.sql

-- Create the database (run as superuser or user with CREATEDB privilege)
-- Note: If database already exists, skip this step
CREATE DATABASE amazon_electronics_rag;

-- Connect to the new database
\c amazon_electronics_rag

-- Enable pgvector extension (required for vector embeddings)
-- Note: pgvector must be installed on your PostgreSQL server first
-- Installation: https://github.com/pgvector/pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Show database info
\l+ amazon_electronics_rag

-- Success message
\echo '✅ Database created and pgvector extension enabled!'
\echo '📋 Next step: Run 02_create_products_table.sql'

