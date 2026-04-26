# Product Metadata Parquet Files

This folder should contain the product metadata Parquet files for Electronics products.

## Required Files

### 10 Parquet Files from Hugging Face

**Download from:**

```
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_Electronics
```

**Instructions:**

### Option 1: Manual Download (Browser)

1. Visit the Hugging Face link above
2. Download all 10 files:
   - `0000.parquet`
   - `0001.parquet`
   - `0002.parquet`
   - `0003.parquet`
   - `0004.parquet`
   - `0005.parquet`
   - `0006.parquet`
   - `0007.parquet`
   - `0008.parquet`
   - `0009.parquet`
3. Place all files in this folder (`data/processed/raw_meta_Electronics/`)

### Option 2: Using Python Script

If you prefer automated download, you can use the Hugging Face datasets library:

```python
from huggingface_hub import hf_hub_download
import os

repo_id = "McAuley-Lab/Amazon-Reviews-2023"
folder = "raw_meta_Electronics"
local_dir = "data/processed/raw_meta_Electronics"

os.makedirs(local_dir, exist_ok=True)

for i in range(10):
    filename = f"{i:04d}.parquet"
    print(f"Downloading {filename}...")
    hf_hub_download(
        repo_id=repo_id,
        filename=f"{folder}/{filename}",
        repo_type="dataset",
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
```

**File Details:**

- Total Files: 10 Parquet files
- Total Size: ~2-3 GB (compressed)
- Total Products: ~1.6 million Electronics products
- Format: Apache Parquet (columnar)

**What they contain:**

- `parent_asin` - Product ID (PRIMARY KEY)
- `title` - Product title
- `description` - Product description
- `features` - Bullet points of product features
- `price` - Product price
- `average_rating` - Average star rating
- `rating_number` - Number of ratings
- `main_category` - Main product category
- `categories` - All categories product belongs to
- `store` - Store/brand name
- `details` - Additional product details (key-value pairs)
- `images` - Product images (URLs and metadata)
- `videos` - Product videos (URLs and metadata)
- And more...

**Purpose:**
These Parquet files are used by `scripts/load_products_to_postgres.py` to load product metadata into PostgreSQL. The script filters these 1.6M products down to the 368K products that appear in the 5-core dataset.

---

## File Structure After Download

```
data/processed/raw_meta_Electronics/
├── 0000.parquet
├── 0001.parquet
├── 0002.parquet
├── 0003.parquet
├── 0004.parquet
├── 0005.parquet
├── 0006.parquet
├── 0007.parquet
├── 0008.parquet
└── 0009.parquet
```

---

## Notes

- These files are excluded from git (too large for GitHub)
- You must download them manually before running the loading scripts
- The `.gitignore` file prevents accidental commits of large data files
- These are one-time downloads; the files will be reused

---

## Verification

After downloading, verify the files:

```bash
# Check all files exist
ls -lh data/processed/raw_meta_Electronics/

# Count total files (should be 10)
ls data/processed/raw_meta_Electronics/*.parquet | wc -l

# Check total size
du -sh data/processed/raw_meta_Electronics/

# Inspect first file using Python
python3 << EOF
import pyarrow.parquet as pq
table = pq.read_table('data/processed/raw_meta_Electronics/0000.parquet')
print(f"Rows: {table.num_rows:,}")
print(f"Columns: {table.num_columns}")
print(f"Schema:\n{table.schema}")
EOF
```

Expected output:

- 10 files present
- Total size: 2-3 GB
- Each file has ~160K rows
- Schema includes parent_asin, title, description, features, price, etc.

---

## Why Parquet?

Parquet is a columnar storage format that offers:

- **Compression**: Smaller file sizes compared to CSV/JSON
- **Fast Reads**: Only read columns you need
- **Type Safety**: Preserves data types (no parsing needed)
- **Efficiency**: Optimized for analytical queries

This makes it perfect for loading large datasets into databases.
