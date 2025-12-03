# Hybrid RAG System (Blair + Graph)

This repository contains the implementation of a Hybrid RAG system that combines **BLAIR** (Cross-modal retrieval) with a **Knowledge Graph** (Neo4j) and a local **LLM** (Llama 3.1).

## Directory Structure

*   **`data_and_env/`**: Contains database setup scripts.
    *   **`postgres_db/`**: Scripts to set up the PostgreSQL database (product data & embeddings).
    *   **`graph_db/`**: Scripts to set up the Neo4j Knowledge Graph.
*   **`rag/`**: Contains the RAG application code, including the retriever, chatbot, and Llama integration.

## Quick Start

1.  **Database Setup**:
    *   Navigate to `data_and_env/postgres_db` and follow the README to set up Postgres.
    *   Navigate to `data_and_env/graph_db` and follow the README to set up Neo4j.

2.  **RAG System**:
    *   Navigate to `rag/` and follow the README to install dependencies and run the application.

## Requirements

*   **Hardware**: NVIDIA GPU (recommended for local LLM & embeddings).
*   **OS**: Linux.
*   **Software**:
    *   Python 3.8+
    *   PostgreSQL with `pgvector` extension.
    *   Neo4j Database (with APOC plugin).
    *   Ollama (for running Llama 3.1).
