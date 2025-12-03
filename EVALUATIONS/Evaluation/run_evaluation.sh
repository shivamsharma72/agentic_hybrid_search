#!/bin/bash

echo "=========================================="
echo "RAG SYSTEM EVALUATION"
echo "=========================================="
echo ""

# Navigate to evaluation directory
cd "$(dirname "$0")"

# Check if dataset exists
if [ ! -f "gemini_product_queries.csv" ]; then
    echo "❌ Error: gemini_product_queries.csv not found!"
    echo "   Please ensure the dataset file is in this directory"
    exit 1
fi

echo "📊 Dataset: gemini_product_queries.csv"
echo "🎯 Evaluating retrieval performance..."
echo ""

# Check if Python dependencies are installed
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    pip install pandas numpy tqdm psycopg2-binary
    echo ""
fi

# Run evaluation with default parameters
echo "🚀 Starting evaluation (this will take 15-20 minutes)..."
echo ""

python3 evaluate_c4.py \
    --dataset gemini_product_queries.csv \
    --top-k 50 \
    --output-dir evaluation/results

echo ""
echo "=========================================="
echo "✅ EVALUATION COMPLETE!"
echo "=========================================="
echo ""
echo "📄 Results saved to:"
echo "   - evaluation/results/c4_evaluation_results.csv"
echo "   - evaluation/results/c4_evaluation_metrics.json"
echo ""
echo "💡 To run with different parameters:"
echo "   python3 evaluate_c4.py --dataset your_queries.csv --top-k 10"
echo ""

