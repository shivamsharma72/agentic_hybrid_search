# Graph Database Setup

This folder contains scripts to set up the Neo4j graph database for the Hybrid RAG system.

## Prerequisites

1.  **Neo4j Database**: You need a running instance of Neo4j (Desktop, Server, or Docker).
    *   Ensure the **APOC plugin** is installed and allowed.
2.  **Python 3.8+**: Required to run the automation scripts.

## Setup Instructions

### 1. Create Virtual Environment

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in this directory with your Neo4j credentials:

```ini
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 4. Run the Import Script

The `python_scripts` folder contains the logic to populate the database.
You can run the main creation script (ensure you are in `data_and_env/graph_db`):

```bash
python python_scripts/create_database.py --action all
```

**Note**: The scripts expect CSV files to be available. If they are not in the default location, you may need to place them in the Neo4j `import` directory manually.
