RAG SYSTEM EVALUATION GUIDE
============================

This folder contains evaluation scripts and results for the laptop search system.

WHAT IS BEING EVALUATED?
-------------------------

We evaluate the RETRIEVAL performance of our hybrid semantic search system:
- Can it find the correct product given a natural language query?
- How well does BLAIR-RoBERTa + review embeddings work?
- Does the hybrid approach (products + reviews) improve accuracy?


EVALUATION DATASET
------------------

File: gemini_product_queries.csv
Format: CSV with columns [query, asin]
Size: 1,632 test queries
Source: Generated using Gemini LLM for diverse, complex queries

Example queries:
- "apple macbook air for heavy use with strong performance and a touchscreen"
- "gaming laptop with liquid cooling under $1000"
- "lightweight laptop for college with good battery life"

Each query has a known "correct" product (ASIN) that should be retrieved.


HOW TO RUN EVALUATION
----------------------

Prerequisites:
1. Database must be set up (see DATA/00_database_setup/)
2. Python dependencies installed
3. BLAIR-RoBERTa model available

Command:
```bash
cd EVALUATIONS/Evaluation

python3 evaluate_c4.py \
  --dataset gemini_product_queries.csv \
  --top-k 50 \
  --output-dir evaluation/results
```

Parameters:
- --dataset: Path to CSV file with queries and expected ASINs
- --top-k: Check if correct product appears in top K results (default: 10)
- --output-dir: Where to save results (default: evaluation/results)


WHAT THE SCRIPT DOES
--------------------

For each query in the dataset:
1. Encode query using BLAIR-RoBERTa (768-dim vector)
2. Search database using hybrid retrieval:
   - Product title/description similarity (40%)
   - Review content similarity (60%)
3. Retrieve top K products
4. Check if expected product is in results
5. Record rank position (1-indexed)

Then calculates aggregate metrics across all queries.


EVALUATION METRICS
------------------

1. RECALL@K
   - What % of queries find the correct product in top K results?
   - Higher is better
   - Our system: 76.96% @ K=50

2. MEAN RECIPROCAL RANK (MRR)
   - Average of 1/rank for all queries
   - Rewards higher rankings (rank 1 better than rank 10)
   - Range: 0.0 to 1.0, higher is better
   - Our system: 0.3485

3. RANK STATISTICS
   - Mean rank: 9.07 (on average, correct product at position 9)
   - Median rank: 3.0 (half of queries find it in top 3!)
   - Min: 1 (best case - correct product is #1)
   - Max: 50 (worst case - found at last position)

4. RANK DISTRIBUTION
   - How many queries find product at each rank?
   - Rank 1: 386 queries (23.7%) - Perfect result!
   - Rank 2: 165 queries (10.1%)
   - Rank 3: 117 queries (7.2%)
   - ...
   - Not found: 376 queries (23.0%) - System couldn't find it


RESULTS FILES
-------------

After running evaluation, you get:

1. c4_evaluation_results.csv
   - Detailed results for each query
   - Columns: query, expected_product_id, rank, recall_at_k, mrr, retrieved_asins
   - Use this to analyze individual query performance

2. c4_evaluation_metrics.json
   - Aggregate metrics (recall, MRR, rank distribution)
   - Use this for reporting overall system performance


INTERPRETING RESULTS
---------------------

GOOD SIGNS:
✓ Recall@50 = 76.96% - System finds correct product 77% of the time
✓ Median rank = 3 - Half of queries get top-3 results
✓ Rank 1 = 23.7% - Almost 1 in 4 queries is perfect

AREAS FOR IMPROVEMENT:
⚠ MRR = 0.35 - Could be higher (closer to 1.0)
⚠ 23% not found - System misses ~1 in 4 queries


EXAMPLE OUTPUT
--------------

When you run the evaluation, you'll see:

```
🔧 Initializing evaluation components...
✅ Components initialized

📂 Loading C4 dataset from gemini_product_queries.csv...
✅ Loaded 1632 queries from dataset

🔍 Filtering to products in database...
   Database has 19847 products
   Filtered: 1632 → 1632 queries
   Removed: 0 queries (products not in DB)

📊 Evaluating 1632 queries (checking top 50 results)...
================================================================================
Evaluating queries: 100%|████████████████████| 1632/1632 [12:34<00:00, 2.16it/s]

================================================================================
📈 AGGREGATE METRICS
================================================================================

📊 Total Queries: 1632
✅ Found in top 50: 1256 (77.0%)
❌ Not found: 376 (23.0%)

🎯 Recall@50: 0.7696 (76.96%)
📈 MRR (Mean Reciprocal Rank): 0.3485

📊 Rank Statistics:
   Mean Rank: 9.07
   Median Rank: 3.00
   Best Rank: 1
   Worst Rank: 50

📋 Rank Distribution:
   Rank 1: 386 queries (23.7%)
   Rank 2: 165 queries (10.1%)
   Rank 3: 117 queries (7.2%)
   Rank 4: 70 queries (4.3%)
   Rank 5: 48 queries (2.9%)
   ...

💾 Saved detailed results to: evaluation/results/c4_evaluation_results.csv
💾 Saved metrics to: evaluation/results/c4_evaluation_metrics.json

================================================================================
✅ EVALUATION COMPLETE!
================================================================================
```


CREATING YOUR OWN TEST SET
---------------------------

To test with your own queries:

1. Create a CSV file:
```csv
query,asin
"your natural language query here",B08FPXS834
"another query",B07DRP6D2R
```

2. Make sure ASINs exist in your database

3. Run evaluation:
```bash
python3 evaluate_c4.py --dataset my_queries.csv --top-k 10
```


UNDERSTANDING THE CODE
----------------------

File: evaluate_c4.py

Key components:

1. C4Evaluator class
   - Initializes BLAIR-RoBERTa embedding model
   - Creates EnhancedHybridRetriever (same as main RAG system)
   - Enables reranker for better accuracy

2. evaluate_query()
   - Encodes query to 768-dim vector
   - Searches using hybrid retrieval (products + reviews)
   - Checks if expected product is in results
   - Calculates per-query metrics

3. calculate_metrics()
   - Aggregates results across all queries
   - Computes Recall@K, MRR, rank statistics
   - Generates rank distribution

4. save_results()
   - Exports CSV with detailed per-query results
   - Exports JSON with aggregate metrics


COMPARISON WITH OTHER SYSTEMS
------------------------------

Our hybrid approach (products + reviews):
- Recall@50: 76.96%
- MRR: 0.3485

Typical baselines:
- BM25 (keyword search): ~40-50% Recall@50
- Product-only embeddings: ~60-70% Recall@50
- Reviews-only: ~50-60% Recall@50

Our hybrid approach combines both for better coverage!


TROUBLESHOOTING
---------------

Error: "Missing required column: 'query'"
→ Check CSV has columns: query, asin

Error: "No queries remaining after filtering"
→ ASINs in dataset don't match database products
→ Check database has products loaded

Error: "Connection refused"
→ PostgreSQL not running
→ Start database first

Slow evaluation (>1 min per query):
→ Normal! BLAIR embeddings + database search take time
→ 1632 queries ≈ 15-20 minutes total


NEXT STEPS
----------

After running evaluation:

1. Analyze failures (queries with rank = null)
2. Check low-ranked queries (rank > 20)
3. Identify patterns in successful queries
4. Tune hybrid weighting (product 40% vs review 60%)
5. Experiment with reranker settings
6. Try different K values (10, 20, 50, 100)


For more details, see the main README.md

