# 🔍 Quick Verification Commands

**Use these commands to verify your project status at any time**

---

## 🚀 QUICK START - Run These First!

### 1. Run Quick Verification Script

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
./quick_verify.sh
```

**This checks everything in one go!**

### 2. Verify Parquet Files

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
python3 verify_parquet_files.py
```

### 3. Verify Database Integrity

```bash
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
python3 verify_data_integrity.py
```

---

## 📊 POSTGRESQL QUICK COMMANDS

### Start/Stop PostgreSQL

```bash
# Start
brew services start postgresql@17

# Stop
brew services stop postgresql@17

# Check status
brew services list | grep postgresql

# Restart
brew services restart postgresql@17
```

### Connect to Database

```bash
# Connect
psql -U postgres -d amazon_electronics_rag

# Connect and run single command
psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
```

---

## 🎯 ESSENTIAL VERIFICATION QUERIES

### Copy-Paste These Into psql:

```bash
# Connect first
psql -U postgres -d amazon_electronics_rag
```

Then run these queries:

```sql
-- 1. Check products count (Expected: 348,228)
SELECT COUNT(*) as total_products FROM products;

-- 2. Check reviews count (Expected: 0 now, 37,512,193 after loading)
SELECT COUNT(*) as total_reviews FROM reviews;

-- 3. Check database size
SELECT pg_size_pretty(pg_database_size('amazon_electronics_rag')) as db_size;

-- 4. Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;

-- 5. Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 6. Sample products
SELECT parent_asin, LEFT(title, 50) as title, average_rating, price
FROM products
LIMIT 10;

-- 7. Products by rating
SELECT
    FLOOR(average_rating) as rating,
    COUNT(*) as count
FROM products
WHERE average_rating IS NOT NULL
GROUP BY FLOOR(average_rating)
ORDER BY rating DESC;

-- 8. Price statistics
SELECT
    COUNT(*) as products_with_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    ROUND(AVG(price)::numeric, 2) as avg_price
FROM products
WHERE price > 0;

-- Exit psql
\q
```

---

## 📁 FILE SYSTEM CHECKS

### Check Parquet Files

```bash
# Product parquet files
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/raw_meta_Electronics/"

# Review parquet files
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/reviews_Electronics/"

# Count files
echo "Product files: $(ls /Users/shivamsharma/Desktop/ASU\ Subjects/semester\ 4\ /swm\ project/data/processed/raw_meta_Electronics/*.parquet 2>/dev/null | wc -l)"
echo "Review files: $(ls /Users/shivamsharma/Desktop/ASU\ Subjects/semester\ 4\ /swm\ project/data/processed/reviews_Electronics/*.parquet 2>/dev/null | wc -l)"

# Check sizes
du -sh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/raw_meta_Electronics/"
du -sh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/reviews_Electronics/"
```

### Check Whitelist Files

```bash
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/logs/"*.pkl
```

### Check Documentation

```bash
ls -lh "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/docs/"
```

---

## 🔢 ONE-LINER CHECKS

Copy and paste these complete commands:

```bash
# 1. PostgreSQL running?
brew services list | grep postgresql

# 2. Products count
psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM products;"

# 3. Reviews count
psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM reviews;"

# 4. Database size
psql -U postgres -d amazon_electronics_rag -t -c "SELECT pg_size_pretty(pg_database_size('amazon_electronics_rag'));"

# 5. Review parquet files count
ls "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/reviews_Electronics/"*.parquet 2>/dev/null | wc -l

# 6. Product parquet files count
ls "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/raw_meta_Electronics/"*.parquet 2>/dev/null | wc -l
```

---

## 📊 DETAILED DATABASE EXPLORATION

### Products Analysis

```bash
psql -U postgres -d amazon_electronics_rag
```

```sql
-- Top 20 most reviewed products
SELECT
    parent_asin,
    LEFT(title, 60) as title,
    rating_number as reviews,
    average_rating as rating,
    price
FROM products
WHERE rating_number IS NOT NULL
ORDER BY rating_number DESC
LIMIT 20;

-- Top 20 highest rated (with min 100 reviews)
SELECT
    parent_asin,
    LEFT(title, 60) as title,
    average_rating as rating,
    rating_number as reviews,
    price
FROM products
WHERE rating_number >= 100
ORDER BY average_rating DESC, rating_number DESC
LIMIT 20;

-- Price distribution
SELECT
    CASE
        WHEN price < 10 THEN '$0-10'
        WHEN price < 25 THEN '$10-25'
        WHEN price < 50 THEN '$25-50'
        WHEN price < 100 THEN '$50-100'
        WHEN price < 200 THEN '$100-200'
        ELSE '$200+'
    END as price_range,
    COUNT(*) as count
FROM products
WHERE price IS NOT NULL
GROUP BY price_range
ORDER BY MIN(price);

-- Top categories
SELECT
    main_category,
    COUNT(*) as count,
    ROUND(AVG(average_rating)::numeric, 2) as avg_rating
FROM products
WHERE main_category IS NOT NULL
GROUP BY main_category
ORDER BY count DESC
LIMIT 20;

-- Top brands/stores
SELECT
    store,
    COUNT(*) as products,
    ROUND(AVG(average_rating)::numeric, 2) as avg_rating
FROM products
WHERE store IS NOT NULL AND store != ''
GROUP BY store
ORDER BY products DESC
LIMIT 20;
```

---

## 🎯 EXPECTED VALUES REFERENCE

| Metric                | Expected Value | Check Command                                                                       |
| --------------------- | -------------- | ----------------------------------------------------------------------------------- |
| Products in DB        | 348,228        | `psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM products;"` |
| Reviews in DB         | 0 (pending)    | `psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM reviews;"`  |
| Product Parquet Files | 10 files       | `ls .../raw_meta_Electronics/ \| wc -l`                                             |
| Review Parquet Files  | 10 files       | `ls .../reviews_Electronics/ \| wc -l`                                              |
| Review Parquet Size   | 7.95 GB        | `du -sh .../reviews_Electronics/`                                                   |
| Product Parquet Size  | 1.82 GB        | `du -sh .../raw_meta_Electronics/`                                                  |
| Electronics Whitelist | 348,228 ASINs  | Check with Python script                                                            |
| Database Size         | ~2-3 GB        | `\l+ amazon_electronics_rag` in psql                                                |

---

## 🚨 TROUBLESHOOTING COMMANDS

### If PostgreSQL Won't Start

```bash
# Check what's wrong
brew services list

# Check logs
tail -50 /opt/homebrew/var/log/postgresql@17.log

# Stop and start
brew services stop postgresql@17
sleep 2
brew services start postgresql@17
```

### If Database Doesn't Exist

```bash
# List all databases
psql -U postgres -l

# Create database if missing
psql -U postgres -c "CREATE DATABASE amazon_electronics_rag;"

# Recreate tables
psql -U postgres -d amazon_electronics_rag -f "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/schema/products_table.sql"
psql -U postgres -d amazon_electronics_rag -f "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/schema/reviews_table.sql"
```

### If Tables Are Empty

```bash
# Check if tables exist
psql -U postgres -d amazon_electronics_rag -c "\dt"

# Reload products
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"
python3 load_products_to_postgres.py

# Load reviews (when ready)
python3 load_reviews_to_postgres.py
```

---

## 📝 VERIFICATION CHECKLIST

Run through this before proceeding:

- [ ] PostgreSQL is running: `brew services list | grep postgresql`
- [ ] Database exists: `psql -U postgres -l | grep amazon_electronics_rag`
- [ ] pgvector installed: `psql -U postgres -d amazon_electronics_rag -c "SELECT * FROM pg_extension WHERE extname='vector';"`
- [ ] Products loaded: `psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"` → 348,228
- [ ] Review Parquet files exist: `ls .../reviews_Electronics/*.parquet | wc -l` → 10
- [ ] Whitelist file exists: `ls .../logs/electronics_products_whitelist.pkl`
- [ ] Documentation complete: `ls .../docs/`

---

## 🎯 NEXT STEPS AFTER VERIFICATION

Once everything checks out:

```bash
# 1. Ensure PostgreSQL is running
brew services start postgresql@17

# 2. Navigate to scripts
cd "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/scripts"

# 3. Load reviews (30-40 minutes)
python3 load_reviews_to_postgres.py

# 4. Verify after loading
python3 verify_data_integrity.py

# 5. Check final counts
psql -U postgres -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products, COUNT(*) FROM reviews;"
```

---

**Save this file for quick reference!** 📌
