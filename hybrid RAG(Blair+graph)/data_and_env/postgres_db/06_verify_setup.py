#!/usr/bin/env python3
"""
Step 6: Verify Database Setup and Test Vector Search
====================================================
This script verifies that the database is set up correctly and
tests vector similarity search functionality.

Usage:
  python3 06_verify_setup.py
"""

import psycopg2
import numpy as np
from datetime import datetime

# ===========================
# Configuration
# ===========================
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

print("=" * 80)
print("🔍 VERIFYING DATABASE SETUP")
print("=" * 80)

# ===========================
# Connect to Database
# ===========================
print("\n[1/6] Connecting to PostgreSQL...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print(f"  ✅ Connected to database: {DB_CONFIG['dbname']}")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    exit(1)

# ===========================
# Check pgvector Extension
# ===========================
print("\n[2/6] Checking pgvector extension...")
cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
result = cur.fetchone()
if result:
    print(f"  ✅ pgvector extension is installed")
    cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
    version = cur.fetchone()[0]
    print(f"     Version: {version}")
else:
    print(f"  ❌ pgvector extension not found!")
    exit(1)

# ===========================
# Check Tables and Data
# ===========================
print("\n[3/6] Checking tables and data...")

# Products
cur.execute("SELECT COUNT(*) FROM products_laptop;")
product_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM products_laptop WHERE blair_embedding IS NOT NULL;")
product_emb_count = cur.fetchone()[0]
print(f"  📦 Products:")
print(f"     Total: {product_count:,}")
print(f"     With embeddings: {product_emb_count:,} ({product_emb_count/product_count*100:.1f}%)")

# Reviews
cur.execute("SELECT COUNT(*) FROM reviews_laptop;")
review_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM reviews_laptop WHERE blair_embedding IS NOT NULL;")
review_emb_count = cur.fetchone()[0]
print(f"  💬 Reviews:")
print(f"     Total: {review_count:,}")
print(f"     With embeddings: {review_emb_count:,} ({review_emb_count/review_count*100:.1f}%)")

# Statistics
cur.execute("SELECT COUNT(DISTINCT parent_asin) FROM reviews_laptop;")
unique_products = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT user_id) FROM reviews_laptop;")
unique_users = cur.fetchone()[0]
print(f"  📊 Statistics:")
print(f"     Unique products (in reviews): {unique_products:,}")
print(f"     Unique users: {unique_users:,}")
print(f"     Avg reviews per product: {review_count/unique_products:.1f}")

if product_count == 0 or review_count == 0:
    print(f"\n  ❌ No data found! Please run 04_load_data_from_parquet.py first")
    exit(1)

# ===========================
# Check Vector Indexes
# ===========================
print("\n[4/6] Checking vector indexes...")

# Check products indexes
cur.execute("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'products_laptop' AND indexdef LIKE '%hnsw%';
""")
product_indexes = cur.fetchall()
if product_indexes:
    print(f"  ✅ Products HNSW index found:")
    for idx_name, idx_def in product_indexes:
        print(f"     {idx_name}")
else:
    print(f"  ⚠️  No HNSW index on products! Vector search will be slow.")
    print(f"     Run 05_create_vector_indexes.sql to create indexes")

# Check reviews indexes
cur.execute("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'reviews_laptop' AND indexdef LIKE '%hnsw%';
""")
review_indexes = cur.fetchall()
if review_indexes:
    print(f"  ✅ Reviews HNSW index found:")
    for idx_name, idx_def in review_indexes:
        print(f"     {idx_name}")
else:
    print(f"  ⚠️  No HNSW index on reviews! Vector search will be slow.")
    print(f"     Run 05_create_vector_indexes.sql to create indexes")

# ===========================
# Test Vector Search (Products)
# ===========================
print("\n[5/6] Testing vector similarity search on products...")

# Get a sample product and its embedding
cur.execute("""
    SELECT parent_asin, title, blair_embedding 
    FROM products_laptop 
    WHERE blair_embedding IS NOT NULL 
    LIMIT 1;
""")
sample = cur.fetchone()
if not sample:
    print(f"  ❌ No products with embeddings found!")
    exit(1)

sample_asin, sample_title, sample_embedding = sample
print(f"  📦 Sample product: {sample_asin}")
print(f"     {sample_title[:60]}...")

# Find similar products using vector search
start_time = datetime.now()
cur.execute("""
    SELECT 
        parent_asin, 
        title, 
        blair_embedding <=> %s::vector AS distance
    FROM products_laptop
    WHERE blair_embedding IS NOT NULL
    ORDER BY blair_embedding <=> %s::vector
    LIMIT 5;
""", (sample_embedding, sample_embedding))
results = cur.fetchall()
query_time = (datetime.now() - start_time).total_seconds() * 1000

print(f"\n  🔍 Top 5 similar products (query time: {query_time:.2f}ms):")
for i, (asin, title, distance) in enumerate(results, 1):
    similarity = 1 - distance
    print(f"     {i}. [{asin}] {title[:50]}... (sim: {similarity:.3f})")

# ===========================
# Test Vector Search (Reviews)
# ===========================
print("\n[6/6] Testing vector similarity search on reviews...")

# Get a sample review and its embedding
cur.execute("""
    SELECT review_id, title, text, blair_embedding 
    FROM reviews_laptop 
    WHERE blair_embedding IS NOT NULL 
    LIMIT 1;
""")
sample = cur.fetchone()
if not sample:
    print(f"  ❌ No reviews with embeddings found!")
    exit(1)

sample_id, sample_title, sample_text, sample_embedding = sample
print(f"  💬 Sample review: {sample_id}")
print(f"     Title: {sample_title[:60] if sample_title else 'N/A'}...")
print(f"     Text: {sample_text[:80] if sample_text else 'N/A'}...")

# Find similar reviews using vector search
start_time = datetime.now()
cur.execute("""
    SELECT 
        review_id, 
        title,
        text,
        rating,
        blair_embedding <=> %s::vector AS distance
    FROM reviews_laptop
    WHERE blair_embedding IS NOT NULL
    ORDER BY blair_embedding <=> %s::vector
    LIMIT 5;
""", (sample_embedding, sample_embedding))
results = cur.fetchall()
query_time = (datetime.now() - start_time).total_seconds() * 1000

print(f"\n  🔍 Top 5 similar reviews (query time: {query_time:.2f}ms):")
for i, (review_id, title, text, rating, distance) in enumerate(results, 1):
    similarity = 1 - distance
    display_title = title[:40] if title else text[:40]
    print(f"     {i}. [#{review_id}] {display_title}... (⭐{rating:.1f}, sim: {similarity:.3f})")

# ===========================
# Test Cross-Modal Search
# ===========================
print("\n[BONUS] Testing cross-modal search (review → products)...")

# Use review embedding to find related products
start_time = datetime.now()
cur.execute("""
    SELECT 
        parent_asin, 
        title,
        blair_embedding <=> %s::vector AS distance
    FROM products_laptop
    WHERE blair_embedding IS NOT NULL
    ORDER BY blair_embedding <=> %s::vector
    LIMIT 5;
""", (sample_embedding, sample_embedding))
results = cur.fetchall()
query_time = (datetime.now() - start_time).total_seconds() * 1000

print(f"  🔍 Products similar to the review (query time: {query_time:.2f}ms):")
for i, (asin, title, distance) in enumerate(results, 1):
    similarity = 1 - distance
    print(f"     {i}. [{asin}] {title[:50]}... (sim: {similarity:.3f})")

# ===========================
# Final Summary
# ===========================
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DATABASE SETUP VERIFICATION COMPLETE!")
print("=" * 80)
print("\n📊 Summary:")
print(f"   • Database: {DB_CONFIG['dbname']}")
print(f"   • Products: {product_count:,} ({product_emb_count:,} with embeddings)")
print(f"   • Reviews: {review_count:,} ({review_emb_count:,} with embeddings)")
print(f"   • Unique users: {unique_users:,}")
print(f"   • Vector indexes: {'✅ Present' if product_indexes and review_indexes else '⚠️ Missing'}")
print(f"   • Vector search: ✅ Working")
print(f"   • Cross-modal search: ✅ Working")
print("\n🎉 Your database is ready for use!")
print("=" * 80)

