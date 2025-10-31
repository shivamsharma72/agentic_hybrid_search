# Data Verification & Exploration Guide

**Purpose**: Commands to verify and explore your PostgreSQL database  
**Database**: `amazon_electronics_rag`  
**Status**: Products loaded (348,228), Reviews pending

---

## 🚀 Quick Start

### 1. Start PostgreSQL (if stopped)

```bash
brew services start postgresql@17
```

### 2. Connect to Database

```bash
psql -U postgres -d amazon_electronics_rag
```

---

## 📊 PART 1: DATABASE OVERVIEW

### Check Database Size

```sql
-- Total database size
SELECT pg_size_pretty(pg_database_size('amazon_electronics_rag')) as db_size;

-- Size by table
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### List All Tables

```sql
-- Show all tables
\dt

-- Table details with row counts
SELECT
    schemaname,
    tablename,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### Check Extensions

```sql
-- Verify pgvector is installed
\dx

-- Or with query
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 📦 PART 2: PRODUCTS TABLE VERIFICATION

### Basic Statistics

```sql
-- Total products
SELECT COUNT(*) as total_products FROM products;
-- Expected: 348,228

-- Table structure
\d products

-- Column completeness (check for NULLs)
SELECT
    COUNT(*) as total_rows,
    COUNT(parent_asin) as has_asin,
    COUNT(title) as has_title,
    COUNT(description) as has_description,
    COUNT(average_rating) as has_rating,
    COUNT(rating_number) as has_rating_count,
    COUNT(price) as has_price,
    COUNT(main_category) as has_category,
    COUNT(store) as has_store
FROM products;
```

### Data Quality Checks

```sql
-- Check for duplicate ASINs (should be 0)
SELECT parent_asin, COUNT(*)
FROM products
GROUP BY parent_asin
HAVING COUNT(*) > 1;

-- Check for invalid ratings (should be between 0-5)
SELECT COUNT(*) as invalid_ratings
FROM products
WHERE average_rating < 0 OR average_rating > 5;

-- Check for invalid prices (should be positive)
SELECT COUNT(*) as negative_prices
FROM products
WHERE price < 0;

-- Check for empty titles (should be 0)
SELECT COUNT(*) as empty_titles
FROM products
WHERE title IS NULL OR TRIM(title) = '';
```

### Statistical Analysis

```sql
-- Rating distribution
SELECT
    FLOOR(average_rating) as rating_bucket,
    COUNT(*) as product_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM products
WHERE average_rating IS NOT NULL
GROUP BY FLOOR(average_rating)
ORDER BY rating_bucket DESC;

-- Price statistics
SELECT
    COUNT(*) as products_with_price,
    ROUND(MIN(price)::numeric, 2) as min_price,
    ROUND(MAX(price)::numeric, 2) as max_price,
    ROUND(AVG(price)::numeric, 2) as avg_price,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::numeric, 2) as median_price
FROM products
WHERE price IS NOT NULL AND price > 0;

-- Price distribution (buckets)
SELECT
    CASE
        WHEN price < 10 THEN '$0-10'
        WHEN price < 25 THEN '$10-25'
        WHEN price < 50 THEN '$25-50'
        WHEN price < 100 THEN '$50-100'
        WHEN price < 200 THEN '$100-200'
        WHEN price < 500 THEN '$200-500'
        ELSE '$500+'
    END as price_range,
    COUNT(*) as count,
    ROUND(AVG(average_rating)::numeric, 2) as avg_rating
FROM products
WHERE price IS NOT NULL
GROUP BY price_range
ORDER BY MIN(price);

-- Review count statistics
SELECT
    MIN(rating_number) as min_reviews,
    MAX(rating_number) as max_reviews,
    ROUND(AVG(rating_number)::numeric, 2) as avg_reviews,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rating_number) as median_reviews
FROM products
WHERE rating_number IS NOT NULL;
```

### Category Analysis

```sql
-- Unique main categories
SELECT
    main_category,
    COUNT(*) as product_count,
    ROUND(AVG(average_rating)::numeric, 2) as avg_rating,
    ROUND(AVG(price)::numeric, 2) as avg_price
FROM products
WHERE main_category IS NOT NULL
GROUP BY main_category
ORDER BY product_count DESC
LIMIT 20;

-- Products with most reviews
SELECT
    parent_asin,
    title,
    rating_number as review_count,
    average_rating,
    price,
    main_category
FROM products
WHERE rating_number IS NOT NULL
ORDER BY rating_number DESC
LIMIT 20;

-- Highest rated products (with min 100 reviews)
SELECT
    parent_asin,
    title,
    average_rating,
    rating_number,
    price,
    main_category
FROM products
WHERE rating_number >= 100
ORDER BY average_rating DESC, rating_number DESC
LIMIT 20;
```

### Store/Brand Analysis

```sql
-- Top stores/brands
SELECT
    store,
    COUNT(*) as product_count,
    ROUND(AVG(average_rating)::numeric, 2) as avg_rating,
    ROUND(AVG(price)::numeric, 2) as avg_price
FROM products
WHERE store IS NOT NULL AND store != ''
GROUP BY store
ORDER BY product_count DESC
LIMIT 20;
```

### JSONB Field Exploration

```sql
-- Check details field (JSONB)
SELECT
    COUNT(*) as has_details,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM products) as percentage
FROM products
WHERE details IS NOT NULL AND details != 'null'::jsonb;

-- Sample details keys
SELECT DISTINCT jsonb_object_keys(details) as detail_key
FROM products
WHERE details IS NOT NULL
LIMIT 50;

-- Most common manufacturers
SELECT
    details->>'Manufacturer' as manufacturer,
    COUNT(*) as product_count
FROM products
WHERE details ? 'Manufacturer'
GROUP BY manufacturer
ORDER BY product_count DESC
LIMIT 20;

-- Sample images structure
SELECT
    parent_asin,
    jsonb_pretty(images) as images_json
FROM products
WHERE images IS NOT NULL
LIMIT 3;
```

### Sample Records

```sql
-- View sample products
SELECT
    parent_asin,
    LEFT(title, 60) as title,
    average_rating,
    rating_number,
    price,
    main_category
FROM products
LIMIT 10;

-- View complete record (pick any ASIN)
SELECT * FROM products LIMIT 1;

-- View as pretty JSON
SELECT row_to_json(products.*)
FROM products
LIMIT 1;
```

---

## 📝 PART 3: REVIEWS TABLE VERIFICATION

**Note**: Reviews table exists but is EMPTY (data pending load)

### Check Table Status

```sql
-- Check if reviews table exists
\d reviews

-- Check row count (should be 0 currently)
SELECT COUNT(*) FROM reviews;

-- View table structure
\d+ reviews
```

### After Loading Reviews (Run These Later)

```sql
-- Total reviews (Expected: 37,512,193)
SELECT COUNT(*) as total_reviews FROM reviews;

-- Reviews by rating
SELECT
    rating,
    COUNT(*) as review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM reviews
GROUP BY rating
ORDER BY rating DESC;

-- Temporal distribution
SELECT
    DATE_TRUNC('year', TO_TIMESTAMP(timestamp)) as year,
    COUNT(*) as review_count
FROM reviews
GROUP BY year
ORDER BY year;

-- Verified vs unverified purchases
SELECT
    verified_purchase,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM reviews
GROUP BY verified_purchase;

-- Reviews per product statistics
SELECT
    MIN(review_count) as min_reviews,
    MAX(review_count) as max_reviews,
    ROUND(AVG(review_count)::numeric, 2) as avg_reviews,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY review_count) as median_reviews
FROM (
    SELECT parent_asin, COUNT(*) as review_count
    FROM reviews
    GROUP BY parent_asin
) subq;

-- Reviews per user statistics
SELECT
    MIN(review_count) as min_reviews,
    MAX(review_count) as max_reviews,
    ROUND(AVG(review_count)::numeric, 2) as avg_reviews,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY review_count) as median_reviews
FROM (
    SELECT user_id, COUNT(*) as review_count
    FROM reviews
    GROUP BY user_id
) subq;

-- Check foreign key integrity
SELECT COUNT(*) as orphaned_reviews
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin
WHERE p.parent_asin IS NULL;
-- Should be 0

-- Top reviewers
SELECT
    user_id,
    COUNT(*) as review_count,
    ROUND(AVG(rating)::numeric, 2) as avg_rating,
    SUM(CASE WHEN verified_purchase THEN 1 ELSE 0 END) as verified_count
FROM reviews
GROUP BY user_id
ORDER BY review_count DESC
LIMIT 20;

-- Most reviewed products
SELECT
    r.parent_asin,
    p.title,
    COUNT(*) as review_count,
    ROUND(AVG(r.rating)::numeric, 2) as avg_rating,
    p.average_rating as product_avg_rating
FROM reviews r
JOIN products p ON r.parent_asin = p.parent_asin
GROUP BY r.parent_asin, p.title, p.average_rating
ORDER BY review_count DESC
LIMIT 20;
```

---

## 🔍 PART 4: DATA INTEGRITY CHECKS

### Cross-Table Validation

```sql
-- All product ASINs in reviews exist in products
-- (Run after reviews are loaded)
SELECT COUNT(DISTINCT parent_asin) as unique_products_in_reviews
FROM reviews;

SELECT COUNT(*) as products_in_products_table
FROM products;

-- Check if there's a mismatch
SELECT
    (SELECT COUNT(DISTINCT parent_asin) FROM reviews) as products_with_reviews,
    (SELECT COUNT(*) FROM products) as total_products,
    (SELECT COUNT(*) FROM products) - (SELECT COUNT(DISTINCT parent_asin) FROM reviews) as products_without_reviews;
```

### Index Verification

```sql
-- List all indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## 📈 PART 5: PARQUET FILE VERIFICATION

### Check Parquet Files

```bash
# Navigate to processed data directory
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed"

# Check product parquet files
echo "=== PRODUCT PARQUET FILES ==="
ls -lh raw_meta_Electronics/
du -sh raw_meta_Electronics/

# Check review parquet files
echo -e "\n=== REVIEW PARQUET FILES ==="
ls -lh reviews_Electronics/
du -sh reviews_Electronics/

# Count total files
echo -e "\n=== FILE COUNTS ==="
echo "Product parquet files: $(ls raw_meta_Electronics/*.parquet 2>/dev/null | wc -l)"
echo "Review parquet files: $(ls reviews_Electronics/*.parquet 2>/dev/null | wc -l)"
```

### Verify Parquet Content (Python)

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"

# Create quick verification script
cat > verify_parquet_files.py << 'EOF'
import pyarrow.parquet as pq
import os
from pathlib import Path

print("=" * 60)
print("PARQUET FILES VERIFICATION")
print("=" * 60)

# Product parquet files
product_dir = Path("../data/processed/raw_meta_Electronics")
if product_dir.exists():
    print("\n📦 PRODUCT PARQUET FILES:")
    product_files = sorted(product_dir.glob("*.parquet"))
    total_products = 0
    for file in product_files:
        table = pq.read_table(file)
        num_rows = len(table)
        total_products += num_rows
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {file.name}: {num_rows:,} rows, {size_mb:.2f} MB")
    print(f"\n  Total products: {total_products:,}")
else:
    print("\n⚠️  Product parquet directory not found")

# Review parquet files
review_dir = Path("../data/processed/reviews_Electronics")
if review_dir.exists():
    print("\n📝 REVIEW PARQUET FILES:")
    review_files = sorted(review_dir.glob("*.parquet"))
    total_reviews = 0
    for file in review_files:
        table = pq.read_table(file)
        num_rows = len(table)
        total_reviews += num_rows
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {file.name}: {num_rows:,} rows, {size_mb:.2f} MB")
    print(f"\n  Total reviews: {total_reviews:,}")
    print(f"  Expected: 37,512,193")

    if total_reviews == 37_512_193:
        print("  ✅ Count matches expected!")
    else:
        print(f"  ⚠️  Mismatch: {abs(total_reviews - 37_512_193):,} difference")
else:
    print("\n⚠️  Review parquet directory not found")

print("\n" + "=" * 60)
EOF

python3 verify_parquet_files.py
```

---

## 🎯 PART 6: WHITELIST VERIFICATION

### Check Whitelist Files

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/logs"

# List whitelist files
ls -lh *.pkl

# Verify whitelist content (Python)
python3 << 'EOF'
import pickle
from pathlib import Path

print("=" * 60)
print("WHITELIST FILES VERIFICATION")
print("=" * 60)

# Electronics whitelist (used for reviews)
electronics_pkl = Path("logs/electronics_products_whitelist.pkl")
if electronics_pkl.exists():
    with open(electronics_pkl, 'rb') as f:
        electronics_asins = pickle.load(f)
    print(f"\n✅ Electronics Products Whitelist:")
    print(f"   Location: {electronics_pkl}")
    print(f"   Products: {len(electronics_asins):,}")
    print(f"   Expected: 348,228")
    print(f"   Sample ASINs: {list(electronics_asins)[:5]}")
else:
    print("\n⚠️  Electronics whitelist not found")

# Original 5-core whitelist
fivecore_pkl = Path("logs/unique_asins_whitelist.pkl")
if fivecore_pkl.exists():
    with open(fivecore_pkl, 'rb') as f:
        fivecore_asins = pickle.load(f)
    print(f"\n📋 5-Core Whitelist (All Categories):")
    print(f"   Location: {fivecore_pkl}")
    print(f"   Products: {len(fivecore_asins):,}")
    print(f"   Expected: ~1,082,594")
else:
    print("\n⚠️  5-core whitelist not found")

print("\n" + "=" * 60)
EOF
```

---

## 📊 PART 7: COMPREHENSIVE VERIFICATION SCRIPT

I'll create a master verification script:

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"

python3 verify_data_integrity.py
```

This script already exists and will check:

- ✅ Database connectivity
- ✅ Product count and completeness
- ✅ Rating statistics
- ✅ Price statistics
- ✅ Category distribution
- ✅ Store/brand analysis
- ✅ Top reviewed products

---

## 🔧 USEFUL PSQL COMMANDS

### Inside psql:

```sql
-- List databases
\l

-- Connect to database
\c amazon_electronics_rag

-- List tables
\dt

-- Describe table structure
\d products
\d reviews

-- List indexes
\di

-- Show table sizes
\dt+

-- List extensions
\dx

-- Quit
\q
```

### Query Execution:

```sql
-- Turn on timing
\timing

-- Pretty output
\x auto

-- Set output format
\pset format wrapped

-- Save query results to file
\o output.txt
SELECT * FROM products LIMIT 10;
\o
```

---

## 📝 VERIFICATION CHECKLIST

Run through this checklist:

```bash
# 1. PostgreSQL running?
brew services list | grep postgresql

# 2. Can connect to database?
psql -U postgres -d amazon_electronics_rag -c "SELECT 1;"

# 3. Products table exists and populated?
psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
# Expected: 348228

# 4. Reviews table exists?
psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"
# Expected: 0 (pending load)

# 5. pgvector extension installed?
psql -U postgres -d amazon_electronics_rag -c "SELECT * FROM pg_extension WHERE extname='vector';"

# 6. Review parquet files exist?
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/reviews_Electronics/"

# 7. Whitelist file exists?
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/logs/electronics_products_whitelist.pkl"

# 8. Run comprehensive verification
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
python3 verify_data_integrity.py
```

---

## 🎯 EXPECTED RESULTS SUMMARY

| Component                | Status       | Expected Value    | What to Check                    |
| ------------------------ | ------------ | ----------------- | -------------------------------- |
| Products in DB           | ✅ Loaded    | 348,228           | `SELECT COUNT(*) FROM products;` |
| Reviews in DB            | ⏸️ Pending   | 0                 | `SELECT COUNT(*) FROM reviews;`  |
| Review Parquet Files     | ✅ Ready     | 10 files, 7.95 GB | `ls reviews_Electronics/`        |
| Total Reviews in Parquet | ✅ Ready     | 37,512,193        | Run Python verification          |
| Database Size            | ✅ OK        | ~2-3 GB           | `\l+ amazon_electronics_rag`     |
| pgvector Extension       | ✅ Installed | Yes               | `\dx` in psql                    |
| Foreign Keys             | ✅ Defined   | Yes               | `\d reviews`                     |
| Indexes                  | ✅ Created   | 16 total          | `\di` in psql                    |

---

## 🚨 TROUBLESHOOTING

### PostgreSQL won't start:

```bash
# Check status
brew services list

# Stop and restart
brew services stop postgresql@17
brew services start postgresql@17

# Check logs
tail -f /opt/homebrew/var/log/postgresql@17.log
```

### Can't connect to database:

```bash
# Check if postgres user exists
psql -U postgres -l

# Recreate postgres user if needed
createuser -s postgres
```

### "relation does not exist" error:

```bash
# Verify you're in the right database
psql -U postgres -d amazon_electronics_rag -c "\dt"
```

---

## 📄 NEXT STEPS AFTER VERIFICATION

Once everything checks out:

1. **Start PostgreSQL** (if stopped)
2. **Load reviews**: `python3 load_reviews_to_postgres.py`
3. **Verify reviews**: Run review queries above
4. **Generate embeddings**: Phase 3 (BLAIR-RoBERTa)

---

**Save this file for reference throughout your project!** 📚
