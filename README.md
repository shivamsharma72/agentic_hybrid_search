# Product Data to PostgreSQL

This folder contains all the necessary files to load Amazon Electronics product metadata into PostgreSQL.

## 📁 Folder Structure

```
product_data_to_postgres/
├── scripts/           # Python scripts for data processing
├── schema/            # Database schema files
├── docs/              # Documentation
├── logs/              # Whitelist pickle files
└── README.md          # This file
```

## 📋 Files Included

### Scripts (in execution order):

1. **extract_unique_asins.py** - Extract unique product ASINs from 5-core CSV
2. **setup_database.py** - Create database and products table
3. **load_products_to_postgres.py** - Load products from Parquet files to PostgreSQL
4. **extract_electronics_whitelist.py** - Extract whitelist from loaded products
5. **verify_data_integrity.py** - Verify loaded data

### Schema:

- **products_table.sql** - PostgreSQL schema for products table

### Documentation:

- **PRODUCT_METADATA_FIELDS.md** - Detailed field documentation
- **DATA_VERIFICATION_GUIDE.md** - How to verify loaded data
- **COMPLETE_REPLICATION_GUIDE.md** - Full replication guide
- **STEP_BY_STEP_WALKTHROUGH.md** - Step-by-step commands
- **DATA_CLARIFICATION.md** - Data source clarifications

### Logs:

- **unique_asins_whitelist.pkl** - Whitelist from 5-core CSV (368K ASINs)
- **electronics_products_whitelist.pkl** - Whitelist from products table (348K ASINs)

## 🚀 Quick Start

### Prerequisites:

- PostgreSQL 17 with pgvector extension
- Python 3.x with: psycopg2, pandas, pyarrow, pickle
- Raw data files:
  - `Electronics_pureid_5core.csv` (in `data/raw/`)
  - 10 Parquet files (in `raw_meta_Electronics/`)

### Execution Flow:

```bash
# Step 1: Extract whitelist from 5-core CSV
cd scripts
python3 extract_unique_asins.py

# Step 2: Setup PostgreSQL database and table
python3 setup_database.py

# Step 3: Load products from Parquet files
python3 load_products_to_postgres.py

# Step 4: Extract whitelist from loaded products (for review filtering)
python3 extract_electronics_whitelist.py

# Step 5: Verify data integrity
python3 verify_data_integrity.py
```

## 📊 Expected Results

- **Total ASINs in 5-core CSV**: 368,228
- **Products loaded to PostgreSQL**: 348,228
- **Missing products**: 20,000 (due to NULL titles or data quality issues)

## 🔗 Related Folders

This folder is part of a larger pipeline:

- **Next step**: Use `electronics_products_whitelist.pkl` to filter and load review data
- **Review loading**: See separate review data loading folder/scripts

## 📝 Notes

- The whitelist files are used to filter data at each stage
- `unique_asins_whitelist.pkl` is for product filtering (from CSV)
- `electronics_products_whitelist.pkl` is for review filtering (from DB)
- All scripts include progress tracking and error handling
