import os
import shutil
import re
import argparse
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../graph_db_env/.env")

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))

# --- CONFIGURATION ---
BATCH_SIZE = 20
# ---------------------

def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

def reset_database(session):
    print("Resetting database...")
    session.run("MATCH (n) DETACH DELETE n")
    print("Database reset complete.")

def copy_csvs_to_import():
    """Copies CSV files from artificial_data to Neo4j import directory."""
    source_dir = os.path.abspath("../python_scripts/artificial_data")
    import_dir = os.path.abspath("../neo4j_home/import")
    
    if not os.path.exists(import_dir):
        print(f" ! Import directory not found: {import_dir}")
        return

    if os.path.exists(source_dir):
        print(f"Copying CSVs from {source_dir} to {import_dir}...")
        for filename in ["reviews.csv", "reviews_sentiment.csv"]:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(import_dir, filename)
            try:
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f" - Copied {filename}")
                else:
                    print(f" ! Source file not found: {src}")
            except Exception as e:
                print(f" ! Failed to copy {filename}: {e}")
    else:
        print(f" ! Source CSV directory not found: {source_dir}")

def run_cypher_with_batch(session, file_path, batch_size):
    """Reads a Cypher file, injects batch size, and executes it."""
    print(f"Reading {file_path}...")
    try:
        with open(file_path, "r") as f:
            query = f.read()
        
        # Inject batch size dynamically
        # Looks for: IN TRANSACTIONS OF <number> ROWS
        new_query = re.sub(
            r"IN TRANSACTIONS OF \d+ ROWS", 
            f"IN TRANSACTIONS OF {batch_size} ROWS", 
            query, 
            flags=re.IGNORECASE
        )
        
        print(f"Executing with batch size {batch_size}...")
        session.run(new_query)
        print(f"✅ Finished {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"❌ Error executing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Batch Import Reviews and Sentiment (Cypher File Based)")
    parser.add_argument(
        "--action",
        type=str,
        choices=["reset", "reviews", "reviews_sentiment", "all"],
        required=True,
        help="Action to perform: 'reset', 'reviews', 'reviews_sentiment', 'all'"
    )
    args = parser.parse_args()

    driver = get_driver()
    try:
        with driver.session() as session:
            if args.action == "reset":
                reset_database(session)
            
            else:
                # Copy CSVs first for any import action
                copy_csvs_to_import()
                
                if args.action == "reviews":
                    run_cypher_with_batch(session, "03_import_reviews.cypher", BATCH_SIZE)
                
                elif args.action == "reviews_sentiment":
                    run_cypher_with_batch(session, "04_import_review_llm.cypher", BATCH_SIZE)
                
                elif args.action == "all":
                    reset_database(session)
                    run_cypher_with_batch(session, "03_import_reviews.cypher", BATCH_SIZE)
                    run_cypher_with_batch(session, "04_import_review_llm.cypher", BATCH_SIZE)
                
            print("\n✅ Action complete!")
            
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
