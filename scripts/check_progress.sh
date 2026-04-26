#!/bin/bash
# Quick progress checker for review loading

echo "=========================================="
echo "REVIEW LOADING PROGRESS"
echo "=========================================="
echo ""

# Check if process is running
if pgrep -f "load_reviews_to_postgres_optimized.py" > /dev/null; then
    echo "✅ Loading script is RUNNING"
else
    echo "⚠️  Loading script is NOT running"
fi

echo ""
echo "Current database status:"
psql -d amazon_electronics_rag -c "
SELECT 
    COUNT(*) as total_reviews,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT parent_asin) as unique_products,
    pg_size_pretty(pg_total_relation_size('reviews')) as table_size
FROM reviews;
"

echo ""
echo "Expected: 37,510,000 reviews"
echo ""

# Show last few lines of log
if [ -f /tmp/review_load.log ]; then
    echo "Last 10 lines of log:"
    echo "----------------------------------------"
    tail -10 /tmp/review_load.log
fi

echo ""
echo "=========================================="
echo "To watch live: tail -f /tmp/review_load.log"
echo "=========================================="

