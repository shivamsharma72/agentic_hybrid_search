# Amazon Graph RAG Product Recommendation System

**Academic Project — Arizona State University**

An end-to-end Graph-Assisted Hybrid RAG system for Amazon Electronics product recommendations, built across multiple phases: raw data ingestion, semantic search, dual ranking by price + sentiment, and graph-based recommendation design.

---

## 🗺️ Project Phases

| Phase | Branch | Description |
|-------|--------|-------------|
| 1 | `reviews_to_postgres` | Load 37.5M Electronics reviews into PostgreSQL |
| 2 | `product_table` | Load product catalog into PostgreSQL |
| 3 | `laptop_rag_system` | Laptop RAG with BLAIR-RoBERTa semantic search |
| 4 | `hybrid-rag-setup` | Hybrid RAG pipeline setup |
| 5 | `dual_ranking_system` | Dual ranking (price + sentiment) with Next.js UI |
| 6 | `details-analysis-and-docs` | Category analysis and graph recommender design |

---

## 🔍 Phase 5: Dual Ranking System (Main Application)

A dual ranking system that uses semantic search and LLM-powered analysis to rank laptops by both price and user sentiment from reviews.

### Features

- **BLAIR-RoBERTa Hybrid Search**: Searches product titles and review content in the same vector space
- **Query-Aware Similarity**: Finds similar products while preserving the user's original search intent
- **Dual Ranking**: Ranks laptops by price (numerical) and user sentiment (LLM-extracted from reviews)
- **AI Purchase Recommendations**: GPT-4 generates personalized buying advice based on query, budget tiers, and review sentiment
- **Modern UI**: Next.js + FastAPI with real-time similarity scores

### Repository Structure

```
dual_ranking_nextjs/
├── CODE/
│   ├── backend/            # FastAPI backend with semantic search
│   └── frontend/           # Next.js React frontend
├── DATA/
│   ├── 00_database_setup/  # PostgreSQL + pgvector setup scripts
│   └── tables_parquet_final/
└── EVALUATIONS/
```

### Quick Start

**Prerequisites:** Python 3.8+, Node.js 18+, PostgreSQL 14+ with pgvector, OpenAI API key

**1. Download Data Files**

- 📦 [laptop_products_with_embeddings.parquet (25 MB)](https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&st=oanflprc&dl=0)
- 💬 [laptop_reviews_with_embeddings.parquet (1.14 GB)](https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&st=9j8o4nc3&dl=0)

Place both in `DATA/tables_parquet_final/`.

**2. Setup Database**

```bash
cd DATA/00_database_setup
./RUN_ALL_SETUP.sh
```

**3. Configure Environment**

```bash
cd CODE/backend
cp dual_ranking_system/env.example .env
# Add your OpenAI API key
```

**4. Run Backend**

```bash
cd CODE/backend
pip install -r requirements.txt
./run_backend.sh
```

**5. Run Frontend**

```bash
cd CODE/frontend
npm install
npm run dev
```

- Frontend: http://localhost:3001
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### System Architecture

1. **Vector Search**: BLAIR-RoBERTa embeddings (768-dim) for products and reviews
2. **Hybrid Scoring**: 40% product similarity + 60% review similarity
3. **LLM Analysis**: GPT-4 extracts features and sentiment from reviews
4. **Dual Ranking**: Side-by-side comparison of price vs. user experience

### Technologies

- **Backend**: FastAPI, PostgreSQL, pgvector, LangChain
- **Frontend**: Next.js 14, React, Tailwind CSS
- **ML/AI**: BLAIR-RoBERTa, OpenAI GPT-4, LangGraph
- **Database**: PostgreSQL 14+ with pgvector

### Data

- 5,455 laptop products (2,075 with prices); 350,105 reviews with BLAIR embeddings
- 768-dimensional vector space shared by products and reviews

### Evaluation (C4 dataset, 1,632 queries)

| Metric | Value |
|--------|-------|
| Recall@50 | 76.96% |
| MRR | 0.3485 |
| Rank 1 Accuracy | 23.7% |
| Median Rank | 3.0 |

```bash
cd EVALUATIONS/Evaluation
python3 evaluate_c4.py --dataset gemini_product_queries.csv --top-k 50
```

---

## 📥 Phase 1: Review Data to PostgreSQL

Loads **37,510,000** Electronics reviews from Parquet files into PostgreSQL with optimized bulk loading (~64,000 rows/sec, 640× faster than row-by-row INSERT).

### Quick Start

```bash
# Place 10 Parquet files in: data/processed/reviews_Electronics/
psql -d amazon_electronics_rag -f schema/reviews_table.sql
cd scripts && python3 load_reviews_to_postgres_optimized.py
```

See [REPLICATION_GUIDE.md](./REPLICATION_GUIDE.md) and [EXECUTION_ORDER.txt](./EXECUTION_ORDER.txt) for full details.

| Metric | Value |
|--------|-------|
| Total Reviews | 37,510,000 |
| Unique Users | 16,618,885 |
| Unique Products | 348,228 |
| Verified Purchases | 92.5% |
| Date Range | 1998–2023 |
| Table Size | ~21 GB |
| Load Time | ~12 minutes |

---

## 🔄 Planned Next Steps

1. Generate BLAIR-RoBERTa embeddings on full review text
2. Build Neo4j graph (user → product → review relationships)
3. Train GNN for graph-based recommendations
4. Full Graph RAG: combine vector search + graph traversal

---

## License

Academic Project — Arizona State University
