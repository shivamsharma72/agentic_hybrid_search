"""
Convert Electronics.jsonl to Parquet Files with Whitelist Filtering
====================================================================
This script converts the raw Electronics.jsonl file to 10 Parquet files,
filtering by the electronics_products_whitelist to ensure referential integrity.

Input:
- data/processed/reviews_Electronics/Electronics.jsonl (43.9M reviews, 21 GB)
- logs/electronics_products_whitelist.pkl (348,228 products)

Output:
- data/processed/parquet/review-part-XXXXX-of-00010.parquet (10 files)
- data/processed/parquet/_metadata.json (statistics)

Features:
- Whitelist filtering (only reviews for products in database)
- Preserves images field as JSON string
- Batch processing (1M records at a time)
- Progress tracking
- Memory efficient streaming
"""

import json
import pickle
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import os
import sys

print("=" * 100)
print("CONVERT ELECTRONICS.JSONL TO PARQUET FILES")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_JSONL = '../data/processed/reviews_Electronics/Electronics.jsonl'
WHITELIST_FILE = '../logs/electronics_products_whitelist.pkl'
OUTPUT_DIR = '../data/processed/parquet'
NUM_FILES = 10
BATCH_SIZE = 1_000_000  # Process 1M records at a time
PROGRESS_INTERVAL = 100_000  # Print progress every 100K records

# ============================================================================
# STEP 1: LOAD WHITELIST
# ============================================================================

print("=" * 100)
print("STEP 1: LOADING WHITELIST")
print("=" * 100)

try:
    with open(WHITELIST_FILE, 'rb') as f:
        whitelist = pickle.load(f)
    print(f"✅ Loaded whitelist: {len(whitelist):,} products")
except Exception as e:
    print(f"❌ ERROR: Could not load whitelist")
    print(f"   {str(e)}")
    sys.exit(1)

# ============================================================================
# STEP 2: DEFINE SCHEMA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 2: DEFINING PARQUET SCHEMA")
print("=" * 100)

# PyArrow schema matching our PostgreSQL schema
schema = pa.schema([
    ('user_id', pa.string()),
    ('asin', pa.string()),
    ('parent_asin', pa.string()),
    ('rating', pa.float32()),
    ('title', pa.string()),
    ('text', pa.string()),
    ('timestamp', pa.int64()),
    ('helpful_vote', pa.int32()),
    ('verified_purchase', pa.bool_()),
    ('images', pa.string())  # Store as JSON string
])

print("Schema fields:")
for i, field in enumerate(schema, 1):
    print(f"   {i}. {field.name:20s} → {field.type}")

# ============================================================================
# STEP 3: PREPARE OUTPUT
# ============================================================================

print("\n" + "=" * 100)
print("STEP 3: PREPARING OUTPUT DIRECTORY")
print("=" * 100)

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"✅ Output directory: {OUTPUT_DIR}")

# Initialize writers for each output file
writers = []
file_paths = []
for i in range(NUM_FILES):
    file_path = f"{OUTPUT_DIR}/review-part-{i+1:05d}-of-{NUM_FILES:05d}.parquet"
    file_paths.append(file_path)
    # Writers will be created on-demand

print(f"✅ Will create {NUM_FILES} Parquet files")

# ============================================================================
# STEP 4: PROCESS JSONL FILE
# ============================================================================

print("\n" + "=" * 100)
print("STEP 4: PROCESSING JSONL FILE")
print("=" * 100)

# Statistics
stats = {
    'total_read': 0,
    'filtered_out': 0,
    'included': 0,
    'has_images': 0,
    'null_text': 0,
    'errors': 0
}

# Buffers for each output file
buffers = [[] for _ in range(NUM_FILES)]
current_file_idx = 0

def serialize_images(images):
    """Convert images array to JSON string"""
    if not images or len(images) == 0:
        return None
    try:
        return json.dumps(images)
    except:
        return None

def write_buffer_to_parquet(buffer, file_idx):
    """Write buffer to Parquet file"""
    if not buffer:
        return
    
    # Create PyArrow table from buffer
    table = pa.Table.from_pydict({
        'user_id': [r['user_id'] for r in buffer],
        'asin': [r['asin'] for r in buffer],
        'parent_asin': [r['parent_asin'] for r in buffer],
        'rating': [r['rating'] for r in buffer],
        'title': [r['title'] for r in buffer],
        'text': [r['text'] for r in buffer],
        'timestamp': [r['timestamp'] for r in buffer],
        'helpful_vote': [r['helpful_vote'] for r in buffer],
        'verified_purchase': [r['verified_purchase'] for r in buffer],
        'images': [r['images'] for r in buffer]
    }, schema=schema)
    
    # Write or append to Parquet file
    file_path = file_paths[file_idx]
    
    if os.path.exists(file_path):
        # Append to existing file
        existing_table = pq.read_table(file_path)
        combined_table = pa.concat_tables([existing_table, table])
        pq.write_table(combined_table, file_path, compression='snappy')
    else:
        # Create new file
        pq.write_table(table, file_path, compression='snappy')

print(f"Reading from: {INPUT_JSONL}")
print(f"Processing in batches of {BATCH_SIZE:,} records")
print(f"Progress updates every {PROGRESS_INTERVAL:,} records\n")

start_time = datetime.now()

try:
    with open(INPUT_JSONL, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                # Parse JSON
                review = json.loads(line.strip())
                stats['total_read'] += 1
                
                # Progress update
                if stats['total_read'] % PROGRESS_INTERVAL == 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = stats['total_read'] / elapsed
                    eta_seconds = (43_886_944 - stats['total_read']) / rate if rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    print(f"   Processed: {stats['total_read']:,} | "
                          f"Included: {stats['included']:,} | "
                          f"Filtered: {stats['filtered_out']:,} | "
                          f"Rate: {rate:,.0f} records/sec | "
                          f"ETA: {eta_minutes:.1f} min")
                
                # Filter by whitelist
                parent_asin = review.get('parent_asin')
                if not parent_asin or parent_asin not in whitelist:
                    stats['filtered_out'] += 1
                    continue
                
                # Check for null text (required field)
                if not review.get('text'):
                    stats['null_text'] += 1
                    continue
                
                # Count reviews with images
                if review.get('images') and len(review.get('images', [])) > 0:
                    stats['has_images'] += 1
                
                # Prepare record for Parquet
                record = {
                    'user_id': review.get('user_id', ''),
                    'asin': review.get('asin', ''),
                    'parent_asin': parent_asin,
                    'rating': float(review.get('rating', 0.0)),
                    'title': review.get('title', ''),
                    'text': review.get('text', ''),
                    'timestamp': int(review.get('timestamp', 0)),
                    'helpful_vote': int(review.get('helpful_vote', 0)),
                    'verified_purchase': bool(review.get('verified_purchase', False)),
                    'images': serialize_images(review.get('images', []))
                }
                
                # Add to appropriate buffer (round-robin distribution)
                buffers[current_file_idx].append(record)
                stats['included'] += 1
                
                # Move to next file
                current_file_idx = (current_file_idx + 1) % NUM_FILES
                
                # Write buffer if it reaches batch size
                for i, buffer in enumerate(buffers):
                    if len(buffer) >= BATCH_SIZE // NUM_FILES:
                        write_buffer_to_parquet(buffer, i)
                        buffers[i] = []
                
            except json.JSONDecodeError:
                stats['errors'] += 1
                if stats['errors'] < 10:
                    print(f"   ⚠️  JSON decode error at line {line_num}")
            except Exception as e:
                stats['errors'] += 1
                if stats['errors'] < 10:
                    print(f"   ⚠️  Error at line {line_num}: {str(e)}")
    
    # Write remaining buffers
    print("\n   Writing remaining buffers...")
    for i, buffer in enumerate(buffers):
        if buffer:
            write_buffer_to_parquet(buffer, i)
    
    print("✅ Processing complete!")
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to process JSONL file")
    print(f"   {str(e)}")
    sys.exit(1)

# ============================================================================
# STEP 5: GENERATE METADATA
# ============================================================================

print("\n" + "=" * 100)
print("STEP 5: GENERATING METADATA")
print("=" * 100)

# Count rows in each Parquet file
file_stats = []
total_rows = 0

for i, file_path in enumerate(file_paths, 1):
    if os.path.exists(file_path):
        table = pq.read_table(file_path)
        num_rows = table.num_rows
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        total_rows += num_rows
        
        file_stats.append({
            'file': os.path.basename(file_path),
            'rows': num_rows,
            'size_mb': round(file_size_mb, 2)
        })
        
        print(f"   {i}. {os.path.basename(file_path):40s} | {num_rows:,} rows | {file_size_mb:.1f} MB")

# Create metadata JSON
metadata = {
    'source_file': INPUT_JSONL,
    'whitelist_file': WHITELIST_FILE,
    'whitelist_size': len(whitelist),
    'total_reviews_in_source': stats['total_read'],
    'reviews_filtered_out': stats['filtered_out'],
    'reviews_included': stats['included'],
    'reviews_with_images': stats['has_images'],
    'reviews_with_null_text_skipped': stats['null_text'],
    'parsing_errors': stats['errors'],
    'num_parquet_files': len(file_stats),
    'total_rows_in_parquet': total_rows,
    'files': file_stats,
    'created_at': datetime.now().isoformat(),
    'schema': {field.name: str(field.type) for field in schema}
}

metadata_path = f"{OUTPUT_DIR}/_metadata.json"
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Metadata saved: {metadata_path}")

# ============================================================================
# STEP 6: FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("CONVERSION SUMMARY")
print("=" * 100)

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print(f"\n📊 INPUT:")
print(f"   Source file: {INPUT_JSONL}")
print(f"   Total reviews read: {stats['total_read']:,}")

print(f"\n📊 FILTERING:")
print(f"   Whitelist size: {len(whitelist):,} products")
print(f"   Reviews filtered out: {stats['filtered_out']:,} ({stats['filtered_out']/stats['total_read']*100:.1f}%)")
print(f"   Reviews included: {stats['included']:,} ({stats['included']/stats['total_read']*100:.1f}%)")
print(f"   Reviews with NULL text (skipped): {stats['null_text']:,}")
print(f"   Parsing errors: {stats['errors']:,}")

print(f"\n📊 OUTPUT:")
print(f"   Parquet files created: {len(file_stats)}")
print(f"   Total rows in Parquet: {total_rows:,}")
print(f"   Reviews with images: {stats['has_images']:,} ({stats['has_images']/stats['included']*100:.1f}%)")
print(f"   Output directory: {OUTPUT_DIR}")
print(f"   Total size: {sum(f['size_mb'] for f in file_stats):.1f} MB")

print(f"\n⏱️  PERFORMANCE:")
print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
print(f"   Processing rate: {stats['total_read']/duration:,.0f} records/second")

if total_rows != stats['included']:
    print(f"\n⚠️  WARNING: Row count mismatch!")
    print(f"   Expected: {stats['included']:,}")
    print(f"   Actual: {total_rows:,}")
    print(f"   Difference: {abs(total_rows - stats['included']):,}")
else:
    print(f"\n✅ Row count verified: {total_rows:,} reviews")

print(f"\n✅ CONVERSION COMPLETE!")
print(f"   Next step: Run verify_review_parquet.py to validate the files")

print("\n" + "=" * 100)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

