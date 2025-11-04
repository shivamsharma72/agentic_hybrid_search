## 🗄️ Database Setup - Complete Replication Guide

This folder contains all scripts needed to replicate the complete PostgreSQL database setup for the Laptop RAG System.

---

## 📋 Prerequisites

### 1. **PostgreSQL Installation**
- PostgreSQL 12 or later
- Install from: https://www.postgresql.org/download/

### 2. **pgvector Extension**
- Required for vector similarity search
- Installation instructions: https://github.com/pgvector/pgvector

**Quick install (Ubuntu/Debian):**
```bash
sudo apt install postgresql-contrib
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

**Quick install (macOS with Homebrew):**
```bash
brew install pgvector
```

### 3. **Python Dependencies**
```bash
pip install psycopg2-binary pandas pyarrow numpy tqdm
```

### 4. **Parquet Files**
Ensure you have the Parquet files in `../tables_parquet_final/`:
- `laptop_products_with_embeddings.parquet` (24.81 MB)
- `laptop_reviews_with_embeddings.parquet` (1.14 GB)

---

## 🚀 Setup Steps (Run in Order)

### **Step 1: Create Database and Enable pgvector**
```bash
psql -U your_username -f 01_create_database.sql
```

**What it does:**
- Creates `amazon_electronics_rag` database
- Enables pgvector extension
- Verifies installation

**Expected output:**
```
✅ Database created and pgvector extension enabled!
```

---

### **Step 2: Create Products Table**
```bash
psql -U your_username -d amazon_electronics_rag -f 02_create_products_table.sql
```

**What it does:**
- Creates `products_laptop` table with proper schema
- Creates standard indexes (rating, category, price, etc.)
- Sets up constraints and checks

**Table structure:**
- 18 columns including `blair_embedding` (vector 768)
- Primary key on `parent_asin`
- 10 standard indexes (vector indexes created later)

**Expected time:** < 5 seconds

---

### **Step 3: Create Reviews Table**
```bash
psql -U your_username -d amazon_electronics_rag -f 03_create_reviews_table.sql
```

**What it does:**
- Creates `reviews_laptop` table with proper schema
- Creates standard indexes (user_id, parent_asin, rating, etc.)
- Sets up constraints and checks

**Table structure:**
- 14 columns including `blair_embedding` (vector 768)
- Primary key on `review_id` (auto-increment)
- 10 standard indexes (vector indexes created later)

**Expected time:** < 5 seconds

---

### **Step 4: Load Data from Parquet Files**
```bash
python3 04_load_data_from_parquet.py
```

**What it does:**
- Loads 5,455 products from Parquet
- Loads 350,105 reviews from Parquet
- Converts numpy embeddings to PostgreSQL vectors
- Shows progress bars
- Verifies data integrity

**User inputs:**
- PostgreSQL username
- PostgreSQL password (or Enter for none)
- Confirmation if tables already have data

**Expected time:**
- Products: ~1-2 minutes
- Reviews: ~10-15 minutes
- **Total: ~15-20 minutes**

**Expected output:**
```
✅ DATA LOADING COMPLETE!
📦 Products in database: 5,455
💬 Reviews in database: 350,105
🎯 Products with embeddings: 5,455 (100.0%)
🎯 Reviews with embeddings: 350,105 (100.0%)
```

---

### **Step 5: Create Vector Indexes**
```bash
psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql
```

**What it does:**
- Creates HNSW index on `products_laptop.blair_embedding`
- Creates HNSW index on `reviews_laptop.blair_embedding`
- Optimizes for fast similarity search

**Index parameters:**
- `m = 16`: connections per layer (good balance)
- `ef_construction = 64`: build quality (high quality)
- Distance metric: Cosine distance

**Expected time:**
- Products (5,455 vectors): ~30-60 seconds
- Reviews (350,105 vectors): ~10-20 minutes
- **Total: ~15-25 minutes**

**⚠️ Important:** Run this AFTER loading data for optimal index quality!

---

### **Step 6: Verify Setup**
```bash
python3 06_verify_setup.py
```

**What it does:**
- Checks pgvector extension
- Verifies table row counts
- Confirms embeddings are loaded
- Tests vector similarity search (products)
- Tests vector similarity search (reviews)
- Tests cross-modal search (review → products)
- Measures query performance

**User inputs:**
- PostgreSQL username
- PostgreSQL password (or Enter for none)

**Expected output:**
```
✅ DATABASE SETUP VERIFICATION COMPLETE!
📊 Summary:
   • Products: 5,455 (5,455 with embeddings)
   • Reviews: 350,105 (350,105 with embeddings)
   • Unique users: 324,817
   • Vector indexes: ✅ Present
   • Vector search: ✅ Working
   • Cross-modal search: ✅ Working
🎉 Your database is ready for use!
```

---

## ⏱️ Total Setup Time

| Step | Time | Description |
|------|------|-------------|
| 1. Create DB | < 5 sec | Database & extension |
| 2. Products Table | < 5 sec | Schema & indexes |
| 3. Reviews Table | < 5 sec | Schema & indexes |
| 4. Load Data | ~15-20 min | 350K+ rows |
| 5. Vector Indexes | ~15-25 min | HNSW build |
| 6. Verify | < 1 min | Testing |
| **TOTAL** | **~30-45 min** | Complete setup |

---

## 📊 Final Database Statistics

### **Products Table (`products_laptop`)**
| Metric | Value |
|--------|-------|
| Rows | 5,455 |
| Columns | 18 |
| Embeddings | 5,455 (100%) |
| Embedding Dimension | 768 |
| Table Size | ~9.7 MB |
| Indexes Size | ~56 MB |
| Total Size | ~100 MB |

### **Reviews Table (`reviews_laptop`)**
| Metric | Value |
|--------|-------|
| Rows | 350,105 |
| Columns | 14 |
| Embeddings | 350,105 (100%) |
| Embedding Dimension | 768 |
| Unique Products | 5,455 |
| Unique Users | 324,817 |
| Table Size | ~219 MB |
| Indexes Size | ~1.4 GB |
| Total Size | ~3 GB |

### **Database Total:** ~3.1 GB

---

## 🔧 Troubleshooting

### **Issue: pgvector extension not found**
**Solution:**
```bash
# Check if pgvector is installed
psql -U your_username -d postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# If not found, install pgvector (see Prerequisites section)
```

### **Issue: Permission denied**
**Solution:**
```bash
# Make sure user has CREATEDB privilege
psql -U postgres -c "ALTER USER your_username CREATEDB;"
```

### **Issue: Out of memory during index creation**
**Solution:**
```sql
-- Reduce index build parameters
-- In 05_create_vector_indexes.sql, change to:
WITH (m = 8, ef_construction = 32)
```

### **Issue: Slow vector search after setup**
**Solution:**
```sql
-- Check if indexes exist
\d products_laptop
\d reviews_laptop

-- If missing, run step 5 again
```

### **Issue: Data already exists**
**Solution:**
```bash
# The scripts will detect existing data and ask for confirmation
# Choose 'yes' to clear and reload, or 'no' to keep existing data
```

---

## 📁 File Structure

```
00_database_setup/
├── 01_create_database.sql              SQL script
├── 02_create_products_table.sql        SQL script
├── 03_create_reviews_table.sql         SQL script
├── 04_load_data_from_parquet.py        Python script
├── 05_create_vector_indexes.sql        SQL script
├── 06_verify_setup.py                  Python script
└── README.md                           This file
```

---

## 🎯 What You Get

After completing all steps, you'll have:

✅ **Fully functional PostgreSQL database** with:
- 5,455 laptop products with complete metadata
- 350,105 laptop reviews with complete metadata
- 100% embedding coverage (768-dim BLAIR-RoBERTa)
- Optimized HNSW indexes for fast similarity search
- All necessary constraints and standard indexes

✅ **Vector search capabilities:**
- Product similarity search
- Review similarity search
- Cross-modal search (products ↔ reviews)
- Query times: < 100ms for most queries

✅ **Ready for:**
- RAG (Retrieval-Augmented Generation) systems
- Recommendation engines
- Semantic search applications
- ML/AI pipelines

---

## 🔗 Next Steps

After setup, you can:

1. **Connect your RAG system** → See `../04_rag_system/rag_chatbot/`
2. **Run sample queries** → Use `06_verify_setup.py` examples
3. **Build applications** → PostgreSQL is ready for connections
4. **Customize indexes** → Adjust HNSW parameters if needed

---

## 📖 References

- **pgvector Documentation:** https://github.com/pgvector/pgvector
- **HNSW Algorithm:** https://arxiv.org/abs/1603.09320
- **BLAIR Model:** https://huggingface.co/hyp1231/blair-roberta-base
- **Amazon Reviews 2023:** https://amazon-reviews-2023.github.io/

---

**Created:** November 4, 2025  
**Version:** 1.0 Final  
**Tested on:** PostgreSQL 14+ with pgvector 0.5.1+

