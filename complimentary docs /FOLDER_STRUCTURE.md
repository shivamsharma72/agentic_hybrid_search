# Project Folder Structure

## 📁 Directory Organization

```
swm project/
├── data/                           # All data files
│   ├── raw/                        # Raw unprocessed data (37 GB)
│   │   ├── Electronics.jsonl       # 22 GB - Review data
│   │   ├── meta_Electronics.jsonl  # 5.2 GB - Product metadata
│   │   └── Electronics_pureid_5core.csv  # 897 MB - 5-core whitelist
│   ├── processed/                  # Processed data (1.82 GB)
│   │   └── raw_meta_Electronics/   # 10 parquet files
│   └── README.md
│
├── schema/                         # Database schemas
│   └── products_table.sql          # PostgreSQL products table
│
├── scripts/                        # Python data processing scripts
│   ├── extract_unique_asins.py     # Extract 5-core whitelist
│   ├── setup_database.py           # Initialize PostgreSQL
│   ├── load_products_to_postgres.py  # Load product data
│   ├── verify_data_integrity.py    # Data quality checks
│   ├── download_meta_parquet.py    # Download from Hugging Face
│   └── check_bought_together.py    # Analyze bought_together field
│
├── logs/                           # Execution logs and reports
│   ├── unique_asins_whitelist.pkl  # 4.6 MB - Whitelist pickle
│   ├── extract_asins_summary.txt   # ASIN extraction stats
│   ├── load_products_summary.txt   # Loading summary
│   ├── load_products_run.log       # Full loading log
│   ├── data_integrity_report.txt   # Data quality report
│   ├── verification_run.log        # Verification log
│   └── db_connection_info.txt      # Database credentials
│
├── docs/                           # Project documentation
│   ├── QUICK_START.md              # Quick reference guide
│   ├── PROJECT_COMPLETION_SUMMARY.md  # Phase 1 summary
│   ├── PRODUCT_METADATA_FIELDS.md  # Product field docs
│   ├── REVIEW_DATA_FIELDS.md       # Review field docs
│   ├── PARQUET_METADATA_FIELD_SUMMARY.md  # Parquet analysis
│   └── sample.json                 # Sample data structure
│
├── archive/                        # Old/unused files (297 MB)
│   ├── processed_esci/             # Old ESCI project
│   ├── electronics_w_his/          # Old data
│   ├── resorces from hugging face/ # Old resources
│   ├── processed_esci.zip          # Compressed archive
│   ├── proposal.pdf                # Old proposal
│   └── FA23-Project-Proposal-Group28-Project9.pdf
│
├── tasks.txt                       # Task checklist (all complete ✅)
├── steps.txt                       # Detailed execution log
├── instructions.txt                # Project instructions
└── FOLDER_STRUCTURE.md             # This file
```

## 📊 Size Summary

- **Total Project:** ~37 GB
- **data/raw/:** ~37 GB (raw JSONL files)
- **data/processed/:** ~1.82 GB (parquet files)
- **logs/:** ~4.6 MB (mainly whitelist pickle)
- **archive/:** ~297 MB (old files)
- **Other:** <1 MB (scripts, docs, schemas)

## 🔄 Recent Changes

- ✅ Organized all data files into `data/raw/` and `data/processed/`
- ✅ Moved all documentation to `docs/`
- ✅ Archived old/unused files to `archive/`
- ✅ Updated script paths to match new structure
- ✅ Cleaned up .DS_Store files
- ✅ Created READMEs for organization

## 🎯 Ready For

- ✅ Phase 1: Product metadata loaded (348,228 products in PostgreSQL)
- 🔄 Phase 2: Ready to load review data
- 📝 All documentation and logs organized
- 🗂️ Clean, maintainable project structure

---

Last Updated: October 7, 2025
