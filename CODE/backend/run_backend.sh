#!/bin/bash

echo "🚀 Starting FastAPI Backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if .env exists in dual_ranking_system (now 3 levels up)
if [ ! -f "../../../dual_ranking_system/.env" ]; then
    echo "❌ Error: .env file not found in dual_ranking_system/"
    echo "Please setup dual_ranking_system first"
    exit 1
fi

echo "✅ Found .env configuration"
echo ""

# Install requirements if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "🌐 Starting server on http://localhost:8000"
echo "📖 API docs at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server
python3 main.py

