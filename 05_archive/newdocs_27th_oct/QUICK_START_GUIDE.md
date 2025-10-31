# 🚀 Quick Start Guide

**Get Up and Running in 30 Minutes**

---

## 📋 For Someone Starting Fresh

### Prerequisites (5 minutes)

```bash
# 1. Install PostgreSQL 17
brew install postgresql@17

# 2. Install pgvector
brew install pgvector

# 3. Install Python packages
pip3 install pyarrow pandas psycopg2-binary tqdm huggingface-hub

# 4. Start PostgreSQL
brew services start postgresql@17
createuser -s postgres
```

---

## 🎯 Three-Step Process

### **Step 1: Get the Data** (Variable time - depends on download speed)

```bash
# Create project structure
mkdir -p myproject/{data/raw,data/processed,logs,scripts,schema}
cd myproject

# Download product metadata (10 parquet files, ~1.82 GB)
# Use Hugging Face CLI or Python script
pip3 install huggingface-hub
huggingface-cli download McAuley-Lab/Amazon-Reviews-2023 \
    --repo-type dataset \
    --include "raw_meta_Electronics/*.parquet" \
    --local-dir ./data/processed/

# Download Electronics.jsonl (~22 GB)
# (Download from your source and place in data/raw/)
```

### **Step 2: Load Products** (5-10 minutes)

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE amazon_electronics_rag;"
psql -U postgres -d amazon_electronics_rag -c "CREATE EXTENSION vector;"

# 2. Create products table
psql -U postgres -d amazon_electronics_rag -f schema/products_table.sql

# 3. Load products (use provided script)
cd scripts
python3 load_products_to_postgres.py
# Result: ~348,228 products loaded

# 4. Extract whitelist for review filtering
python3 extract_electronics_whitelist.py
# Result: logs/electronics_products_whitelist.pkl created
```

### **Step 3: Process and Load Reviews** (35-45 minutes)

```bash
# 1. Convert JSONL to Parquet (4-5 minutes)
python3 convert_reviews_to_parquet.py
# Result: 10 parquet files with 37.5M reviews

# 2. Create reviews table
psql -U postgres -d amazon_electronics_rag -f schema/reviews_table.sql

# 3. Load reviews to database (30-40 minutes)
python3 load_reviews_to_postgres.py
# Result: 37,512,193 reviews loaded
```

---

## ✅ Verify Everything Works

```bash
# Quick check
psql -U postgres -d amazon_electronics_rag -c "
SELECT 'Products' as table, COUNT(*)::text FROM products
UNION ALL
SELECT 'Reviews' as table, COUNT(*)::text FROM reviews;
"

# Expected output:
#   table   |   count
# ----------+------------
#  Products | 348228
#  Reviews  | 37512193
```

---

## 🎯 What You Get

After completing these steps:

✅ **348,228 Electronics products** in PostgreSQL  
✅ **37,512,193 Electronics reviews** in PostgreSQL  
✅ **100% data quality** (no FK violations, no duplicates)  
✅ **Indexes created** for fast queries  
✅ **pgvector enabled** for embeddings (Phase 3)  
✅ **Ready for BLAIR embeddings** generation

---

## 📂 Required Scripts

You need these 3 Python scripts (full code in COMPLETE_REPLICATION_GUIDE.md):

1. **`load_products_to_postgres.py`** - Loads products from parquet to PostgreSQL
2. **`extract_electronics_whitelist.py`** - Creates whitelist from products table
3. **`convert_reviews_to_parquet.py`** - Converts JSONL to filtered parquet files
4. **`load_reviews_to_postgres.py`** - Loads reviews from parquet to PostgreSQL

And 2 SQL schema files:

1. **`products_table.sql`** - Products table schema
2. **`reviews_table.sql`** - Reviews table schema

---

## 🔧 Key Points

### Why This Order?

1. **Products First**: Must load products to create whitelist
2. **Whitelist Second**: Extract ASINs from loaded products (ensures 100% match)
3. **Reviews Third**: Filter reviews using whitelist (guarantees no FK violations)

### Why Electronics Only?

- The original `Electronics.jsonl` contains **43.9M reviews** for all categories
- We filter to **37.5M reviews** that match our **348,228 Electronics products**
- This ensures **data consistency** and **referential integrity**

### Critical Whitelist Detail

**DO NOT** use the 5-core CSV as a whitelist for reviews!

- The CSV contains **1.08M products from ALL categories**
- Your products table contains **348K Electronics products only**
- Using the CSV causes **foreign key violations**

**ALWAYS** extract the whitelist from your products table after loading!

---

## 💡 Pro Tips

### Optimize Loading Speed

```python
# In loading scripts, adjust batch size based on your RAM:
batch_size = 10000  # Default
batch_size = 20000  # If you have 16GB+ RAM
batch_size = 5000   # If loading fails with memory errors
```

### Monitor Progress

```bash
# In another terminal, watch database size grow:
watch -n 5 'psql -U postgres -d amazon_electronics_rag -t -c "SELECT pg_size_pretty(pg_database_size(\"amazon_electronics_rag\"));"'

# Watch review count:
watch -n 10 'psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM reviews;"'
```

### Free Up Space After Loading

```bash
# After reviews are in PostgreSQL, you can delete parquet files:
# rm -rf data/processed/reviews_Electronics/  # Frees up 7.95 GB

# Keep product parquets - they're small (1.82 GB) and useful for reference
```

---

## 🚨 Common Issues

### "relation does not exist"

- **Cause**: Forgot to create table schema
- **Fix**: Run the SQL schema file first

### Foreign key violations during review loading

- **Cause**: Used wrong whitelist (probably 5-core CSV)
- **Fix**: Re-extract whitelist from products table, re-convert reviews

### PostgreSQL connection refused

- **Cause**: PostgreSQL not running
- **Fix**: `brew services start postgresql@17`

### Out of memory during loading

- **Cause**: Batch size too large
- **Fix**: Reduce `batch_size` in loading scripts

---

## 📊 Expected Timings

| Task                       | Time           | Output                    |
| -------------------------- | -------------- | ------------------------- |
| Download product parquet   | 5-10 min       | 1.82 GB (10 files)        |
| Download reviews JSONL     | 10-30 min      | 22 GB (1 file)            |
| Load products to DB        | 5 min          | 348,228 products          |
| Extract whitelist          | 30 sec         | 348,228 ASINs             |
| Convert reviews to parquet | 4-5 min        | 37.5M reviews (10 files)  |
| Load reviews to DB         | 30-40 min      | 37.5M reviews             |
| **Total**                  | **~1-2 hours** | **Ready for embeddings!** |

---

## 📖 Next Steps

After completing this guide:

1. **Generate embeddings** using BLAIR-RoBERTa (Phase 3)
2. **Build Neo4j graph** with users, products, reviews (Phase 4)
3. **Train GNN** for graph-enhanced embeddings (Phase 5)
4. **Implement RAG** system (Phase 6)

---

**Need detailed code?** See `COMPLETE_REPLICATION_GUIDE.md`

**Need to verify?** See `DATA_VERIFICATION_GUIDE.md`

**Having issues?** Check the Troubleshooting section in COMPLETE_REPLICATION_GUIDE.md
