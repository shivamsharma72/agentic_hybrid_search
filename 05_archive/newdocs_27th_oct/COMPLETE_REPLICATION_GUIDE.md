# 🔄 Complete Replication Guide

**How to Replicate This Entire Data Pipeline from Scratch**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Setup](#system-setup)
3. [Data Acquisition](#data-acquisition)
4. [Phase 1: Product Metadata Processing](#phase-1-product-metadata-processing)
5. [Phase 2: Review Data Processing](#phase-2-review-data-processing)
6. [Phase 3: Database Loading](#phase-3-database-loading)
7. [Phase 4: Verification](#phase-4-verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

```bash
# 1. Python 3.10+
python3 --version  # Should be 3.10 or higher

# 2. PostgreSQL 17
brew install postgresql@17

# 3. Python packages
pip3 install pyarrow pandas psycopg2-binary tqdm
```

### Required Data Files

You need to obtain these from Amazon Reviews 2023 dataset:

1. **Product Metadata** (Parquet files from Hugging Face)

   - Source: `McAuley-Lab/Amazon-Reviews-2023`
   - Path: `raw_meta_Electronics/`
   - Files: 10 parquet files (~1.82 GB)

2. **Review Data** (JSONL format)

   - File: `Electronics.jsonl` (~22 GB)
   - Contains: ~43.9M review records

3. **5-Core Filter CSV** (Optional, for reference)
   - File: `Electronics_pureid_5core.csv` (~532 MB)
   - Contains: Product IDs with ≥5 interactions

### Storage Requirements

- **Working Space**: 50 GB minimum
- **Database Space**: 20 GB for final database
- **Temporary Space**: 15 GB for intermediate files

---

## System Setup

### Step 1: Install PostgreSQL 17

```bash
# Install PostgreSQL 17
brew install postgresql@17

# Start PostgreSQL
brew services start postgresql@17

# Create postgres user (if doesn't exist)
createuser -s postgres

# Verify installation
psql -U postgres -c "SELECT version();"
```

### Step 2: Install pgvector Extension

```bash
# Install pgvector
brew install pgvector

# Verify pgvector files
ls /opt/homebrew/share/postgresql@17/extension/vector*
```

### Step 3: Create Project Structure

```bash
# Set base directory (adjust path as needed)
PROJECT_DIR="/path/to/your/project"
cd "$PROJECT_DIR"

# Create directory structure
mkdir -p data/raw
mkdir -p data/processed/raw_meta_Electronics
mkdir -p data/processed/reviews_Electronics
mkdir -p logs
mkdir -p scripts
mkdir -p schema
mkdir -p docs

# Create tracking files
touch tasks.txt
touch steps.txt
```

---

## Data Acquisition

### Step 1: Download Product Metadata (Parquet Files)

**Option A: Using Hugging Face CLI**

```bash
# Install Hugging Face CLI
pip3 install huggingface-hub

# Download product metadata
cd data/processed
huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
    --repo-type dataset \
    --include "raw_meta_Electronics/*.parquet" \
    --local-dir ./
```

**Option B: Using Python Script**

Create `scripts/download_meta_parquet.py`:

```python
from huggingface_hub import hf_hub_download
import os

repo_id = "McAuley-Lab/Amazon-Reviews-2023"
files = [
    "raw_meta_Electronics/full-00000-of-00010.parquet",
    "raw_meta_Electronics/full-00001-of-00010.parquet",
    "raw_meta_Electronics/full-00002-of-00010.parquet",
    "raw_meta_Electronics/full-00003-of-00010.parquet",
    "raw_meta_Electronics/full-00004-of-00010.parquet",
    "raw_meta_Electronics/full-00005-of-00010.parquet",
    "raw_meta_Electronics/full-00006-of-00010.parquet",
    "raw_meta_Electronics/full-00007-of-00010.parquet",
    "raw_meta_Electronics/full-00008-of-00010.parquet",
    "raw_meta_Electronics/full-00009-of-00010.parquet",
]

output_dir = "../data/processed/raw_meta_Electronics"
os.makedirs(output_dir, exist_ok=True)

for file in files:
    print(f"Downloading {file}...")
    hf_hub_download(
        repo_id=repo_id,
        filename=file,
        repo_type="dataset",
        local_dir="../data/processed"
    )
```

Run it:

```bash
cd scripts
python3 download_meta_parquet.py
```

### Step 2: Download Review Data

```bash
# Download Electronics.jsonl (adjust URL/method based on your source)
cd data/raw
# Use wget, curl, or Hugging Face CLI to download Electronics.jsonl
```

### Step 3: Verify Downloaded Files

```bash
# Check product parquet files
ls -lh data/processed/raw_meta_Electronics/
# Expected: 10 .parquet files, ~1.82 GB total

# Check review JSONL
ls -lh data/raw/Electronics.jsonl
# Expected: ~22 GB file
```

---

## Phase 1: Product Metadata Processing

### Step 1: Create Database and Schema

**Create Database:**

```bash
psql -U postgres -c "CREATE DATABASE amazon_electronics_rag;"
```

**Install pgvector Extension:**

```bash
psql -U postgres -d amazon_electronics_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Create Products Table Schema:**

Save this as `schema/products_table.sql`:

```sql
-- Drop table if exists (for fresh start)
DROP TABLE IF EXISTS products CASCADE;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create products table
CREATE TABLE products (
    parent_asin VARCHAR(20) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    features TEXT,
    average_rating REAL,
    rating_number INTEGER,
    price REAL,
    main_category VARCHAR(100),
    categories TEXT[],
    store VARCHAR(200),
    details JSONB,
    images JSONB,
    videos JSONB,
    blair_embedding VECTOR(768)
);

-- Create indexes
CREATE INDEX idx_products_rating ON products(average_rating);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_category ON products(main_category);
CREATE INDEX idx_products_rating_number ON products(rating_number);
CREATE INDEX idx_products_store ON products(store);
CREATE INDEX idx_products_categories ON products USING GIN(categories);
CREATE INDEX idx_products_details ON products USING GIN(details);
CREATE INDEX idx_products_embedding ON products USING ivfflat(blair_embedding vector_cosine_ops);
```

Execute it:

```bash
psql -U postgres -d amazon_electronics_rag -f schema/products_table.sql
```

### Step 2: Load Products to PostgreSQL

Create `scripts/load_products_to_postgres.py`:

```python
import pyarrow.parquet as pq
import psycopg2
from pathlib import Path
import json
from tqdm import tqdm

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="amazon_electronics_rag",
    user="postgres"
)
cur = conn.cursor()

# Helper functions
def clean_text(text):
    if text is None or text == 'null':
        return None
    return str(text).strip()

def clean_price(price_str):
    if not price_str or price_str == 'null':
        return None
    try:
        price_str = str(price_str).replace('$', '').replace(',', '').strip()
        return float(price_str)
    except:
        return None

def join_array_to_text(arr):
    if not arr or arr == 'null':
        return None
    if isinstance(arr, list):
        return '\n'.join(str(x) for x in arr if x and x != 'null')
    return None

def convert_to_postgres_array(arr):
    if not arr or arr == 'null':
        return None
    if isinstance(arr, list):
        cleaned = [str(x) for x in arr if x and x != 'null']
        return cleaned if cleaned else None
    return None

def convert_to_jsonb(data):
    if not data or data == 'null':
        return None
    if isinstance(data, dict):
        cleaned_dict = {k: v for k, v in data.items()
                       if v is not None and v != 'null'}
        if not cleaned_dict:
            return None
        return cleaned_dict  # Return dict, psycopg2 handles JSONB serialization
    return None

# Load products from parquet files
parquet_dir = Path("../data/processed/raw_meta_Electronics")
parquet_files = sorted(parquet_dir.glob("*.parquet"))

total_loaded = 0
total_skipped = 0
batch_size = 5000
batch = []

for parquet_file in parquet_files:
    print(f"\nProcessing {parquet_file.name}...")
    table = pq.read_table(parquet_file)
    df = table.to_pandas()

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        # Extract and clean fields
        parent_asin = clean_text(row.get('parent_asin'))
        title = clean_text(row.get('title'))

        # Skip if no ASIN or title
        if not parent_asin or not title:
            total_skipped += 1
            continue

        # Prepare record
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

        # Insert batch
        if len(batch) >= batch_size:
            try:
                cur.executemany("""
                    INSERT INTO products (
                        parent_asin, title, description, features,
                        average_rating, rating_number, price, main_category,
                        categories, store, details, images, videos
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (parent_asin) DO NOTHING
                """, batch)
                conn.commit()
                total_loaded += len(batch)
                batch = []
            except Exception as e:
                print(f"Error inserting batch: {e}")
                conn.rollback()
                batch = []

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
        conn.commit()
        total_loaded += len(batch)
    except Exception as e:
        print(f"Error inserting final batch: {e}")
        conn.rollback()

print(f"\n✅ Loading Complete!")
print(f"Total products loaded: {total_loaded:,}")
print(f"Total skipped: {total_skipped:,}")

cur.close()
conn.close()
```

Run it:

```bash
cd scripts
python3 load_products_to_postgres.py
```

Expected output: **~348,228 products loaded**

### Step 3: Extract Electronics Whitelist

Create `scripts/extract_electronics_whitelist.py`:

```python
import psycopg2
import pickle
from pathlib import Path

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="amazon_electronics_rag",
    user="postgres"
)
cur = conn.cursor()

# Extract all parent_asin values
print("Extracting Electronics product ASINs from database...")
cur.execute("SELECT parent_asin FROM products;")
results = cur.fetchall()

# Create set of ASINs
electronics_asins = {row[0] for row in results}

print(f"Extracted {len(electronics_asins):,} Electronics product ASINs")

# Save to pickle file
output_dir = Path("../logs")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "electronics_products_whitelist.pkl"

with open(output_file, 'wb') as f:
    pickle.dump(electronics_asins, f)

print(f"✅ Whitelist saved to: {output_file}")
print(f"   ASINs: {len(electronics_asins):,}")

cur.close()
conn.close()
```

Run it:

```bash
cd scripts
python3 extract_electronics_whitelist.py
```

Expected output: **whitelist with 348,228 ASINs**

---

## Phase 2: Review Data Processing

### Step 1: Convert Reviews JSONL to Parquet (Electronics Only)

Create `scripts/convert_reviews_to_parquet.py`:

```python
import json
import pickle
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from tqdm import tqdm
import hashlib

# Load Electronics whitelist
whitelist_file = Path("../logs/electronics_products_whitelist.pkl")
print(f"Loading whitelist from {whitelist_file}...")
with open(whitelist_file, 'rb') as f:
    electronics_asins = pickle.load(f)
print(f"Loaded {len(electronics_asins):,} Electronics product ASINs")

# Input and output paths
input_file = Path("../data/raw/Electronics.jsonl")
output_dir = Path("../data/processed/reviews_Electronics")
output_dir.mkdir(parents=True, exist_ok=True)

# Configuration
NUM_OUTPUT_FILES = 10
ROWS_PER_FILE = None  # Will calculate based on total
reviews_per_file = []
current_file_idx = 0
current_reviews = []

# Schema for parquet
schema = pa.schema([
    ('review_id', pa.string()),
    ('user_id', pa.string()),
    ('parent_asin', pa.string()),
    ('rating', pa.float32()),
    ('title', pa.string()),
    ('text', pa.string()),
    ('timestamp', pa.int64()),
    ('helpful_vote', pa.int32()),
    ('verified_purchase', pa.bool_()),
    ('images', pa.string())  # JSON string
])

def generate_review_id(user_id, parent_asin, timestamp):
    """Generate unique review ID"""
    data = f"{user_id}_{parent_asin}_{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()

def clean_text(text):
    if not text:
        return None
    return str(text).strip()

# First pass: count Electronics reviews
print("\nFirst pass: Counting Electronics reviews...")
total_electronics_reviews = 0
with open(input_file, 'r', encoding='utf-8') as f:
    for line in tqdm(f, desc="Counting"):
        try:
            review = json.loads(line)
            if review.get('parent_asin') in electronics_asins:
                total_electronics_reviews += 1
        except:
            continue

print(f"Total Electronics reviews found: {total_electronics_reviews:,}")
reviews_per_output_file = total_electronics_reviews // NUM_OUTPUT_FILES + 1
print(f"Reviews per output file: {reviews_per_output_file:,}")

# Second pass: Convert and write
print("\nSecond pass: Converting to Parquet...")
processed = 0
skipped = 0
current_file_idx = 1
current_reviews = []

with open(input_file, 'r', encoding='utf-8') as f:
    for line in tqdm(f, total=total_electronics_reviews, desc="Converting"):
        try:
            review = json.loads(line)

            # Filter by Electronics whitelist
            parent_asin = review.get('parent_asin')
            if parent_asin not in electronics_asins:
                continue

            # Extract fields
            user_id = review.get('user_id')
            timestamp = review.get('timestamp', 0)
            rating = float(review.get('rating', 0))
            title_text = clean_text(review.get('title'))
            review_text = clean_text(review.get('text'))
            helpful_vote = int(review.get('helpful_vote', 0))
            verified = bool(review.get('verified_purchase', False))
            images = json.dumps(review.get('images', [])) if review.get('images') else None

            # Generate review ID
            review_id = generate_review_id(user_id, parent_asin, timestamp)

            # Add to batch
            current_reviews.append({
                'review_id': review_id,
                'user_id': user_id,
                'parent_asin': parent_asin,
                'rating': rating,
                'title': title_text,
                'text': review_text,
                'timestamp': timestamp,
                'helpful_vote': helpful_vote,
                'verified_purchase': verified,
                'images': images
            })

            processed += 1

            # Write file when batch is full
            if len(current_reviews) >= reviews_per_output_file:
                output_file = output_dir / f"review-part-{current_file_idx:05d}-of-{NUM_OUTPUT_FILES:05d}.parquet"
                table = pa.Table.from_pylist(current_reviews, schema=schema)
                pq.write_table(
                    table,
                    output_file,
                    compression='snappy'
                )
                print(f"\n✅ Written {output_file.name}: {len(current_reviews):,} reviews")
                current_reviews = []
                current_file_idx += 1

        except Exception as e:
            skipped += 1
            continue

# Write remaining reviews
if current_reviews:
    output_file = output_dir / f"review-part-{current_file_idx:05d}-of-{NUM_OUTPUT_FILES:05d}.parquet"
    table = pa.Table.from_pylist(current_reviews, schema=schema)
    pq.write_table(table, output_file, compression='snappy')
    print(f"\n✅ Written {output_file.name}: {len(current_reviews):,} reviews")

print(f"\n✅ Conversion Complete!")
print(f"Total processed: {processed:,}")
print(f"Total skipped: {skipped:,}")
print(f"Output files: {current_file_idx}")
```

Run it:

```bash
cd scripts
python3 convert_reviews_to_parquet.py
```

Expected output: **10 parquet files with 37,512,193 total reviews**

This will take **~4-5 minutes** depending on your system.

---

## Phase 3: Database Loading

### Step 1: Create Reviews Table Schema

Save this as `schema/reviews_table.sql`:

```sql
-- Drop table if exists
DROP TABLE IF EXISTS reviews CASCADE;

-- Create reviews table
CREATE TABLE reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    parent_asin VARCHAR(20) NOT NULL,
    rating REAL NOT NULL,
    title TEXT,
    text TEXT,
    timestamp BIGINT NOT NULL,
    helpful_vote INTEGER DEFAULT 0,
    verified_purchase BOOLEAN DEFAULT FALSE,
    images JSONB,
    blair_embedding VECTOR(768),

    -- Foreign key constraint
    CONSTRAINT fk_reviews_parent_asin
        FOREIGN KEY (parent_asin)
        REFERENCES products(parent_asin)
        ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_product ON reviews(parent_asin);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_timestamp ON reviews(timestamp);
CREATE INDEX idx_reviews_verified ON reviews(verified_purchase);
CREATE INDEX idx_reviews_helpful ON reviews(helpful_vote);
CREATE INDEX idx_reviews_user_product ON reviews(user_id, parent_asin);
CREATE INDEX idx_reviews_embedding ON reviews USING ivfflat(blair_embedding vector_cosine_ops);
```

Execute it:

```bash
psql -U postgres -d amazon_electronics_rag -f schema/reviews_table.sql
```

### Step 2: Load Reviews to PostgreSQL

Create `scripts/load_reviews_to_postgres.py`:

```python
import pyarrow.parquet as pq
import psycopg2
from pathlib import Path
from tqdm import tqdm
import json

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="amazon_electronics_rag",
    user="postgres"
)
cur = conn.cursor()

# Load review parquet files
parquet_dir = Path("../data/processed/reviews_Electronics")
parquet_files = sorted(parquet_dir.glob("*.parquet"))

print(f"Found {len(parquet_files)} parquet files")

total_loaded = 0
total_skipped = 0
batch_size = 10000
batch = []

for parquet_file in parquet_files:
    print(f"\nProcessing {parquet_file.name}...")
    table = pq.read_table(parquet_file)
    df = table.to_pandas()

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Loading"):
        try:
            # Parse images if exists
            images_json = None
            if row.get('images') and row['images'] != 'null':
                try:
                    images_json = json.loads(row['images'])
                except:
                    pass

            # Prepare record
            record = (
                row['review_id'],
                row['user_id'],
                row['parent_asin'],
                float(row['rating']),
                row.get('title'),
                row.get('text'),
                int(row['timestamp']),
                int(row.get('helpful_vote', 0)),
                bool(row.get('verified_purchase', False)),
                json.dumps(images_json) if images_json else None
            )

            batch.append(record)

            # Insert batch
            if len(batch) >= batch_size:
                try:
                    cur.executemany("""
                        INSERT INTO reviews (
                            review_id, user_id, parent_asin, rating,
                            title, text, timestamp, helpful_vote,
                            verified_purchase, images
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (review_id) DO NOTHING
                    """, batch)
                    conn.commit()
                    total_loaded += len(batch)
                    batch = []
                except Exception as e:
                    print(f"\nError inserting batch: {e}")
                    conn.rollback()
                    total_skipped += len(batch)
                    batch = []

        except Exception as e:
            total_skipped += 1
            continue

# Insert remaining
if batch:
    try:
        cur.executemany("""
            INSERT INTO reviews (
                review_id, user_id, parent_asin, rating,
                title, text, timestamp, helpful_vote,
                verified_purchase, images
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (review_id) DO NOTHING
        """, batch)
        conn.commit()
        total_loaded += len(batch)
    except Exception as e:
        print(f"\nError inserting final batch: {e}")
        conn.rollback()
        total_skipped += len(batch)

print(f"\n✅ Loading Complete!")
print(f"Total reviews loaded: {total_loaded:,}")
print(f"Total skipped: {total_skipped:,}")

cur.close()
conn.close()
```

Run it:

```bash
cd scripts
python3 load_reviews_to_postgres.py
```

Expected: **37,512,193 reviews loaded** (takes 30-40 minutes)

---

## Phase 4: Verification

### Verify Database Contents

```bash
psql -U postgres -d amazon_electronics_rag << 'EOF'
-- Check counts
SELECT 'Products' as table, COUNT(*)::text as count FROM products
UNION ALL
SELECT 'Reviews' as table, COUNT(*)::text as count FROM reviews;

-- Check database size
SELECT pg_size_pretty(pg_database_size('amazon_electronics_rag')) as db_size;

-- Sample products
SELECT parent_asin, LEFT(title, 50), average_rating, price
FROM products LIMIT 5;

-- Sample reviews
SELECT review_id, user_id, parent_asin, rating, LEFT(text, 50)
FROM reviews LIMIT 5;

-- Verify no orphaned reviews (should be 0)
SELECT COUNT(*) as orphaned_reviews
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin
WHERE p.parent_asin IS NULL;
EOF
```

Expected results:

- Products: **348,228**
- Reviews: **37,512,193**
- Database size: **~18-20 GB**
- Orphaned reviews: **0**

---

## Troubleshooting

### PostgreSQL Won't Start

```bash
# Check logs
tail -50 /opt/homebrew/var/log/postgresql@17.log

# Restart
brew services restart postgresql@17
```

### Database Connection Error

```bash
# Create postgres user if missing
createuser -s postgres

# Test connection
psql -U postgres -l
```

### pgvector Extension Error

```bash
# Reinstall pgvector
brew reinstall pgvector

# Verify
psql -U postgres -d amazon_electronics_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Foreign Key Violations During Review Loading

This means some reviews reference products not in your database. **This shouldn't happen** if you:

1. First loaded products to DB
2. Extracted whitelist FROM that DB
3. Used that whitelist to filter reviews

If it happens:

```bash
# Check which ASINs are causing issues
psql -U postgres -d amazon_electronics_rag -c "
SELECT DISTINCT r.parent_asin
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin
WHERE p.parent_asin IS NULL
LIMIT 10;
"
```

### Out of Disk Space

```bash
# Check available space
df -h

# Clean up temporary files
rm -rf data/processed/reviews_Electronics/*.tmp
```

---

## Summary Checklist

- [ ] PostgreSQL 17 installed and running
- [ ] pgvector extension installed
- [ ] Downloaded 10 product parquet files (1.82 GB)
- [ ] Downloaded Electronics.jsonl (22 GB)
- [ ] Created project directory structure
- [ ] Created products table in PostgreSQL
- [ ] Loaded 348,228 products to PostgreSQL
- [ ] Extracted electronics whitelist (348,228 ASINs)
- [ ] Converted reviews to 10 parquet files (37.5M reviews)
- [ ] Created reviews table in PostgreSQL
- [ ] Loaded 37.5M reviews to PostgreSQL
- [ ] Verified: 0 orphaned reviews
- [ ] Database size: ~18-20 GB

---

## Next Steps After Replication

Once all data is loaded:

1. **Generate BLAIR Embeddings** (Phase 3)
2. **Build Neo4j Graph** (Phase 4)
3. **Train GNN** (Phase 5)
4. **Implement RAG System** (Phase 6)

---

**Total Time to Replicate**: ~2-3 hours (depending on download speeds)

**Storage Required**: ~50 GB total (including temporary files)

**Result**: Fully loaded PostgreSQL database with 348K products and 37.5M reviews, ready for embeddings generation!
