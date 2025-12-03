# 🚀 Quick Start Guide

Get your database up and running in 3 commands!

---

## ⚡ Super Quick Setup

```bash
# Navigate to setup folder
cd "final/00_database_setup"

# Run automated setup (all steps)
./RUN_ALL_SETUP.sh
```

That's it! The script will guide you through everything.

---

## 📋 Manual Setup (Step-by-Step)

If you prefer manual control:

```bash
# Step 1: Create database
psql -U your_username -f 01_create_database.sql

# Step 2: Create products table
psql -U your_username -d amazon_electronics_rag -f 02_create_products_table.sql

# Step 3: Create reviews table
psql -U your_username -d amazon_electronics_rag -f 03_create_reviews_table.sql

# Step 4: Load data (interactive)
python3 04_load_data_from_parquet.py

# Step 5: Create vector indexes (takes 15-25 min)
psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql

# Step 6: Verify everything works
python3 06_verify_setup.py
```

---

## ✅ Prerequisites Checklist

Before running setup:

- [ ] PostgreSQL 12+ installed
- [ ] pgvector extension installed
- [ ] Python 3.8+ with packages: `psycopg2-binary pandas pyarrow numpy tqdm`
- [ ] Parquet files in `../tables_parquet_final/`
- [ ] ~3 GB free disk space
- [ ] 30-45 minutes of time

---

## ⏱️ Time Expectations

| Step | Time |
|------|------|
| Database creation | < 5 sec |
| Table creation | < 10 sec |
| Data loading | 15-20 min |
| Vector indexes | 15-25 min |
| Verification | < 1 min |
| **TOTAL** | **30-45 min** |

---

## 🎯 What You'll Get

After setup completes:

```
Database: amazon_electronics_rag
├── products_laptop
│   ├── 5,455 laptop products
│   ├── 768-dim embeddings (100%)
│   ├── Complete metadata
│   └── HNSW vector index
│
└── reviews_laptop
    ├── 350,105 laptop reviews
    ├── 768-dim embeddings (100%)
    ├── Complete metadata
    └── HNSW vector index

Total Size: ~3.1 GB
Query Time: < 100ms (vector search)
```

---

## 🆘 Need Help?

**Detailed instructions:** See `README.md` in this folder

**Common issues:**
- pgvector not found → See Prerequisites in README.md
- Permission denied → Grant CREATEDB privilege to your user
- Out of memory → Reduce HNSW parameters in step 5

---

**Happy coding! 🎉**

