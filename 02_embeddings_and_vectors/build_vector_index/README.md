# Build Vector Index for Product Embeddings

## 📋 Overview

This script creates an **IVFFlat vector index** on the `blair_embedding` column in the `products` table, enabling fast similarity search.

## 🎯 What is IVFFlat?

**IVFFlat** (Inverted File with Flat compression) is an **approximate nearest neighbor (ANN)** algorithm:

- **Clusters vectors** into `lists` groups during index build
- **Searches only nearby clusters** during query (controlled by `probes`)
- **Trade-off**: Speed vs Accuracy (more probes = better accuracy but slower)

## ⚙️ Parameters

### **Lists** (Build-time parameter)

- Number of clusters to divide vectors into
- **Formula**: `sqrt(num_rows)` is optimal
- **For 348K products**: `sqrt(348228) ≈ 590` → We use **500**
- Set once during index creation

### **Probes** (Query-time parameter)

- Number of clusters to search
- **Default**: `lists/10` → **50 probes**
- **More probes** = better recall, slower search
- Can be adjusted per query

## 🚀 Usage

```bash
cd build_vector_index
python3 create_ivfflat_index.py
```

## ⏱️ Performance

- **Build time**: 2-5 minutes for 348K products
- **Index size**: ~200-300 MB
- **Query time**: 10-50ms per search
- **Recall**: 90-95% (with 50 probes)

## 📊 Expected Output

```
================================================================================
CREATE IVFFLAT VECTOR INDEX FOR PRODUCT EMBEDDINGS
================================================================================

✅ Connected to database: amazon_electronics_rag

📊 Checking current state...
   Products with embeddings: 348,228
   No existing indexes on blair_embedding

🔧 Running ANALYZE on products table...
   (This helps PostgreSQL optimize queries)
   ✅ ANALYZE complete (2.3s)

🚀 Creating IVFFlat index...
   Index name: products_blair_embedding_ivfflat_idx
   Lists (clusters): 500
   Distance metric: Cosine (best for embeddings)
   Estimated time: 2-5 minutes

   Building index... (this will take a few minutes)

   ✅ Index created successfully!
   ⏱️  Build time: 187.4 seconds (3.1 minutes)

⚙️  Setting search parameters...
   Probes: 50 (more probes = better accuracy, slower search)
   ✅ Search probes set to 50

📋 Index Information:
   Index size: 267 MB
   Definition: CREATE INDEX products_blair_embedding_ivfflat_idx ON public.products...

🧪 Testing index with sample query...
   Test product: B00XYZ123 - Wireless Bluetooth Headphones...

   Finding 5 most similar products...

   ✅ Query completed in 23.4ms

   Top 5 similar products:
      1. [B00ABC456] Sony WH-1000XM4 Wireless Headphones...
         Similarity: 0.8723
      2. [B00DEF789] Bose QuietComfort 35 II...
         Similarity: 0.8456
      ...

================================================================================
INDEX CREATION SUMMARY
================================================================================
Total time: 195.6 seconds (3.3 minutes)
Products indexed: 348,228
Index name: products_blair_embedding_ivfflat_idx
Index type: IVFFlat
Lists: 500
Probes: 50
Distance metric: Cosine

✅ SUCCESS! Vector index is ready for similarity search

📝 Usage in queries:
   1. Set probes: SET ivfflat.probes = 50;
   2. Search: SELECT * FROM products
      ORDER BY blair_embedding <=> '[query_embedding]'::vector
      LIMIT 10;

🎯 Next steps:
   1. Test similarity search with real queries
   2. Tune probes parameter (50-100 for better accuracy)
   3. Build HNSW index for comparison (optional)
================================================================================
```

## 🔧 Configuration

Edit these variables in `create_ivfflat_index.py`:

```python
DB_NAME = "amazon_electronics_rag"
INDEX_NAME = "products_blair_embedding_ivfflat_idx"
LISTS = 500    # Number of clusters (sqrt of rows)
PROBES = 50    # Clusters to search (lists/10)
```

## 📝 Using the Index in Queries

### Set Probes (per session or query)

```sql
SET ivfflat.probes = 50;
```

### Find Similar Products

```sql
-- Find products similar to a given embedding
SELECT
    parent_asin,
    title,
    1 - (blair_embedding <=> '[your_768_dim_vector]'::vector) as similarity
FROM products
WHERE blair_embedding IS NOT NULL
ORDER BY blair_embedding <=> '[your_768_dim_vector]'::vector
LIMIT 10;
```

### Distance Operators

- `<=>` = Cosine distance (1 - cosine_similarity)
- `<->` = L2 distance (Euclidean)
- `<#>` = Inner product

## 🎛️ Tuning Probes

Adjust probes based on your needs:

| Probes | Recall | Speed     | Use Case                  |
| ------ | ------ | --------- | ------------------------- |
| 10     | ~85%   | Very Fast | Real-time search          |
| 50     | ~92%   | Fast      | General purpose (default) |
| 100    | ~96%   | Medium    | High accuracy             |
| 200    | ~98%   | Slow      | Maximum accuracy          |

```sql
-- Example: High accuracy search
SET ivfflat.probes = 100;
SELECT * FROM products
ORDER BY blair_embedding <=> '[vector]'::vector
LIMIT 10;
```

## 🚨 Troubleshooting

**Error: operator does not exist: vector <=> vector**

```bash
# Install pgvector extension
psql -d amazon_electronics_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Index build is slow (> 10 minutes)**

- Normal for large datasets
- Check `shared_buffers` in PostgreSQL config
- Consider increasing `maintenance_work_mem`

**Query is slow (> 100ms)**

- Increase `probes` parameter
- Run `VACUUM ANALYZE products;`
- Check index is being used: `EXPLAIN ANALYZE SELECT ...`

## 📊 Verify Index Usage

```sql
-- Check if index is being used
EXPLAIN ANALYZE
SELECT parent_asin, title
FROM products
ORDER BY blair_embedding <=> '[vector]'::vector
LIMIT 10;

-- Should see: "Index Scan using products_blair_embedding_ivfflat_idx"
```

## 🔄 Rebuilding Index

If you update many embeddings, rebuild the index:

```sql
-- Drop old index
DROP INDEX products_blair_embedding_ivfflat_idx;

-- Recreate (or run the script again)
```

## 📈 Next Steps

1. ✅ Index created → Test similarity search
2. ⚙️ Tune probes → Find optimal accuracy/speed
3. 🔬 Compare with HNSW → Better recall (optional)
4. 🚀 Build RAG system → Use for product recommendations

---

**Created:** 2025-10-29  
**Products:** 348,228  
**Index Type:** IVFFlat  
**Lists:** 500  
**Probes:** 50

