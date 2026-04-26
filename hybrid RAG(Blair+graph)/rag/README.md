# Hybrid RAG System Setup

This folder contains the RAG (Retrieval-Augmented Generation) system, which combines:
1.  **BLAIR**: Cross-modal retrieval (Text + Image embeddings).
2.  **Graph DB**: Knowledge graph for structured filtering and sentiment enrichment.
3.  **Llama 3.1**: Local LLM for natural language response generation.

## Prerequisites

1.  **NVIDIA GPU**: Required for efficient embedding generation and local LLM inference.
2.  **Linux**: Recommended OS.
3.  **Ollama**: For running Llama 3.1 locally.
4.  **Postgres & Neo4j**: Ensure the databases are set up (see `../data_and_env`).

## Setup Instructions

### 1. Install and Run Ollama

The system uses Ollama to run Llama 3.1 locally.

1.  **Install Ollama**:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
2.  **Pull Llama 3.1 Model**:
    ```bash
    ollama pull llama3.1
    ```
3.  **Start Ollama Server**:
    Ensure Ollama is running (usually it starts automatically). You can check with:
    ```bash
    systemctl status ollama
    ```
    Or run it manually:
    ```bash
    ollama serve
    ```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```
*Note: This will install PyTorch with CUDA support (via `sentence-transformers` dependency chain usually, or explicitly).*

### 4. Configure Environment Variables

Create a `.env` file in this directory:

```ini
# Postgres
DB_NAME=laptop_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# OpenAI (Optional, if using OpenAI instead of Ollama)
OPENAI_API_KEY=sk-...
```

### 5. Run the Application

You can run the Streamlit chatbot interface:

```bash
streamlit run app.py
```

Or run the retriever test script:

```bash
python retriever.py
```
