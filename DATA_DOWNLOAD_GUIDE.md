# Data Download Guide - Review Data

This guide explains where and how to download the required review dataset for loading into PostgreSQL.

## 📥 Required Downloads

You need to download the Electronics review JSONL file before running the conversion scripts.

---

## Electronics Review Data (JSONL)

### What it is:

Complete review data (text, ratings, timestamps, etc.) for all Electronics products on Amazon.

### Download Link:

```
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_review_Electronics
```

### Instructions:

#### Option A: Manual Download (Browser)

1. Visit: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_review_Electronics
2. Look for the JSONL file (might be compressed as `.jsonl.gz`)
3. Click to download
4. If compressed, extract: `gunzip Electronics.jsonl.gz`
5. Place in: `data/raw/Electronics.jsonl`

#### Option B: Using Hugging Face Datasets Library

```python
from datasets import load_dataset

# Load the dataset (streaming to avoid memory issues)
dataset = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    "raw_review_Electronics",
    split="full",
    streaming=True
)

# Save to JSONL
with open("data/raw/Electronics.jsonl", "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")
```

#### Option C: Using Hugging Face CLI

```bash
pip install huggingface_hub

cd data/raw/

huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
    --repo-type dataset \
    --include "raw_review_Electronics/*" \
    --local-dir ./
```

### File Details:

- **Size:** ~5-6 GB (uncompressed JSONL)
- **Format:** JSON Lines (one JSON object per line)
- **Total Reviews:** ~20-25 million (full, unfiltered)
- **Fields:** user_id, parent_asin, rating, title, text, timestamp, helpful_vote, verified_purchase, images

### Command Line Download (if direct link available):

```bash
cd data/raw/

# If compressed file is available
wget [DIRECT_LINK_TO_Electronics.jsonl.gz]

# Extract
gunzip Electronics.jsonl.gz

# Verify
ls -lh Electronics.jsonl
wc -l Electronics.jsonl
head -1 Electronics.jsonl | python3 -m json.tool
```

---

## 📂 Final Folder Structure

After downloading, your structure should look like:

```
review_data_to_postgres/
└── data/
    ├── raw/
    │   ├── Electronics.jsonl  (5-6 GB)
    │   └── README.md
    └── processed/
        └── reviews_Electronics/
            └── README.md (will contain Parquet files after conversion)
```

---

## ✅ Verification

After downloading, verify the file:

```bash
# Check file exists and size
ls -lh data/raw/Electronics.jsonl

# Count lines (reviews)
wc -l data/raw/Electronics.jsonl

# Check first review is valid JSON
head -1 data/raw/Electronics.jsonl | python3 -m json.tool

# Sample review fields
head -1 data/raw/Electronics.jsonl | python3 -c "import sys, json; print(json.loads(sys.stdin.read()).keys())"
```

Expected output:

- File size: 5-6 GB
- Lines: 20-25 million
- Valid JSON with fields: user_id, parent_asin, rating, text, timestamp, etc.

---

## 🔄 Processing Pipeline

```
Electronics.jsonl (raw, 20-25M reviews)
         ↓
[Filter by electronics_products_whitelist.pkl - keep only reviews for 348K products]
         ↓
reviews_Electronics/*.parquet (processed, ~14-15M reviews)
         ↓
PostgreSQL reviews table (~14-15M reviews)
```

**Key Point:** The conversion script will filter this large file down to only reviews for products that exist in your PostgreSQL products table (348K products).

---

## 📊 What Gets Filtered

The raw JSONL contains reviews for ~1.6 million products, but we only load reviews for:

- The 368K products in the 5-core dataset
- That successfully loaded into PostgreSQL (348K products)

Reviews excluded:

- Products not in the 5-core dataset
- The 20K products that failed to load due to data issues
- Non-Electronics products (if any)

**Result:** ~14-15 million reviews loaded (from ~20-25 million)

---

## 💾 Disk Space Requirements

Plan for adequate disk space:

| Stage             | Size          | Purpose               |
| ----------------- | ------------- | --------------------- |
| Raw JSONL         | 5-6 GB        | Original download     |
| Processed Parquet | 3-4 GB        | Filtered, compressed  |
| PostgreSQL        | 8-10 GB       | Database storage      |
| **Total**         | **~18-20 GB** | **Complete pipeline** |

Note: You can delete the processed Parquet files after loading to PostgreSQL to save space.

---

## 🚀 Next Steps

Once data is downloaded:

1. **Convert to Parquet:** `python3 scripts/convert_reviews_to_parquet_corrected.py`

   - Reads raw JSONL
   - Filters by whitelist
   - Writes Parquet chunks
   - Time: ~30-45 minutes

2. **Load to PostgreSQL:** `python3 scripts/load_reviews_to_postgres.py`
   - Reads Parquet chunks
   - Batch inserts to database
   - Time: ~45-60 minutes

See `EXECUTION_ORDER.txt` for detailed steps.

---

## 📚 Additional Resources

- **Amazon 2023 Dataset:** https://amazon-reviews-2023.github.io/
- **Dataset Paper:** https://arxiv.org/abs/2403.03952
- **Hugging Face Repo:** https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- **Data Explorer:** https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/viewer

---

## ⚠️ Important Notes

1. **Large File:** 5-6 GB download. Ensure stable internet and adequate disk space.
2. **Git Ignore:** This file is excluded from git. Don't commit it to the repository.
3. **Prerequisites:** Must complete product data loading first (products table must exist).
4. **Whitelist Required:** Must have `logs/electronics_products_whitelist.pkl` from product pipeline.
5. **Processing Time:** Conversion and loading takes 1-2 hours total.
6. **One-Time Download:** Keep the file for potential reprocessing or analysis.

---

## 🔗 Dependencies

**Critical:** This pipeline requires:

- ✅ Product data loaded (348K products in database)
- ✅ `logs/electronics_products_whitelist.pkl` file (from product pipeline)
- ✅ PostgreSQL running with `products` table populated

If you haven't completed the product data pipeline, do that first:

- See: `../product_data_to_postgres/`
