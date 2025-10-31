"""
Load Filtered Products from Parquet to PostgreSQL
==================================================
This script:
1. Loads the whitelist of unique parent_asin from 5-core dataset
2. Iterates through all 10 parquet files
3. Filters products to keep only those with reviews in 5-core
4. Transforms and cleans the data
5. Batch inserts into PostgreSQL products table

Expected: ~368,228 products to be loaded
Source: 10 parquet files (1.6M total products)
Target: PostgreSQL amazon_electronics_rag database
"""

import pickle
import pyarrow.parquet as pq
import psycopg2
from psycopg2.extras import execute_batch
import json
from datetime import datetime
import numpy as np
import pandas as pd

print("=" * 100)
print("LOADING FILTERED PRODUCTS TO POSTGRESQL")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

PARQUET_DIR = '../data/processed/raw_meta_Electronics/'
WHITELIST_FILE = '../logs/unique_asins_whitelist.pkl'
BATCH_SIZE = 5000  # Insert 5000 records at a time

# Statistics tracking
stats = {
    'total_processed': 0,
    'total_filtered': 0,
    'total_inserted': 0,
    'total_errors': 0,
    'files_processed': 0
}

# Load whitelist
print("=" * 100)
print("STEP 1: Loading Product Whitelist")
print("=" * 100)

try:
    with open(WHITELIST_FILE, 'rb') as f:
        whitelist = pickle.load(f)
    print(f"✅ Loaded whitelist: {len(whitelist):,} unique parent_asins")
    print(f"   Sample ASINs: {list(whitelist)[:5]}\n")
except FileNotFoundError:
    print(f"❌ ERROR: Whitelist file not found: {WHITELIST_FILE}")
    print("   Please run extract_unique_asins.py first")
    exit(1)

# Connect to PostgreSQL
print("=" * 100)
print("STEP 2: Connecting to PostgreSQL")
print("=" * 100)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False  # We'll manage transactions manually
    cursor = conn.cursor()
    print(f"✅ Connected to database: {DB_CONFIG['dbname']}")
    print(f"   Connection: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
except Exception as e:
    print(f"❌ ERROR connecting to PostgreSQL: {str(e)}")
    exit(1)

# Helper functions
def clean_price(price_value):
    """Convert price to float, handling None and string values"""
    if price_value is None or price_value == 'None':
        return None
    # Handle pandas NA/NaN
    if pd.isna(price_value):
        return None
    try:
        return float(price_value)
    except (ValueError, TypeError):
        return None

def clean_text(text_value):
    """Clean text fields, handling None and empty values"""
    if text_value is None:
        return None
    # Handle pandas NA/NaN
    if pd.isna(text_value):
        return None
    if isinstance(text_value, str):
        return text_value.strip() if text_value.strip() else None
    return str(text_value).strip() if str(text_value).strip() else None

def join_array_to_text(array_value):
    """Join array of strings to single text, handling numpy arrays"""
    if array_value is None:
        return None
    # Handle pandas NA/NaN
    try:
        if pd.isna(array_value):
            return None
    except (TypeError, ValueError):
        # For arrays, pd.isna() might fail, continue processing
        pass
    
    try:
        # Convert numpy array to list
        if isinstance(array_value, np.ndarray):
            # Check if array is empty
            if array_value.size == 0:
                return None
            array_value = array_value.tolist()
        
        # Process list
        if isinstance(array_value, list):
            if len(array_value) == 0:
                return None
            cleaned = [str(item) for item in array_value if item and not pd.isna(item)]
            return ' '.join(cleaned) if cleaned else None
        
        return None
    except Exception:
        return None

def convert_to_postgres_array(array_value):
    """Convert to PostgreSQL TEXT[] array format"""
    if array_value is None:
        return None
    # Handle pandas NA/NaN
    try:
        if pd.isna(array_value):
            return None
    except (TypeError, ValueError):
        # For arrays, pd.isna() might fail, continue processing
        pass
    
    try:
        # Convert numpy array to list
        if isinstance(array_value, np.ndarray):
            # Check if array is empty
            if array_value.size == 0:
                return None
            array_value = array_value.tolist()
        
        # Process list
        if isinstance(array_value, list):
            if len(array_value) == 0:
                return None
            # Filter out None, empty strings, and NaN values
            cleaned = [str(item) for item in array_value if item and not pd.isna(item)]
            return cleaned if cleaned else None
        
        return None
    except Exception:
        return None

def convert_to_jsonb(dict_value):
    """Convert dictionary/object to JSON string for JSONB insertion"""
    if dict_value is None:
        return None
    # Handle pandas NA/NaN
    try:
        if pd.isna(dict_value):
            return None
    except (TypeError, ValueError):
        # For dicts, pd.isna() might fail, continue processing
        pass
    
    try:
        # Handle numpy arrays within dictionaries
        if isinstance(dict_value, dict):
            cleaned_dict = {}
            for key, value in dict_value.items():
                # Skip None and NaN values
                if value is None:
                    continue
                try:
                    if pd.isna(value):
                        continue
                except (TypeError, ValueError):
                    pass
                
                # Convert numpy arrays to lists
                if isinstance(value, np.ndarray):
                    if value.size == 0:
                        continue
                    cleaned_dict[key] = value.tolist()
                elif isinstance(value, list):
                    # Clean list items
                    cleaned_list = [item for item in value if item and not (isinstance(item, float) and pd.isna(item))]
                    if cleaned_list:
                        cleaned_dict[key] = cleaned_list
                else:
                    cleaned_dict[key] = value
            
            # Return JSON string - psycopg2 can handle this with ::jsonb cast
            return json.dumps(cleaned_dict) if cleaned_dict else None
        
        # For non-dict types, try to serialize
        return json.dumps(dict_value) if dict_value else None
    except Exception:
        return None

# Prepare INSERT statement
insert_sql = """
    INSERT INTO products (
        parent_asin, title, description, features,
        average_rating, rating_number, price,
        main_category, categories, store,
        details, images, videos,
        blair_embedding
    ) VALUES (
        %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s::jsonb, %s::jsonb, %s::jsonb,
        %s::vector
    )
    ON CONFLICT (parent_asin) DO NOTHING;
"""

# Process all parquet files
print("=" * 100)
print("STEP 3: Processing Parquet Files")
print("=" * 100)

import glob
parquet_files = sorted(glob.glob(f"{PARQUET_DIR}/*.parquet"))

if not parquet_files:
    print(f"❌ ERROR: No parquet files found in {PARQUET_DIR}")
    exit(1)

print(f"📁 Found {len(parquet_files)} parquet files to process\n")

batch_data = []

for file_idx, parquet_file in enumerate(parquet_files, 1):
    filename = parquet_file.split('/')[-1]
    print(f"\n{'='*100}")
    print(f"[{file_idx}/{len(parquet_files)}] Processing: {filename}")
    print(f"{'='*100}")
    
    try:
        # Read parquet file
        table = pq.read_table(parquet_file)
        df = table.to_pandas()
        
        file_total = len(df)
        file_filtered = 0
        file_errors = 0
        
        print(f"📊 Total products in file: {file_total:,}")
        
        # Process each product
        for idx, row in df.iterrows():
            stats['total_processed'] += 1
            
            parent_asin = row['parent_asin']
            
            # Filter by whitelist
            if parent_asin not in whitelist:
                continue
            
            file_filtered += 1
            stats['total_filtered'] += 1
            
            try:
                # Transform data with proper NA handling
                # Average rating
                avg_rating = row.get('average_rating')
                avg_rating = float(avg_rating) if avg_rating is not None and not pd.isna(avg_rating) else None
                
                # Rating number
                rating_num = row.get('rating_number')
                rating_num = int(rating_num) if rating_num is not None and not pd.isna(rating_num) else None
                
                record = (
                    parent_asin,                                    # parent_asin
                    clean_text(row.get('title')),                  # title
                    join_array_to_text(row.get('description')),    # description
                    join_array_to_text(row.get('features')),       # features
                    avg_rating,                                     # average_rating
                    rating_num,                                     # rating_number
                    clean_price(row.get('price')),                 # price
                    clean_text(row.get('main_category')),          # main_category
                    convert_to_postgres_array(row.get('categories')),  # categories
                    clean_text(row.get('store')),                  # store
                    convert_to_jsonb(row.get('details')),          # details
                    convert_to_jsonb(row.get('images')),           # images
                    convert_to_jsonb(row.get('videos')),           # videos
                    '[' + ','.join(['0'] * 768) + ']'              # blair_embedding (placeholder zeros)
                )
                
                batch_data.append(record)
                
                # Insert batch when it reaches BATCH_SIZE
                if len(batch_data) >= BATCH_SIZE:
                    try:
                        execute_batch(cursor, insert_sql, batch_data, page_size=BATCH_SIZE)
                        conn.commit()
                        stats['total_inserted'] += len(batch_data)
                        print(f"   ✅ Inserted batch: {len(batch_data):,} products (Total: {stats['total_inserted']:,})")
                        batch_data = []
                    except Exception as e:
                        conn.rollback()
                        print(f"   ❌ ERROR inserting batch: {str(e)}")
                        stats['total_errors'] += len(batch_data)
                        batch_data = []
            
            except Exception as e:
                file_errors += 1
                stats['total_errors'] += 1
                if file_errors <= 5:  # Show first 5 errors per file
                    print(f"   ⚠️  Error processing {parent_asin}: {str(e)}")
        
        print(f"\n📊 File Summary:")
        print(f"   Processed: {file_total:,}")
        print(f"   Filtered (in whitelist): {file_filtered:,}")
        print(f"   Errors: {file_errors:,}")
        
        stats['files_processed'] += 1
    
    except Exception as e:
        print(f"❌ ERROR reading file {filename}: {str(e)}")
        continue

# Insert remaining batch
if batch_data:
    try:
        execute_batch(cursor, insert_sql, batch_data, page_size=len(batch_data))
        conn.commit()
        stats['total_inserted'] += len(batch_data)
        print(f"\n✅ Inserted final batch: {len(batch_data):,} products")
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR inserting final batch: {str(e)}")
        stats['total_errors'] += len(batch_data)

# Final summary
print(f"\n{'='*100}")
print("FINAL SUMMARY")
print(f"{'='*100}")

# Get actual count from database
cursor.execute("SELECT COUNT(*) FROM products;")
db_count = cursor.fetchone()[0]

print(f"📊 Files processed: {stats['files_processed']}/{len(parquet_files)}")
print(f"📊 Total products scanned: {stats['total_processed']:,}")
print(f"📊 Products in whitelist: {stats['total_filtered']:,}")
print(f"📊 Successfully inserted: {stats['total_inserted']:,}")
print(f"📊 Errors encountered: {stats['total_errors']:,}")
print(f"📊 Final database count: {db_count:,}")
print(f"\n✅ Data loading complete!")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}")

# Save summary to log file
with open('../logs/load_products_summary.txt', 'w') as f:
    f.write(f"Product Loading Summary\n")
    f.write(f"=======================\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"Files processed: {stats['files_processed']}/{len(parquet_files)}\n")
    f.write(f"Total products scanned: {stats['total_processed']:,}\n")
    f.write(f"Products in whitelist: {stats['total_filtered']:,}\n")
    f.write(f"Successfully inserted: {stats['total_inserted']:,}\n")
    f.write(f"Errors encountered: {stats['total_errors']:,}\n")
    f.write(f"Final database count: {db_count:,}\n")

print(f"\n📄 Summary saved to: logs/load_products_summary.txt")

# Close connection
cursor.close()
conn.close()
print(f"\n🔌 Database connection closed")

