# Test Vector Similarity Search

## 📋 Overview

This script tests the **vector similarity search** on product embeddings and compares it with traditional text search.

## 🎯 What It Does

1. **Loads BLAIR-RoBERTa model** (same as product embeddings)
2. **Embeds query text** into 768-dim vector
3. **Searches using vector similarity** (IVFFlat index)
4. **Compares with text search** (PostgreSQL ILIKE)
5. **Shows performance metrics** and results

## 🚀 Usage

```bash
cd test_similarity_search
python3 test_vector_search.py
```

## 📊 Test Queries

The script includes 10 predefined queries:

- "wireless bluetooth headphones"
- "gaming laptop with RTX graphics card"
- "4K smart TV 55 inch"
- "USB-C charging cable for iPhone"
- "mechanical keyboard with RGB lighting"
- And more...

## 🎮 Interactive Mode

After running predefined queries, you can enter custom queries:

```
> wireless headphones with noise cancelling
> gaming mouse RGB
> laptop for programming
```

## ⏱️ Performance Expectations

### Vector Search

- **Query time**: 50-100ms (with probes=50)
- **Accuracy**: High semantic similarity
- **Finds**: Related products even with different wording

### Text Search

- **Query time**: 10-50ms
- **Accuracy**: Exact keyword matches only
- **Finds**: Products with query words in title

## 📝 Example Output

```
================================================================================
Query: "wireless bluetooth headphones"
================================================================================

🔄 Generating query embedding...
   ✅ Embedding generated (45.2ms)
   Embedding shape: (768,)
   First 5 values: [-0.0234, 0.1456, -0.0891, 0.0567, 0.2134]

🔍 Vector Similarity Search:

   Vector Results (68.9ms):
      1. [B08HMWZBXC] (sim: 0.9234)
         Sony WH-1000XM4 Wireless Bluetooth Noise Cancelling Headphones...
         ⭐ 4.7 (12,345) | $348.00

      2. [B07XJ8C8F5] (sim: 0.9156)
         Bose QuietComfort 35 II Wireless Bluetooth Headphones...
         ⭐ 4.5 (8,976) | $299.00

      3. [B0863TXGM3] (sim: 0.8987)
         JBL Live 650BTNC Wireless Over-Ear Noise-Cancelling Headphones...
         ⭐ 4.3 (2,345) | $149.99

      ...

📝 Traditional Text Search:

   Text Results (34.2ms):
      1. [B08HMWZBXC]
         Sony WH-1000XM4 Wireless Bluetooth Noise Cancelling Headphones...
         ⭐ 4.7 (12,345) | $348.00

      2. [B07XJ8C8F5]
         Bose QuietComfort 35 II Wireless Bluetooth Headphones...
         ⭐ 4.5 (8,976) | $299.00

      ...

📊 Performance Comparison:
   Vector search: 68.9ms (10 results)
   Text search:   34.2ms (10 results)
   📝 Text is 2.01x faster

================================================================================
```

## 🔧 Configuration

Edit these variables in `test_vector_search.py`:

```python
DB_NAME = "amazon_electronics_rag"
MODEL_NAME = "henrychur/blair-roberta-base"
PROBES = 50  # More probes = better accuracy but slower
TOP_K = 10   # Number of results to return
```

## 🎛️ Tuning Performance

### Faster Search (Lower Accuracy)

```python
PROBES = 10  # ~85% recall, very fast
```

### Better Accuracy (Slower Search)

```python
PROBES = 100  # ~96% recall, slower
```

## 📈 Advantages of Vector Search

1. **Semantic Understanding**

   - "laptop for coding" → finds "developer workstation", "programming computer"
   - Text search: misses these

2. **Synonym Handling**

   - "earphones" → finds "earbuds", "in-ear headphones"
   - Text search: only finds exact "earphones"

3. **Typo Tolerance**

   - "wireles headfones" → still finds wireless headphones (after embedding)
   - Text search: no results

4. **Cross-lingual** (if model supports)
   - Query in one language, find products in another

## 🚨 Troubleshooting

**Error: Model not found**

```bash
# Install transformers
pip install transformers torch
```

**Slow query (> 200ms)**

```sql
-- Check if index is being used
EXPLAIN ANALYZE
SELECT * FROM products
ORDER BY blair_embedding <=> '[vector]'::vector
LIMIT 10;

-- Should see: "Index Scan using products_blair_embedding_ivfflat_idx"
```

**Out of memory**

```python
# Use CPU instead of GPU
device = "cpu"
```

## 🎯 Next Steps

After testing:

1. ✅ **Tune probes** for optimal speed/accuracy
2. 🔄 **Build HNSW index** (better recall)
3. 🚀 **Integrate into RAG system**
4. 📊 **Add filtering** (price, category, ratings)

---

**Created:** 2025-10-29  
**Products:** 348,228  
**Index Type:** IVFFlat  
**Model:** BLAIR-RoBERTa
