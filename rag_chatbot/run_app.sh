#!/bin/bash
# Quick start script for Laptop RAG Chatbot

echo "======================================"
echo "🧠 Laptop RAG Chatbot"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create .env file with your OpenAI API key"
    echo "   Copy from env.example and edit:"
    echo "   $ cp env.example .env"
    echo ""
    read -p "Press Enter to continue anyway (will fail without API key)..."
fi

echo "🚀 Starting Streamlit app..."
echo "   Opening in browser at http://localhost:8501"
echo ""

streamlit run app.py
