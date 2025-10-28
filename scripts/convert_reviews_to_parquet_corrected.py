"""
Convert Reviews JSONL to Parquet Files (CORRECTED VERSION)
===========================================================
This script converts Electronics.jsonl to Parquet files using the CORRECT whitelist:
- Uses Electronics products from products table (348,228 products)
- NOT the mixed-category 5-core CSV

Input:
- data/raw/Electronics.jsonl (~44M lines)
- logs/electronics_products_whitelist.pkl (348,228 Electronics products)

Output:
- data/processed/reviews_Electronics/ (10 parquet files with Electronics-only reviews)

Expected: ~9-12M Electronics reviews (not 15.6M mixed)
Time: ~15-20 minutes
"""

import json
import os
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
from collections import defaultdict
import pickle

print("=" * 100)
print("CONVERT REVIEWS JSONL TO PARQUET (CORRECTED - ELECTRONICS ONLY)")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Configuration
INPUT_JSONL = '../data/raw/Electronics.jsonl'
WHITELIST_FILE = '../logs/electronics_products_whitelist.pkl'
OUTPUT_DIR = '../data/processed/reviews_Electronics'
NUM_FILES = 10
BATCH_SIZE = 10000
PROGRESS_INTERVAL = 100000

# Statistics tracking
stats = {
    'lines_processed': 0,
    'reviews_filtered': 0,
    'json_errors': 0,
    'files_created': 0
}

# Step 1: Create output directory
print("=" * 100)
print("STEP 1: Creating Output Directory")
print("=" * 100)

os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"✅ Created/verified directory: {OUTPUT_DIR}\n")

# Step 2: Load Electronics products whitelist
print("=" * 100)
print("STEP 2: Loading Electronics Products Whitelist")
print("=" * 100)

print(f"📂 Reading: {WHITELIST_FILE}")

try:
    with open(WHITELIST_FILE, 'rb') as f:
        whitelist = pickle.load(f)
    
    print(f"✅ Loaded {len(whitelist):,} Electronics products")
    print(f"   Sample ASINs: {list(whitelist)[:5]}\n")
except FileNotFoundError:
    print(f"❌ ERROR: Whitelist file not found: {WHITELIST_FILE}")
    exit(1)

# Step 3: Define Parquet Schema
print("=" * 100)
print("STEP 3: Defining Parquet Schema")
print("=" * 100)

schema = pa.schema([
    ('rating', pa.float32()),
    ('title', pa.string()),
    ('text', pa.string()),
    ('asin', pa.string()),
    ('parent_asin', pa.string()),
    ('user_id', pa.string()),
    ('timestamp', pa.int64()),
    ('helpful_vote', pa.int32()),
    ('verified_purchase', pa.bool_()),
])

print("✅ Schema defined with 9 fields\n")

# Step 4: Initialize Parquet Writers
print("=" * 100)
print("STEP 4: Initializing Parquet Writers")
print("=" * 100)

writers = {}
file_paths = {}

for i in range(1, NUM_FILES + 1):
    file_path = os.path.join(OUTPUT_DIR, f'review-part-{i:05d}-of-{NUM_FILES:05d}.parquet')
    file_paths[i] = file_path

print(f"✅ Prepared {NUM_FILES} output files\n")

# Step 5: Process JSONL and Convert to Parquet
print("=" * 100)
print("STEP 5: Processing JSONL and Converting to Parquet")
print("=" * 100)

batches = defaultdict(list)
current_file_idx = 1

def write_batch_to_parquet(file_idx, batch_data):
    """Write accumulated batch to parquet file"""
    if not batch_data:
        return
    
    table = pa.Table.from_pylist(batch_data, schema=schema)
    file_path = file_paths[file_idx]
    
    if file_idx not in writers:
        writers[file_idx] = pq.ParquetWriter(file_path, schema, compression='snappy')
        stats['files_created'] += 1
    
    writers[file_idx].write_table(table)

def clean_review_data(review):
    """Extract and clean review fields for parquet"""
    return {
        'rating': float(review.get('rating', 0.0)),
        'title': str(review.get('title', '')) if review.get('title') else None,
        'text': str(review.get('text', '')) if review.get('text') else None,
        'asin': str(review.get('asin', '')),
        'parent_asin': str(review.get('parent_asin', '')),
        'user_id': str(review.get('user_id', '')),
        'timestamp': int(review.get('timestamp', 0)),
        'helpful_vote': int(review.get('helpful_vote', 0)),
        'verified_purchase': bool(review.get('verified_purchase', False))
    }

print(f"📂 Reading: {INPUT_JSONL}")
print(f"   Filtering by Electronics products whitelist ({len(whitelist):,} products)")
print(f"   Progress updates every {PROGRESS_INTERVAL:,} lines\n")

try:
    with open(INPUT_JSONL, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['lines_processed'] += 1
            
            if not line.strip():
                continue
            
            try:
                review = json.loads(line)
                parent_asin = review.get('parent_asin', '')
                
                # Check if parent_asin is in Electronics whitelist
                if parent_asin in whitelist:
                    stats['reviews_filtered'] += 1
                    
                    cleaned = clean_review_data(review)
                    batches[current_file_idx].append(cleaned)
                    
                    if len(batches[current_file_idx]) >= BATCH_SIZE:
                        write_batch_to_parquet(current_file_idx, batches[current_file_idx])
                        batches[current_file_idx] = []
                    
                    current_file_idx = (current_file_idx % NUM_FILES) + 1
            
            except json.JSONDecodeError:
                stats['json_errors'] += 1
                if stats['json_errors'] <= 5:
                    print(f"   ⚠️  JSON error at line {line_num}")
            except Exception as e:
                if stats['json_errors'] <= 5:
                    print(f"   ⚠️  Error at line {line_num}: {str(e)}")
                stats['json_errors'] += 1
            
            if line_num % PROGRESS_INTERVAL == 0:
                print(f"   Processed {line_num:,} lines... (Filtered: {stats['reviews_filtered']:,} Electronics reviews)")
    
    print(f"\n✅ Finished reading JSONL file")
    print(f"   Total lines: {stats['lines_processed']:,}")
    print(f"   Filtered Electronics reviews: {stats['reviews_filtered']:,}")

except FileNotFoundError:
    print(f"❌ ERROR: Input file not found: {INPUT_JSONL}")
    exit(1)

# Step 6: Write remaining batches and close writers
print(f"\n{'='*100}")
print("STEP 6: Writing Final Batches")
print("=" * 100)

for file_idx in range(1, NUM_FILES + 1):
    if batches[file_idx]:
        write_batch_to_parquet(file_idx, batches[file_idx])
        print(f"   ✅ Wrote final batch to file {file_idx}")

for file_idx, writer in writers.items():
    writer.close()

print(f"\n✅ All writers closed")

# Step 7: Verify files and generate statistics
print(f"\n{'='*100}")
print("STEP 7: Verifying Files and Generating Statistics")
print("=" * 100)

file_stats = []
total_size = 0
total_records = 0

for i in range(1, NUM_FILES + 1):
    file_path = file_paths[i]
    if os.path.exists(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        total_size += size_mb
        
        parquet_file = pq.read_table(file_path)
        num_records = len(parquet_file)
        total_records += num_records
        
        file_stats.append({
            'file': f'review-part-{i:05d}-of-{NUM_FILES:05d}.parquet',
            'size_mb': size_mb,
            'records': num_records
        })
        
        print(f"   ✅ File {i:2d}: {size_mb:6.1f} MB | {num_records:,} records")

print(f"\n📊 Summary:")
print(f"   Total files: {len(file_stats)}")
print(f"   Total size: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
print(f"   Total records: {total_records:,}")
print(f"   JSON errors: {stats['json_errors']:,}")

if total_records == stats['reviews_filtered']:
    print(f"\n✅ Record count verified: {total_records:,} matches filtered count")
else:
    print(f"\n⚠️  WARNING: Record count mismatch!")
    print(f"   Filtered: {stats['reviews_filtered']:,}")
    print(f"   In files: {total_records:,}")

# Step 8: Create metadata file
print(f"\n{'='*100}")
print("STEP 8: Creating Metadata")
print("=" * 100)

metadata = {
    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'source': 'Electronics.jsonl',
    'whitelist': 'electronics_products_whitelist.pkl (from products table)',
    'whitelist_count': len(whitelist),
    'total_lines_processed': stats['lines_processed'],
    'reviews_filtered': stats['reviews_filtered'],
    'total_records': total_records,
    'num_files': len(file_stats),
    'total_size_mb': round(total_size, 2),
    'note': 'Electronics-only reviews (not mixed categories)',
    'files': file_stats
}

import json as json_module
metadata_path = os.path.join(OUTPUT_DIR, '_metadata.json')
with open(metadata_path, 'w') as f:
    json_module.dump(metadata, f, indent=2)

print(f"✅ Metadata saved to: {metadata_path}")

# Final Summary
print(f"\n{'='*100}")
print("CONVERSION COMPLETE - ELECTRONICS ONLY")
print("=" * 100)
print(f"✅ Processed {stats['lines_processed']:,} lines")
print(f"✅ Filtered {stats['reviews_filtered']:,} Electronics reviews")
print(f"✅ Created {len(file_stats)} parquet files")
print(f"✅ Total size: {total_size/1024:.2f} GB")
print(f"✅ Output: {OUTPUT_DIR}")
print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

# Save summary to log
summary_path = '../logs/convert_reviews_corrected_summary.txt'
with open(summary_path, 'w') as f:
    f.write(f"Review JSONL to Parquet Conversion (CORRECTED)\n")
    f.write(f"===============================================\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"Whitelist: Electronics products only ({len(whitelist):,})\n")
    f.write(f"Lines processed: {stats['lines_processed']:,}\n")
    f.write(f"Electronics reviews filtered: {stats['reviews_filtered']:,}\n")
    f.write(f"Records in files: {total_records:,}\n")
    f.write(f"Files created: {len(file_stats)}\n")
    f.write(f"Total size: {total_size:.1f} MB ({total_size/1024:.2f} GB)\n")
    f.write(f"JSON errors: {stats['json_errors']:,}\n")

print(f"\n📄 Summary saved to: {summary_path}")


