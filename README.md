# Laptop Dual Ranking System

**CSE 573 - Semantic Web Mining**  
**Fall 2025 - Group Project**

## Overview

A dual ranking system that uses semantic search and LLM-powered analysis to rank laptops by both price and user sentiment from reviews.

## Features

- **BLAIR-RoBERTa Hybrid Search**: Searches both product titles and review content in the same vector space
- **Query-Aware Similarity**: Finds similar products while preserving user's original search intent
- **Dual Ranking Analysis**: Ranks laptops by:
  - Price (numerical sort)
  - User sentiment (LLM-extracted features from reviews)
- **AI Purchase Recommendations**: GPT-4 generates personalized buying advice based on your search query, budget tiers, and review sentiment
- **Modern UI**: Next.js + FastAPI architecture with real-time similarity scores

## Repository Structure

```
dual_ranking_nextjs/
├── CODE/                    # Application source code
│   ├── backend/            # FastAPI backend with semantic search
│   └── frontend/           # Next.js React frontend
├── DATA/                    # Dataset and database setup
│   ├── 00_database_setup/  # PostgreSQL + pgvector setup scripts
│   └── tables_parquet_final/  # Product and review data (parquet format)
└── EVALUATIONS/            # Evaluation metrics and results
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 14+ with pgvector extension
- OpenAI API key (for GPT-4)

### 1. Download Data Files

**⚠️ REQUIRED:** Download the parquet files with pre-computed BLAIR-RoBERTa embeddings:

- 📦 **Products (25 MB):** [laptop_products_with_embeddings.parquet](https://www.dropbox.com/scl/fi/2i61diskzrfhuzbsuxzs9/laptop_products_with_embeddings.parquet?rlkey=6wtt1023tnybnnjmo4g826s25&st=oanflprc&dl=0)
- 💬 **Reviews (1.14 GB):** [laptop_reviews_with_embeddings.parquet](https://www.dropbox.com/scl/fi/5cnzuduion6tlzsqgef8w/laptop_reviews_with_embeddings.parquet?rlkey=2vx7kpv4zdjj9l4h4uommf0hc&st=9j8o4nc3&dl=0)

**After downloading**, place both files in: `DATA/tables_parquet_final/`

### 2. Setup Database

```bash
cd DATA/00_database_setup
./RUN_ALL_SETUP.sh
```

This will create the database, tables, load the parquet data, and create vector indexes.

### 3. Configure Environment

```bash
cd CODE/backend
cp dual_ranking_system/env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Run Backend

```bash
cd CODE/backend
pip install -r requirements.txt
./run_backend.sh
```

### 5. Run Frontend

```bash
cd CODE/frontend
npm install
npm run dev
```

### 6. Access Application

- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## System Architecture

1. **Vector Search**: BLAIR-RoBERTa embeddings (768-dim) for products and reviews
2. **Hybrid Scoring**: 40% product similarity + 60% review similarity
3. **LLM Analysis**: GPT-4 extracts features and sentiment from reviews
4. **Dual Ranking**: Side-by-side comparison of price vs. user experience

## Technologies

- **Backend**: FastAPI, PostgreSQL, pgvector, LangChain
- **Frontend**: Next.js 14, React, Tailwind CSS
- **ML/AI**: BLAIR-RoBERTa, OpenAI GPT-4, LangGraph
- **Database**: PostgreSQL 14+ with pgvector for vector similarity search

## Data

- **Products**: 5,455 laptop products from Amazon (5-core filtered)
  - 2,075 products with prices (used for dual ranking analysis)
  - 3,380 products without prices (available for search only)
- **Reviews**: 350,105 user reviews with BLAIR embeddings
  - 179,355 reviews for products with prices
- **Vector Space**: Products and reviews in same 768-dimensional space
- **Embeddings**: Pre-computed BLAIR-RoBERTa (768-dim) for all products and reviews

## Evaluation

The system has been evaluated using a C4 dataset with 1,632 complex product queries.

### Performance Metrics

- **Recall@50**: 76.96% - System finds the correct product in top 50 results
- **Mean Reciprocal Rank (MRR)**: 0.3485 - Average reciprocal rank of correct product
- **Rank 1 Accuracy**: 23.7% (386/1632) - Correct product appears first
- **Median Rank**: 3.0 - Half of queries find correct product in top 3

### Running Evaluation

```bash
cd EVALUATIONS/Evaluation

# Run evaluation on test dataset
python3 evaluate_c4.py --dataset gemini_product_queries.csv --top-k 50

# Results saved to:
# - evaluation/results/c4_evaluation_results.csv (detailed results)
# - evaluation/results/c4_evaluation_metrics.json (aggregate metrics)
```

### Evaluation Metrics Explained

- **Recall@K**: Percentage of queries where correct product appears in top K results
- **MRR**: Average of 1/rank for all queries (rewards higher rankings)
- **Rank Distribution**: Shows how many queries find product at each rank position

### Dataset Format

The evaluation dataset (`gemini_product_queries.csv`) contains:

- **query**: Natural language product search query
- **asin**: Expected product ASIN that should be retrieved

Example:

```csv
query,asin
"gaming laptop with liquid cooling under $1000",B08FPXS834
"lightweight laptop for college with good battery",B07DRP6D2R
```

### Custom Evaluation

To evaluate with your own queries:

1. Create a CSV file with columns: `query`, `asin`
2. Run: `python3 evaluate_c4.py --dataset your_queries.csv --top-k 10`
3. Check results in `evaluation/results/`

## License

Academic Project - Arizona State University
