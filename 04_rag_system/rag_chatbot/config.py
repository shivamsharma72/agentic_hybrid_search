"""Configuration for the RAG chatbot"""

import os

# OpenAI API Key (load from environment variable)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Database
DB_NAME = "amazon_electronics_rag"

# Model settings
QUERY_ENHANCER_MODEL = "gpt-3.5-turbo"  # Fast and cheap for query parsing
RESPONSE_GENERATOR_MODEL = "gpt-3.5-turbo"  # Can upgrade to gpt-4 for better responses

# Search settings
MAX_RESULTS = 20
SEARCH_MODE = "semantic"  # Options: "semantic" (vector), "bm25" (keyword), "hybrid" (both)
USE_VECTOR_SEARCH = True  # Semantic search with BLAIR-RoBERTa embeddings (for semantic mode)
EMBEDDING_MODEL_NAME = "hyp1231/blair-roberta-base"

# Set environment variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

