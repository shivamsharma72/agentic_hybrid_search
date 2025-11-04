# 🧠 Laptop RAG System - Complete Package

A production-ready **Retrieval-Augmented Generation (RAG)** system for intelligent laptop product search using semantic vector embeddings and cross-modal retrieval.

---

## 🎯 What is This?

This is a **semantic search chatbot** that helps users find laptops using natural language queries. It combines:
- **BLAIR-RoBERTa embeddings** for semantic understanding
- **PostgreSQL + pgvector** for fast vector similarity search
- **OpenAI GPT** for natural language responses
- **Streamlit** for a beautiful web interface

**Example Query:** *"quiet laptop for office work"*  
**System Response:** Recommends relevant laptops with supporting review evidence

---

## 📁 Project Structure

```
laptop_hybrid_search/
│
├── 📦 requirements.txt               # ALL Python dependencies (install first!)
├── 🚀 SETUP.md                       # Complete setup guide with venv instructions
├── 📖 README.md                      # This file - project overview
│
├── 📊 tables_parquet_final/          # Dataset (1.17 GB - Download Required)
│   ├── laptop_products_with_embeddings.parquet    (24.81 MB)
│   ├── laptop_reviews_with_embeddings.parquet     (1.14 GB)
│   └── README.md                     → Data specifications & usage
│
├── 🗄️ 00_database_setup/             # PostgreSQL Setup Scripts
│   ├── 01-06_*.sql / *.py            → Database creation & loading
│   ├── RUN_ALL_SETUP.sh              → Automated setup script
│   └── README.md                     → Complete setup guide
│
└── 🤖 rag_chatbot/                   # Streamlit Application
    ├── app.py                        → Main Streamlit interface
    ├── retriever.py                  → Vector search engine
    ├── response_generator.py         → OpenAI GPT integration
    ├── embedding_model.py            → BLAIR-RoBERTa encoder
    ├── config.py                     → Configuration settings
    ├── requirements.txt              → Chatbot-specific dependencies
    ├── env.example                   → Environment template
    └── README.md                     → Application guide
```

---

## 🚀 Quick Start Guide

> **📘 For detailed setup instructions with virtual environment, see [SETUP.md](SETUP.md)**

### **Step 0: Setup Virtual Environment** 🐍 *(Recommended)*

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install ALL dependencies at once
pip install -r requirements.txt
```

---

### **Step 1: Download Data Files** 📥

⚠️ **IMPORTANT:** The parquet data files (1.17 GB) are too large for GitHub.

**Download from Dropbox:**
- 📦 **Products (24.81 MB):** [laptop_products_with_embeddings.parquet](https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&dl=1)
- 💬 **Reviews (1.14 GB):** [laptop_reviews_with_embeddings.parquet](https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&dl=1)

**After downloading**, place both `.parquet` files in:
```
laptop_hybrid_search/tables_parquet_final/
```

**Expected file structure:**
```
laptop_hybrid_search/
└── tables_parquet_final/
    ├── laptop_products_with_embeddings.parquet    (24.81 MB)
    └── laptop_reviews_with_embeddings.parquet     (1.14 GB)
```

---

### **Step 2: Setup Database** 🗄️

Navigate to database setup:
```bash
cd 00_database_setup
```

**Read the complete guide:**
```bash
cat README.md
```

**Run automated setup:**
```bash
./RUN_ALL_SETUP.sh
```

**Expected time:** ~30-45 minutes (loads 350K+ reviews with embeddings)

---

### **Step 3: Run the Application** 🤖

Navigate to chatbot:
```bash
cd ../rag_chatbot
```

**Configure API key:**
```bash
cp env.example .env
# Edit .env and add your OpenAI API key
```

**Launch the app:**
```bash
streamlit run app.py
```

**Access at:** http://localhost:8501

---

## 📖 Navigation Guide

### **For First-Time Users:**
1. **Start here** → Read this README
2. **Download data** → From Dropbox links above
3. **Setup database** → Follow `00_database_setup/README.md`
4. **Run chatbot** → Follow `rag_chatbot/README.md`

### **For Developers:**
- **Database Schema** → `00_database_setup/02_create_products_table.sql`
- **Search Logic** → `rag_chatbot/retriever.py`
- **GPT Integration** → `rag_chatbot/response_generator.py`
- **UI Components** → `rag_chatbot/app.py`

### **For Researchers:**
- **Data Specifications** → `tables_parquet_final/README.md`
- **Embedding Details** → BLAIR-RoBERTa (768-dim vectors)
- **Dataset Stats** → 5,455 products, 350,105 reviews, 5-core filtered

---

## 🎓 Key Features

✅ **Semantic Search** - Understands meaning, not just keywords  
✅ **Cross-Modal Retrieval** - Matches products with relevant reviews  
✅ **Evidence-Based** - Shows real user feedback for recommendations  
✅ **Fast Queries** - HNSW index for sub-100ms vector search  
✅ **Production Ready** - Complete with error handling & optimization

---

## 📊 Dataset Overview

| Component | Count | Details |
|-----------|-------|---------|
| **Products** | 5,455 | Laptops with full metadata |
| **Reviews** | 350,105 | User reviews with ratings |
| **Unique Users** | 324,817 | Review authors |
| **Embeddings** | 355,560 | 768-dim BLAIR-RoBERTa vectors |
| **Total Size** | 1.17 GB | Compressed Parquet format |

**Quality:** 5-core filtered (all products have ≥5 reviews, all users have ≥5 reviews)

---

## 🛠️ Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** with pgvector extension
- **OpenAI API Key** (for GPT responses)
- **~3 GB disk space** (for database)
- **~2 GB RAM** (for embedding model)

---

## 📚 Technologies Used

- **Vector Search:** PostgreSQL + pgvector (HNSW index)
- **Embeddings:** BLAIR-RoBERTa (`hyp1231/blair-roberta-base`)
- **LLM:** OpenAI GPT-3.5-turbo / GPT-4
- **Frontend:** Streamlit
- **Data Format:** Parquet (with numpy embeddings)
- **Dataset:** Amazon Reviews 2023 (McAuley Lab, UCSD)

---

## 🐛 Troubleshooting

### **Issue: "Data files not found"**
**Solution:** Download parquet files from Dropbox (see Step 1)

### **Issue: "Database connection failed"**
**Solution:** Ensure PostgreSQL is running and database is created:
```bash
psql -l | grep amazon_electronics_rag
```

### **Issue: "OpenAI API key not found"**
**Solution:** Create `.env` file in `rag_chatbot/` with your API key:
```bash
cd rag_chatbot
cp env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

### **Issue: "Slow search queries"**
**Solution:** Check if vector indexes are created:
```bash
cd 00_database_setup
psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql
```

---

## 📜 License & Attribution

**Dataset:**  
Amazon Reviews 2023 - McAuley Lab, UCSD  
https://amazon-reviews-2023.github.io/

**Embedding Model:**  
BLAIR-RoBERTa (MIT License)  
https://huggingface.co/hyp1231/blair-roberta-base

**This Project:**  
Academic research project - ASU Software Engineering  
Free to use for educational and research purposes

---

## 📞 Support

For detailed documentation:
- **Database Setup** → `00_database_setup/README.md`
- **Application Guide** → `rag_chatbot/README.md`
- **Data Specifications** → `tables_parquet_final/README.md`

---

**Version:** 1.0 Final  
**Last Updated:** November 4, 2025  
**Status:** ✅ Production Ready

---

## 🎯 Quick Reference Card

```bash
# Complete Setup (First Time)
1. Download data → Dropbox links above
2. cd 00_database_setup && ./RUN_ALL_SETUP.sh
3. cd ../rag_chatbot && pip install -r requirements.txt
4. cp env.example .env  # Add your OpenAI key
5. streamlit run app.py

# Regular Usage (After Setup)
cd laptop_hybrid_search/rag_chatbot
streamlit run app.py
```

**That's it! Happy searching! 🚀**

