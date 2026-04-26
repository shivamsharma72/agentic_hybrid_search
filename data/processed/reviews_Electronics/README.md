# Processed Review Parquet Files

This folder will contain the processed review data in Parquet format after running the conversion script.

## What Goes Here

After running `scripts/convert_reviews_to_parquet_corrected.py`, this folder will contain:

```
reviews_Electronics/
├── reviews_Electronics_chunk_0.parquet
├── reviews_Electronics_chunk_1.parquet
├── reviews_Electronics_chunk_2.parquet
├── ...
└── reviews_Electronics_chunk_N.parquet
```

**File Details:**

- Format: Apache Parquet (columnar)
- Chunk Size: ~1 million reviews per file
- Total Reviews: ~14-15 million (filtered)
- Compression: Snappy (default)

## Why This Folder Exists

### Purpose:

This is an **intermediate processing step** in the pipeline:

```
JSONL (raw) → Parquet (processed) → PostgreSQL (database)
```

### Benefits of Parquet Intermediate Format:

1. **Filtering**: Raw JSONL has ~20-25M reviews, but we only need ~14-15M (for products in our DB)
2. **Compression**: Parquet is compressed (smaller than JSONL)
3. **Speed**: Columnar format allows fast batch loading into PostgreSQL
4. **Reusability**: Can reload database without re-processing JSONL
5. **Inspection**: Easy to inspect/sample data before loading

## How It's Generated

Run the conversion script:

```bash
cd scripts
python3 convert_reviews_to_parquet_corrected.py
```

The script will:

1. Load `logs/electronics_products_whitelist.pkl` (348K product ASINs)
2. Read `data/raw/Electronics.jsonl` line by line
3. Keep only reviews where `parent_asin` is in the whitelist
4. Write filtered reviews to Parquet chunks in this folder

**Processing Time:** ~30-45 minutes (depending on disk I/O)

## File Structure After Conversion

```
data/processed/reviews_Electronics/
├── reviews_Electronics_chunk_0.parquet  (~200-300 MB)
├── reviews_Electronics_chunk_1.parquet  (~200-300 MB)
├── reviews_Electronics_chunk_2.parquet  (~200-300 MB)
├── ...
└── reviews_Electronics_chunk_N.parquet  (~200-300 MB)
```

Total size: ~3-4 GB (compressed Parquet)

## Verification

After conversion, verify the files:

```bash
# Check files exist
ls -lh data/processed/reviews_Electronics/

# Count chunks
ls data/processed/reviews_Electronics/*.parquet | wc -l

# Check total size
du -sh data/processed/reviews_Electronics/

# Inspect first chunk
python3 << EOF
import pyarrow.parquet as pq
table = pq.read_table('data/processed/reviews_Electronics/reviews_Electronics_chunk_0.parquet')
print(f"Reviews in chunk 0: {table.num_rows:,}")
print(f"Columns: {table.num_columns}")
print(f"Schema:\n{table.schema}")
EOF

# Count total reviews across all chunks
python3 << EOF
import pyarrow.parquet as pq
import glob

total = 0
files = sorted(glob.glob('data/processed/reviews_Electronics/*.parquet'))
for f in files:
    table = pq.read_table(f)
    total += table.num_rows
print(f"Total reviews: {total:,}")
EOF
```

## What's Filtered Out?

Reviews are excluded if:

- `parent_asin` is NOT in the whitelist (product doesn't exist in our database)
- This includes:
  - Reviews for the 20K products that failed to load
  - Reviews for products not in the 5-core dataset

## Next Step

After conversion, load into PostgreSQL:

```bash
cd scripts
python3 load_reviews_to_postgres.py
```

This will read all Parquet chunks and batch insert into the `reviews` table.

---

## Notes

- These files are excluded from git (large intermediate files)
- The `.gitignore` prevents accidental commits
- You can delete these files after successfully loading to PostgreSQL
- If you need to reload the database, you can regenerate from raw JSONL or reuse these Parquet files

---

## Column Schema

The Parquet files contain the following columns:

| Column            | Type          | Description                                |
| ----------------- | ------------- | ------------------------------------------ |
| user_id           | string        | Reviewer ID                                |
| parent_asin       | string        | Product ASIN (validated against whitelist) |
| rating            | float         | Star rating (1.0 to 5.0)                   |
| title             | string        | Review title (can be null)                 |
| text              | string        | Full review text                           |
| timestamp         | int64         | Unix timestamp (milliseconds)              |
| helpful_vote      | int           | Number of helpful votes                    |
| verified_purchase | bool          | Whether purchase was verified              |
| images            | string (JSON) | Review images (if any)                     |

Note: The `review_id` and `blair_embedding` columns are generated during PostgreSQL loading, not stored in Parquet.
