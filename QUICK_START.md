# Quick Start Guide - 5 Minutes

## 🚀 Get Started in 3 Commands

```bash
# 1. Verify Parquet files (2 min)
cd review_data_to_postgres/scripts
python3 verify_review_data.py

# 2. Create table (< 1 sec)
psql -d amazon_electronics_rag -f ../schema/reviews_table.sql

# 3. Load reviews (10-12 min)
python3 load_reviews_to_postgres_optimized.py
```

**Done!** 37.5M reviews loaded in ~12 minutes.

---

## 📦 Prerequisites

Before starting, ensure you have:

- [ ] PostgreSQL 14+ running
- [ ] Python 3.8+ installed
- [ ] Database `amazon_electronics_rag` created
- [ ] Products table loaded (348,228 products)
- [ ] 10 Parquet files downloaded
- [ ] 40+ GB free disk space

**Install packages:**

```bash
pip install pandas pyarrow psycopg2-binary
```

---

## 📥 Download Parquet Files

**Link:** [INSERT YOUR DOWNLOAD LINK]

Place files in: `review_data_to_postgres/data/processed/reviews_Electronics/`

Expected files:

- `reviews_Electronics_part_0.parquet` through `part_9.parquet`
- Total: 10 files, ~12 GB

---

## ⚡ What Happens

1. **Verify** - Checks files and schema (2 min)
2. **Create** - Creates table with indexes (< 1 sec)
3. **Load** - Loads 37.5M reviews (10 min)
4. **Index** - Rebuilds 8 indexes (9 min)
5. **Validate** - Creates foreign key (2 min)
6. **Done!** - Ready for queries (22 min total)

---

## 🔍 Monitor Progress

In another terminal:

```bash
cd scripts
./check_progress.sh
```

Or watch live:

```bash
watch -n 5 'psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"'
```

---

## ✅ Verify Success

```sql
-- Should return 37,510,000
SELECT COUNT(*) FROM reviews;

-- Should return 16,618,885
SELECT COUNT(DISTINCT user_id) FROM reviews;

-- Should return 9
SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'reviews';
```

All checks pass? **You're done!** 🎉

---

## 🆘 Troubleshooting

**Files not found?**

```bash
ls -lh data/processed/reviews_Electronics/*.parquet
# Should show 10 files
```

**Database error?**

```bash
pg_isready  # Check if PostgreSQL running
psql -d amazon_electronics_rag -c "SELECT version();"
```

**Out of space?**

```bash
df -h  # Need 40+ GB free
```

**Loading slow?**

- Should be ~64,000 rows/sec
- If slower, check CPU/disk usage
- See TROUBLESHOOTING.md

---

## 📖 Full Documentation

- **EXECUTION_ORDER.txt** - Detailed step-by-step
- **REPLICATION_GUIDE.md** - Complete walkthrough
- **TROUBLESHOOTING.md** - Common issues
- **OPTIMIZATION_SUMMARY.md** - Performance details

---

**Time:** 25-30 minutes total  
**Result:** 37.5M reviews ready for RAG system!
