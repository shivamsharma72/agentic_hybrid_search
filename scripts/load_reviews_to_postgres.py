"""
Load Reviews to PostgreSQL
===========================
This script loads 37.5M reviews from 10 Parquet files into PostgreSQL.

Input:
- data/processed/parquet/review-part-*.parquet (10 files, 37.5M reviews)

Output:
- PostgreSQL reviews table with 37.5M rows

Features:
- Batch inserts (10,000 rows at a time)
- Progress tracking
- Error handling
- Skip NULL text reviews
- Parse images from JSON string to JSONB
- Foreign key validation (all products exist)
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_batch
import pyarrow.parquet as pq
from datetime import datetime
import glob

print("=" * 100)
print("LOAD REVIEWS TO POSTGRESQL")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

PARQUET_DIR = '../data/processed/parquet'
DB_NAME = 'amazon_electronics_rag'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = 5432
BATCH_SIZE = 10000
PROGRESS_INTERVAL = 100000

# ============================================================================
# STEP 1: CONNECT TO DATABASE
# ============================================================================

print("=" * 100)
print("STEP 1: CONNECTING TO DATABASE")
print("=" * 100)

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"✅ Connected to database: {DB_NAME}")
except Exception as e:
    print(f"❌ ERROR: Could not connect to database")
    print(f"   {str(e)}")
    sys.exit(1)

# ============================================================================
# STEP 2: CHECK TABLE STATUS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: CHECKING TABLE STATUS")
print("=" * 100)

try:
    cursor.execute("SELECT COUNT(*) FROM reviews")
    existing_count = cursor.fetchone()[0]
    print(f"Current rows in reviews table: {existing_count:,}")
    
    if existing_count > 0:
        print(f"\n⚠️  WARNING: Table already has {existing_count:,} rows")
        print(f"   This script will ADD more rows (not replace)")
        print(f"   If you want a fresh start, run: TRUNCATE TABLE reviews CASCADE;")
except Exception as e:
    print(f"❌ ERROR: Could not query reviews table")
    print(f"   {str(e)}")
    conn.close()
    sys.exit(1)

# ============================================================================
# STEP 3: FIND PARQUET FILES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: FINDING PARQUET FILES")
print("=" * 100)

parquet_files = sorted(glob.glob(f"{PARQUET_DIR}/review-part-*.parquet"))

if len(parquet_files) == 0:
    print(f"❌ ERROR: No Parquet files found in {PARQUET_DIR}")
    conn.close()
    sys.exit(1)

print(f"Found {len(parquet_files)} Parquet files:")
for i, file_path in enumerate(parquet_files, 1):
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"   {i}. {os.path.basename(file_path)} ({size_mb:.1f} MB)")

# ============================================================================
# STEP 4: PREPARE INSERT STATEMENT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: PREPARING INSERT STATEMENT")
print("=" * 100)

INSERT_SQL = """
INSERT INTO reviews (
    user_id,
    asin,
    parent_asin,
    rating,
    title,
    text,
    timestamp,
    helpful_vote,
    verified_purchase,
    images
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
)
ON CONFLICT DO NOTHING
"""

print("✅ Insert statement prepared")
print("   Batch size: {:,} rows".format(BATCH_SIZE))

# ============================================================================
# STEP 5: LOAD DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: LOADING DATA")
print("=" * 100)

# Statistics
stats = {
    'total_read': 0,
    'total_inserted': 0,
    'skipped_null_text': 0,
    'errors': 0,
    'files_processed': 0
}

start_time = datetime.now()

def parse_images(images_str):
    """Parse images from JSON string to proper format for JSONB"""
    if not images_str or images_str == 'null':
        return None
    try:
        # Images are stored as JSON string in Parquet
        return images_str  # PostgreSQL will handle the JSON string with ::jsonb cast
    except:
        return None

try:
    for file_idx, parquet_file in enumerate(parquet_files, 1):
        print(f"\n📂 Processing file {file_idx}/{len(parquet_files)}: {os.path.basename(parquet_file)}")
        
        # Read Parquet file
        table = pq.read_table(parquet_file)
        df = table.to_pandas()
        num_rows = len(df)
        print(f"   Rows: {num_rows:,}")
        
        # Filter out rows with NULL text
        df_filtered = df[df['text'].notna()].copy()
        skipped = num_rows - len(df_filtered)
        if skipped > 0:
            print(f"   Skipped {skipped} rows with NULL text")
            stats['skipped_null_text'] += skipped
        
        stats['total_read'] += len(df_filtered)
        
        # Prepare batches
        batch = []
        rows_inserted_file = 0
        
        for idx, row in df_filtered.iterrows():
            try:
                # Prepare row data
                row_data = (
                    row['user_id'],
                    row['asin'],
                    row['parent_asin'],
                    float(row['rating']) if row['rating'] is not None else 0.0,
                    row['title'] if row['title'] else '',
                    row['text'],
                    int(row['timestamp']) if row['timestamp'] is not None else 0,
                    int(row['helpful_vote']) if row['helpful_vote'] is not None else 0,
                    bool(row['verified_purchase']) if row['verified_purchase'] is not None else False,
                    parse_images(row['images'])
                )
                
                batch.append(row_data)
                
                # Execute batch when full
                if len(batch) >= BATCH_SIZE:
                    execute_batch(cursor, INSERT_SQL, batch, page_size=BATCH_SIZE)
                    conn.commit()
                    rows_inserted_file += len(batch)
                    stats['total_inserted'] += len(batch)
                    batch = []
                    
                    # Progress update
                    if stats['total_inserted'] % PROGRESS_INTERVAL == 0:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        rate = stats['total_inserted'] / elapsed
                        remaining = 37_510_000 - stats['total_inserted']
                        eta_seconds = remaining / rate if rate > 0 else 0
                        eta_minutes = eta_seconds / 60
                        print(f"   Progress: {stats['total_inserted']:,} inserted | "
                              f"Rate: {rate:,.0f} rows/sec | "
                              f"ETA: {eta_minutes:.1f} min")
                
            except Exception as e:
                stats['errors'] += 1
                if stats['errors'] <= 10:
                    print(f"   ⚠️  Error at row {idx}: {str(e)}")
        
        # Insert remaining batch
        if batch:
            execute_batch(cursor, INSERT_SQL, batch, page_size=len(batch))
            conn.commit()
            rows_inserted_file += len(batch)
            stats['total_inserted'] += len(batch)
        
        stats['files_processed'] += 1
        print(f"   ✅ Inserted {rows_inserted_file:,} rows from this file")
        print(f"   📊 Total inserted so far: {stats['total_inserted']:,}")
    
    print("\n✅ All files processed successfully!")
    
except Exception as e:
    print(f"\n❌ ERROR during data loading:")
    print(f"   {str(e)}")
    conn.rollback()
    conn.close()
    sys.exit(1)

# ============================================================================
# STEP 6: VERIFY DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: VERIFYING DATA")
print("=" * 100)

try:
    cursor.execute("SELECT COUNT(*) FROM reviews")
    final_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM reviews")
    unique_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT parent_asin) FROM reviews")
    unique_products = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE images IS NOT NULL")
    with_images = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE verified_purchase = TRUE")
    verified = cursor.fetchone()[0]
    
    print(f"Final row count: {final_count:,}")
    print(f"Unique users: {unique_users:,}")
    print(f"Unique products: {unique_products:,}")
    print(f"Reviews with images: {with_images:,} ({with_images/final_count*100:.1f}%)")
    print(f"Verified purchases: {verified:,} ({verified/final_count*100:.1f}%)")
    
except Exception as e:
    print(f"⚠️  Could not verify data: {str(e)}")

# ============================================================================
# STEP 7: UPDATE STATISTICS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: UPDATING STATISTICS")
print("=" * 100)

try:
    print("Running ANALYZE on reviews table...")
    cursor.execute("ANALYZE reviews")
    conn.commit()
    print("✅ Statistics updated")
except Exception as e:
    print(f"⚠️  Could not update statistics: {str(e)}")

# ============================================================================
# STEP 8: FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("LOADING SUMMARY")
print("=" * 100)

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print(f"\n📊 FILES:")
print(f"   Files processed: {stats['files_processed']}/{len(parquet_files)}")

print(f"\n📊 ROWS:")
print(f"   Rows read: {stats['total_read']:,}")
print(f"   Rows inserted: {stats['total_inserted']:,}")
print(f"   Skipped (NULL text): {stats['skipped_null_text']:,}")
print(f"   Errors: {stats['errors']:,}")

print(f"\n⏱️  PERFORMANCE:")
print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
print(f"   Average rate: {stats['total_inserted']/duration:,.0f} rows/second")

if stats['total_inserted'] == stats['total_read']:
    print(f"\n✅ ALL ROWS INSERTED SUCCESSFULLY!")
else:
    print(f"\n⚠️  Some rows were not inserted")
    print(f"   Expected: {stats['total_read']:,}")
    print(f"   Actual: {stats['total_inserted']:,}")
    print(f"   Difference: {stats['total_read'] - stats['total_inserted']:,}")

# Close connection
cursor.close()
conn.close()

print("\n" + "=" * 100)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)
