"""
Load Products with Detailed Error Logging
==========================================
This diagnostic version will:
1. Attempt to load all products from the whitelist
2. Track which ones already exist (will be skipped)
3. Capture detailed error information for failures
4. Generate a comprehensive error report

This will NOT delete existing data - just attempts to insert and logs failures.
"""

import pickle
import pyarrow.parquet as pq
import psycopg2
from psycopg2 import errors as pg_errors
import json
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

print("=" * 100)
print("DIAGNOSTIC PRODUCT LOADING WITH ERROR TRACKING")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

PARQUET_DIR = Path('../data/processed/raw_meta_Electronics/')
WHITELIST_FILE = Path('../logs/unique_asins_whitelist.pkl')
BATCH_SIZE = 1000  # Smaller batches for better error isolation

# Statistics tracking
stats = {
    'total_in_whitelist': 0,
    'total_processed': 0,
    'total_skipped_existing': 0,
    'total_inserted': 0,
    'total_failed': 0,
    'files_processed': 0
}

# Detailed error tracking
error_details = {
    'null_title': [],
    'null_asin': [],
    'duplicate_key': 0,
    'jsonb_errors': [],
    'array_errors': [],
    'varchar_too_long': [],
    'foreign_key_errors': [],
    'data_type_errors': [],
    'batch_failures': [],
    'unknown_errors': []
}

# Failed ASINs for further investigation
failed_asins = []

# Helper functions
def clean_text(text):
    """Clean and validate text fields"""
    if text is None or text == 'null' or (isinstance(text, float) and str(text) == 'nan'):
        return None
    text_str = str(text).strip()
    return text_str if text_str else None

def clean_price(price_str):
    """Clean and convert price to float"""
    if not price_str or price_str == 'null':
        return None
    try:
        price_str = str(price_str).replace('$', '').replace(',', '').strip()
        return float(price_str)
    except (ValueError, AttributeError):
        return None

def join_array_to_text(arr):
    """Convert array to newline-separated text"""
    if not arr or arr == 'null':
        return None
    if isinstance(arr, list):
        cleaned = [str(x) for x in arr if x and x != 'null']
        return '\n'.join(cleaned) if cleaned else None
    return None

def convert_to_postgres_array(arr):
    """Convert to PostgreSQL array format"""
    if not arr or arr == 'null':
        return None
    if isinstance(arr, list):
        cleaned = [str(x) for x in arr if x and x != 'null']
        return cleaned if cleaned else None
    return None

def convert_to_jsonb(data):
    """Convert dict to JSONB (returns dict, psycopg2 handles serialization)"""
    if not data or data == 'null':
        return None
    if isinstance(data, dict):
        cleaned_dict = {k: v for k, v in data.items() 
                       if v is not None and v != 'null'}
        if not cleaned_dict:
            return None
        return cleaned_dict  # Return dict, not JSON string!
    return None

# Load whitelist
print("=" * 100)
print("STEP 1: Loading Product Whitelist")
print("=" * 100)

try:
    with open(WHITELIST_FILE, 'rb') as f:
        whitelist = pickle.load(f)
    stats['total_in_whitelist'] = len(whitelist)
    print(f"✅ Loaded whitelist: {len(whitelist):,} unique parent_asins")
    print(f"   Sample ASINs: {list(whitelist)[:5]}\n")
except FileNotFoundError:
    print(f"❌ Error: Whitelist file not found: {WHITELIST_FILE}")
    print("   Please run extract_unique_asins.py first.")
    exit(1)

# Connect to database
print("=" * 100)
print("STEP 2: Connecting to Database")
print("=" * 100)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print(f"✅ Connected to database: {DB_CONFIG['dbname']}\n")
    
    # Check existing count
    cur.execute("SELECT COUNT(*) FROM products;")
    existing_count = cur.fetchone()[0]
    print(f"📊 Current products in database: {existing_count:,}\n")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Process parquet files
print("=" * 100)
print("STEP 3: Processing Parquet Files with Detailed Error Tracking")
print("=" * 100)

parquet_files = sorted(PARQUET_DIR.glob("*.parquet"))
print(f"Found {len(parquet_files)} parquet files\n")

for parquet_file in parquet_files:
    print(f"\n{'='*100}")
    print(f"Processing: {parquet_file.name}")
    print(f"{'='*100}")
    
    try:
        table = pq.read_table(parquet_file)
        df = table.to_pandas()
        stats['files_processed'] += 1
        
        batch = []
        batch_asins = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Reading {parquet_file.name}"):
            stats['total_processed'] += 1
            
            # Extract and validate required fields
            parent_asin = clean_text(row.get('parent_asin'))
            title = clean_text(row.get('title'))
            
            # Skip if not in whitelist
            if parent_asin not in whitelist:
                continue
            
            # Track validation errors
            if not parent_asin:
                error_details['null_asin'].append(f"Row {idx}")
                stats['total_failed'] += 1
                continue
            
            if not title:
                error_details['null_title'].append(parent_asin)
                stats['total_failed'] += 1
                failed_asins.append(parent_asin)
                continue
            
            # Prepare record with all transformations
            try:
                record = (
                    parent_asin,
                    title,
                    clean_text(row.get('description')),
                    join_array_to_text(row.get('features')),
                    float(row['average_rating']) if row.get('average_rating') else None,
                    int(row['rating_number']) if row.get('rating_number') else None,
                    clean_price(row.get('price')),
                    clean_text(row.get('main_category')),
                    convert_to_postgres_array(row.get('categories')),
                    clean_text(row.get('store')),
                    convert_to_jsonb(row.get('details')),
                    convert_to_jsonb(row.get('images')),
                    convert_to_jsonb(row.get('videos'))
                )
                
                batch.append(record)
                batch_asins.append(parent_asin)
                
            except Exception as e:
                error_details['data_type_errors'].append(f"ASIN {parent_asin}: {str(e)}")
                stats['total_failed'] += 1
                failed_asins.append(parent_asin)
                continue
            
            # Insert batch when full
            if len(batch) >= BATCH_SIZE:
                try:
                    cur.executemany("""
                        INSERT INTO products (
                            parent_asin, title, description, features,
                            average_rating, rating_number, price, main_category,
                            categories, store, details, images, videos
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (parent_asin) DO NOTHING
                    """, batch)
                    
                    inserted = cur.rowcount
                    conn.commit()
                    
                    stats['total_inserted'] += inserted
                    stats['total_skipped_existing'] += (len(batch) - inserted)
                    
                    if inserted == 0:
                        error_details['duplicate_key'] += len(batch)
                    
                except pg_errors.UniqueViolation as e:
                    conn.rollback()
                    error_details['duplicate_key'] += len(batch)
                    stats['total_skipped_existing'] += len(batch)
                    
                except pg_errors.DataException as e:
                    conn.rollback()
                    error_msg = str(e)
                    if 'jsonb' in error_msg.lower():
                        error_details['jsonb_errors'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {error_msg[:100]}")
                    elif 'array' in error_msg.lower():
                        error_details['array_errors'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {error_msg[:100]}")
                    else:
                        error_details['data_type_errors'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {error_msg[:100]}")
                    
                    stats['total_failed'] += len(batch)
                    failed_asins.extend(batch_asins)
                    
                except pg_errors.StringDataRightTruncation as e:
                    conn.rollback()
                    error_details['varchar_too_long'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {str(e)[:100]}")
                    stats['total_failed'] += len(batch)
                    failed_asins.extend(batch_asins)
                    
                except pg_errors.ForeignKeyViolation as e:
                    conn.rollback()
                    error_details['foreign_key_errors'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {str(e)[:100]}")
                    stats['total_failed'] += len(batch)
                    failed_asins.extend(batch_asins)
                    
                except Exception as e:
                    conn.rollback()
                    error_details['unknown_errors'].append(f"Batch with ASINs: {batch_asins[:5]}... Error: {str(e)[:100]}")
                    stats['total_failed'] += len(batch)
                    failed_asins.extend(batch_asins)
                
                # Clear batch
                batch = []
                batch_asins = []
        
        # Insert remaining records
        if batch:
            try:
                cur.executemany("""
                    INSERT INTO products (
                        parent_asin, title, description, features,
                        average_rating, rating_number, price, main_category,
                        categories, store, details, images, videos
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (parent_asin) DO NOTHING
                """, batch)
                
                inserted = cur.rowcount
                conn.commit()
                
                stats['total_inserted'] += inserted
                stats['total_skipped_existing'] += (len(batch) - inserted)
                
                if inserted == 0:
                    error_details['duplicate_key'] += len(batch)
                    
            except Exception as e:
                conn.rollback()
                error_details['batch_failures'].append(f"Final batch: {str(e)[:100]}")
                stats['total_failed'] += len(batch)
                failed_asins.extend(batch_asins)
        
        print(f"✅ Completed {parquet_file.name}")
        
    except Exception as e:
        print(f"❌ Error reading {parquet_file.name}: {e}")
        continue

# Final verification
print("\n" + "=" * 100)
print("STEP 4: Final Verification")
print("=" * 100)

cur.execute("SELECT COUNT(*) FROM products;")
final_count = cur.fetchone()[0]
print(f"📊 Final products in database: {final_count:,}")
print(f"📊 New products inserted: {stats['total_inserted']:,}")
print(f"📊 Products already existed: {stats['total_skipped_existing']:,}\n")

# Generate detailed error report
print("\n" + "=" * 100)
print("DETAILED ERROR ANALYSIS")
print("=" * 100)

print(f"\n📊 SUMMARY:")
print(f"   Total in whitelist:        {stats['total_in_whitelist']:,}")
print(f"   Total processed:           {stats['total_processed']:,}")
print(f"   Already in DB (skipped):   {stats['total_skipped_existing']:,}")
print(f"   Successfully inserted:     {stats['total_inserted']:,}")
print(f"   Failed to insert:          {stats['total_failed']:,}")

print(f"\n🔍 ERROR BREAKDOWN:")
print(f"   Null/missing title:        {len(error_details['null_title']):,}")
print(f"   Null/missing ASIN:         {len(error_details['null_asin']):,}")
print(f"   Duplicate key conflicts:   {error_details['duplicate_key']:,}")
print(f"   JSONB format errors:       {len(error_details['jsonb_errors']):,}")
print(f"   Array format errors:       {len(error_details['array_errors']):,}")
print(f"   VARCHAR too long:          {len(error_details['varchar_too_long']):,}")
print(f"   Foreign key violations:    {len(error_details['foreign_key_errors']):,}")
print(f"   Data type errors:          {len(error_details['data_type_errors']):,}")
print(f"   Unknown errors:            {len(error_details['unknown_errors']):,}")

# Show samples
if error_details['null_title']:
    print(f"\n❌ Sample ASINs with null/missing title (first 20):")
    for i, asin in enumerate(error_details['null_title'][:20], 1):
        print(f"   {i}. {asin}")

if error_details['jsonb_errors']:
    print(f"\n❌ Sample JSONB errors (first 5):")
    for i, error in enumerate(error_details['jsonb_errors'][:5], 1):
        print(f"   {i}. {error}")

if error_details['array_errors']:
    print(f"\n❌ Sample Array errors (first 5):")
    for i, error in enumerate(error_details['array_errors'][:5], 1):
        print(f"   {i}. {error}")

if error_details['varchar_too_long']:
    print(f"\n❌ Sample VARCHAR length errors (first 5):")
    for i, error in enumerate(error_details['varchar_too_long'][:5], 1):
        print(f"   {i}. {error}")

if error_details['data_type_errors']:
    print(f"\n❌ Sample data type errors (first 5):")
    for i, error in enumerate(error_details['data_type_errors'][:5], 1):
        print(f"   {i}. {error}")

if error_details['unknown_errors']:
    print(f"\n❌ Sample unknown errors (first 5):")
    for i, error in enumerate(error_details['unknown_errors'][:5], 1):
        print(f"   {i}. {error}")

# Save failed ASINs to file
if failed_asins:
    failed_asins_unique = list(set(failed_asins))
    output_file = Path('../logs/failed_product_asins.txt')
    with open(output_file, 'w') as f:
        f.write('\n'.join(failed_asins_unique))
    print(f"\n💾 Saved {len(failed_asins_unique):,} unique failed ASINs to: {output_file}")

print("\n" + "=" * 100)
print("DIAGNOSTIC COMPLETE")
print("=" * 100)
print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Close database connection
cur.close()
conn.close()


