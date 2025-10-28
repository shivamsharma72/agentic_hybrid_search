# Data Download Guide

This guide explains where and how to download the required datasets for loading product data into PostgreSQL.

## 📥 Required Downloads

You need to download 2 sets of data files before running the scripts:

---

## 1. Electronics 5-Core CSV File

### What it is:

Core interaction data (user reviews) for Electronics products, filtered to 5-core (users and products with at least 5 interactions).

### Download Link:

```
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/benchmark/5core/rating_only/Electronics.csv.gz
```

### Instructions:

1. Click the link above or visit the UCSD Amazon 2023 dataset page
2. Download `Electronics.csv.gz`
3. Extract the gzip file: `gunzip Electronics.csv.gz`
4. Rename to: `Electronics_pureid_5core.csv`
5. Place in: `data/raw/Electronics_pureid_5core.csv`

### File Details:

- **Compressed Size:** ~200 MB
- **Uncompressed Size:** ~855 MB
- **Format:** CSV
- **Rows:** 15,473,536 reviews
- **Columns:** user_id, parent_asin, rating, timestamp

### Command Line Download:

```bash
cd data/raw/

# Download
wget https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/benchmark/5core/rating_only/Electronics.csv.gz

# Extract
gunzip Electronics.csv.gz

# Rename
mv Electronics.csv Electronics_pureid_5core.csv

# Verify
ls -lh Electronics_pureid_5core.csv
head -5 Electronics_pureid_5core.csv
```

---

## 2. Product Metadata Parquet Files

### What it is:

Complete product metadata (titles, descriptions, prices, images, etc.) for all Electronics products on Amazon.

### Download Link:

```
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_Electronics
```

### Instructions:

You need to download **10 Parquet files** (0000.parquet through 0009.parquet):

#### Option A: Manual Download (Browser)

1. Visit: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_Electronics
2. Click on each file (0000.parquet through 0009.parquet)
3. Click the download icon/button
4. Place all 10 files in: `data/processed/raw_meta_Electronics/`

#### Option B: Using Python Script

```python
from huggingface_hub import hf_hub_download
import os

# Configuration
repo_id = "McAuley-Lab/Amazon-Reviews-2023"
folder = "raw_meta_Electronics"
local_dir = "data/processed/raw_meta_Electronics"

os.makedirs(local_dir, exist_ok=True)

# Download all 10 files
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

print("✅ All files downloaded!")
```

Save this as `download_parquet.py` and run:

```bash
pip install huggingface_hub
python3 download_parquet.py
```

#### Option C: Using Hugging Face CLI

```bash
pip install huggingface_hub

cd data/processed/raw_meta_Electronics/

# Download all files
for i in {0..9}; do
    huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
        --repo-type dataset \
        --include "raw_meta_Electronics/$(printf "%04d" $i).parquet" \
        --local-dir ./
done
```

### File Details:

- **Total Files:** 10 Parquet files
- **Total Size:** ~2-3 GB (compressed)
- **Total Products:** ~1.6 million Electronics products
- **Format:** Apache Parquet (columnar)
- **Columns:** parent_asin, title, description, features, price, ratings, images, videos, etc.

### Verification:

```bash
# Check all files are present
ls data/processed/raw_meta_Electronics/*.parquet

# Should show 10 files
ls data/processed/raw_meta_Electronics/*.parquet | wc -l

# Check total size
du -sh data/processed/raw_meta_Electronics/

# Verify first file
python3 << EOF
import pyarrow.parquet as pq
table = pq.read_table('data/processed/raw_meta_Electronics/0000.parquet')
print(f"✅ Rows: {table.num_rows:,}")
print(f"✅ Columns: {table.num_columns}")
EOF
```

Expected output:

- 10 files present
- ~160K rows per file
- 14 columns per file

---

## 📂 Final Folder Structure

After downloading all files, your structure should look like:

```
product_data_to_postgres/
└── data/
    ├── raw/
    │   ├── Electronics_pureid_5core.csv  (855 MB)
    │   └── README.md
    └── processed/
        └── raw_meta_Electronics/
            ├── 0000.parquet
            ├── 0001.parquet
            ├── 0002.parquet
            ├── 0003.parquet
            ├── 0004.parquet
            ├── 0005.parquet
            ├── 0006.parquet
            ├── 0007.parquet
            ├── 0008.parquet
            ├── 0009.parquet
            └── README.md
```

---

## ✅ Verification Checklist

Before running the scripts, verify:

- [ ] `data/raw/Electronics_pureid_5core.csv` exists (~855 MB)
- [ ] CSV has 15,473,537 lines (including header)
- [ ] `data/processed/raw_meta_Electronics/` contains 10 Parquet files
- [ ] Total Parquet size is ~2-3 GB
- [ ] You can read the Parquet files with Python (pyarrow installed)

---

## 🚀 Next Steps

Once data is downloaded, proceed with:

1. **Extract whitelist:** `python3 scripts/extract_unique_asins.py`
2. **Setup database:** `python3 scripts/setup_database.py`
3. **Load products:** `python3 scripts/load_products_to_postgres.py`

See `EXECUTION_ORDER.txt` for detailed steps.

---

## 📚 Additional Resources

- **Amazon 2023 Dataset:** https://amazon-reviews-2023.github.io/
- **Dataset Paper:** https://arxiv.org/abs/2403.03952
- **Hugging Face Repo:** https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- **UCSD Lab:** https://cseweb.ucsd.edu/~jmcauley/datasets.html

---

## ⚠️ Important Notes

1. **File Sizes:** Total download is ~3-4 GB. Ensure you have enough disk space.
2. **Git Ignore:** These files are excluded from git (see `.gitignore`). Don't commit them.
3. **One-Time Download:** Once downloaded, files are reused across all scripts.
4. **Internet Speed:** Downloads may take 10-30 minutes depending on your connection.
5. **Storage:** Keep these files; they're needed if you want to reload/reprocess data.
