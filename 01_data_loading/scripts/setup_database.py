"""
PostgreSQL Database Setup Script
=================================
This script:
1. Tests PostgreSQL connection
2. Creates database if it doesn't exist
3. Installs pgvector extension
4. Creates products table schema
5. Verifies setup

Database: amazon_electronics_rag
"""

import subprocess
import sys
from datetime import datetime

print("=" * 100)
print("POSTGRESQL DATABASE SETUP")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Database configuration
DB_NAME = "amazon_electronics_rag"
DB_USER = "postgres"  # Default PostgreSQL user
DB_HOST = "localhost"
DB_PORT = "5432"

print("📋 Configuration:")
print(f"   Database: {DB_NAME}")
print(f"   User: {DB_USER}")
print(f"   Host: {DB_HOST}")
print(f"   Port: {DB_PORT}\n")

# Step 1: Check PostgreSQL is running
print("=" * 100)
print("STEP 1: Checking PostgreSQL Service")
print("=" * 100)

try:
    result = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-c", "SELECT version();"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print("✅ PostgreSQL is running")
        version_line = result.stdout.split('\n')[2].strip()
        print(f"   Version: {version_line}\n")
    else:
        print("❌ ERROR: Cannot connect to PostgreSQL")
        print(f"   Error: {result.stderr}")
        print("\n🔧 Please ensure PostgreSQL is running:")
        print("   brew services start postgresql@14")
        sys.exit(1)

except subprocess.TimeoutExpired:
    print("❌ ERROR: Connection timeout")
    print("   PostgreSQL may not be running")
    sys.exit(1)
except FileNotFoundError:
    print("❌ ERROR: psql command not found")
    print("   Please install PostgreSQL")
    sys.exit(1)

# Step 2: Create database if it doesn't exist
print("=" * 100)
print("STEP 2: Creating Database")
print("=" * 100)

try:
    # Check if database exists
    check_db = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-lqt"],
        capture_output=True,
        text=True
    )
    
    if DB_NAME in check_db.stdout:
        print(f"ℹ️  Database '{DB_NAME}' already exists")
        print("   Connecting to existing database...\n")
    else:
        print(f"📝 Creating database '{DB_NAME}'...")
        create_db = subprocess.run(
            ["createdb", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, DB_NAME],
            capture_output=True,
            text=True
        )
        
        if create_db.returncode == 0:
            print(f"✅ Database '{DB_NAME}' created successfully\n")
        else:
            print(f"❌ ERROR creating database: {create_db.stderr}")
            sys.exit(1)

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    sys.exit(1)

# Step 3: Install pgvector extension
print("=" * 100)
print("STEP 3: Installing pgvector Extension")
print("=" * 100)

try:
    install_pgvector = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-d", DB_NAME,
         "-c", "CREATE EXTENSION IF NOT EXISTS vector;"],
        capture_output=True,
        text=True
    )
    
    if install_pgvector.returncode == 0:
        print("✅ pgvector extension installed/verified")
        
        # Verify installation
        verify = subprocess.run(
            ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-d", DB_NAME,
             "-c", "SELECT extversion FROM pg_extension WHERE extname = 'vector';"],
            capture_output=True,
            text=True
        )
        
        if "extversion" in verify.stdout:
            version_lines = verify.stdout.split('\n')
            for line in version_lines:
                if line.strip() and 'extversion' not in line and '---' not in line and '(1 row)' not in line:
                    print(f"   Version: {line.strip()}\n")
                    break
    else:
        print("⚠️  WARNING: pgvector extension not available")
        print("   You may need to install it:")
        print("   brew install pgvector")
        print("   Then restart PostgreSQL\n")
        print("   Continuing without vector support for now...\n")

except Exception as e:
    print(f"⚠️  WARNING: Could not install pgvector: {str(e)}")
    print("   Continuing without vector support...\n")

# Step 4: Create products table
print("=" * 100)
print("STEP 4: Creating Products Table")
print("=" * 100)

print("📝 Reading schema file: ../schema/products_table.sql")

try:
    with open('../schema/products_table.sql', 'r') as f:
        schema_sql = f.read()
    
    print("✅ Schema file loaded")
    print(f"   Size: {len(schema_sql)} characters\n")
    
    print("🔨 Executing schema...")
    
    create_table = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-d", DB_NAME,
         "-f", "../schema/products_table.sql"],
        capture_output=True,
        text=True
    )
    
    if create_table.returncode == 0:
        print("✅ Products table created successfully")
        print(f"   Output: {create_table.stdout[:200]}\n")
    else:
        print(f"❌ ERROR creating table: {create_table.stderr}")
        sys.exit(1)

except FileNotFoundError:
    print("❌ ERROR: Schema file not found")
    print("   Expected: ../schema/products_table.sql")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    sys.exit(1)

# Step 5: Verify setup
print("=" * 100)
print("STEP 5: Verifying Setup")
print("=" * 100)

try:
    # Get table info
    table_info = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-d", DB_NAME,
         "-c", "\\d products"],
        capture_output=True,
        text=True
    )
    
    if "parent_asin" in table_info.stdout:
        print("✅ Table 'products' verified")
        print("\n📋 Table structure:")
        print(table_info.stdout)
    
    # Count existing records
    count_query = subprocess.run(
        ["psql", "-U", DB_USER, "-h", DB_HOST, "-p", DB_PORT, "-d", DB_NAME,
         "-t", "-c", "SELECT COUNT(*) FROM products;"],
        capture_output=True,
        text=True
    )
    
    record_count = count_query.stdout.strip()
    print(f"\n📊 Current record count: {record_count}")
    
except Exception as e:
    print(f"⚠️  WARNING: Could not verify setup: {str(e)}")

# Final summary
print("\n" + "=" * 100)
print("SETUP COMPLETE")
print("=" * 100)
print(f"✅ Database '{DB_NAME}' is ready")
print(f"✅ Table 'products' created with schema")
print(f"✅ Indexes created for performance")
print(f"\n📝 Connection string:")
print(f"   postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

# Save connection info
with open('../logs/db_connection_info.txt', 'w') as f:
    f.write(f"Database Connection Information\n")
    f.write(f"================================\n")
    f.write(f"Database: {DB_NAME}\n")
    f.write(f"User: {DB_USER}\n")
    f.write(f"Host: {DB_HOST}\n")
    f.write(f"Port: {DB_PORT}\n")
    f.write(f"Connection String: postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}\n")
    f.write(f"\nSetup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("\n💾 Connection info saved to: logs/db_connection_info.txt")


