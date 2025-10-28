# Raw Data Files

This folder should contain the raw dataset files needed for product data loading.

## Required Files

### 1. Electronics_pureid_5core.csv

**Download from:**

```
https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/benchmark/5core/rating_only/Electronics.csv.gz
```

**Instructions:**

1. Download `Electronics.csv.gz` from the link above
2. Extract the `.gz` file to get `Electronics.csv`
3. Rename it to `Electronics_pureid_5core.csv`
4. Place it in this folder (`data/raw/`)

**File Details:**

- Size: ~855 MB (uncompressed)
- Format: CSV
- Rows: ~15.47 million reviews
- Columns: `user_id`, `parent_asin`, `rating`, `timestamp`
- Description: 5-core filtered dataset (users and products with at least 5 interactions)

**What it contains:**

- Core interaction data for Electronics products
- User IDs (anonymized)
- Product ASINs (parent_asin)
- Ratings (1.0 to 5.0)
- Unix timestamps (milliseconds)

**Purpose:**
This file is used by `scripts/extract_unique_asins.py` to create the whitelist of products that have at least 5 reviews. This ensures we only load high-quality, well-reviewed products.

---

## File Structure After Download

```
data/raw/
└── Electronics_pureid_5core.csv  (855 MB)
```

---

## Notes

- This file is excluded from git (too large for GitHub)
- You must download it manually before running the scripts
- The `.gitignore` file prevents accidental commits of large data files
- This is a one-time download; the file will be reused across all scripts

---

## Verification

After downloading, verify the file:

```bash
# Check file exists
ls -lh data/raw/Electronics_pureid_5core.csv

# Check row count (should be ~15.47 million + 1 header)
wc -l data/raw/Electronics_pureid_5core.csv

# Check first few lines
head -5 data/raw/Electronics_pureid_5core.csv
```

Expected output:

```
user_id,parent_asin,rating,timestamp
AGCI7FAH4GL5FI65HYLKWTMFZ2CQ,B0047T79VS,3.0,1344406083000
...
```
