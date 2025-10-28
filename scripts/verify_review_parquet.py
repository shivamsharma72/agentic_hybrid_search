"""
Verify Review Parquet Files
============================
This script verifies the review Parquet files to ensure they meet our requirements:
1. Correct number of files (10)
2. Correct schema (expected columns)
3. Reviews are filtered by electronics_products_whitelist
4. Data quality checks (no nulls in required fields, valid ratings, etc.)

Input:
- data/processed/reviews_Electronics/*.parquet (10 files)
- logs/electronics_products_whitelist.pkl (348K ASINs)

Output:
- Console report with statistics and validation results
"""

import os
import sys
import pickle
from datetime import datetime
import pyarrow.parquet as pq
import pyarrow as pa
import glob

print("=" * 100)
print("VERIFY REVIEW PARQUET FILES")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
# Check main project folder first, then local folder
import os.path
if os.path.exists('../../data/processed/reviews_Electronics'):
    PARQUET_DIR = '../../data/processed/reviews_Electronics'
else:
    PARQUET_DIR = '../data/processed/reviews_Electronics'

WHITELIST_FILE = '../logs/electronics_products_whitelist.pkl'

# Expected schema
EXPECTED_COLUMNS = [
    'user_id',
    'parent_asin',
    'rating',
    'title',
    'text',
    'timestamp',
    'helpful_vote',
    'verified_purchase',
    'images'
]

# Statistics
stats = {
    'total_files': 0,
    'total_reviews': 0,
    'unique_users': set(),
    'unique_products': set(),
    'rating_distribution': {},
    'verified_purchase_count': 0,
    'reviews_with_images': 0,
    'reviews_with_text': 0,
    'null_parent_asin': 0,
    'null_rating': 0,
    'null_text': 0,
    'invalid_products': 0
}

print("=" * 100)
print("STEP 1: Loading Whitelist")
print("=" * 100)

try:
    with open(WHITELIST_FILE, 'rb') as f:
        whitelist = pickle.load(f)
    print(f"✅ Loaded whitelist: {len(whitelist):,} products")
except Exception as e:
    print(f"❌ ERROR: Could not load whitelist")
    print(f"   {str(e)}")
    sys.exit(1)

print("\n" + "=" * 100)
print("STEP 2: Finding Parquet Files")
print("=" * 100)

# Find all parquet files
parquet_files = sorted(glob.glob(f"{PARQUET_DIR}/*.parquet"))
stats['total_files'] = len(parquet_files)

print(f"Found {len(parquet_files)} Parquet files")
if len(parquet_files) == 0:
    print("❌ ERROR: No Parquet files found!")
    print(f"   Expected location: {PARQUET_DIR}/*.parquet")
    sys.exit(1)

for i, f in enumerate(parquet_files, 1):
    size_mb = os.path.getsize(f) / (1024 * 1024)
    print(f"   {i}. {os.path.basename(f)} ({size_mb:.1f} MB)")

print("\n" + "=" * 100)
print("STEP 3: Verifying Schema")
print("=" * 100)

# Check schema of first file
first_file = parquet_files[0]
table = pq.read_table(first_file)
schema = table.schema

print(f"Schema from {os.path.basename(first_file)}:")
print(f"   Columns: {table.num_columns}")
print(f"   Column names: {table.column_names}")

# Check if all expected columns exist
missing_columns = set(EXPECTED_COLUMNS) - set(table.column_names)
extra_columns = set(table.column_names) - set(EXPECTED_COLUMNS)

if missing_columns:
    print(f"\n❌ MISSING COLUMNS: {missing_columns}")
else:
    print(f"\n✅ All expected columns present")

if extra_columns:
    print(f"ℹ️  Extra columns found: {extra_columns}")

# Print schema details
print(f"\nColumn Types:")
for i, field in enumerate(schema):
    print(f"   {i+1}. {field.name:20s} → {field.type}")

print("\n" + "=" * 100)
print("STEP 4: Analyzing Data")
print("=" * 100)

for file_idx, parquet_file in enumerate(parquet_files, 1):
    print(f"\nProcessing file {file_idx}/{len(parquet_files)}: {os.path.basename(parquet_file)}")
    
    try:
        # Read parquet file
        table = pq.read_table(parquet_file)
        num_rows = table.num_rows
        stats['total_reviews'] += num_rows
        
        print(f"   Rows: {num_rows:,}")
        
        # Convert to pandas for easier analysis
        df = table.to_pandas()
        
        # Collect unique users and products
        stats['unique_users'].update(df['user_id'].unique())
        stats['unique_products'].update(df['parent_asin'].unique())
        
        # Check for nulls in critical fields
        null_asin = df['parent_asin'].isna().sum()
        null_rating = df['rating'].isna().sum()
        null_text = df['text'].isna().sum()
        
        stats['null_parent_asin'] += null_asin
        stats['null_rating'] += null_rating
        stats['null_text'] += null_text
        
        if null_asin > 0:
            print(f"   ⚠️  NULL parent_asin: {null_asin}")
        if null_rating > 0:
            print(f"   ⚠️  NULL rating: {null_rating}")
        if null_text > 0:
            print(f"   ⚠️  NULL text: {null_text}")
        
        # Rating distribution
        rating_counts = df['rating'].value_counts().to_dict()
        for rating, count in rating_counts.items():
            stats['rating_distribution'][rating] = stats['rating_distribution'].get(rating, 0) + count
        
        # Verified purchase count
        if 'verified_purchase' in df.columns:
            stats['verified_purchase_count'] += df['verified_purchase'].sum()
        
        # Reviews with images
        if 'images' in df.columns:
            stats['reviews_with_images'] += df['images'].notna().sum()
        
        # Reviews with text
        stats['reviews_with_text'] += df['text'].notna().sum()
        
        # Check if products are in whitelist
        invalid_products = set(df['parent_asin'].unique()) - whitelist
        if invalid_products:
            stats['invalid_products'] += len(invalid_products)
            print(f"   ⚠️  Products NOT in whitelist: {len(invalid_products)}")
            print(f"       Sample: {list(invalid_products)[:5]}")
        
        print(f"   ✅ Processed successfully")
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")

print("\n" + "=" * 100)
print("STEP 5: VERIFICATION SUMMARY")
print("=" * 100)

print(f"\n📊 FILE STATISTICS:")
print(f"   Total Parquet files: {stats['total_files']}")
print(f"   Expected files: 10")
if stats['total_files'] == 10:
    print(f"   ✅ File count is correct")
else:
    print(f"   ❌ File count mismatch!")

print(f"\n📊 REVIEW STATISTICS:")
print(f"   Total reviews: {stats['total_reviews']:,}")
print(f"   Unique users: {len(stats['unique_users']):,}")
print(f"   Unique products: {len(stats['unique_products']):,}")
print(f"   Avg reviews per user: {stats['total_reviews'] / len(stats['unique_users']):.1f}")
print(f"   Avg reviews per product: {stats['total_reviews'] / len(stats['unique_products']):.1f}")

print(f"\n📊 DATA QUALITY:")
print(f"   Reviews with text: {stats['reviews_with_text']:,} ({stats['reviews_with_text']/stats['total_reviews']*100:.1f}%)")
print(f"   Reviews with images: {stats['reviews_with_images']:,} ({stats['reviews_with_images']/stats['total_reviews']*100:.1f}%)")
print(f"   Verified purchases: {stats['verified_purchase_count']:,} ({stats['verified_purchase_count']/stats['total_reviews']*100:.1f}%)")

print(f"\n📊 RATING DISTRIBUTION:")
for rating in sorted(stats['rating_distribution'].keys()):
    count = stats['rating_distribution'][rating]
    percentage = count / stats['total_reviews'] * 100
    print(f"   ⭐ {rating}: {count:,} ({percentage:.1f}%)")

print(f"\n📊 NULL VALUES:")
print(f"   NULL parent_asin: {stats['null_parent_asin']:,}")
print(f"   NULL rating: {stats['null_rating']:,}")
print(f"   NULL text: {stats['null_text']:,}")

if stats['null_parent_asin'] == 0 and stats['null_rating'] == 0 and stats['null_text'] == 0:
    print(f"   ✅ No null values in critical fields")
else:
    print(f"   ⚠️  Found null values in critical fields")

print(f"\n📊 WHITELIST VALIDATION:")
print(f"   Products in whitelist: {len(whitelist):,}")
print(f"   Products in Parquet files: {len(stats['unique_products']):,}")
print(f"   Products NOT in whitelist: {stats['invalid_products']}")

if stats['invalid_products'] == 0:
    print(f"   ✅ All products are in the whitelist")
else:
    print(f"   ❌ Found products NOT in whitelist!")
    print(f"       This means reviews exist for products not in the database")
    print(f"       These will cause FOREIGN KEY violations during loading")

# Check if products in parquet are subset of whitelist
products_in_parquet = stats['unique_products']
products_not_in_whitelist = products_in_parquet - whitelist
products_in_whitelist_not_parquet = whitelist - products_in_parquet

print(f"\n📊 PRODUCT OVERLAP:")
print(f"   Products in both Parquet & whitelist: {len(products_in_parquet & whitelist):,}")
print(f"   Products in Parquet but NOT whitelist: {len(products_not_in_whitelist):,}")
print(f"   Products in whitelist but NOT Parquet: {len(products_in_whitelist_not_parquet):,}")

if len(products_not_in_whitelist) > 0:
    print(f"\n   ❌ WARNING: Found {len(products_not_in_whitelist)} products in Parquet that are NOT in whitelist!")
    print(f"      Sample ASINs: {list(products_not_in_whitelist)[:10]}")

print("\n" + "=" * 100)
print("VERIFICATION RESULT")
print("=" * 100)

# Final verdict
issues = []

if stats['total_files'] != 10:
    issues.append(f"Expected 10 files, found {stats['total_files']}")

if stats['null_parent_asin'] > 0:
    issues.append(f"Found {stats['null_parent_asin']} NULL parent_asin values")

if stats['null_rating'] > 0:
    issues.append(f"Found {stats['null_rating']} NULL rating values")

if stats['null_text'] > 0:
    issues.append(f"Found {stats['null_text']} NULL text values")

if len(products_not_in_whitelist) > 0:
    issues.append(f"Found {len(products_not_in_whitelist)} products NOT in whitelist (will cause FK errors)")

if len(issues) == 0:
    print("✅ ALL CHECKS PASSED!")
    print("   The Parquet files are ready for loading into PostgreSQL")
    print(f"   Expected to load: {stats['total_reviews']:,} reviews")
else:
    print("❌ VERIFICATION FAILED!")
    print(f"   Found {len(issues)} issue(s):")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\n   ⚠️  Fix these issues before loading to PostgreSQL")

print("\n" + "=" * 100)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

