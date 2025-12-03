import psycopg2
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import config

# Load env vars
load_dotenv()

def test_postgres():
    print("-" * 50)
    print("Testing PostgreSQL Connection...")
    print(f"Host: {config.DB_HOST}:{config.DB_PORT}")
    print(f"Database: {config.DB_NAME}")
    print(f"User: {config.DB_USER}")
    # Mask password
    masked_pwd = "*" * len(config.DB_PASSWORD) if config.DB_PASSWORD else "None"
    print(f"Password: {masked_pwd}")
    
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        print("✅ PostgreSQL Connection Successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL Connection Failed: {e}")
        return False

def test_neo4j():
    print("-" * 50)
    print("Testing Neo4j Connection...")
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    print(f"URI: {uri}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password)}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("✅ Neo4j Connection Successful!")
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
        return False

if __name__ == "__main__":
    pg_success = test_postgres()
    neo_success = test_neo4j()
    
    print("-" * 50)
    if pg_success and neo_success:
        print("🎉 All systems go!")
    else:
        print("⚠️  Some connections failed. Please check your credentials.")
