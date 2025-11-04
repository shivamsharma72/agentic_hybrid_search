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
DB_USER = os.getenv("DB_USER", "postgres")  # PostgreSQL username (default: postgres)
DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # PostgreSQL password (default: empty)
DB_HOST = os.getenv("DB_HOST", "localhost")  # Database host
DB_PORT = os.getenv("DB_PORT", "5432")  # Database port

PRODUCTS_TABLE = "products_laptop"  # 5,455 laptop products with embeddings
REVIEWS_TABLE = "reviews_laptop"    # 350,105 laptop reviews with embeddings

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
