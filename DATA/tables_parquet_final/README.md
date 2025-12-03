# 📦 Final Laptop Dataset - Parquet Files with Numpy Embeddings

**Export Date:** November 4, 2025  
**Source:** PostgreSQL `amazon_electronics_rag` database  
**Embedding Model:** BLAIR-RoBERTa (hyp1231/blair-roberta-base)

---

## ⚠️ IMPORTANT: Download Required

**These files are too large for GitHub (1.17 GB total).**

### 📥 Download from Dropbox:

- 📦 **Products (25 MB):** [laptop_products_with_embeddings.parquet](https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&st=oanflprc&dl=0)
- 💬 **Reviews (1.14 GB):** [laptop_reviews_with_embeddings.parquet](https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&st=9j8o4nc3&dl=0)

**After downloading**, place both `.parquet` files in this folder:
```
laptop_hybrid_search/tables_parquet_final/
```

> 💡 **Direct Download Tip:** The links above use `?dl=1` for automatic download. Click to download directly!

---

## 📁 Files in This Folder

```
tables_parquet_final/
├── 📊 DATA FILES (1.17 GB total)
│   ├── laptop_products_with_embeddings.parquet     (24.81 MB)
│   └── laptop_reviews_with_embeddings.parquet      (1.14 GB)
│
├── 📋 METADATA
│   ├── products_export_log.json
│   └── reviews_export_log.json
│
├── 🔧 SCRIPTS
│   ├── 03_reexport_products_with_proper_embeddings.py
│   ├── 04_reexport_reviews_with_proper_embeddings.py
│   └── verify_exports.py
│
└── 📄 README.md (this file)
```

---

## 📊 Dataset Statistics

### **Products Table**
| Metric | Value |
|--------|-------|
| Total Products | 5,455 |
| With Embeddings | 5,455 (100%) |
| Embedding Dimension | 768 |
| Embedding Format | **numpy.ndarray (float32)** |
| File Size | 24.81 MB |

### **Reviews Table**
| Metric | Value |
|--------|-------|
| Total Reviews | 350,105 |
| With Embeddings | 350,105 (100%) |
| Unique Products | 5,455 |
| Unique Users | 324,817 |
| Embedding Dimension | 768 |
| Embedding Format | **numpy.ndarray (float32)** |
| File Size | 1,141.65 MB (1.14 GB) |
| Avg Rating | 3.73 / 5.0 |
| Reviews per Product | 64.2 (average) |
| Verified Purchase Rate | 88.9% |

---

## ✨ Key Features

### ✅ **Proper Numpy Embeddings**
- Embeddings stored as **native numpy arrays** (not strings!)
- Ready for immediate use in ML/AI pipelines
- No parsing required

### ✅ **Data Quality**
- 5-core filtered dataset
- Laptop network adapters removed
- All products have ≥5 reviews
- All users have ≥5 reviews

### ✅ **Complete Metadata**
**Products:**
- `parent_asin`, `title`, `description`, `features`
- `average_rating`, `rating_number`, `price`
- `main_category`, `categories`, `store`
- `details` (JSON), `images` (JSON), `videos` (JSON)
- `blair_embedding` (768-dim numpy array)
- `description_array`, `features_array`

**Reviews:**
- `review_id`, `asin`, `parent_asin`, `user_id`
- `rating`, `title`, `text`
- `timestamp`, `helpful_vote`, `verified_purchase`
- `blair_embedding` (768-dim numpy array)

---

## 🚀 Usage Examples

### Load Products
```python
import pandas as pd
import numpy as np

# Load products
products = pd.read_parquet('laptop_products_with_embeddings.parquet')
print(f"Products loaded: {len(products):,}")

# Access embeddings (already numpy arrays!)
first_emb = products.iloc[0]['blair_embedding']
print(f"Embedding type: {type(first_emb)}")  # numpy.ndarray
print(f"Embedding shape: {first_emb.shape}")  # (768,)
print(f"Embedding dtype: {first_emb.dtype}")  # float32
```

### Load Reviews
```python
# Load reviews
reviews = pd.read_parquet('laptop_reviews_with_embeddings.parquet')
print(f"Reviews loaded: {len(reviews):,}")

# Get reviews for a specific product
product_reviews = reviews[reviews['parent_asin'] == 'B00006LS92']
print(f"Reviews for product: {len(product_reviews)}")

# Access review embeddings
review_emb = reviews.iloc[0]['blair_embedding']
print(f"Shape: {review_emb.shape}")  # (768,)
```

### Compute Similarity
```python
from sklearn.metrics.pairwise import cosine_similarity

# Get all product embeddings
product_embs = np.vstack(products['blair_embedding'].values)
print(f"Product embeddings matrix: {product_embs.shape}")  # (5455, 768)

# Find similar products
query_emb = product_embs[0].reshape(1, -1)
similarities = cosine_similarity(query_emb, product_embs)[0]
top_5_idx = np.argsort(similarities)[-5:][::-1]

print("Top 5 similar products:")
for idx in top_5_idx:
    print(f"  {products.iloc[idx]['title'][:60]}... (sim: {similarities[idx]:.3f})")
```

### Cross-Modal Search (Product ↔ Review)
```python
# Find products similar to a review
review_emb = reviews.iloc[0]['blair_embedding'].reshape(1, -1)
product_embs = np.vstack(products['blair_embedding'].values)

similarities = cosine_similarity(review_emb, product_embs)[0]
top_products = np.argsort(similarities)[-10:][::-1]

print("Products similar to this review:")
for idx in top_products:
    print(f"  {products.iloc[idx]['parent_asin']}: {products.iloc[idx]['title'][:50]}")
```

---

## 🔧 Re-Export Scripts

If you need to regenerate the Parquet files:

```bash
# Export products
python3 03_reexport_products_with_proper_embeddings.py

# Export reviews
python3 04_reexport_reviews_with_proper_embeddings.py

# Verify exports
python3 verify_exports.py
```

---

## 📝 Technical Details

### Embedding Specifications
- **Model:** BLAIR-RoBERTa (`hyp1231/blair-roberta-base`)
- **Dimension:** 768
- **Data Type:** float32 (4 bytes per value)
- **Size per embedding:** 3,072 bytes (~3 KB)
- **Total embeddings:** 355,560 (5,455 products + 350,105 reviews)

### Storage Efficiency
- **Products:** 24.81 MB (includes all metadata + embeddings)
- **Reviews:** 1.14 GB (includes all metadata + embeddings)
- **Total:** 1.17 GB (highly optimized with Snappy compression)

### Cross-Modal Properties
BLAIR embeddings have the unique property that:
- Product embeddings and review embeddings exist in the **same vector space**
- Similar products and their reviews are close together
- Enables powerful cross-modal similarity search

---

## 🎯 Use Cases

1. **RAG System** - Direct input for retrieval-augmented generation
2. **Recommendation Engine** - Product similarity and collaborative filtering
3. **Semantic Search** - Find products by natural language queries
4. **Review Analysis** - Cluster and analyze review sentiment
5. **Cross-Modal Retrieval** - Find products from review descriptions
6. **ML Training** - Pre-embedded features for downstream models

---

## 🔗 Related Resources

### Upstream Sources
- **PostgreSQL Tables:** `products_laptop`, `reviews_laptop`
- **Database:** `amazon_electronics_rag`
- **Original CSVs:** `10_final_5core_laptop_dataset/`

### Downstream Applications
- **RAG System:** `04_rag_system/rag_chatbot/`
- **Enhanced Retriever:** `enhanced_hybrid_retriever.py`
- **Streamlit Apps:** `app.py`, `app_enhanced.py`

---

## 📖 Citation

**Dataset Source:**  
McAuley Lab, UCSD - Amazon Reviews 2023  
https://amazon-reviews-2023.github.io/

**Embedding Model:**  
BLAIR-RoBERTa (hyp1231/blair-roberta-base)  
https://huggingface.co/hyp1231/blair-roberta-base

---

**Status:** ✅ Production Ready  
**Version:** 2.0 Final (with proper numpy embeddings)  
**Last Updated:** November 4, 2025

