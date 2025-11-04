"""
Configuration for Laptop RAG Chatbot
Centralized settings for database, models, and search parameters
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===========================
# API Configuration
# ===========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY not found in environment.")
    print("   Please create a .env file with your OpenAI API key.")

# ===========================
# Database Configuration
# ===========================
DB_NAME = "amazon_electronics_rag"
PRODUCTS_TABLE = "products_backup"  # 5,455 laptop products with embeddings
REVIEWS_TABLE = "reviews_backup"    # 350,105 laptop reviews with embeddings

# ===========================
# Model Configuration
# ===========================
# OpenAI model for response generation
RESPONSE_MODEL = "gpt-3.5-turbo"  # Can use "gpt-4" for better quality

# BLAIR-RoBERTa for semantic embeddings
EMBEDDING_MODEL_NAME = "hyp1231/blair-roberta-base"

# ===========================
# Search Configuration
# ===========================
# Maximum number of results to retrieve
MAX_PRODUCTS = 20
MAX_REVIEWS = 50

# Search strategy: "balanced", "product_focused", or "review_focused"
DEFAULT_SEARCH_STRATEGY = "balanced"
