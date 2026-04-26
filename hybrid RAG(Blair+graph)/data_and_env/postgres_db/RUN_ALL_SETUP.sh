#!/bin/bash
# =====================================================
# Complete Database Setup - Run All Steps
# =====================================================
# This script runs all setup steps in sequence
# Usage: ./RUN_ALL_SETUP.sh

set -e  # Exit on any error

echo "================================================================================"
echo "🗄️  COMPLETE DATABASE SETUP FOR LAPTOP RAG SYSTEM"
echo "================================================================================"
echo ""
echo "This script will:"
echo "  1. Create database and enable pgvector"
echo "  2. Create products_laptop table"
echo "  3. Create reviews_laptop table"
echo "  4. Load data from Parquet files (interactive)"
echo "  5. Create vector indexes (takes time!)"
echo "  6. Verify setup (interactive)"
echo ""
echo "⏱️  Expected total time: 30-45 minutes"
echo "💾 Final database size: ~3.1 GB"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Get PostgreSQL username
echo ""
read -p "Enter your PostgreSQL username: " PGUSER
export PGUSER

# =====================================================
# Step 1: Create Database
# =====================================================
echo ""
echo "================================================================================"
echo "[1/6] Creating database and enabling pgvector..."
echo "================================================================================"
psql -f 01_create_database.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 1 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Step 2: Create Products Table
# =====================================================
echo ""
echo "================================================================================"
echo "[2/6] Creating products_laptop table..."
echo "================================================================================"
psql -d amazon_electronics_rag -f 02_create_products_table.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 2 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Step 3: Create Reviews Table
# =====================================================
echo ""
echo "================================================================================"
echo "[3/6] Creating reviews_laptop table..."
echo "================================================================================"
psql -d amazon_electronics_rag -f 03_create_reviews_table.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 3 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Step 4: Load Data
# =====================================================
echo ""
echo "================================================================================"
echo "[4/6] Loading data from Parquet files..."
echo "================================================================================"
echo "⏱️  This will take ~15-20 minutes"
echo ""
python3 04_load_data_from_parquet.py

if [ $? -ne 0 ]; then
    echo "❌ Step 4 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Step 5: Create Vector Indexes
# =====================================================
echo ""
echo "================================================================================"
echo "[5/6] Creating vector similarity indexes..."
echo "================================================================================"
echo "⏱️  This will take ~15-25 minutes"
echo "⚠️  This is the slowest step - please be patient!"
echo ""
psql -d amazon_electronics_rag -f 05_create_vector_indexes.sql

if [ $? -ne 0 ]; then
    echo "❌ Step 5 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Step 6: Verify Setup
# =====================================================
echo ""
echo "================================================================================"
echo "[6/6] Verifying setup and testing vector search..."
echo "================================================================================"
python3 06_verify_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Step 6 failed! Please check the error message above."
    exit 1
fi

# =====================================================
# Success!
# =====================================================
echo ""
echo "================================================================================"
echo "🎉 COMPLETE SETUP FINISHED SUCCESSFULLY!"
echo "================================================================================"
echo ""
echo "✅ Database: amazon_electronics_rag"
echo "✅ Products: 5,455 with embeddings"
echo "✅ Reviews: 350,105 with embeddings"
echo "✅ Vector indexes: Created and tested"
echo "✅ Setup verified: All tests passed"
echo ""
echo "Your database is now ready to use!"
echo "================================================================================"

