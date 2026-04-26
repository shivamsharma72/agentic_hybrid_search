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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy_key") # Set dummy key to avoid errors if not using OpenAI
# if not OPENAI_API_KEY:
#     print("⚠️  Warning: OPENAI_API_KEY not found in environment.")
#     print("   Please create a .env file with your OpenAI API key.")

# ===========================
# Database Configuration
# ===========================
DB_NAME = "amazon_electronics_rag"
DB_USER = os.getenv("DB_USER", "akshat")  # PostgreSQL username (default: akshat)
DB_PASSWORD = os.getenv("DB_PASSWORD", "2139")  # PostgreSQL password (default: 2139)
DB_HOST = os.getenv("DB_HOST", "localhost")  # Database host
DB_PORT = os.getenv("DB_PORT", "5432")  # Database port

PRODUCTS_TABLE = "products_laptop"  # 5,455 laptop products with embeddings
REVIEWS_TABLE = "reviews_laptop"    # 350,105 laptop reviews with embeddings

# ===========================
# Model Configuration
# ===========================
# OpenAI model for response generation
#RESPONSE_MODEL = "gpt-3.5-turbo"  # Can use "gpt-4" for better quality
RESPONSE_MODEL = "llama3.1"

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
