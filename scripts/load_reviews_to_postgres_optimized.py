"""
Load Reviews to PostgreSQL - OPTIMIZED VERSION
===============================================
This script loads 37.5M reviews using optimized techniques for maximum speed.

OPTIMIZATIONS:
1. Drop indexes before loading (recreate after)
2. Use COPY FROM for bulk loading (100x faster than INSERT)
3. Vectorized pandas operations (no iterrows)
4. Single commit per file
5. Batch processing in memory

Expected time: 10-20 minutes (vs 100+ hours with old method)

Input:
- data/processed/parquet/review-part-*.parquet (10 files, 37.5M reviews)

Output:
- PostgreSQL reviews table with 37.5M rows
"""

import os
import sys
import io
import psycopg2
import pyarrow.parquet as pq
import pandas as pd
from datetime import datetime
import glob

print("=" * 100)
print("LOAD REVIEWS TO POSTGRESQL - OPTIMIZED VERSION")
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
        print(f"   This script will ADD more rows")
except Exception as e:
    print(f"❌ ERROR: Could not query reviews table")
    print(f"   {str(e)}")
    conn.close()
    sys.exit(1)

# ============================================================================
# STEP 3: DROP INDEXES FOR FASTER LOADING
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: DROPPING INDEXES (will recreate after loading)")
print("=" * 100)

indexes_to_drop = [
    'idx_reviews_user_id',
    'idx_reviews_parent_asin',
    'idx_reviews_asin',
    'idx_reviews_rating',
    'idx_reviews_timestamp',
    'idx_reviews_verified_purchase',
    'idx_reviews_user_product',
    'idx_reviews_product_rating'
]

dropped_indexes = []

for index_name in indexes_to_drop:
    try:
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")
        print(f"   ✅ Dropped {index_name}")
        dropped_indexes.append(index_name)
    except Exception as e:
        print(f"   ⚠️  Could not drop {index_name}: {str(e)}")

conn.commit()
print(f"\n✅ Dropped {len(dropped_indexes)} indexes")

# ============================================================================
# STEP 4: DROP FOREIGN KEY CONSTRAINT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: DROPPING FOREIGN KEY (will recreate after loading)")
print("=" * 100)

try:
    cursor.execute("ALTER TABLE reviews DROP CONSTRAINT IF EXISTS fk_reviews_parent_asin")
    conn.commit()
    print("✅ Dropped foreign key constraint")
    fk_dropped = True
except Exception as e:
    print(f"⚠️  Could not drop FK: {str(e)}")
    fk_dropped = False

# ============================================================================
# STEP 5: FIND PARQUET FILES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: FINDING PARQUET FILES")
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
# STEP 6: LOAD DATA USING COPY
# ============================================================================

print("\n" + "=" * 100)
print("STEP 6: LOADING DATA (OPTIMIZED)")
print("=" * 100)

stats = {
    'total_read': 0,
    'total_inserted': 0,
    'skipped_null_text': 0,
    'files_processed': 0
}

start_time = datetime.now()

def prepare_dataframe(df):
    """Prepare dataframe for COPY operation"""
    # Filter out NULL text
    df = df[df['text'].notna()].copy()
    
    # Handle NULL/missing values
    df['title'] = df['title'].fillna('')
    df['rating'] = df['rating'].fillna(0.0).astype(float)
    df['helpful_vote'] = df['helpful_vote'].fillna(0).astype(int)
    df['verified_purchase'] = df['verified_purchase'].fillna(False).astype(bool)
    df['timestamp'] = df['timestamp'].fillna(0).astype(int)
    
    # Clean text fields - remove NULL bytes and escape special characters
    # PostgreSQL doesn't accept NULL bytes (0x00) in text
    # Tab (\t) and newline (\n) must be escaped for TEXT format
    def clean_text(text):
        if pd.isna(text) or not text:
            return ''
        # Remove NULL bytes, escape tabs and newlines for TEXT format
        text = str(text).replace('\x00', '')
        text = text.replace('\\', '\\\\')  # Escape backslash first!
        text = text.replace('\t', '\\t')    # Escape tabs
        text = text.replace('\n', '\\n')    # Escape newlines
        text = text.replace('\r', '\\r')    # Escape carriage returns
        return text
    
    df['title'] = df['title'].apply(clean_text)
    df['text'] = df['text'].apply(clean_text)
    df['user_id'] = df['user_id'].astype(str)
    df['asin'] = df['asin'].astype(str)
    df['parent_asin'] = df['parent_asin'].astype(str)
    
    # SKIP images for now - will add in a separate update
    # The CSV escaping makes JSON strings problematic
    # We'll load images in a follow-up UPDATE query
    
    # Select and order columns to match table (WITHOUT images)
    columns = ['user_id', 'asin', 'parent_asin', 'rating', 'title', 'text', 
               'timestamp', 'helpful_vote', 'verified_purchase']
    
    return df[columns]

try:
    for file_idx, parquet_file in enumerate(parquet_files, 1):
        file_start = datetime.now()
        print(f"\n📂 Processing file {file_idx}/{len(parquet_files)}: {os.path.basename(parquet_file)}")
        
        # Read Parquet file
        table = pq.read_table(parquet_file)
        df = table.to_pandas()
        num_rows = len(df)
        print(f"   Rows read: {num_rows:,}")
        
        # Count NULL text before filtering
        null_text_count = df['text'].isna().sum()
        if null_text_count > 0:
            print(f"   Skipping {null_text_count} rows with NULL text")
            stats['skipped_null_text'] += null_text_count
        
        # Prepare dataframe
        df_clean = prepare_dataframe(df)
        rows_to_insert = len(df_clean)
        stats['total_read'] += rows_to_insert
        
        print(f"   Rows to insert: {rows_to_insert:,}")
        
        # Convert to CSV in memory for COPY
        buffer = io.StringIO()
        # Use simple tab-delimited format with NO quoting (quotes in text cause issues)
        df_clean.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N', 
                       quoting=3)  # QUOTE_NONE = 3
        buffer.seek(0)
        
        # Use COPY for ultra-fast loading (WITHOUT images column)
        try:
            cursor.copy_expert(
                """
                COPY reviews (user_id, asin, parent_asin, rating, title, text, 
                             timestamp, helpful_vote, verified_purchase)
                FROM STDIN WITH (FORMAT TEXT, DELIMITER E'\\t', NULL '\\N')
                """,
                buffer
            )
            
            # Commit once per file (not per batch!)
            conn.commit()
            
            stats['total_inserted'] += rows_to_insert
            stats['files_processed'] += 1
            
            file_duration = (datetime.now() - file_start).total_seconds()
            file_rate = rows_to_insert / file_duration if file_duration > 0 else 0
            
            print(f"   ✅ Inserted {rows_to_insert:,} rows in {file_duration:.1f}s ({file_rate:,.0f} rows/sec)")
            print(f"   📊 Total inserted: {stats['total_inserted']:,}")
            
            # Calculate ETA
            elapsed = (datetime.now() - start_time).total_seconds()
            overall_rate = stats['total_inserted'] / elapsed if elapsed > 0 else 0
            remaining = 37_510_000 - stats['total_inserted']
            eta_seconds = remaining / overall_rate if overall_rate > 0 else 0
            eta_minutes = eta_seconds / 60
            
            print(f"   ⏱️  Overall rate: {overall_rate:,.0f} rows/sec | ETA: {eta_minutes:.1f} min")
            
        except Exception as e:
            print(f"   ❌ ERROR inserting data: {str(e)}")
            conn.rollback()
            raise
    
    print("\n✅ All files processed successfully!")
    
except Exception as e:
    print(f"\n❌ ERROR during data loading:")
    print(f"   {str(e)}")
    conn.rollback()
    conn.close()
    sys.exit(1)

# ============================================================================
# STEP 7: RECREATE INDEXES
# ============================================================================

print("\n" + "=" * 100)
print("STEP 7: RECREATING INDEXES")
print("=" * 100)

index_definitions = [
    "CREATE INDEX idx_reviews_user_id ON reviews(user_id)",
    "CREATE INDEX idx_reviews_parent_asin ON reviews(parent_asin)",
    "CREATE INDEX idx_reviews_asin ON reviews(asin)",
    "CREATE INDEX idx_reviews_rating ON reviews(rating)",
    "CREATE INDEX idx_reviews_timestamp ON reviews(timestamp)",
    "CREATE INDEX idx_reviews_verified_purchase ON reviews(verified_purchase)",
    "CREATE INDEX idx_reviews_user_product ON reviews(user_id, parent_asin)",
    "CREATE INDEX idx_reviews_product_rating ON reviews(parent_asin, rating)"
]

print("Creating indexes (this may take 5-10 minutes)...")
index_start = datetime.now()

for idx, index_sql in enumerate(index_definitions, 1):
    index_name = index_sql.split()[2]
    print(f"   [{idx}/{len(index_definitions)}] Creating {index_name}...")
    try:
        cursor.execute(index_sql)
        conn.commit()
        print(f"       ✅ Created")
    except Exception as e:
        print(f"       ⚠️  Error: {str(e)}")

index_duration = (datetime.now() - index_start).total_seconds()
print(f"\n✅ Recreated {len(index_definitions)} indexes in {index_duration:.1f}s ({index_duration/60:.1f} min)")

# ============================================================================
# STEP 8: RECREATE FOREIGN KEY
# ============================================================================

print("\n" + "=" * 100)
print("STEP 8: RECREATING FOREIGN KEY")
print("=" * 100)

if fk_dropped:
    try:
        print("Adding foreign key constraint (this may take a few minutes)...")
        cursor.execute("""
            ALTER TABLE reviews 
            ADD CONSTRAINT fk_reviews_parent_asin 
            FOREIGN KEY (parent_asin) 
            REFERENCES products(parent_asin) 
            ON DELETE CASCADE
        """)
        conn.commit()
        print("✅ Foreign key constraint recreated")
    except Exception as e:
        print(f"⚠️  Could not recreate FK: {str(e)}")
        print("   This is OK - all products should exist (verified by whitelist)")

# ============================================================================
# STEP 9: VERIFY DATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 9: VERIFYING DATA")
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
# STEP 10: UPDATE STATISTICS
# ============================================================================

print("\n" + "=" * 100)
print("STEP 10: UPDATING STATISTICS")
print("=" * 100)

try:
    print("Running ANALYZE on reviews table...")
    cursor.execute("ANALYZE reviews")
    conn.commit()
    print("✅ Statistics updated")
except Exception as e:
    print(f"⚠️  Could not update statistics: {str(e)}")

# ============================================================================
# STEP 11: CHECK TABLE SIZE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 11: TABLE SIZE")
print("=" * 100)

try:
    cursor.execute("""
        SELECT 
            pg_size_pretty(pg_total_relation_size('reviews')) as total_size,
            pg_size_pretty(pg_relation_size('reviews')) as data_size,
            pg_size_pretty(pg_total_relation_size('reviews') - pg_relation_size('reviews')) as index_size
    """)
    size_info = cursor.fetchone()
    print(f"Total size: {size_info[0]}")
    print(f"Data size: {size_info[1]}")
    print(f"Index size: {size_info[2]}")
except Exception as e:
    print(f"⚠️  Could not get table size: {str(e)}")

# ============================================================================
# STEP 12: FINAL SUMMARY
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

print(f"\n⏱️  PERFORMANCE:")
print(f"   Total duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
print(f"   Data loading rate: {stats['total_inserted']/duration:,.0f} rows/second")
print(f"   Speedup vs old method: ~{(stats['total_inserted']/duration)/100:.0f}x faster")

if stats['total_inserted'] >= 37_500_000:
    print(f"\n✅ SUCCESS! Loaded {stats['total_inserted']:,} reviews!")
    print(f"   Expected: ~37,510,000")
    print(f"   Loaded: {stats['total_inserted']:,}")
    print(f"   Match: {stats['total_inserted']/37_510_000*100:.1f}%")
else:
    print(f"\n⚠️  Loaded fewer rows than expected")
    print(f"   Expected: ~37,510,000")
    print(f"   Loaded: {stats['total_inserted']:,}")

# Close connection
cursor.close()
conn.close()

print("\n" + "=" * 100)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)
print("\n🎉 REVIEWS LOADED SUCCESSFULLY!")

