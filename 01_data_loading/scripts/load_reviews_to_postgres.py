"""
Load Reviews from Parquet to PostgreSQL
========================================
This script loads 15.6M reviews from 10 Parquet files into PostgreSQL.
Optimized for batch insertion with progress tracking.

Input:
- data/processed/reviews_Electronics/ (10 parquet files)

Output:
- PostgreSQL reviews table (15,615,410 reviews)
- Log files with statistics

Expected: ~15-20 minutes for full load
"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_batch
import pyarrow.parquet as pq

print("=" * 100)
print("LOAD REVIEWS FROM PARQUET TO POSTGRESQL")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
PARQUET_DIR = '../data/processed/reviews_Electronics'
DB_NAME = 'amazon_electronics_rag'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'
BATCH_SIZE = 5000  # Insert 5,000 reviews per batch
PROGRESS_INTERVAL = 100000  # Progress update every 100K reviews

# Statistics tracking
stats = {
    'files_processed': 0,
    'reviews_loaded': 0,
    'errors': 0,
    'start_time': datetime.now()
}

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
    conn.autocommit = False  # Manual transaction control for batch inserts
    cursor = conn.cursor()
    print(f"✅ Connected to database: {DB_NAME}")
    print(f"   User: {DB_USER}")
    print(f"   Host: {DB_HOST}:{DB_PORT}\n")
except Exception as e:
    print(f"❌ ERROR: Could not connect to database")
    print(f"   {str(e)}")
    sys.exit(1)

# Step 2: Verify reviews table exists
print("=" * 100)
print("STEP 2: Verifying Reviews Table")
print("=" * 100)

try:
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'reviews'
    """)
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("❌ ERROR: Reviews table does not exist!")
        print("   Run schema/reviews_table.sql first")
        sys.exit(1)
    
    # Get current row count
    cursor.execute("SELECT COUNT(*) FROM reviews")
    existing_count = cursor.fetchone()[0]
    print(f"✅ Reviews table exists")
    print(f"   Existing records: {existing_count:,}\n")
    
except Exception as e:
    print(f"❌ ERROR: Could not verify table")
    print(f"   {str(e)}")
    sys.exit(1)

# Step 3: Get list of parquet files
print("=" * 100)
print("STEP 3: Finding Parquet Files")
print("=" * 100)

parquet_files = sorted([
    os.path.join(PARQUET_DIR, f) 
    for f in os.listdir(PARQUET_DIR) 
    if f.endswith('.parquet')
])

if not parquet_files:
    print(f"❌ ERROR: No parquet files found in {PARQUET_DIR}")
    sys.exit(1)

print(f"✅ Found {len(parquet_files)} parquet files")
for i, file in enumerate(parquet_files, 1):
    filename = os.path.basename(file)
    size_mb = os.path.getsize(file) / (1024 * 1024)
    print(f"   {i:2d}. {filename} ({size_mb:.1f} MB)")
print()

# Step 4: Prepare insert query
print("=" * 100)
print("STEP 4: Preparing Insert Query")
print("=" * 100)

insert_query = """
    INSERT INTO reviews (
        user_id, asin, parent_asin, rating, title, text, 
        timestamp, helpful_vote, verified_purchase
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
"""

print("✅ Insert query prepared")
print("   Batch size: {:,} reviews per batch\n".format(BATCH_SIZE))

# Step 5: Load reviews from parquet files
print("=" * 100)
print("STEP 5: Loading Reviews from Parquet Files")
print("=" * 100)
print(f"Progress updates every {PROGRESS_INTERVAL:,} reviews\n")

total_reviews_loaded = 0
batch_buffer = []

def insert_batch(cursor, batch):
    """Insert a batch of reviews into PostgreSQL"""
    try:
        execute_batch(cursor, insert_query, batch, page_size=BATCH_SIZE)
        return len(batch)
    except Exception as e:
        print(f"   ⚠️  Batch insert error: {str(e)}")
        # Try inserting one by one to identify problematic records
        success_count = 0
        for record in batch:
            try:
                cursor.execute(insert_query, record)
                success_count += 1
            except Exception as e2:
                stats['errors'] += 1
                if stats['errors'] <= 5:
                    print(f"   ⚠️  Record error: {str(e2)}")
        return success_count

try:
    for file_idx, parquet_file in enumerate(parquet_files, 1):
        filename = os.path.basename(parquet_file)
        print(f"Processing file {file_idx}/{len(parquet_files)}: {filename}")
        
        # Read parquet file
        table = pq.read_table(parquet_file)
        df = table.to_pandas()
        
        file_review_count = 0
        
        # Process each review
        for idx, row in df.iterrows():
            # Prepare review data
            review_data = (
                str(row['user_id']),
                str(row['asin']),
                str(row['parent_asin']),
                float(row['rating']),
                str(row['title']) if row['title'] and str(row['title']) != 'None' else None,
                str(row['text']) if row['text'] and str(row['text']) != 'None' else None,
                int(row['timestamp']),
                int(row['helpful_vote']),
                bool(row['verified_purchase'])
            )
            
            batch_buffer.append(review_data)
            file_review_count += 1
            total_reviews_loaded += 1
            
            # Insert batch when buffer is full
            if len(batch_buffer) >= BATCH_SIZE:
                inserted = insert_batch(cursor, batch_buffer)
                batch_buffer = []
                conn.commit()  # Commit after each batch
            
            # Progress update
            if total_reviews_loaded % PROGRESS_INTERVAL == 0:
                elapsed = (datetime.now() - stats['start_time']).total_seconds()
                rate = total_reviews_loaded / elapsed if elapsed > 0 else 0
                print(f"   Loaded {total_reviews_loaded:,} reviews... ({rate:.0f} reviews/sec)")
        
        # Insert remaining reviews from this file
        if batch_buffer:
            inserted = insert_batch(cursor, batch_buffer)
            batch_buffer = []
            conn.commit()
        
        stats['files_processed'] += 1
        print(f"   ✅ Loaded {file_review_count:,} reviews from {filename}\n")

    # Insert any remaining reviews
    if batch_buffer:
        inserted = insert_batch(cursor, batch_buffer)
        conn.commit()
    
    stats['reviews_loaded'] = total_reviews_loaded
    print(f"✅ Finished loading all reviews")
    print(f"   Total loaded: {total_reviews_loaded:,}")
    print(f"   Files processed: {stats['files_processed']}/{len(parquet_files)}")
    
except Exception as e:
    print(f"\n❌ ERROR during loading:")
    print(f"   {str(e)}")
    conn.rollback()
    sys.exit(1)

# Step 6: Verify data integrity
print(f"\n{'='*100}")
print("STEP 6: Verifying Data Integrity")
print("=" * 100)

try:
    # Total count
    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_count = cursor.fetchone()[0]
    print(f"✅ Total reviews in database: {total_count:,}")
    
    # Check for nulls in required fields
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE user_id IS NULL) as null_user_id,
            COUNT(*) FILTER (WHERE parent_asin IS NULL) as null_parent_asin,
            COUNT(*) FILTER (WHERE text IS NULL) as null_text,
            COUNT(*) FILTER (WHERE rating IS NULL) as null_rating
        FROM reviews
    """)
    null_counts = cursor.fetchone()
    print(f"   NULL checks:")
    print(f"     user_id: {null_counts[0]:,}")
    print(f"     parent_asin: {null_counts[1]:,}")
    print(f"     text: {null_counts[2]:,}")
    print(f"     rating: {null_counts[3]:,}")
    
    # Rating distribution
    cursor.execute("""
        SELECT rating, COUNT(*) as count
        FROM reviews
        GROUP BY rating
        ORDER BY rating DESC
    """)
    print(f"\n   Rating distribution:")
    for row in cursor.fetchall():
        print(f"     {row[0]:.1f} stars: {row[1]:,} reviews")
    
    # Verified purchase stats
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE verified_purchase = TRUE) as verified,
            COUNT(*) FILTER (WHERE verified_purchase = FALSE) as unverified
        FROM reviews
    """)
    verified_stats = cursor.fetchone()
    print(f"\n   Purchase verification:")
    print(f"     Verified: {verified_stats[0]:,} ({verified_stats[0]/total_count*100:.1f}%)")
    print(f"     Unverified: {verified_stats[1]:,} ({verified_stats[1]/total_count*100:.1f}%)")
    
    # Top products by review count
    cursor.execute("""
        SELECT parent_asin, COUNT(*) as review_count
        FROM reviews
        GROUP BY parent_asin
        ORDER BY review_count DESC
        LIMIT 5
    """)
    print(f"\n   Top 5 products by review count:")
    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1]:,} reviews")

except Exception as e:
    print(f"❌ ERROR during verification:")
    print(f"   {str(e)}")

# Step 7: Optimize database
print(f"\n{'='*100}")
print("STEP 7: Optimizing Database")
print("=" * 100)

try:
    print("Running VACUUM ANALYZE on reviews table...")
    conn.commit()  # Ensure all transactions are committed
    
    # VACUUM and ANALYZE need to be run outside of transaction
    old_isolation_level = conn.isolation_level
    conn.set_isolation_level(0)  # AUTOCOMMIT mode
    
    cursor.execute("VACUUM ANALYZE reviews")
    
    conn.set_isolation_level(old_isolation_level)
    
    print("✅ Database optimized")
    
    # Get table size
    cursor.execute("""
        SELECT pg_size_pretty(pg_total_relation_size('reviews')) as total_size,
               pg_size_pretty(pg_relation_size('reviews')) as table_size,
               pg_size_pretty(pg_total_relation_size('reviews') - pg_relation_size('reviews')) as index_size
    """)
    size_info = cursor.fetchone()
    print(f"\n   Table sizes:")
    print(f"     Total (with indexes): {size_info[0]}")
    print(f"     Table data: {size_info[1]}")
    print(f"     Indexes: {size_info[2]}")

except Exception as e:
    print(f"⚠️  Warning during optimization:")
    print(f"   {str(e)}")

# Step 8: Generate final summary
print(f"\n{'='*100}")
print("LOADING COMPLETE")
print("=" * 100)

stats['end_time'] = datetime.now()
stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()

print(f"✅ Successfully loaded reviews to PostgreSQL")
print(f"\n📊 Summary:")
print(f"   Files processed: {stats['files_processed']}")
print(f"   Reviews loaded: {stats['reviews_loaded']:,}")
print(f"   Errors: {stats['errors']:,}")
print(f"   Duration: {stats['duration']:.1f} seconds ({stats['duration']/60:.1f} minutes)")
print(f"   Average rate: {stats['reviews_loaded']/stats['duration']:.0f} reviews/second")
print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

# Close connection
cursor.close()
conn.close()

# Save summary to log
summary_path = '../logs/load_reviews_summary.txt'
with open(summary_path, 'w') as f:
    f.write(f"Reviews Loading Summary\n")
    f.write(f"======================\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"Files processed: {stats['files_processed']}\n")
    f.write(f"Reviews loaded: {stats['reviews_loaded']:,}\n")
    f.write(f"Errors: {stats['errors']:,}\n")
    f.write(f"Duration: {stats['duration']:.1f} seconds\n")
    f.write(f"Average rate: {stats['reviews_loaded']/stats['duration']:.0f} reviews/second\n")

print(f"\n📄 Summary saved to: {summary_path}")


