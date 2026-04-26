# 🚀 Complete Setup Guide - Laptop Hybrid Search

**Quick start guide for setting up the entire project from scratch**

---

## 📋 Prerequisites

- **Python 3.8+** (Python 3.10 recommended)
- **PostgreSQL 12+** with pgvector extension
- **~5 GB disk space** (3 GB for database, 2 GB for Python packages)
- **OpenAI API key** (for GPT responses)

---

## 🔧 Step-by-Step Setup

### **Step 1: Clone the Repository** 📥

```bash
git clone https://github.com/shivamsharma72/agentic_hybrid_search.git
cd agentic_hybrid_search
git checkout laptop_rag_system
```

---

### **Step 2: Create Virtual Environment** 🐍

#### **On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

#### **On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

---

### **Step 3: Install All Dependencies** 📦

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

**Expected install time:** 5-10 minutes (downloading ~2-3 GB)

**Verify installation:**
```bash
pip list | grep -E "streamlit|psycopg2|openai|transformers|torch"
```

---

### **Step 4: Download Data Files** 📥

⚠️ **IMPORTANT:** Data files are not in the repository (too large for GitHub)

**Download from Dropbox:**
- 📦 **Products (24.81 MB):** [laptop_products_with_embeddings.parquet](https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&dl=1)
- 💬 **Reviews (1.14 GB):** [laptop_reviews_with_embeddings.parquet](https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&dl=1)

**Place files in:**
```bash
laptop_hybrid_search/tables_parquet_final/
├── laptop_products_with_embeddings.parquet    (24.81 MB)
└── laptop_reviews_with_embeddings.parquet     (1.14 GB)
```

> 💡 **Tip:** The links above will start downloading automatically. Save them to the `tables_parquet_final/` folder.

**Verify files:**
```bash
ls -lh tables_parquet_final/*.parquet
```

---

### **Step 5: Setup PostgreSQL Database** 🗄️

#### **5.1 Install PostgreSQL + pgvector**

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew install pgvector
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
# Install pgvector from source (see 00_database_setup/README.md)
```

#### **5.2 Run Database Setup**

```bash
cd 00_database_setup

# Option A: Automated setup (recommended)
./RUN_ALL_SETUP.sh

# Option B: Manual setup (step by step)
psql -U your_username -f 01_create_database.sql
psql -U your_username -d amazon_electronics_rag -f 02_create_products_table.sql
psql -U your_username -d amazon_electronics_rag -f 03_create_reviews_table.sql
python3 04_load_data_from_parquet.py
psql -U your_username -d amazon_electronics_rag -f 05_create_vector_indexes.sql
python3 06_verify_setup.py
```

**Expected time:** 30-45 minutes (loading 350K+ reviews)

---

### **Step 6: Configure API Keys** 🔑

```bash
cd ../rag_chatbot

# Copy environment template
cp env.example .env

# Edit .env file and add your OpenAI API key
nano .env  # or use your favorite editor
```

**Add to `.env`:**
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Get API key from:** https://platform.openai.com/api-keys

---

### **Step 7: Run the Application** 🎉

```bash
# Make sure you're in rag_chatbot/ folder
cd rag_chatbot

# Make sure venv is still activated
# If not: source ../venv/bin/activate

# Launch Streamlit app
streamlit run app.py
```

**The app will open in your browser at:** http://localhost:8501

---

## ✅ Verification Checklist

Before running the app, verify:

- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] All packages installed (`pip list` shows streamlit, torch, etc.)
- [ ] Data files in `tables_parquet_final/` (1.17 GB total)
- [ ] PostgreSQL running (`psql -l` works)
- [ ] Database exists (`psql -l | grep amazon_electronics_rag`)
- [ ] Products loaded (5,455 rows)
- [ ] Reviews loaded (350,105 rows)
- [ ] Vector indexes created (check with `\d products_laptop` in psql)
- [ ] `.env` file created with OpenAI API key
- [ ] Port 8501 available (for Streamlit)

---

## 🐛 Common Issues

### **Issue 1: "torch not found" or "CUDA error"**

**Solution:** Install CPU version of PyTorch
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### **Issue 2: "psycopg2 installation failed"**

**Solution:** Use binary version (already in requirements.txt)
```bash
pip install psycopg2-binary
```

### **Issue 3: "pgvector extension not found"**

**Solution:** Install pgvector extension
```bash
# macOS
brew install pgvector

# Linux (build from source)
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### **Issue 4: "Permission denied on PostgreSQL"**

**Solution:** Create database as superuser
```bash
sudo -u postgres psql
CREATE DATABASE amazon_electronics_rag;
CREATE EXTENSION vector;
\q
```

### **Issue 5: "Parquet files not found"**

**Solution:** Ensure files are downloaded and in correct location
```bash
ls -lh tables_parquet_final/*.parquet
# Should show two files totaling ~1.17 GB
```

---

## 📂 Project Structure After Setup

```
laptop_hybrid_search/
├── venv/                           ✅ Virtual environment
├── requirements.txt                ✅ All dependencies
├── SETUP.md                        ✅ This file
├── README.md                       ✅ Main documentation
│
├── 00_database_setup/              ✅ Database scripts
│   └── [Setup completed]
│
├── rag_chatbot/                    ✅ Application
│   ├── .env                        ✅ API keys (created)
│   └── [Python modules]
│
└── tables_parquet_final/           ✅ Data files
    ├── laptop_products_with_embeddings.parquet   (24.81 MB)
    └── laptop_reviews_with_embeddings.parquet    (1.14 GB)
```

---

## 🔄 Daily Usage

Once setup is complete, to run the app:

```bash
# 1. Navigate to project
cd laptop_hybrid_search

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# 3. Run app
cd rag_chatbot
streamlit run app.py
```

---

## 🛑 Deactivating

When you're done working:

```bash
# Stop Streamlit (in terminal)
Ctrl + C

# Deactivate virtual environment
deactivate
```

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8 | 3.10+ |
| **RAM** | 4 GB | 8 GB+ |
| **Disk Space** | 5 GB | 10 GB |
| **PostgreSQL** | 12 | 14+ |
| **OS** | Any | macOS/Linux |

---

## 🎯 Quick Command Reference

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install requirements
pip install -r requirements.txt

# Setup database
cd 00_database_setup && ./RUN_ALL_SETUP.sh

# Run app
cd rag_chatbot && streamlit run app.py

# Deactivate venv
deactivate
```

---

## 📚 Additional Resources

- **Database Setup Details:** `00_database_setup/README.md`
- **Application Guide:** `rag_chatbot/README.md`
- **Data Specifications:** `tables_parquet_final/README.md`
- **Project Overview:** `README.md`

---

## 💡 Pro Tips

1. **Use Python 3.10** - Best compatibility with all packages
2. **SSD recommended** - Faster database operations
3. **Close other apps** - Free up RAM for embedding model (~2 GB)
4. **GPU optional** - CPU works fine, GPU makes it faster
5. **Keep venv activated** - While working on the project

---

**Setup complete? Try a query: "quiet laptop for office work"** 🚀

---

**Need help?** Check the troubleshooting sections in individual README files.

