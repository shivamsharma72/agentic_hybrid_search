# 🧠 Laptop RAG Chatbot

A Retrieval-Augmented Generation (RAG) system for intelligent laptop product search and recommendations using semantic vector search.

---

## 📖 What is This?

This is a **semantic search chatbot** that helps users find laptops by understanding natural language queries. It uses:

1. **BLAIR-RoBERTa embeddings** - Converts products and reviews into 768-dimensional vectors
2. **PostgreSQL + pgvector** - Stores and searches these vectors efficiently
3. **OpenAI GPT** - Generates natural, helpful responses
4. **Streamlit** - Provides a beautiful web interface

### **How It Works (Simple)**

```
User Query: "quiet laptop for office work"
     ↓
1. Convert query to vector (BLAIR-RoBERTa)
     ↓
2. Search database for similar product vectors (PostgreSQL)
     ↓
3. Search database for similar review vectors (Cross-modal)
     ↓
4. Combine products + supporting reviews
     ↓
5. Generate response (OpenAI GPT)
     ↓
User gets: Relevant laptops with review evidence
```

---

## 🎯 Key Features

✅ **Semantic Search** - Understands meaning, not just keywords  
✅ **Cross-Modal Retrieval** - Matches products with relevant reviews  
✅ **Review Evidence** - Shows real user feedback for recommendations  
✅ **Fast Queries** - HNSW index for sub-100ms vector search  
✅ **Clean UI** - Streamlit interface with beautiful design  

---

## 📁 Project Structure

```
rag_chatbot/
├── app.py                    # Streamlit web interface
├── retriever.py              # Vector search logic (products + reviews)
├── response_generator.py     # OpenAI GPT integration
├── embedding_model.py        # BLAIR-RoBERTa embeddings
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── env.example               # Example environment file
├── run_app.sh                # Quick start script
└── README.md                 # This file
```

---

## 🚀 Quick Start

### **1. Prerequisites**

- Python 3.8+
- PostgreSQL with pgvector extension
- Database setup completed (see `../00_database_setup/`)
- OpenAI API key

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Configure Environment**

Create a `.env` file (copy from `env.example`):

```bash
cp env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### **4. Run the Application**

```bash
streamlit run app.py
```

Or use the provided script:

```bash
./run_app.sh
```

The app will open in your browser at `http://localhost:8501`

---

## 🔧 How It Works (Technical)

### **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                         │
│                     (Streamlit App)                         │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─── User Query
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                   Query Processing                          │
│         (Convert text to 768-dim vector)                    │
│              BLAIR-RoBERTa Model                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─── Query Embedding [768 floats]
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                  Vector Search (retriever.py)               │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Product Search       │  │ Review Search        │        │
│  │ (products_laptop)    │  │ (reviews_laptop)     │        │
│  │                      │  │                      │        │
│  │ HNSW Index           │  │ HNSW Index           │        │
│  │ Cosine Distance      │  │ Cosine Distance      │        │
│  └──────────┬───────────┘  └──────────┬───────────┘        │
│             │                         │                     │
│             └────── Merge Results ────┘                     │
│                          │                                  │
│                 Products + Reviews                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─── Retrieved Context
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│            Response Generation (OpenAI GPT)                 │
│  • Formats product information                             │
│  • Includes review evidence                                │
│  • Generates natural language response                     │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
        User Response
```

### **Search Strategies**

The system supports three search strategies:

1. **Balanced** (default)
   - 20 products from product search
   - 50 reviews from review search
   - Best for general queries

2. **Product Focused**
   - 30 products, 30 reviews
   - Emphasizes product specifications

3. **Review Focused**
   - 10 products, 80 reviews
   - Emphasizes user experiences

---

## 💾 Database Schema

### **products_laptop Table**
```sql
- parent_asin       (PK) - Unique product ID
- title             - Product name
- description       - Product description
- features          - Feature list
- average_rating    - Average rating (1-5)
- rating_number     - Total number of ratings
- price             - Product price
- blair_embedding   - 768-dim vector
+ 10 more columns...
```

### **reviews_laptop Table**
```sql
- review_id         (PK) - Unique review ID
- parent_asin       (FK) - Links to product
- user_id           - Reviewer ID
- rating            - Review rating (1-5)
- title             - Review title
- text              - Review content
- blair_embedding   - 768-dim vector
+ 7 more columns...
```

---

## 📝 Configuration (`config.py`)

Key settings you can modify:

```python
# Database
DB_NAME = "amazon_electronics_rag"
PRODUCTS_TABLE = "products_laptop"
REVIEWS_TABLE = "reviews_laptop"

# Model
RESPONSE_MODEL = "gpt-3.5-turbo"  # or "gpt-4"
EMBEDDING_MODEL_NAME = "hyp1231/blair-roberta-base"

# Search
MAX_PRODUCTS = 20
MAX_REVIEWS = 50
DEFAULT_SEARCH_STRATEGY = "balanced"
```

---

## 🎨 Example Queries

The system works best with natural language queries:

### **Good Queries:**
- "quiet laptop for office work"
- "gaming laptop under $1000"
- "lightweight laptop for travel"
- "laptop with long battery life for students"
- "powerful laptop for video editing"

### **What Makes Cross-Modal Search Special:**

Traditional search: Matches query → products only

Our system: Matches query → products **AND** reviews

Example:
- Query: "quiet laptop"
- Finds: Products with "quiet" descriptions **AND** reviews mentioning "quiet fan", "silent operation", etc.
- Result: Better, more accurate recommendations

---

## 🔍 Components Explained

### **1. retriever.py** - Vector Search Engine

```python
class EnhancedHybridRetriever:
    def search_unified(query_embedding, strategy):
        # Search products by vector similarity
        products = search_products(query_embedding)
        
        # Search reviews by vector similarity
        reviews = search_reviews(query_embedding)
        
        # Merge and rank results
        return merge_results(products, reviews)
```

**What it does:**
- Converts your query to a vector
- Searches both products and reviews in parallel
- Uses HNSW index for fast approximate nearest neighbor search
- Merges results intelligently (reviews boost product relevance)

### **2. response_generator.py** - GPT Integration

```python
class ResponseGenerator:
    def generate_response(query, products, reviews):
        # Build context from retrieved data
        context = format_products_and_reviews(products, reviews)
        
        # Create prompt for GPT
        prompt = build_prompt(query, context)
        
        # Generate natural response
        return openai.chat.completions.create(...)
```

**What it does:**
- Takes raw data from retriever
- Formats it into a clear context
- Sends to OpenAI GPT with instructions
- Returns natural language response

### **3. embedding_model.py** - Text → Vectors

```python
class EmbeddingModel:
    def encode(text):
        # BLAIR-RoBERTa converts text to 768 numbers
        return model.encode(text)  # [0.23, -0.45, ...]
```

**What it does:**
- Loads BLAIR-RoBERTa model (once)
- Converts text to 768-dimensional vectors
- Uses CLS token pooling for sentence embeddings

### **4. app.py** - Streamlit Interface

```python
# Simple Streamlit app structure
query = st.text_input("Ask about laptops...")
if query:
    # Get embedding
    embedding = model.encode(query)
    
    # Search
    results = retriever.search(embedding)
    
    # Generate response
    response = generator.generate(query, results)
    
    # Display
    st.write(response)
```

---

## 🎓 For Students/Reviewers

### **What Makes This System Unique?**

1. **Cross-Modal Alignment**
   - BLAIR model is trained so product descriptions and reviews are in the same vector space
   - This enables matching products with relevant reviews semantically

2. **Evidence-Based Recommendations**
   - Not just showing products
   - Shows WHY products are recommended (actual user reviews)

3. **Semantic Understanding**
   - Understands synonyms: "quiet" = "silent" = "low noise"
   - Understands concepts: "student laptop" → affordable, portable, long battery

### **Technologies Demonstrated**

- ✅ Vector databases (PostgreSQL + pgvector)
- ✅ Semantic search (BLAIR-RoBERTa embeddings)
- ✅ RAG architecture (retrieval + generation)
- ✅ LLM integration (OpenAI GPT)
- ✅ Full-stack development (Python, SQL, Streamlit)

---

## 📊 Performance

- **Query Time:** < 100ms for vector search
- **Products DB:** 5,455 laptops, ~100 MB
- **Reviews DB:** 350,105 reviews, ~3 GB
- **Embedding Dimension:** 768 (BLAIR-RoBERTa)
- **Index Type:** HNSW (Hierarchical Navigable Small World)

---

## 🐛 Troubleshooting

### **Issue: "OPENAI_API_KEY not found"**
**Solution:** Create `.env` file with your API key (see Quick Start)

### **Issue: "Connection to database failed"**
**Solution:** 
1. Check PostgreSQL is running
2. Verify database exists: `psql -l | grep amazon_electronics_rag`
3. Run database setup if needed: `../00_database_setup/RUN_ALL_SETUP.sh`

### **Issue: "ModuleNotFoundError"**
**Solution:** Install dependencies: `pip install -r requirements.txt`

### **Issue: "Slow search queries"**
**Solution:** Check HNSW indexes exist:
```sql
\d products_laptop
\d reviews_laptop
```
If missing, run: `../00_database_setup/05_create_vector_indexes.sql`

---

## 📚 References

- **BLAIR Model:** https://huggingface.co/hyp1231/blair-roberta-base
- **pgvector:** https://github.com/pgvector/pgvector
- **Amazon Reviews 2023:** https://amazon-reviews-2023.github.io/
- **Streamlit:** https://streamlit.io/

---

## 📜 License

This project uses publicly available Amazon Reviews 2023 dataset.  
See dataset license: https://amazon-reviews-2023.github.io/

---

**Version:** 1.0 Final  
**Last Updated:** November 2025  
**Status:** ✅ Production Ready

