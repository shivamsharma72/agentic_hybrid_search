# Review Data to PostgreSQL - Complete Guide

## 📋 Overview

This folder contains all scripts, schemas, and documentation needed to load 37.5 million Electronics reviews into PostgreSQL for the Graph-Assisted Hybrid RAG system.

---

## 🎯 What This Does

Loads **37,510,000** Electronics reviews from Parquet files into PostgreSQL with:

- Full review text, ratings, and metadata
- Optimized bulk loading (10-12 minutes)
- 9 performance indexes
- Foreign key referential integrity
- Production-ready for embeddings and graph building

---

## 📦 Prerequisites

### Required Software

```bash
# PostgreSQL 14+ with pgvector extension
postgres --version  # Should be >= 14

# Python 3.8+
python3 --version

# Required Python packages
pip install pandas pyarrow psycopg2-binary
```

### Required Data Files

**You need to download Parquet files separately.**

📥 **Download Link:** [Provide your link here]

**Expected files (10 Parquet files):**

```
data/processed/reviews_Electronics/
├── reviews_Electronics_part_0.parquet (3.75M reviews)
├── reviews_Electronics_part_1.parquet (3.75M reviews)
├── reviews_Electronics_part_2.parquet (3.75M reviews)
├── reviews_Electronics_part_3.parquet (3.75M reviews)
├── reviews_Electronics_part_4.parquet (3.75M reviews)
├── reviews_Electronics_part_5.parquet (3.75M reviews)
├── reviews_Electronics_part_6.parquet (3.75M reviews)
├── reviews_Electronics_part_7.parquet (3.75M reviews)
├── reviews_Electronics_part_8.parquet (3.75M reviews)
└── reviews_Electronics_part_9.parquet (3.76M reviews)
```

**Total:** 37,510,000 reviews

---

## 📁 Folder Structure

```
review_data_to_postgres/
├── README.md                          # This file
├── EXECUTION_ORDER.txt                # Step-by-step execution guide
├── REPLICATION_GUIDE.md              # Detailed replication instructions
├── OPTIMIZATION_SUMMARY.md           # Performance optimizations explained
├── TROUBLESHOOTING.md                # Common issues and solutions
├── scripts/
│   ├── load_reviews_to_postgres_optimized.py  # Main loading script (FAST)
│   ├── verify_review_data.py                  # Verification script
│   ├── check_progress.sh                      # Progress monitoring
│   └── sample_queries.sql                     # Useful queries
├── schema/
│   └── reviews_table.sql                      # Table schema with comments
├── docs/
│   └── PERFORMANCE_ANALYSIS.md                # Loading performance details
└── data/
    └── processed/
        └── reviews_Electronics/               # Place Parquet files here
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download Parquet Files

```bash
# Create the directory
mkdir -p data/processed/reviews_Electronics

# Download Parquet files from provided link
# Place all 10 files in: data/processed/reviews_Electronics/
```

### Step 2: Verify Files

```bash
cd scripts
python3 verify_review_data.py
```

### Step 3: Create Database Table

```bash
# Create table (if not exists)
psql -d amazon_electronics_rag -f schema/reviews_table.sql
```

### Step 4: Load Reviews

```bash
# This takes 10-12 minutes for 37.5M reviews
cd scripts
python3 load_reviews_to_postgres_optimized.py
```

### Step 5: Monitor Progress (Optional)

```bash
# In another terminal
cd scripts
./check_progress.sh
```

**Done!** 🎉

---

## 📖 Detailed Instructions

See **[REPLICATION_GUIDE.md](./REPLICATION_GUIDE.md)** for:

- Detailed step-by-step walkthrough
- Troubleshooting common issues
- Verification commands
- Sample queries

See **[EXECUTION_ORDER.txt](./EXECUTION_ORDER.txt)** for:

- Exact command sequence
- Expected outputs
- Timing estimates

---

## ⚡ Performance

**Loading Speed:**

- **37.5M reviews in ~10-12 minutes**
- **~64,000 rows/sec**
- **640x faster** than row-by-row INSERT

**Final Database Size:**

- Data: 14 GB
- Indexes: 7.9 GB
- Total: ~21 GB

---

## 🔍 Verification

After loading, verify with:

```sql
-- Check total reviews
SELECT COUNT(*) FROM reviews;
-- Expected: 37,510,000

-- Check unique users
SELECT COUNT(DISTINCT user_id) FROM reviews;
-- Expected: 16,618,885

-- Check unique products
SELECT COUNT(DISTINCT parent_asin) FROM reviews;
-- Expected: 348,228

-- Check verified purchases
SELECT
    COUNT(*) FILTER (WHERE verified_purchase = TRUE) as verified,
    COUNT(*) as total,
    ROUND(COUNT(*) FILTER (WHERE verified_purchase = TRUE)::numeric / COUNT(*) * 100, 1) as pct
FROM reviews;
-- Expected: 92.5% verified
```

---

## 📊 Key Statistics

| Metric             | Value       |
| ------------------ | ----------- |
| Total Reviews      | 37,510,000  |
| Unique Users       | 16,618,885  |
| Unique Products    | 348,228     |
| Unique ASINs       | 595,385     |
| Verified Purchases | 92.5%       |
| Date Range         | 1998-2023   |
| Table Size         | 21 GB       |
| Loading Time       | ~12 minutes |

---

## 🛠️ Troubleshooting

### Issue: Parquet files not found

```bash
# Verify files exist
ls -lh data/processed/reviews_Electronics/*.parquet
```

### Issue: Database connection error

```bash
# Test connection
psql -d amazon_electronics_rag -c "SELECT version();"
```

### Issue: Out of disk space

```bash
# Check space (need ~25 GB free)
df -h
```

### Issue: Slow loading

```bash
# Check if indexes/FK were dropped
psql -d amazon_electronics_rag -c "SELECT indexname FROM pg_indexes WHERE tablename = 'reviews';"
# Should show NO indexes during loading
```

See **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** for more solutions.

---

## 📞 Support

For issues or questions:

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review [REPLICATION_GUIDE.md](./REPLICATION_GUIDE.md)
3. Verify your Parquet files match expected schema

---

## ✅ Success Criteria

Loading is successful when:

- ✅ 37,510,000 rows in `reviews` table
- ✅ 9 indexes created (8 + primary key)
- ✅ Foreign key constraint active
- ✅ No NULL values in required fields
- ✅ All queries return expected counts

---

## 🔄 Next Steps

After loading reviews:

1. **Generate Embeddings** - Use BLAIR-RoBERTa on review text
2. **Build Neo4j Graph** - Create user-product-review relationships
3. **Train GNN** - Graph Neural Network for recommendations
4. **Build RAG System** - Combine vector search + graph traversal

---

**Created:** 2025-10-28  
**Version:** 1.0  
**Database:** PostgreSQL 14+ with pgvector
