# Troubleshooting Guide - Review Data Loading

## 📋 Quick Diagnosis

Run these commands first to identify the issue:

```bash
# Check if database is running
pg_isready

# Check if table exists
psql -d amazon_electronics_rag -c "\dt reviews"

# Check current row count
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"

# Check disk space (need 40+ GB free)
df -h

# Check if Parquet files exist
ls -lh data/processed/reviews_Electronics/*.parquet | wc -l
# Should output: 10
```

---

## 🔍 Common Issues & Solutions

### 1. FileNotFoundError: Parquet files not found

**Error message:**

```
FileNotFoundError: [Errno 2] No such file or directory:
'data/processed/reviews_Electronics/reviews_Electronics_part_0.parquet'
```

**Cause:** Parquet files weren't downloaded or are in wrong location.

**Solution:**

```bash
# Check current location
pwd
# Should be: /path/to/review_data_to_postgres

# Check if files exist
ls -lh data/processed/reviews_Electronics/

# If empty, download from provided link
# Then verify
ls -lh data/processed/reviews_Electronics/*.parquet
# Should show 10 files
```

---

### 2. Database Connection Error

**Error message:**

```
psycopg2.OperationalError: could not connect to server:
Connection refused
```

**Cause:** PostgreSQL not running or wrong connection parameters.

**Solution:**

```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start PostgreSQL
# macOS (Homebrew):
brew services start postgresql@14

# Linux (systemd):
sudo systemctl start postgresql

# Linux (older):
sudo service postgresql start

# Verify it's running
pg_isready
# Should output: accepting connections

# Check if database exists
psql -l | grep amazon_electronics_rag

# If database doesn't exist
createdb amazon_electronics_rag
```

---

### 3. Foreign Key Constraint Violation

**Error message:**

```
ERROR: insert or update on table "reviews" violates foreign key
constraint "fk_reviews_parent_asin"
DETAIL: Key (parent_asin)=(B00XXXXX) is not present in table "products".
```

**Cause:** Products table not loaded or missing products.

**Solution:**

```bash
# Check if products table exists and has data
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM products;"
# Should return: 348228

# If 0 or error, you need to load products first
cd ../product_data_to_postgres
# Follow instructions in that folder first

# Verify all parent_asins in reviews exist in products
psql -d amazon_electronics_rag -c "
SELECT COUNT(DISTINCT r.parent_asin) as reviews_asins,
       COUNT(DISTINCT p.parent_asin) as products_asins
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin;
"
# Both columns should match
```

---

### 4. Out of Disk Space

**Error message:**

```
ERROR: could not extend file "base/16384/16389":
No space left on device
```

**Cause:** Insufficient disk space.

**Solution:**

```bash
# Check available space
df -h

# You need at least 40 GB free:
# - Parquet files: 12 GB
# - Database data: 14 GB
# - Database indexes: 8 GB
# - Temp space: 5 GB

# Option 1: Free up space
# Delete unnecessary files

# Option 2: Move PostgreSQL to larger drive
# 1. Stop PostgreSQL
brew services stop postgresql@14  # macOS
sudo systemctl stop postgresql    # Linux

# 2. Find current data directory
psql -c "SHOW data_directory;"

# 3. Move data to new location
sudo rsync -av /old/location/data /new/location/

# 4. Update postgresql.conf
# Set: data_directory = '/new/location/data'

# 5. Start PostgreSQL
brew services start postgresql@14
```

---

### 5. Slow Loading (< 10,000 rows/sec)

**Symptoms:** Loading taking hours instead of minutes.

**Possible causes and solutions:**

**A. Indexes weren't dropped**

```sql
-- Check indexes during loading
SELECT indexname FROM pg_indexes WHERE tablename = 'reviews';

-- Should only show 'reviews_pkey' during loading
-- If you see 8+ indexes, they weren't dropped

-- Fix: The script drops them automatically
-- Verify script has permission to drop indexes
```

**B. Foreign key wasn't dropped**

```sql
-- Check constraints
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'reviews'::regclass;

-- During loading, should only see:
-- - reviews_pkey (primary key)
-- - reviews_rating_check (check constraint)
-- Should NOT see fk_reviews_parent_asin during loading

-- Fix: Script drops it automatically
```

**C. Disk I/O bottleneck**

```bash
# Install iostat (if not available)
# macOS: available by default
# Linux: sudo apt-get install sysstat

# Monitor disk I/O
iostat -x 1

# Look at %util column:
# - < 50%: Disk is fine
# - 50-80%: Moderate I/O
# - > 80%: Disk is bottleneck

# Solutions:
# 1. Use SSD instead of HDD
# 2. Move database to faster drive
# 3. Reduce other disk activity
```

**D. Memory swapping**

```bash
# Check memory usage
free -h  # Linux
vm_stat  # macOS

# If swap is heavily used:
# 1. Close other applications
# 2. Increase PostgreSQL shared_buffers
# 3. Add more RAM
```

---

### 6. Python Package Errors

**Error message:**

```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**

```bash
# Install packages
pip install pandas pyarrow psycopg2-binary

# If using Python 3.12+, you might need:
pip install pandas pyarrow psycopg2-binary --break-system-packages

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install pandas pyarrow psycopg2-binary

# Verify installation
python3 -c "import pandas, pyarrow, psycopg2; print('Success!')"
```

---

### 7. Script Crashes Mid-Loading

**Symptoms:** Script stops, partial data loaded.

**Solution:**

```bash
# 1. Check how much was loaded
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"

# 2. Check for error in script output
# Look for traceback or error message

# 3. If you want to start fresh:
psql -d amazon_electronics_rag -c "TRUNCATE TABLE reviews CASCADE;"

# 4. Re-run the script
cd scripts
python3 load_reviews_to_postgres_optimized.py

# The script is idempotent - safe to run multiple times
```

---

### 8. CSV/Text Encoding Errors

**Error message:**

```
ERROR: invalid byte sequence for encoding "UTF8": 0x00
```

**Cause:** NULL bytes in text data (already fixed in optimized script).

**Verification:**

```bash
# Check if using optimized script
grep "clean_text" scripts/load_reviews_to_postgres_optimized.py
# Should show function that removes \x00 and \r

# If using old script, switch to optimized version
```

---

### 9. Incorrect Row Count After Loading

**Symptoms:**

- Expected: 37,510,000 rows
- Got: Different number

**Solution:**

```bash
# Check actual count
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"

# Check Parquet file counts
cd scripts
python3 verify_review_data.py

# Compare counts

# If count is LESS than expected:
# - Some files might not have been processed
# - Check script output for errors
# - Re-run script

# If count is MORE than expected:
# - Script was run multiple times
# - Clear and reload:
psql -d amazon_electronics_rag -c "TRUNCATE TABLE reviews CASCADE;"
python3 load_reviews_to_postgres_optimized.py
```

---

### 10. Index Creation Fails

**Error message:**

```
ERROR: could not create unique index "reviews_pkey"
DETAIL: Key (review_id)=(123) is duplicated.
```

**Cause:** Duplicate review_ids (shouldn't happen with auto-increment).

**Solution:**

```sql
-- Check for duplicates
SELECT review_id, COUNT(*)
FROM reviews
GROUP BY review_id
HAVING COUNT(*) > 1;

-- If duplicates exist:
-- 1. This indicates script was run multiple times
-- 2. Clear table and reload
TRUNCATE TABLE reviews CASCADE;

-- Then re-run loading script
```

---

### 11. Foreign Key Recreation Fails

**Error message:**

```
ERROR: insert or update on table "reviews" violates foreign key
constraint "fk_reviews_parent_asin"
```

**Cause:** Some reviews reference products that don't exist.

**Solution:**

```sql
-- Find orphaned reviews
SELECT DISTINCT r.parent_asin
FROM reviews r
LEFT JOIN products p ON r.parent_asin = p.parent_asin
WHERE p.parent_asin IS NULL
LIMIT 10;

-- This shouldn't happen if using correct Parquet files
-- Parquet files are already filtered to match products table

-- If orphaned reviews exist:
-- 1. The Parquet files are incorrect
-- 2. Re-download Parquet files
-- 3. Reload reviews
```

---

### 12. Permission Denied Errors

**Error message:**

```
ERROR: permission denied for table reviews
```

**Solution:**

```bash
# Check current user
psql -d amazon_electronics_rag -c "SELECT current_user;"

# Grant permissions
psql -d amazon_electronics_rag -c "
GRANT ALL PRIVILEGES ON TABLE reviews TO your_username;
GRANT USAGE, SELECT ON SEQUENCE reviews_review_id_seq TO your_username;
"

# Or connect as superuser
psql -U postgres -d amazon_electronics_rag
```

---

### 13. Table Already Exists Error

**Error message:**

```
ERROR: relation "reviews" already exists
```

**Cause:** Trying to create table that already exists.

**Solution:**

```bash
# Option 1: Skip table creation (if schema is correct)
# Just run the loading script

# Option 2: Drop and recreate
psql -d amazon_electronics_rag -c "DROP TABLE IF EXISTS reviews CASCADE;"
psql -d amazon_electronics_rag -f schema/reviews_table.sql

# Option 3: Check if table has data before dropping
psql -d amazon_electronics_rag -c "SELECT COUNT(*) FROM reviews;"
```

---

### 14. Connection Timeout During Loading

**Error message:**

```
psycopg2.OperationalError: server closed the connection unexpectedly
```

**Cause:** Database timeout or crash during loading.

**Solutions:**

```bash
# Check PostgreSQL logs
# macOS:
tail -f /usr/local/var/log/postgres.log

# Linux:
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Common causes:
# 1. Out of memory - increase shared_buffers
# 2. Out of disk - free up space
# 3. Connection timeout - increase statement_timeout

# Increase timeouts in postgresql.conf:
# statement_timeout = 0  # No timeout
# lock_timeout = 0       # No lock timeout

# Restart PostgreSQL after config change
```

---

## 🔧 Advanced Diagnostics

### Check PostgreSQL Configuration

```bash
# Show important settings
psql -d amazon_electronics_rag -c "
SELECT name, setting, unit
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'max_connections'
);
"

# Recommended for loading:
# shared_buffers: 2-4 GB
# maintenance_work_mem: 1-2 GB
# work_mem: 64-128 MB
```

### Monitor Loading Progress

```bash
# In separate terminal during loading
watch -n 5 "psql -d amazon_electronics_rag -c 'SELECT COUNT(*) FROM reviews;'"

# Or use the progress script
cd scripts
watch -n 5 ./check_progress.sh
```

### Check Table Statistics

```sql
-- After loading completes
SELECT
    schemaname,
    tablename,
    n_live_tup as rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'reviews';
```

---

## 📞 Still Having Issues?

If none of the above solutions work:

1. **Check logs:**

   - Script output
   - PostgreSQL logs
   - System logs

2. **Verify setup:**

   - PostgreSQL version >= 14
   - Python version >= 3.8
   - All packages installed
   - Sufficient disk space

3. **Try diagnostic loading:**

   ```python
   # Load just one file for testing
   # Modify script to process only part_0.parquet
   # Should load 3.75M rows in ~1 minute
   ```

4. **Check system resources:**

   ```bash
   # CPU
   top

   # Memory
   free -h

   # Disk I/O
   iostat -x 1

   # Disk space
   df -h
   ```

5. **Verify data integrity:**
   ```bash
   cd scripts
   python3 verify_review_data.py --verbose
   ```

---

## 📋 Pre-Loading Checklist

Before running the loading script, verify:

- [ ] PostgreSQL 14+ installed and running
- [ ] Python 3.8+ with pandas, pyarrow, psycopg2
- [ ] 40+ GB free disk space
- [ ] Database `amazon_electronics_rag` exists
- [ ] Products table loaded (348,228 products)
- [ ] 10 Parquet files downloaded
- [ ] Parquet files in correct directory
- [ ] Table schema created (reviews_table.sql)
- [ ] No other heavy processes running

---

**Created:** 2025-10-28  
**Version:** 1.0
