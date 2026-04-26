# Raw Review Data

This folder should contain the raw review data file for Electronics products.

## Required Files

### Electronics.jsonl

**Download from:**

```
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_review_Electronics
```

**Instructions:**

### Option 1: Manual Download (Browser)

1. Visit the Hugging Face link above
2. Look for the Electronics review file (usually named `Electronics.jsonl.gz` or similar)
3. Download the file
4. Extract the `.gz` file to get `Electronics.jsonl`
5. Place it in this folder (`data/raw/`)

### Option 2: Using Hugging Face CLI

```bash
# Install huggingface-cli if needed
pip install huggingface_hub

# Download the file
huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
  --repo-type dataset \
  --include "raw_review_Electronics/*" \
  --local-dir ./
```

### Option 3: Using Python

```python
from huggingface_hub import hf_hub_download

repo_id = "McAuley-Lab/Amazon-Reviews-2023"
filename = "raw_review_Electronics/Electronics.jsonl.gz"

hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    repo_type="dataset",
    local_dir="data/raw/"
)
```

**File Details:**

- Size: ~5-6 GB (uncompressed JSONL)
- Format: JSON Lines (one JSON object per line)
- Rows: ~20-25 million reviews (full dataset, not filtered)
- Description: Complete review data for all Electronics products

**What it contains:**
Each line is a JSON object with:

- `user_id` - Reviewer ID (anonymized)
- `parent_asin` - Product ASIN being reviewed
- `rating` - Star rating (1.0 to 5.0)
- `title` - Review title/headline
- `text` - Full review text
- `timestamp` - Unix timestamp (milliseconds)
- `helpful_vote` - Number of helpful votes
- `verified_purchase` - Whether purchase was verified
- `images` - Array of review images (if any)

**Purpose:**
This file is used by `scripts/convert_reviews_to_parquet_corrected.py` to:

1. Filter reviews for only the 348K products in our database
2. Convert from JSONL to efficient Parquet format
3. Prepare data for loading into PostgreSQL

---

## File Structure After Download

```
data/raw/
└── Electronics.jsonl  (5-6 GB)
```

---

## Notes

- This file is excluded from git (too large for GitHub)
- You must download it manually before running the conversion scripts
- The `.gitignore` file prevents accidental commits of large data files
- This is a one-time download

---

## Verification

After downloading, verify the file:

```bash
# Check file exists and size
ls -lh data/raw/Electronics.jsonl

# Count total lines (reviews)
wc -l data/raw/Electronics.jsonl

# Check first review
head -1 data/raw/Electronics.jsonl | python3 -m json.tool

# Check last review
tail -1 data/raw/Electronics.jsonl | python3 -m json.tool
```

Expected output:

- File size: 5-6 GB
- Lines: 20-25 million reviews
- Each line is valid JSON with review fields

---

## Processing Pipeline

```
Electronics.jsonl (raw)
    ↓
[Filter by electronics_products_whitelist.pkl]
    ↓
reviews_Electronics/*.parquet (processed)
    ↓
PostgreSQL reviews table (~14-15M reviews)
```

Only reviews for products that exist in the products table will be kept, ensuring foreign key integrity.

---

## Alternative: Full Dataset Repository

If you want the complete Amazon 2023 dataset (all categories):

- Visit: https://amazon-reviews-2023.github.io/
- Documentation: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Note: We only need the Electronics category for this project

