#!/bin/bash
# Run the Streamlit app

cd "$(dirname "$0")"

echo "🚀 Starting Electronics Shopping Assistant..."
echo ""
echo "📱 The app will open in your browser at http://localhost:8501"
echo ""

streamlit run app.py

