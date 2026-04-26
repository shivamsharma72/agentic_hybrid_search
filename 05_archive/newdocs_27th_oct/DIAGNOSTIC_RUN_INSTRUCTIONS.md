# 🔬 Diagnostic Run Instructions

## What This Does

The `load_products_diagnostic.py` script will:

1. ✅ **NOT delete any existing data** - your 348,228 products are safe
2. ✅ Attempt to insert all 368,228 products from the whitelist
3. ✅ Track which ones already exist (will be skipped by `ON CONFLICT DO NOTHING`)
4. ✅ Capture **detailed error information** for the ~20,000 that fail
5. ✅ Generate a comprehensive error report
6. ✅ Save failed ASINs to a file for further investigation

---

## How to Run

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
python3 load_products_diagnostic.py
```

**Time**: ~5-10 minutes (faster than original because smaller batches for better error isolation)

---

## What You'll See

### During Execution:

```
===========================================
DIAGNOSTIC PRODUCT LOADING WITH ERROR TRACKING
===========================================

STEP 1: Loading Product Whitelist
✅ Loaded whitelist: 368,228 unique parent_asins

STEP 2: Connecting to Database
✅ Connected to database: amazon_electronics_rag
📊 Current products in database: 348,228

STEP 3: Processing Parquet Files with Detailed Error Tracking
Processing: full-00000-of-00010.parquet
[Progress bar...]
```

### Final Report Will Show:

```
===========================================
DETAILED ERROR ANALYSIS
===========================================

📊 SUMMARY:
   Total in whitelist:        368,228
   Total processed:           1,610,012  (all records checked)
   Already in DB (skipped):   348,228    (existing products)
   Successfully inserted:     0          (or small number)
   Failed to insert:          ~20,000    (what we're investigating)

🔍 ERROR BREAKDOWN:
   Null/missing title:        X
   Null/missing ASIN:         Y
   Duplicate key conflicts:   348,228 (expected)
   JSONB format errors:       Z
   Array format errors:       W
   VARCHAR too long:          V
   Foreign key violations:    0 (hopefully)
   Data type errors:          U
   Unknown errors:            T

❌ Sample ASINs with null/missing title (first 20):
   1. B0833QD5XL
   2. B002JH5BM4
   ...

❌ Sample JSONB errors (first 5):
   1. Batch with ASINs: [...]... Error: invalid input syntax for type json
   ...

💾 Saved 20,000 unique failed ASINs to: logs/failed_product_asins.txt
```

---

## What Gets Created

### 1. Console Output

- Real-time progress bars
- Detailed error analysis
- Sample error messages

### 2. File: `logs/failed_product_asins.txt`

- List of all ASINs that failed to load
- One ASIN per line
- You can use this for further investigation

---

## Key Differences from Original Script

| Feature               | Original Script | Diagnostic Script                |
| --------------------- | --------------- | -------------------------------- |
| Batch Size            | 5,000           | 1,000 (better error isolation)   |
| Error Tracking        | Minimal         | Comprehensive                    |
| Error Categorization  | No              | Yes (8 categories)               |
| Failed ASIN Logging   | No              | Yes (saves to file)              |
| Sample Error Messages | No              | Yes (shows first 5 of each type) |
| Data Safety           | Safe            | Safe (ON CONFLICT DO NOTHING)    |

---

## Expected Results

### Scenario 1: Missing Title/Required Fields

```
Null/missing title: 20,000
→ These ASINs exist but lack required data
→ Explains why they weren't loaded
```

### Scenario 2: JSONB Format Errors

```
JSONB format errors: 15,000
→ The details/images/videos fields have invalid JSON
→ JSONB bug might not be fully fixed for edge cases
```

### Scenario 3: Data Type Mismatches

```
Data type errors: 10,000
→ Rating/price fields have unexpected values
→ Array fields have wrong format
```

### Scenario 4: Already in Database

```
Duplicate key conflicts: 348,228
Successfully inserted: 0
→ All good products already loaded
→ The 20K missing have inherent issues
```

---

## After Running - Next Steps

### If you find the 20K have null titles:

→ **Expected and correct** - nothing to fix

### If you find JSONB errors:

→ **Data quality issue** in source - can't be fixed without fixing source data

### If you find data type errors:

→ **Can potentially fix** by adjusting transformation functions

### If errors are unclear:

→ **Investigate specific ASINs** from the failed list in parquet files

---

## Safety Guarantees

✅ **Your existing 348,228 products are 100% safe**

- Uses `ON CONFLICT DO NOTHING` - won't overwrite
- No DROP or DELETE commands
- Only INSERT attempts

✅ **Your reviews are safe**

- Doesn't touch reviews table
- Won't break FK relationships

✅ **Rollback on errors**

- Each batch failure is rolled back
- Database stays consistent

---

## Tips

### To focus on specific error types:

After running, check `logs/failed_product_asins.txt` and pick a few ASINs to investigate in the parquet files.

### To verify a specific ASIN:

```python
import pyarrow.parquet as pq
import pandas as pd

# Load parquet
table = pq.read_table("data/processed/raw_meta_Electronics/full-00001-of-00010.parquet")
df = table.to_pandas()

# Find specific ASIN
asin = 'B0833QD5XL'
product = df[df['parent_asin'] == asin]
print(product.to_dict('records')[0])
```

### To see current database state:

```sql
psql -U postgres -d amazon_electronics_rag -c "
SELECT
    COUNT(*) as total,
    COUNT(DISTINCT parent_asin) as unique_asins
FROM products;
"
```

---

## Ready to Run!

The script is ready at:
`scripts/load_products_diagnostic.py`

Just run:

```bash
cd scripts
python3 load_products_diagnostic.py
```

And you'll get the full diagnostic report! 🔬

