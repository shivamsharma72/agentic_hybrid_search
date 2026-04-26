"""
Extract Electronics Products Whitelist from PostgreSQL
======================================================
This script extracts the 655,694 Electronics products from the products table
and creates a whitelist for filtering reviews.

Output:
- logs/electronics_products_whitelist.pkl (set of parent_asin values)
"""

import psycopg2
import pickle
from datetime import datetime

print("=" * 100)
print("EXTRACT ELECTRONICS PRODUCTS WHITELIST")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
DB_NAME = 'amazon_electronics_rag'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
OUTPUT_FILE = '../logs/electronics_products_whitelist.pkl'

# Step 1: Connect to PostgreSQL
print("=" * 100)
print("STEP 1: Connecting to PostgreSQL")
print("=" * 100)

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print(f"✅ Connected to database: {DB_NAME}\n")
except Exception as e:
    print(f"❌ ERROR: Could not connect to database")
    print(f"   {str(e)}")
    exit(1)

# Step 2: Extract parent_asin from products table
print("=" * 100)
print("STEP 2: Extracting Electronics Products")
print("=" * 100)

try:
    cursor.execute("SELECT parent_asin FROM products")
    products = cursor.fetchall()
    
    # Create set of parent_asin values
    electronics_whitelist = set(row[0] for row in products)
    
    print(f"✅ Extracted {len(electronics_whitelist):,} unique Electronics products")
    print(f"   Sample ASINs: {list(electronics_whitelist)[:5]}\n")
    
except Exception as e:
    print(f"❌ ERROR: Could not extract products")
    print(f"   {str(e)}")
    exit(1)

# Step 3: Save whitelist to pickle file
print("=" * 100)
print("STEP 3: Saving Whitelist")
print("=" * 100)

try:
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(electronics_whitelist, f)
    
    print(f"✅ Whitelist saved to: {OUTPUT_FILE}")
    
    # Get file size
    import os
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"   File size: {size_mb:.2f} MB\n")
    
except Exception as e:
    print(f"❌ ERROR: Could not save whitelist")
    print(f"   {str(e)}")
    exit(1)

# Close connection
cursor.close()
conn.close()

print("=" * 100)
print("EXTRACTION COMPLETE")
print("=" * 100)
print(f"✅ Electronics products whitelist ready")
print(f"   Count: {len(electronics_whitelist):,} products")
print(f"   File: {OUTPUT_FILE}")
print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

