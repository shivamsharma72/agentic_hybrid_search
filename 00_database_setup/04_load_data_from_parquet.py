#!/usr/bin/env python3
"""
Step 4: Load Data from Parquet Files into PostgreSQL
====================================================
This script loads laptop products and reviews from Parquet files
into the PostgreSQL database.

Prerequisites:
- Database and tables created (steps 1-3)
- Parquet files available in ../tables_parquet_final/

Usage:
  python3 04_load_data_from_parquet.py
"""

import psycopg2
from psycopg2.extensions import register_adapter, AsIs
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import sys
import json

# ===========================
# Register numpy array adapter for psycopg2
# ===========================
def adapt_numpy_array(numpy_array):
    """
    Convert numpy array to PostgreSQL-compatible format.
    For vectors, convert to list. For other arrays, convert to JSON.
    """
    if isinstance(numpy_array, np.ndarray):
        return AsIs(f"'{json.dumps(numpy_array.tolist())}'")
    return AsIs(repr(numpy_array))

# Register the adapter
register_adapter(np.ndarray, adapt_numpy_array)

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

# Paths to Parquet files (relative to this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PARQUET_DIR = os.path.join(PROJECT_ROOT, 'tables_parquet_final')

PRODUCTS_PARQUET = os.path.join(PARQUET_DIR, 'laptop_products_with_embeddings.parquet')
REVIEWS_PARQUET = os.path.join(PARQUET_DIR, 'laptop_reviews_with_embeddings.parquet')

BATCH_SIZE = 1000  # Products
REVIEW_BATCH_SIZE = 5000  # Reviews

print("=" * 80)
print("📦 LOADING DATA FROM PARQUET FILES")
print("=" * 80)

# ===========================
# Step 1: Verify Files Exist
# ===========================
print("\n[1/5] Verifying Parquet files...")
if not os.path.exists(PRODUCTS_PARQUET):
    print(f"  ❌ Products file not found: {PRODUCTS_PARQUET}")
    sys.exit(1)
if not os.path.exists(REVIEWS_PARQUET):
    print(f"  ❌ Reviews file not found: {REVIEWS_PARQUET}")
    sys.exit(1)

print(f"  ✅ Products file: {os.path.basename(PRODUCTS_PARQUET)}")
print(f"  ✅ Reviews file: {os.path.basename(REVIEWS_PARQUET)}")

# ===========================
# Step 2: Connect to Database
# ===========================
print("\n[2/5] Connecting to PostgreSQL...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print(f"  ✅ Connected to database: {DB_CONFIG['dbname']}")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    sys.exit(1)

# ===========================
# Step 3: Load Products
# ===========================
print("\n[3/5] Loading products from Parquet...")
products_df = pd.read_parquet(PRODUCTS_PARQUET)
print(f"  📊 Loaded {len(products_df):,} products from Parquet")

# Check if table already has data
cur.execute("SELECT COUNT(*) FROM products_laptop;")
existing_count = cur.fetchone()[0]
if existing_count > 0:
    print(f"  ⚠️  Table already has {existing_count} products")
    response = input("  Clear and reload? (yes/no): ")
    if response.lower() == 'yes':
        cur.execute("TRUNCATE TABLE products_laptop CASCADE;")
        conn.commit()
        print("  ✅ Table cleared")
    else:
        print("  ⏭️  Skipping products (keeping existing data)")
        products_df = pd.DataFrame()  # Skip loading

if len(products_df) > 0:
    print(f"  📥 Inserting {len(products_df):,} products...")
    
    insert_query = """
        INSERT INTO products_laptop (
            parent_asin, title, description, features, average_rating, rating_number,
            price, main_category, categories, store, details, images, videos,
            blair_embedding, description_array, features_array
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (parent_asin) DO NOTHING;
    """
    
    with tqdm(total=len(products_df), desc="Inserting products", unit="rows") as pbar:
        for i in range(0, len(products_df), BATCH_SIZE):
            batch = products_df.iloc[i:i+BATCH_SIZE]
            
            for idx, row in batch.iterrows():
                # Convert numpy arrays to lists for PostgreSQL
                embedding = row['blair_embedding'].tolist() if isinstance(row['blair_embedding'], np.ndarray) else row['blair_embedding']
                desc_array = row['description_array'].tolist() if isinstance(row['description_array'], np.ndarray) else row['description_array']
                feat_array = row['features_array'].tolist() if isinstance(row['features_array'], np.ndarray) else row['features_array']
                
                cur.execute(insert_query, (
                    row['parent_asin'],
                    row['title'],
                    row['description'],
                    row['features'],
                    float(row['average_rating']) if pd.notna(row['average_rating']) else None,
                    int(row['rating_number']) if pd.notna(row['rating_number']) else None,
                    float(row['price']) if pd.notna(row['price']) else None,
                    row['main_category'],
                    row['categories'],
                    row['store'],
                    row['details'],
                    row['images'],
                    row['videos'],
                    embedding,
                    desc_array,
                    feat_array
                ))
            
            conn.commit()
            pbar.update(len(batch))
    
    print(f"  ✅ Inserted {len(products_df):,} products")

# ===========================
# Step 4: Load Reviews
# ===========================
print("\n[4/5] Loading reviews from Parquet...")
reviews_df = pd.read_parquet(REVIEWS_PARQUET)
print(f"  📊 Loaded {len(reviews_df):,} reviews from Parquet")

# Check if table already has data
cur.execute("SELECT COUNT(*) FROM reviews_laptop;")
existing_count = cur.fetchone()[0]
if existing_count > 0:
    print(f"  ⚠️  Table already has {existing_count} reviews")
    response = input("  Clear and reload? (yes/no): ")
    if response.lower() == 'yes':
        cur.execute("TRUNCATE TABLE reviews_laptop;")
        conn.commit()
        print("  ✅ Table cleared")
    else:
        print("  ⏭️  Skipping reviews (keeping existing data)")
        reviews_df = pd.DataFrame()  # Skip loading

if len(reviews_df) > 0:
    print(f"  📥 Inserting {len(reviews_df):,} reviews...")
    
    insert_query = """
        INSERT INTO reviews_laptop (
            asin, parent_asin, user_id, rating, title, text,
            timestamp, helpful_vote, verified_purchase, blair_embedding, images
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
    """
    
    with tqdm(total=len(reviews_df), desc="Inserting reviews", unit="rows") as pbar:
        for i in range(0, len(reviews_df), REVIEW_BATCH_SIZE):
            batch = reviews_df.iloc[i:i+REVIEW_BATCH_SIZE]
            
            for idx, row in batch.iterrows():
                # Convert numpy arrays to lists for PostgreSQL
                embedding = row['blair_embedding'].tolist() if isinstance(row['blair_embedding'], np.ndarray) else row['blair_embedding']
                
                cur.execute(insert_query, (
                    row['asin'],
                    row['parent_asin'],
                    row['user_id'],
                    float(row['rating']),
                    row['title'],
                    row['text'],
                    int(row['timestamp']),
                    int(row['helpful_vote']),
                    bool(row['verified_purchase']),
                    embedding,
                    row.get('images')
                ))
            
            conn.commit()
            pbar.update(len(batch))
    
    print(f"  ✅ Inserted {len(reviews_df):,} reviews")

# ===========================
# Step 5: Verify Data
# ===========================
print("\n[5/5] Verifying data...")

# Count products
cur.execute("SELECT COUNT(*) FROM products_laptop;")
product_count = cur.fetchone()[0]
print(f"  📦 Products in database: {product_count:,}")

# Count reviews
cur.execute("SELECT COUNT(*) FROM reviews_laptop;")
review_count = cur.fetchone()[0]
print(f"  💬 Reviews in database: {review_count:,}")

# Check embeddings
cur.execute("SELECT COUNT(*) FROM products_laptop WHERE blair_embedding IS NOT NULL;")
product_emb_count = cur.fetchone()[0]
print(f"  🎯 Products with embeddings: {product_emb_count:,} ({product_emb_count/product_count*100:.1f}%)")

cur.execute("SELECT COUNT(*) FROM reviews_laptop WHERE blair_embedding IS NOT NULL;")
review_emb_count = cur.fetchone()[0]
print(f"  🎯 Reviews with embeddings: {review_emb_count:,} ({review_emb_count/review_count*100:.1f}%)")

# Show table sizes
cur.execute("""
    SELECT 
        'products_laptop' as table_name,
        pg_size_pretty(pg_total_relation_size('products_laptop')) as total_size,
        pg_size_pretty(pg_relation_size('products_laptop')) as table_size,
        pg_size_pretty(pg_indexes_size('products_laptop')) as indexes_size
    UNION ALL
    SELECT 
        'reviews_laptop' as table_name,
        pg_size_pretty(pg_total_relation_size('reviews_laptop')) as total_size,
        pg_size_pretty(pg_relation_size('reviews_laptop')) as table_size,
        pg_size_pretty(pg_indexes_size('reviews_laptop')) as indexes_size;
""")

print("\n  📊 Table sizes:")
for row in cur.fetchall():
    print(f"     {row[0]:20} Total: {row[1]:10} Table: {row[2]:10} Indexes: {row[3]:10}")

# ===========================
# Cleanup
# ===========================
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DATA LOADING COMPLETE!")
print("=" * 80)
print("\n📋 Next steps:")
print("   1. Run 05_create_vector_indexes.sql to create vector similarity indexes")
print("   2. Run 06_verify_setup.py to test the complete setup")
print("=" * 80)

