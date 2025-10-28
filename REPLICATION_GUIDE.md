# Complete Replication Guide - Review Data Loading

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Data Preparation](#data-preparation)
4. [Step-by-Step Instructions](#step-by-step-instructions)
5. [Verification](#verification)
6. [Performance Expectations](#performance-expectations)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

This guide walks you through loading **37,510,000** Electronics reviews into PostgreSQL. The entire process takes approximately **25-30 minutes**.

### What You'll Get

- ✅ 37.5 million reviews in PostgreSQL
- ✅ 16.6 million unique users
- ✅ 348K products covered
- ✅ 9 performance indexes
- ✅ Foreign key referential integrity
- ✅ Ready for embeddings and graph building

---

## Prerequisites

### Software Requirements

| Software   | Minimum Version | Check Command        |
| ---------- | --------------- | -------------------- |
| PostgreSQL | 14.0+           | `postgres --version` |
| Python     | 3.8+            | `python3 --version`  |
| pip        | 20.0+           | `pip --version`      |

### Python Packages

```bash
pip install pandas pyarrow psycopg2-binary
```

**Verify installation:**

```bash
python3 -c "import pandas, pyarrow, psycopg2; print('All packages installed!')"
```

### Database Setup

```bash
# Create database (if not exists)
createdb amazon_electronics_rag

# Test connection
psql -d amazon_electronics_rag -c "SELECT version();"
```

### Disk Space

Check available space:

```bash
df -h
```

**Required space:**

- Parquet files: ~12 GB
- Database (data): ~14 GB
- Database (indexes): ~8 GB
- Temp space: ~5 GB
- **Total needed: ~40 GB**

### Important: Products Table Must Exist

The reviews table has a foreign key to the products table. You must load products first.

**Verify products exist:**

```bash
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
# Should return: 348228
```

If products don't exist, see the `product_data_to_postgres` folder first.

---

## Data Preparation

### Download Parquet Files

**📥 Download Link:** [INSERT YOUR LINK HERE]

You need to download 10 Parquet files:

| File                               | Rows           | Size       |
| ---------------------------------- | -------------- | ---------- |
| reviews_Electronics_part_0.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_1.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_2.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_3.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_4.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_5.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_6.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_7.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_8.parquet | 3,751,000      | ~1.2 GB    |
| reviews_Electronics_part_9.parquet | 3,760,000      | ~1.2 GB    |
| **Total**                          | **37,510,000** | **~12 GB** |

### Place Files in Correct Location

```bash
# Navigate to review_data_to_postgres folder
cd review_data_to_postgres

# Create directory structure
mkdir -p data/processed/reviews_Electronics

# Move/download Parquet files here
# Expected location: data/processed/reviews_Electronics/*.parquet
```

**Verify files:**

```bash
ls -lh data/processed/reviews_Electronics/*.parquet
```

You should see 10 files, each ~1.2 GB.

---

## Step-by-Step Instructions

### Step 1: Verify Parquet Files (2-3 minutes)

This script checks file integrity and schema.

```bash
cd scripts
python3 verify_review_data.py
```

**Expected output:**

```
================================================================================
PARQUET FILE VERIFICATION
================================================================================

Found 10 Parquet files

File: reviews_Electronics_part_0.parquet
  Rows: 3,751,000
  Columns: 9
  Size: 1.2 GB
  Schema: ✅ Valid

... (continues for all 10 files) ...

================================================================================
SUMMARY
================================================================================
✅ Total files: 10
✅ Total reviews: 37,510,000
✅ All schemas match
✅ No missing columns
✅ No NULL values in required fields
✅ Ready for loading
================================================================================
```

**If verification fails**, see [Troubleshooting](#troubleshooting).

---

### Step 2: Create Database Table (< 1 second)

Create the reviews table with schema, indexes, and constraints.

```bash
psql -d amazon_electronics_rag -f schema/reviews_table.sql
```

**Expected output:**

```
CREATE TABLE
CREATE INDEX
CREATE INDEX
... (9 times total for all indexes)
ALTER TABLE
COMMENT ON TABLE
COMMENT ON COLUMN
... (10 times for all columns)
```

**Verify table was created:**

```bash
psql -d amazon_electronics_rag -c "\d reviews"
```

You should see:

- 10 columns (review_id, user_id, asin, parent_asin, rating, title, text, timestamp, helpful_vote, verified_purchase)
- 9 indexes
- 1 foreign key constraint (fk_reviews_parent_asin)
- 1 check constraint (rating 0-5)

---

### Step 3: Load Reviews (10-12 minutes)

This is the main loading step using optimized bulk loading.

```bash
cd scripts
python3 load_reviews_to_postgres_optimized.py
```

**What happens:**

**Phase 1: Preparation (10 seconds)**

```
Starting review loading process...
Dropping indexes for faster loading...
  Dropped: idx_reviews_user_id
  Dropped: idx_reviews_parent_asin
  Dropped: idx_reviews_asin
  Dropped: idx_reviews_rating
  Dropped: idx_reviews_timestamp
  Dropped: idx_reviews_verified_purchase
  Dropped: idx_reviews_user_product
  Dropped: idx_reviews_product_rating
Dropped 8 indexes

Dropping foreign key constraint...
  Dropped: fk_reviews_parent_asin
```

**Phase 2: Data Loading (10-12 minutes)**

```
Processing file 1/10: reviews_Electronics_part_0.parquet
  Reading Parquet file... Done (2.1s)
  Preparing data... Done (1.3s)
  Loading to PostgreSQL... Done (54.9s)
  Loaded 3,751,000 rows in 58.3 seconds (64,378 rows/sec)
  Committed batch 1/10

Processing file 2/10: reviews_Electronics_part_1.parquet
  Reading Parquet file... Done (2.0s)
  Preparing data... Done (1.2s)
  Loading to PostgreSQL... Done (55.9s)
  Loaded 3,751,000 rows in 59.1 seconds (63,452 rows/sec)
  Committed batch 2/10

... (continues for all 10 files) ...

Loading complete! Loaded 37,510,000 rows in 10.2 minutes
Average speed: 61,275 rows/sec
```

**Phase 3: Index Recreation (8-10 minutes)**

```
Recreating indexes...
  Creating idx_reviews_user_id... Done (2.3 min)
  Creating idx_reviews_parent_asin... Done (2.1 min)
  Creating idx_reviews_asin... Done (1.9 min)
  Creating idx_reviews_rating... Done (1.5 min)
  Creating idx_reviews_timestamp... Done (1.7 min)
  Creating idx_reviews_verified_purchase... Done (1.2 min)
  Creating idx_reviews_user_product... Done (2.8 min)
  Creating idx_reviews_product_rating... Done (2.4 min)
All indexes created in 8.9 minutes
```

**Phase 4: Foreign Key & Statistics (2-3 minutes)**

```
Recreating foreign key constraint...
  Foreign key created in 2.1 minutes

Running ANALYZE to update statistics...
  ANALYZE complete in 1.2 minutes

================================================================================
LOADING COMPLETE
================================================================================
✅ Total reviews loaded: 37,510,000
✅ Unique users: 16,618,885
✅ Unique products: 348,228
✅ Verified purchases: 34,702,870 (92.5%)
✅ Table size: 21 GB (14 GB data + 8 GB indexes)
✅ Total time: 22.4 minutes
================================================================================
```

---

### Step 4: Verify Loaded Data (1 minute)

Run comprehensive verification to ensure everything loaded correctly.

```bash
psql -d amazon_electronics_rag
```

**Verification queries:**

```sql
-- 1. Check total count (should be 37,510,000)
SELECT COUNT(*) as total_reviews FROM reviews;

-- 2. Check unique users (should be 16,618,885)
SELECT COUNT(DISTINCT user_id) as unique_users FROM reviews;

-- 3. Check unique products (should be 348,228)
SELECT COUNT(DISTINCT parent_asin) as unique_products FROM reviews;

-- 4. Check verified purchases (should be ~92.5%)
SELECT
    COUNT(*) FILTER (WHERE verified_purchase = TRUE) as verified,
    COUNT(*) as total,
    ROUND(COUNT(*) FILTER (WHERE verified_purchase = TRUE)::numeric / COUNT(*) * 100, 1) as verified_pct
FROM reviews;

-- 5. Check rating distribution
SELECT rating, COUNT(*) as count,
       ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER() * 100, 1) as percentage
FROM reviews
GROUP BY rating
ORDER BY rating;

-- 6. Check indexes exist (should show 9)
SELECT indexname FROM pg_indexes
WHERE tablename = 'reviews'
ORDER BY indexname;

-- 7. Check foreign key exists
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'reviews'::regclass;

-- 8. Check table size
SELECT
    pg_size_pretty(pg_relation_size('reviews')) as data_size,
    pg_size_pretty(pg_total_relation_size('reviews') - pg_relation_size('reviews')) as index_size,
    pg_size_pretty(pg_total_relation_size('reviews')) as total_size
FROM pg_class
WHERE relname = 'reviews';
```

**Expected results:**

- Total reviews: 37,510,000 ✅
- Unique users: 16,618,885 ✅
- Unique products: 348,228 ✅
- Verified: 92.5% ✅
- Indexes: 9 ✅
- Foreign key: fk_reviews_parent_asin ✅
- Total size: ~21 GB ✅

---

### Step 5: Test Query Performance (Optional)

Test that indexes are working properly.

```bash
psql -d amazon_electronics_rag -f scripts/sample_queries.sql
```

All queries should complete in **< 1 second** thanks to indexes!

---

## Verification

### Quick Verification Checklist

```bash
# Run this quick check script
cd scripts
./check_progress.sh
```

Expected output:

```
==========================================
REVIEW LOADING PROGRESS
==========================================

⚠️  Loading script is NOT running

Current database status:
 total_reviews | unique_users | unique_products | table_size
---------------+--------------+-----------------+------------
      37510000 |     16618885 |          348228 | 21 GB
(1 row)

Expected: 37,510,000 reviews
==========================================
```

### Detailed Verification

Run `scripts/verify_review_data.py` again:

```bash
cd scripts
python3 verify_review_data.py --check-database
```

This checks:

- ✅ All rows loaded
- ✅ No NULL values in required fields
- ✅ All indexes exist and valid
- ✅ Foreign key constraint active
- ✅ Rating range (0-5)
- ✅ Date range valid

---

## Performance Expectations

### Timeline

| Phase                  | Time          | What's Happening          |
| ---------------------- | ------------- | ------------------------- |
| Download Parquet files | 5-10 min      | Network speed dependent   |
| Verify files           | 2-3 min       | Schema validation         |
| Create table           | < 1 sec       | DDL execution             |
| Drop indexes/FK        | 10 sec        | Preparation for bulk load |
| **Load 37.5M rows**    | **10-12 min** | **Bulk COPY operation**   |
| Recreate 8 indexes     | 8-10 min      | B-tree construction       |
| Recreate FK            | 2-3 min       | Constraint validation     |
| ANALYZE                | 1-2 min       | Statistics update         |
| **Total**              | **25-30 min** | **End-to-end**            |

### Resource Usage

**CPU:**

- During loading: 80-100% (single core)
- During indexing: 400-800% (multi-core)

**Memory:**

- Python process: ~2-3 GB
- PostgreSQL: ~4-8 GB

**Disk I/O:**

- Write speed: ~20-25 MB/sec
- Peak during loading and indexing

**Network:**

- Only during Parquet download
- No network activity during loading

---

## Troubleshooting

### Issue: Parquet files not found

**Error:**

```
FileNotFoundError: data/processed/reviews_Electronics/reviews_Electronics_part_0.parquet
```

**Solution:**

```bash
# Check if files exist
ls -lh data/processed/reviews_Electronics/*.parquet

# Should see 10 files
# If not, re-download from provided link
```

---

### Issue: Database connection error

**Error:**

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**

```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start it
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Verify database exists
psql -l | grep amazon_electronics_rag
```

---

### Issue: Foreign key violation

**Error:**

```
ERROR: insert or update on table "reviews" violates foreign key constraint
```

**Solution:**

```bash
# This means products table doesn't have all required parent_asins
# The Parquet files are already filtered - this shouldn't happen

# Check if products table is loaded
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
# Should return: 348228

# If products don't exist, load products first
cd ../product_data_to_postgres
# Follow instructions there
```

---

### Issue: Out of disk space

**Error:**

```
ERROR: could not extend file ... No space left on device
```

**Solution:**

```bash
# Check available space
df -h

# Need at least 40 GB free
# Free up space or move database to larger drive

# Move PostgreSQL data directory (advanced):
# 1. Stop PostgreSQL
# 2. Move data directory: mv /var/lib/postgresql/data /new/location/
# 3. Update postgresql.conf: data_directory = '/new/location/data'
# 4. Start PostgreSQL
```

---

### Issue: Slow loading (< 10,000 rows/sec)

**Possible causes:**

1. **Indexes weren't dropped**

```sql
-- Check if indexes exist during loading
SELECT indexname FROM pg_indexes WHERE tablename = 'reviews';
-- Should only show 'reviews_pkey' during loading
```

2. **Foreign key wasn't dropped**

```sql
-- Check constraints
SELECT conname FROM pg_constraint WHERE conrelid = 'reviews'::regclass AND contype = 'f';
-- Should return 0 rows during loading
```

3. **Disk I/O bottleneck**

```bash
# Check disk I/O
iostat -x 1
# If %util is > 90%, disk is the bottleneck
```

4. **Insufficient memory**

```bash
# Check memory
free -h
# If swap is being used heavily, add more RAM
```

---

### Issue: Script crashes mid-loading

**If loading crashes halfway:**

```bash
# 1. Check how much was loaded
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"

# 2. Clear partial data
psql -d amazon_electronics_rag -c "TRUNCATE TABLE reviews CASCADE;"

# 3. Re-run loading script
cd scripts
python3 load_reviews_to_postgres_optimized.py
```

The script is idempotent - safe to run multiple times.

---

### Issue: Python package errors

**Error:**

```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**

```bash
# Install required packages
pip install pandas pyarrow psycopg2-binary

# If using virtual environment
python3 -m venv venv
source venv/bin/activate
pip install pandas pyarrow psycopg2-binary
```

---

## FAQ

### Q: Can I load reviews without loading products first?

**A:** No. The reviews table has a foreign key to products.parent_asin. You must load products first. See `product_data_to_postgres` folder.

---

### Q: Why are indexes dropped during loading?

**A:** Indexes slow down INSERT operations dramatically. By dropping them, we achieve 640x faster loading. They're recreated after loading completes.

---

### Q: How much faster is the optimized script?

**A:**

- Old method: ~100 rows/sec = 104 hours for 37.5M rows
- New method: ~64,000 rows/sec = 10 minutes
- **Improvement: 640x faster**

---

### Q: Can I load only some of the Parquet files?

**A:** Yes, but modify the script to process only specific files. The script automatically processes all files in the directory.

---

### Q: Where are the images stored?

**A:** Images column exists but is empty (NULL). Images were skipped during loading due to CSV/JSON escaping issues. Only 4.4% of reviews have images, so this is not critical. They can be loaded later with an UPDATE query if needed.

---

### Q: Can I run this on a smaller machine?

**A:** Minimum requirements:

- 8 GB RAM
- 50 GB free disk space
- 2 CPU cores

Loading will be slower on smaller machines but will still work.

---

### Q: How do I update a single review?

**A:**

```sql
UPDATE reviews
SET rating = 4.5, text = 'Updated review text'
WHERE review_id = 12345;
```

---

### Q: How do I delete all reviews for a product?

**A:**

```sql
DELETE FROM reviews WHERE parent_asin = 'B00EXAMPLE';
```

Foreign key is `ON DELETE CASCADE`, so deleting a product will automatically delete its reviews.

---

### Q: What's next after loading reviews?

**A:**

1. Generate embeddings using BLAIR-RoBERTa
2. Build Neo4j graph with user-product-review relationships
3. Train GNN for recommendations
4. Build RAG system combining vector search + graph traversal

---

## Success!

If you've reached this point with all verifications passing, **congratulations!** 🎉

You now have:

- ✅ 37.5M reviews loaded
- ✅ 16.6M users
- ✅ 348K products
- ✅ All indexes optimized
- ✅ Referential integrity enforced
- ✅ Ready for embeddings

**Next:** Generate embeddings or build Neo4j graph!

---

**Created:** 2025-10-28  
**Version:** 1.0  
**Author:** SWM Project Team
