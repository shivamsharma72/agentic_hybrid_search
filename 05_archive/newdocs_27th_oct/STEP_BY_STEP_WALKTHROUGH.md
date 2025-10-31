# 🎯 Step-by-Step Walkthrough

**Exact Commands to Replicate the Entire Pipeline**

---

## 📋 Prerequisites Check

```bash
# Check Python version (need 3.10+)
python3 --version

# Check if PostgreSQL is installed
brew list | grep postgresql

# Check if pgvector is installed
brew list | grep pgvector

# If not installed:
brew install postgresql@17 pgvector

# Install Python packages
pip3 install pyarrow pandas psycopg2-binary tqdm huggingface-hub
```

---

## 🚀 Phase 1: Initial Setup (5 minutes)

### Step 1.1: Create Project Structure

```bash
# Set your project directory
export PROJECT_DIR="$HOME/amazon_rag_project"

# Create directories
mkdir -p "$PROJECT_DIR"/{data/{raw,processed/{raw_meta_Electronics,reviews_Electronics}},logs,scripts,schema,docs}

cd "$PROJECT_DIR"
```

### Step 1.2: Start PostgreSQL

```bash
# Start PostgreSQL
brew services start postgresql@17

# Create postgres user if doesn't exist
createuser -s postgres 2>/dev/null || echo "postgres user already exists"

# Test connection
psql -U postgres -c "SELECT version();"
```

Expected output: PostgreSQL version info

---

## 📥 Phase 2: Download Data (Variable time)

### Step 2.1: Download Product Metadata

```bash
cd "$PROJECT_DIR/data/processed"

# Using Hugging Face CLI (recommended)
huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
    --repo-type dataset \
    --include "raw_meta_Electronics/*.parquet" \
    --local-dir ./
```

**OR** use Python script (save as `scripts/download_meta.py`):

```python
from huggingface_hub import hf_hub_download
import os

repo_id = "McAuley-Lab/Amazon-Reviews-2023"
files = [f"raw_meta_Electronics/full-{i:05d}-of-00010.parquet" for i in range(10)]

for file in files:
    print(f"Downloading {file}...")
    hf_hub_download(repo_id=repo_id, filename=file, repo_type="dataset",
                    local_dir="../data/processed")
```

```bash
cd scripts
python3 download_meta.py
```

Verify:

```bash
ls -lh data/processed/raw_meta_Electronics/
# Should see 10 .parquet files (~1.82 GB total)
```

### Step 2.2: Download Review Data

Place `Electronics.jsonl` in `data/raw/` (22 GB file)

Verify:

```bash
ls -lh data/raw/Electronics.jsonl
# Should be ~22 GB
```

---

## 🗄️ Phase 3: Database Setup (2 minutes)

### Step 3.1: Create Database

```bash
cd "$PROJECT_DIR"

# Create database
psql -U postgres -c "CREATE DATABASE amazon_electronics_rag;"

# Enable pgvector
psql -U postgres -d amazon_electronics_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify
psql -U postgres -d amazon_electronics_rag -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

Expected: Should show vector extension

### Step 3.2: Create Products Table

Save this as `schema/products_table.sql`:

```sql
DROP TABLE IF EXISTS products CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;

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

CREATE INDEX idx_products_rating ON products(average_rating);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_category ON products(main_category);
CREATE INDEX idx_products_rating_number ON products(rating_number);
CREATE INDEX idx_products_store ON products(store);
CREATE INDEX idx_products_categories ON products USING GIN(categories);
CREATE INDEX idx_products_details ON products USING GIN(details);
CREATE INDEX idx_products_embedding ON products USING ivfflat(blair_embedding vector_cosine_ops);
```

Execute:

```bash
psql -U postgres -d amazon_electronics_rag -f schema/products_table.sql
```

Expected: Table created with 8 indexes

---

## 📦 Phase 4: Load Products (5 minutes)

### Step 4.1: Create Loading Script

Save this as `scripts/load_products.py` (abbreviated, see COMPLETE_REPLICATION_GUIDE.md for full code):

```python
import pyarrow.parquet as pq
import psycopg2
from pathlib import Path
from tqdm import tqdm
import json

conn = psycopg2.connect(host="localhost", database="amazon_electronics_rag", user="postgres")
cur = conn.cursor()

# Helper functions
def clean_text(text):
    return str(text).strip() if text and text != 'null' else None

def clean_price(price_str):
    if not price_str or price_str == 'null':
        return None
    try:
        return float(str(price_str).replace('$', '').replace(',', '').strip())
    except:
        return None

def convert_to_jsonb(data):
    if not data or data == 'null' or not isinstance(data, dict):
        return None
    cleaned = {k: v for k, v in data.items() if v is not None and v != 'null'}
    return cleaned if cleaned else None

# Load from parquet files
parquet_dir = Path("../data/processed/raw_meta_Electronics")
batch_size = 5000
total_loaded = 0

for parquet_file in sorted(parquet_dir.glob("*.parquet")):
    print(f"\nProcessing {parquet_file.name}...")
    df = pq.read_table(parquet_file).to_pandas()
    batch = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        parent_asin = clean_text(row.get('parent_asin'))
        title = clean_text(row.get('title'))
        if not parent_asin or not title:
            continue

        record = (
            parent_asin, title,
            clean_text(row.get('description')),
            '\n'.join(str(x) for x in row.get('features', []) if x) if row.get('features') else None,
            float(row['average_rating']) if row.get('average_rating') else None,
            int(row['rating_number']) if row.get('rating_number') else None,
            clean_price(row.get('price')),
            clean_text(row.get('main_category')),
            [str(x) for x in row.get('categories', []) if x] or None,
            clean_text(row.get('store')),
            convert_to_jsonb(row.get('details')),
            convert_to_jsonb(row.get('images')),
            convert_to_jsonb(row.get('videos'))
        )
        batch.append(record)

        if len(batch) >= batch_size:
            cur.executemany("""
                INSERT INTO products (parent_asin, title, description, features,
                    average_rating, rating_number, price, main_category,
                    categories, store, details, images, videos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (parent_asin) DO NOTHING
            """, batch)
            conn.commit()
            total_loaded += len(batch)
            batch = []

    if batch:
        cur.executemany("""
            INSERT INTO products (parent_asin, title, description, features,
                average_rating, rating_number, price, main_category,
                categories, store, details, images, videos)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (parent_asin) DO NOTHING
        """, batch)
        conn.commit()
        total_loaded += len(batch)

print(f"\n✅ Total products loaded: {total_loaded:,}")
cur.close()
conn.close()
```

### Step 4.2: Run Loading Script

```bash
cd "$PROJECT_DIR/scripts"
python3 load_products.py
```

Expected output: `✅ Total products loaded: 348,228`

### Step 4.3: Verify Products

```bash
psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
```

Expected: `348228`

---

## 🎯 Phase 5: Extract Whitelist (30 seconds)

### Step 5.1: Create Extraction Script

Save as `scripts/extract_whitelist.py`:

```python
import psycopg2
import pickle
from pathlib import Path

conn = psycopg2.connect(host="localhost", database="amazon_electronics_rag", user="postgres")
cur = conn.cursor()

print("Extracting Electronics product ASINs...")
cur.execute("SELECT parent_asin FROM products;")
electronics_asins = {row[0] for row in cur.fetchall()}

output_file = Path("../logs/electronics_products_whitelist.pkl")
output_file.parent.mkdir(exist_ok=True)

with open(output_file, 'wb') as f:
    pickle.dump(electronics_asins, f)

print(f"✅ Whitelist saved: {len(electronics_asins):,} ASINs")
cur.close()
conn.close()
```

### Step 5.2: Run Extraction

```bash
cd "$PROJECT_DIR/scripts"
python3 extract_whitelist.py
```

Expected: `✅ Whitelist saved: 348,228 ASINs`

### Step 5.3: Verify Whitelist

```bash
python3 -c "
import pickle
with open('../logs/electronics_products_whitelist.pkl', 'rb') as f:
    asins = pickle.load(f)
print(f'Whitelist contains: {len(asins):,} ASINs')
"
```

Expected: `Whitelist contains: 348,228 ASINs`

---

## 📝 Phase 6: Convert Reviews to Parquet (4-5 minutes)

### Step 6.1: Create Conversion Script

Save as `scripts/convert_reviews.py` (abbreviated):

```python
import json
import pickle
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from tqdm import tqdm
import hashlib

# Load whitelist
with open("../logs/electronics_products_whitelist.pkl", 'rb') as f:
    electronics_asins = pickle.load(f)
print(f"Loaded {len(electronics_asins):,} Electronics ASINs")

input_file = Path("../data/raw/Electronics.jsonl")
output_dir = Path("../data/processed/reviews_Electronics")
output_dir.mkdir(parents=True, exist_ok=True)

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
    ('images', pa.string())
])

def generate_review_id(user_id, parent_asin, timestamp):
    return hashlib.md5(f"{user_id}_{parent_asin}_{timestamp}".encode()).hexdigest()

# First pass: count
print("Counting Electronics reviews...")
total_reviews = 0
with open(input_file, 'r') as f:
    for line in tqdm(f):
        try:
            if json.loads(line).get('parent_asin') in electronics_asins:
                total_reviews += 1
        except:
            continue

print(f"Found {total_reviews:,} Electronics reviews")
reviews_per_file = total_reviews // 10 + 1

# Second pass: convert
print("Converting to Parquet...")
current_batch = []
file_idx = 1

with open(input_file, 'r') as f:
    for line in tqdm(f, total=total_reviews):
        try:
            review = json.loads(line)
            if review.get('parent_asin') not in electronics_asins:
                continue

            current_batch.append({
                'review_id': generate_review_id(review['user_id'], review['parent_asin'], review.get('timestamp', 0)),
                'user_id': review['user_id'],
                'parent_asin': review['parent_asin'],
                'rating': float(review.get('rating', 0)),
                'title': review.get('title'),
                'text': review.get('text'),
                'timestamp': int(review.get('timestamp', 0)),
                'helpful_vote': int(review.get('helpful_vote', 0)),
                'verified_purchase': bool(review.get('verified_purchase', False)),
                'images': json.dumps(review.get('images', []))
            })

            if len(current_batch) >= reviews_per_file:
                output_file = output_dir / f"review-part-{file_idx:05d}-of-00010.parquet"
                pq.write_table(pa.Table.from_pylist(current_batch, schema=schema),
                             output_file, compression='snappy')
                print(f"\nWrote {output_file.name}: {len(current_batch):,} reviews")
                current_batch = []
                file_idx += 1
        except:
            continue

if current_batch:
    output_file = output_dir / f"review-part-{file_idx:05d}-of-00010.parquet"
    pq.write_table(pa.Table.from_pylist(current_batch, schema=schema),
                 output_file, compression='snappy')
    print(f"\nWrote {output_file.name}: {len(current_batch):,} reviews")

print("✅ Conversion complete!")
```

### Step 6.2: Run Conversion

```bash
cd "$PROJECT_DIR/scripts"
python3 convert_reviews.py
```

Expected: 10 parquet files created, ~37.5M total reviews

### Step 6.3: Verify Parquet Files

```bash
ls -lh ../data/processed/reviews_Electronics/
# Should see 10 files, ~800MB each
```

---

## 💾 Phase 7: Load Reviews to Database (30-40 minutes)

### Step 7.1: Create Reviews Table

Save as `schema/reviews_table.sql`:

```sql
DROP TABLE IF EXISTS reviews CASCADE;

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
    CONSTRAINT fk_reviews_parent_asin
        FOREIGN KEY (parent_asin)
        REFERENCES products(parent_asin)
        ON DELETE CASCADE
);

CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_product ON reviews(parent_asin);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_timestamp ON reviews(timestamp);
CREATE INDEX idx_reviews_verified ON reviews(verified_purchase);
CREATE INDEX idx_reviews_helpful ON reviews(helpful_vote);
CREATE INDEX idx_reviews_user_product ON reviews(user_id, parent_asin);
CREATE INDEX idx_reviews_embedding ON reviews USING ivfflat(blair_embedding vector_cosine_ops);
```

Execute:

```bash
psql -U postgres -d amazon_electronics_rag -f schema/reviews_table.sql
```

### Step 7.2: Create Loading Script

Save as `scripts/load_reviews.py` (see COMPLETE_REPLICATION_GUIDE.md for full code)

### Step 7.3: Run Loading

```bash
cd "$PROJECT_DIR/scripts"
python3 load_reviews.py
```

**This will take 30-40 minutes**

Monitor progress in another terminal:

```bash
watch -n 10 'psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM reviews;"'
```

Expected: `37,512,193` reviews loaded

---

## ✅ Phase 8: Final Verification (2 minutes)

### Step 8.1: Check Counts

```bash
psql -U postgres -d amazon_electronics_rag << 'EOF'
SELECT 'Products' as table, COUNT(*)::text as count FROM products
UNION ALL
SELECT 'Reviews' as table, COUNT(*)::text as count FROM reviews;
EOF
```

Expected:

```
   table   |   count
-----------+------------
 Products  | 348228
 Reviews   | 37512193
```

### Step 8.2: Check Database Size

```bash
psql -U postgres -d amazon_electronics_rag -c "
SELECT pg_size_pretty(pg_database_size('amazon_electronics_rag')) as db_size;
"
```

Expected: ~18-20 GB

### Step 8.3: Verify Data Integrity

```bash
psql -U postgres -d amazon_electronics_rag -c "
-- Check for orphaned reviews (should be 0)
SELECT COUNT(*) as orphaned_reviews
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin
WHERE p.parent_asin IS NULL;
"
```

Expected: `0`

### Step 8.4: Sample Data Check

```bash
psql -U postgres -d amazon_electronics_rag -c "
-- Sample products
SELECT parent_asin, LEFT(title, 50), average_rating, price
FROM products
LIMIT 5;
"
```

Should show 5 products with data

```bash
psql -U postgres -d amazon_electronics_rag -c "
-- Sample reviews
SELECT review_id, user_id, rating, LEFT(text, 50)
FROM reviews
LIMIT 5;
"
```

Should show 5 reviews with data

---

## 🎉 Success Criteria

You've successfully replicated the pipeline if:

- [x] PostgreSQL 17 running with pgvector
- [x] Database `amazon_electronics_rag` created
- [x] Products table has 348,228 rows
- [x] Reviews table has 37,512,193 rows
- [x] Database size is ~18-20 GB
- [x] 0 orphaned reviews (foreign key integrity)
- [x] Sample queries return valid data

---

## 🚀 Next Steps

With the database fully loaded, you're ready for:

1. **Phase 3**: Generate BLAIR embeddings for products and reviews
2. **Phase 4**: Build Neo4j graph (users, products, reviews)
3. **Phase 5**: Train GNN on the graph
4. **Phase 6**: Implement hybrid RAG system

---

## 💡 Time Breakdown

| Phase     | Task              | Time           |
| --------- | ----------------- | -------------- |
| 1         | Setup             | 5 min          |
| 2         | Download data     | 15-45 min      |
| 3         | Database setup    | 2 min          |
| 4         | Load products     | 5 min          |
| 5         | Extract whitelist | 30 sec         |
| 6         | Convert reviews   | 4-5 min        |
| 7         | Load reviews      | 30-40 min      |
| 8         | Verify            | 2 min          |
| **Total** |                   | **~1-2 hours** |

---

**You're done! 🎉 Your database is ready for embeddings generation!**

