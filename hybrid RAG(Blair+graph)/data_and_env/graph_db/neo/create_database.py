import argparse
from neo4j import GraphDatabase
import os
import shutil
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))


def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)

def reset_database(session):
    print("WARNING: Starting full database reset (Data + Schema)...")
    
    # 1. Delete all Data (Nodes & Relationships)
    session.run("MATCH (n) DETACH DELETE n")
    print(" - Deleted all nodes and relationships.")
    
    # 2. Drop all Schema (Constraints & Indexes) using APOC
    try:
        session.run("CALL apoc.schema.assert({},{},true)")
        print(" - Dropped all constraints and indexes using APOC.")
    except Exception as e:
        print(f" ! APOC schema reset failed: {e}")
        print(" ! Falling back to manual schema deletion...")
        
        # Fallback: Manual deletion
        constraints = session.run("SHOW CONSTRAINTS")
        for record in constraints:
            name = record["name"]
            try:
                session.run(f"DROP CONSTRAINT `{name}` IF EXISTS")
                print(f" - Dropped constraint: {name}")
            except Exception as e:
                print(f" ! Could not drop constraint {name}: {e}")

        indexes = session.run("SHOW INDEXES")
        for record in indexes:
            name = record["name"]
            if record["type"] == "LOOKUP": continue
            try:
                session.run(f"DROP INDEX `{name}` IF EXISTS")
                print(f" - Dropped index: {name}")
            except Exception as e:
                print(f" ! Could not drop index {name}: {e}")
    
    print("Database reset complete.")

def create_schema(session):
    print("Creating schema (Constraints & Indexes)...")
    try:
        # Product: parent_asin
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.parent_asin IS UNIQUE")
        print(" - Created constraint for Product(parent_asin)")
        
        # User: user_id
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE")
        print(" - Created constraint for User(user_id)")
        
        # Review: review_id
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Review) REQUIRE r.review_id IS UNIQUE")
        print(" - Created constraint for Review(review_id)")
        
        # Brand: name
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE")
        print(" - Created constraint for Brand(name)")
        
        # Performance Optimization: Index for User(review_id)
        # Required for fast lookups in review_llm import
        session.run("CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.review_id)")
        print(" - Created index for User(review_id)")

        # Performance Optimization: Composite Index for Feature(review_id, name)
        # Required for fast MERGE on Feature nodes
        session.run("CREATE INDEX IF NOT EXISTS FOR (f:Feature) ON (f.review_id, f.name)")
        print(" - Created composite index for Feature(review_id, name)")

        # Performance Optimization: Constraint for Sentiment(value)
        # Required for fast lookup of shared Sentiment nodes
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sentiment) REQUIRE s.value IS UNIQUE")
        print(" - Created constraint for Sentiment(value)")
        
    except Exception as e:
        print(f" ! Failed to create schema: {e}")

def load_data_with_progress(session, file_path, query, batch_size=1000, desc="Loading"):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        return

    # Count total lines for progress bar
    try:
        total_rows = sum(1 for _ in open(file_path)) - 1 # Subtract header
    except Exception:
        total_rows = None

    print(f"Processing {file_path}...")
    
    # Read CSV in chunks
    chunks = pd.read_csv(file_path, chunksize=batch_size)
    
    with tqdm(total=total_rows, desc=desc, unit="rows") as pbar:
        for chunk in chunks:
            # Convert chunk to list of dicts
            rows = chunk.to_dict('records')
            
            # Replace NaN with None (Neo4j handles None as null)
            rows = [{k: (v if pd.notna(v) else None) for k, v in row.items()} for row in rows]
            
            try:
                session.run(query, rows=rows)
                pbar.update(len(rows))
            except Exception as e:
                print(f"\n❌ Error executing batch:")
                print(f"Error Details: {e}")
                # Optional: continue or raise
                raise e
    
    print(f"✅ Finished {file_path}")

# Cypher Queries (Adapted to use UNWIND $rows AS row)

QUERY_PRODUCTS = """
UNWIND $rows AS row
// 1. Create Product Node
MERGE (p:Product {parent_asin: row.parent_asin})
SET p.name = row.Brand_Normalized + " " + row.`Model Name`,
    p.embedding = row.blair_embedding,
    p.brand = row.Brand_Normalized,
    p.model = row.`Model Name`

// 2. Create Brand Node and Relationship
WITH p, row
WHERE row.Brand_Normalized IS NOT NULL AND row.Brand_Normalized <> ""
MERGE (b:Brand {name: row.Brand_Normalized})
MERGE (p)-[:MANUFACTURED_BY]->(b);
"""

QUERY_DETAILS = """
UNWIND $rows AS row
MATCH (p:Product {parent_asin: row.parent_asin})

// 1. Price Category
WITH p, row,
     CASE 
        WHEN toFloat(row.price) < 300 THEN 'Cheap'
        WHEN toFloat(row.price) >= 300 AND toFloat(row.price) < 700 THEN 'Budget'
        ELSE 'Expensive'
     END AS price_category
MERGE (pc:PriceCategory {name: price_category})
MERGE (p)-[:HAS_PRICE_CATEGORY]->(pc)

// 2. Rating
WITH p, row
WHERE row.rated IS NOT NULL AND row.rated <> ""
MERGE (r:Rating {value: row.rated})
MERGE (p)-[:IS_RATED]->(r)

// 3. Leaf Category
WITH p, row
WHERE row.Leaf_Category IS NOT NULL AND row.Leaf_Category <> ""
MERGE (c:Category {name: row.Leaf_Category})
MERGE (p)-[:IS_UNDER_THE_CATEGORY]->(c)

// 4. Color
WITH p, row
WHERE row.Color IS NOT NULL AND row.Color <> ""
MERGE (co:Color {name: row.Color})
MERGE (p)-[:IS_OF_COLOR]->(co)

// 5. Chipset Brand
WITH p, row
WHERE row.`Chipset Brand` IS NOT NULL AND row.`Chipset Brand` <> ""
MERGE (cb:ChipsetBrand {name: row.`Chipset Brand`})
MERGE (p)-[:HAS_A_PROCESSOR_OF]->(cb)

// 6. Operating System
WITH p, row
WHERE row.`Operating System` IS NOT NULL AND row.`Operating System` <> ""
MERGE (os:OS {name: row.`Operating System`})
MERGE (p)-[:HAS_OPERATING_SYSTEM]->(os)

// 7. Battery Life
WITH p, row
WHERE row.`Average Battery Life (in hours)` IS NOT NULL AND row.`Average Battery Life (in hours)` <> ""
MERGE (bl:BatteryLife {value: row.`Average Battery Life (in hours)`})
MERGE (p)-[:HAS_BATTERY_LIFE_OF]->(bl)

// 8. RAM Size
WITH p, row
WHERE row.RAM_Size IS NOT NULL AND row.RAM_Size <> ""
MERGE (rs:RAMSize {value: row.RAM_Size})
MERGE (p)-[:HAS_RAM]->(rs)

// 9. RAM Type
WITH p, row
WHERE row.RAM_Type IS NOT NULL AND row.RAM_Type <> ""
MERGE (rt:RAMType {name: row.RAM_Type})
MERGE (p)-[:HAS_A_RAM_TYPE]->(rt)

// 10. Storage Size
WITH p, row
WHERE row.Storage_Size IS NOT NULL AND row.Storage_Size <> ""
MERGE (ss:StorageSize {value: row.Storage_Size})
MERGE (p)-[:HAS_STORAGE_SIZE_OF]->(ss)

// 11. Storage Type
WITH p, row
WHERE row.Storage_Type IS NOT NULL AND row.Storage_Type <> ""
MERGE (st:StorageType {name: row.Storage_Type})
MERGE (p)-[:HAS_TYPE]->(st)

// 12. Screen Category
WITH p, row
WHERE row.Screen_Category IS NOT NULL AND row.Screen_Category <> ""
MERGE (sc:ScreenCategory {name: row.Screen_Category})
MERGE (p)-[:HAS_A_SCREEN_CATEGORY]->(sc)

// 13. Weight Category
WITH p, row
WHERE row.Weight_Category IS NOT NULL AND row.Weight_Category <> ""
MERGE (wc:WeightCategory {name: row.Weight_Category})
MERGE (p)-[:LAPTOP_IS_WEIGHT_CATEGORY]->(wc);
"""

QUERY_REVIEWS = """
UNWIND $rows AS row
WITH row
WHERE
  row.review_id IS NOT NULL AND
  row.parent_asin IS NOT NULL AND
  row.user_id IS NOT NULL

// 1. Match the Product
MATCH (p:Product {parent_asin: row.parent_asin})

// 2. Create/Merge User node and store review_id
MERGE (u:User {user_id: row.user_id})
SET u.review_id = row.review_id

// 3. Connect User to Product
MERGE (u)-[:REVIEWED]->(p)

// 4. Handle Verified Purchase Status
// Create the status node (True or False)
MERGE (vs:VerifiedStatus {value: toBoolean(row.verified_purchase)})

// Connect User to the status node
MERGE (u)-[:verified_purchase]->(vs)
"""

QUERY_REVIEW_LLM = """
UNWIND $rows AS row
WITH row
WHERE row.review_id IS NOT NULL AND row.feature IS NOT NULL AND row.sentiment IS NOT NULL

// 1. Match User who wrote this review (using review_id stored on User)
MATCH (u:User {review_id: row.review_id})

// 2. Create/Merge Review Node
MERGE (r:Review {review_id: row.review_id})
MERGE (u)-[:WROTE]->(r)

// 3. Create Feature Node (Unique per review to capture specific context)
MERGE (f:Feature {name: row.feature, review_id: row.review_id})
MERGE (r)-[:USER_SAID]->(f)

// 4. Create Sentiment Node (Shared nodes: Positive, Negative, Neutral)
MERGE (s:Sentiment {value: row.sentiment})
MERGE (f)-[:HAS_SENTIMENT]->(s)
"""

def main():
    parser = argparse.ArgumentParser(description="Manage Neo4j Graph Database State")
    parser.add_argument(
        "--action", 
        type=str, 
        choices=["reset", "products", "product_relation", "reviews", "review_llm", "all"], 
        required=True,
        help="Action to perform: 'reset', 'products', 'product_relation', 'reviews', 'review_llm', 'all'"
    )
    
    args = parser.parse_args()
    
    # Define file paths
    # Using the same paths as in the original script's copy_csvs_to_import logic, 
    # but we read directly from the source or import dir. 
    # Since we are using python driver, we can read from anywhere.
    # Let's stick to the source_dir used in copy_csvs_to_import for simplicity if it exists,
    # or the import dir.
    
    # Actually, the original script copied to neo4j_home/import. 
    # Since we are running python locally, we can read the files directly from python_scripts/data
    # or wherever they are.
    
    DATA_DIR = os.path.abspath("../python_scripts/data")
    # If using artificial data as per previous context, check if that path is better
    # The original script had: source_dir = os.path.abspath("../python_scripts/data")
    
    # Map actions to (file_name, query, description)
    ACTIONS = {
        "products": ("products.csv", QUERY_PRODUCTS, "Importing Products"),
        "product_relation": ("products_relation.csv", QUERY_DETAILS, "Importing Product Details"),
        "reviews": ("reviews.csv", QUERY_REVIEWS, "Importing Reviews"),
        "review_llm": ("reviews_sentiment.csv", QUERY_REVIEW_LLM, "Importing Review Sentiment")
    }

    driver = get_driver()
    try:
        with driver.session() as session:
            if args.action == "reset":
                reset_database(session)
                create_schema(session)
            elif args.action == "all":
                reset_database(session)
                create_schema(session)
                for key in ["products", "product_relation", "reviews", "review_llm"]:
                    filename, query, desc = ACTIONS[key]
                    file_path = os.path.join(DATA_DIR, filename)
                    load_data_with_progress(session, file_path, query, desc=desc)
            elif args.action in ACTIONS:
                # Always ensure schema exists before loading
                create_schema(session)
                filename, query, desc = ACTIONS[args.action]
                file_path = os.path.join(DATA_DIR, filename)
                load_data_with_progress(session, file_path, query, desc=desc)
            else:
                print(f"Unknown action: {args.action}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()
        print("\nNeo4j Browser is available at: http://localhost:7474")

if __name__ == "__main__":
    main()