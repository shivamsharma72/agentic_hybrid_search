# 🔧 Database Setup Troubleshooting Guide

Common issues and solutions when setting up the PostgreSQL database.

---

## ❌ Error: `can't adapt type 'numpy.ndarray'`

### **Problem:**
```
psycopg2.ProgrammingError: can't adapt type 'numpy.ndarray'
```

### **Cause:**
psycopg2 doesn't know how to convert numpy arrays (from Parquet files) to PostgreSQL format.

### **Solution:**
✅ **This is now FIXED in the latest version of `04_load_data_from_parquet.py`**

The script now:
1. Registers a custom numpy array adapter at startup
2. Explicitly converts all numpy arrays to Python lists before insertion

### **If you still see this error:**

**Option 1: Update your script**
```bash
# Pull latest changes from GitHub
git pull origin laptop_rag_system
```

**Option 2: Manual fix**
Add this at the top of `04_load_data_from_parquet.py` (after imports):

```python
from psycopg2.extensions import register_adapter, AsIs
import json

def adapt_numpy_array(numpy_array):
    if isinstance(numpy_array, np.ndarray):
        return AsIs(f"'{json.dumps(numpy_array.tolist())}'")
    return AsIs(repr(numpy_array))

register_adapter(np.ndarray, adapt_numpy_array)
```

**Option 3: Install correct version of psycopg2**
```bash
pip install --upgrade psycopg2-binary
```

---

## ❌ Error: pgvector extension not found

### **Problem:**
```
ERROR: extension "vector" does not exist
```

### **Cause:**
pgvector extension is not installed in PostgreSQL.

### **Solution:**

**macOS (Homebrew):**
```bash
brew install pgvector
brew services restart postgresql@14
```

**Ubuntu/Debian:**
```bash
# Install dependencies
sudo apt install postgresql-server-dev-14 build-essential

# Build from source
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Verify installation:**
```bash
psql -U your_username -d postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
```

---

## ❌ Error: Permission denied for database creation

### **Problem:**
```
ERROR: permission denied to create database
```

### **Solution:**

**Grant CREATEDB privilege:**
```bash
# As PostgreSQL superuser
sudo -u postgres psql
ALTER USER your_username CREATEDB;
\q
```

**Or create database as superuser:**
```bash
sudo -u postgres psql -f 01_create_database.sql
```

---

## ❌ Error: Connection refused

### **Problem:**
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

### **Cause:**
PostgreSQL is not running.

### **Solution:**

**Check PostgreSQL status:**
```bash
# macOS
brew services list | grep postgresql

# Ubuntu/Debian
sudo systemctl status postgresql
```

**Start PostgreSQL:**
```bash
# macOS
brew services start postgresql@14

# Ubuntu/Debian
sudo systemctl start postgresql
```

**Verify it's running:**
```bash
psql -l
```

---

## ❌ Error: Password authentication failed

### **Problem:**
```
psycopg2.OperationalError: FATAL: password authentication failed for user "your_username"
```

### **Solution:**

**Option 1: Use trust authentication (local development)**
Edit `pg_hba.conf`:
```bash
# Find config file
psql -U postgres -c "SHOW hba_file;"

# Edit it (requires sudo)
sudo nano /path/to/pg_hba.conf
```

Change:
```
local   all   all   peer
```
To:
```
local   all   all   trust
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql  # Linux
brew services restart postgresql   # macOS
```

**Option 2: Set/reset password**
```bash
sudo -u postgres psql
ALTER USER your_username WITH PASSWORD 'your_password';
\q
```

---

## ❌ Error: Parquet files not found

### **Problem:**
```
❌ Products file not found: laptop_products_with_embeddings.parquet
```

### **Solution:**

**1. Download the files:**
```bash
cd tables_parquet_final

# Download products
curl -L -o laptop_products_with_embeddings.parquet "https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&dl=1"

# Download reviews
curl -L -o laptop_reviews_with_embeddings.parquet "https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&dl=1"
```

**2. Verify files:**
```bash
ls -lh tables_parquet_final/*.parquet
```

Should show:
- `laptop_products_with_embeddings.parquet` (~25 MB)
- `laptop_reviews_with_embeddings.parquet` (~1.2 GB)

---

## ❌ Error: Out of memory during index creation

### **Problem:**
```
ERROR: out of memory
```

### **Cause:**
Creating HNSW indexes for 350K+ vectors requires significant memory.

### **Solution:**

**Option 1: Increase PostgreSQL memory settings**

Edit `postgresql.conf`:
```bash
# Find config
psql -U postgres -c "SHOW config_file;"

# Edit it
sudo nano /path/to/postgresql.conf
```

Increase these values:
```conf
shared_buffers = 2GB          # was 128MB
work_mem = 256MB              # was 4MB
maintenance_work_mem = 1GB    # was 64MB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

**Option 2: Reduce index build parameters**

Edit `05_create_vector_indexes.sql`, change:
```sql
-- FROM:
WITH (m = 16, ef_construction = 64)

-- TO:
WITH (m = 8, ef_construction = 32)
```

This creates smaller indexes (slightly slower queries, but uses less memory).

---

## ❌ Error: Slow vector search after setup

### **Problem:**
Queries take > 1 second

### **Solution:**

**1. Verify indexes exist:**
```bash
psql -U your_username -d amazon_electronics_rag
\d products_laptop
\d reviews_laptop
```

Should show indexes like:
- `products_laptop_blair_embedding_idx`
- `reviews_laptop_blair_embedding_idx`

**2. If missing, create them:**
```bash
psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql
```

**3. Analyze tables:**
```bash
psql -U your_username -d amazon_electronics_rag
ANALYZE products_laptop;
ANALYZE reviews_laptop;
\q
```

---

## ❌ Error: ModuleNotFoundError

### **Problem:**
```
ModuleNotFoundError: No module named 'psycopg2'
ModuleNotFoundError: No module named 'pandas'
```

### **Solution:**

**Ensure virtual environment is activated:**
```bash
# Check if venv is active
which python
# Should show: /path/to/venv/bin/python

# If not active, activate it:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Install requirements:**
```bash
pip install -r requirements.txt
```

**Or install individually:**
```bash
pip install psycopg2-binary pandas pyarrow numpy tqdm
```

---

## ❌ Error: Table already exists

### **Problem:**
```
ERROR: relation "products_laptop" already exists
```

### **Solution:**

**Option 1: Drop and recreate**
```bash
psql -U your_username -d amazon_electronics_rag
DROP TABLE IF EXISTS products_laptop CASCADE;
DROP TABLE IF EXISTS reviews_laptop CASCADE;
\q

# Then rerun table creation
psql -U your_username -d amazon_electronics_rag -f 02_create_products_table.sql
psql -U your_username -d amazon_electronics_rag -f 03_create_reviews_table.sql
```

**Option 2: Skip table creation**
If tables are correct, just skip to data loading:
```bash
python3 04_load_data_from_parquet.py
```

---

## ⚠️ Warning: Data already in table

### **Message:**
```
⚠️  Table already has 5,455 products
Clear and reload? (yes/no):
```

### **What to do:**

- Type `yes` - Clears existing data and reloads fresh
- Type `no` - Keeps existing data, skips loading

**Note:** The script asks for confirmation to prevent accidental data loss.

---

## 🔍 Verification Commands

After setup, verify everything is working:

```bash
# Connect to database
psql -U your_username -d amazon_electronics_rag

# Check row counts
SELECT COUNT(*) FROM products_laptop;      -- Should be 5,455
SELECT COUNT(*) FROM reviews_laptop;       -- Should be 350,105

# Check embeddings
SELECT COUNT(*) FROM products_laptop WHERE blair_embedding IS NOT NULL;
SELECT COUNT(*) FROM reviews_laptop WHERE blair_embedding IS NOT NULL;

# Check indexes
\di

# Test vector search
SELECT parent_asin, title 
FROM products_laptop 
ORDER BY blair_embedding <-> (SELECT blair_embedding FROM products_laptop LIMIT 1) 
LIMIT 5;

# Exit
\q
```

---

## 📞 Still Having Issues?

**Check these in order:**

1. ✅ PostgreSQL is running (`psql -l` works)
2. ✅ pgvector is installed (see error solutions above)
3. ✅ Database exists (`psql -l | grep amazon_electronics_rag`)
4. ✅ Virtual environment is activated
5. ✅ All packages installed (`pip list`)
6. ✅ Parquet files downloaded (1.17 GB total)
7. ✅ Script is latest version (from GitHub)

**Run the verification script:**
```bash
python3 06_verify_setup.py
```

This will check all components and report any issues.

---

## 📚 Additional Resources

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **pgvector GitHub:** https://github.com/pgvector/pgvector
- **psycopg2 Documentation:** https://www.psycopg.org/docs/

---

**Updated:** November 4, 2025  
**For:** laptop_hybrid_search database setup

