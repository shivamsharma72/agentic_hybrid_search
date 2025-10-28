#!/usr/bin/env python3
"""
Verify Review Data - Parquet Files and PostgreSQL
Verifies data integrity before and after loading
"""

import os
import sys
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

# Database connection (optional)
try:
    import psycopg2
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️  psycopg2 not installed - skipping database verification")

# Configuration
PARQUET_DIR = Path(__file__).parent.parent / "data" / "processed" / "reviews_Electronics"
DB_NAME = "amazon_electronics_rag"
EXPECTED_FILES = 10
EXPECTED_TOTAL_ROWS = 37_510_000
EXPECTED_COLUMNS = ['user_id', 'asin', 'parent_asin', 'rating', 'title', 
                    'text', 'timestamp', 'helpful_vote', 'verified_purchase']

def verify_parquet_files():
    """Verify Parquet files exist and have correct schema"""
    print("=" * 80)
    print("PARQUET FILE VERIFICATION")
    print("=" * 80)
    print()
    
    if not PARQUET_DIR.exists():
        print(f"❌ Directory not found: {PARQUET_DIR}")
        print(f"   Please download Parquet files and place them in this directory")
        return False
    
    # Find all parquet files
    parquet_files = sorted(PARQUET_DIR.glob("reviews_Electronics_part_*.parquet"))
    
    if len(parquet_files) == 0:
        print(f"❌ No Parquet files found in {PARQUET_DIR}")
        print(f"   Expected: reviews_Electronics_part_0.parquet through part_9.parquet")
        return False
    
    print(f"Found {len(parquet_files)} Parquet files")
    print()
    
    total_rows = 0
    schema_issues = []
    
    for i, file_path in enumerate(parquet_files):
        print(f"File {i+1}/{len(parquet_files)}: {file_path.name}")
        
        try:
            # Read metadata only (fast)
            parquet_file = pq.ParquetFile(file_path)
            num_rows = parquet_file.metadata.num_rows
            schema = parquet_file.schema.names
            
            # Read a small sample to check data
            df_sample = pd.read_parquet(file_path, columns=EXPECTED_COLUMNS[:3])
            sample_rows = len(df_sample)
            
            print(f"  Rows: {num_rows:,}")
            print(f"  Columns: {len(schema)}")
            print(f"  Size: {file_path.stat().st_size / 1024**3:.2f} GB")
            
            # Verify schema
            missing_cols = set(EXPECTED_COLUMNS) - set(schema)
            extra_cols = set(schema) - set(EXPECTED_COLUMNS)
            
            if missing_cols:
                schema_issues.append(f"{file_path.name}: Missing columns {missing_cols}")
                print(f"  ⚠️  Missing columns: {missing_cols}")
            
            if extra_cols:
                print(f"  ℹ️  Extra columns: {extra_cols}")
            
            if not missing_cols:
                print(f"  ✅ Schema valid")
            
            total_rows += num_rows
            print()
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            schema_issues.append(f"{file_path.name}: {e}")
            print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if len(parquet_files) == EXPECTED_FILES:
        print(f"✅ File count: {len(parquet_files)} (expected {EXPECTED_FILES})")
    else:
        print(f"⚠️  File count: {len(parquet_files)} (expected {EXPECTED_FILES})")
    
    if total_rows == EXPECTED_TOTAL_ROWS:
        print(f"✅ Total rows: {total_rows:,} (expected {EXPECTED_TOTAL_ROWS:,})")
    else:
        print(f"⚠️  Total rows: {total_rows:,} (expected {EXPECTED_TOTAL_ROWS:,})")
    
    if schema_issues:
        print(f"❌ Schema issues found:")
        for issue in schema_issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ All schemas valid")
    
    print()
    print("✅ Parquet files ready for loading")
    print("=" * 80)
    return True

def verify_database():
    """Verify data loaded in PostgreSQL"""
    if not DB_AVAILABLE:
        print("\n⚠️  Skipping database verification (psycopg2 not installed)")
        return
    
    print()
    print("=" * 80)
    print("DATABASE VERIFICATION")
    print("=" * 80)
    print()
    
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME}")
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'reviews'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("⚠️  Table 'reviews' does not exist yet")
            print("   Run: psql -d amazon_electronics_rag -f schema/reviews_table.sql")
            return
        
        # Get row count
        cur.execute("SELECT COUNT(*) FROM reviews;")
        row_count = cur.fetchone()[0]
        print(f"Total reviews in database: {row_count:,}")
        
        if row_count == 0:
            print("⚠️  No data loaded yet")
            print("   Run: python3 scripts/load_reviews_to_postgres_optimized.py")
            return
        
        # Get statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT parent_asin) as unique_products,
                COUNT(DISTINCT asin) as unique_asins,
                MIN(rating) as min_rating,
                MAX(rating) as max_rating,
                ROUND(AVG(rating)::numeric, 2) as avg_rating,
                COUNT(*) FILTER (WHERE verified_purchase = TRUE) as verified,
                COUNT(*) FILTER (WHERE text IS NULL) as null_text
            FROM reviews;
        """)
        
        stats = cur.fetchone()
        total, unique_users, unique_products, unique_asins, min_rating, max_rating, avg_rating, verified, null_text = stats
        
        print(f"\nStatistics:")
        print(f"  Total reviews: {total:,}")
        print(f"  Unique users: {unique_users:,}")
        print(f"  Unique products: {unique_products:,}")
        print(f"  Unique ASINs: {unique_asins:,}")
        print(f"  Rating range: {min_rating} - {max_rating}")
        print(f"  Average rating: {avg_rating}")
        print(f"  Verified purchases: {verified:,} ({verified/total*100:.1f}%)")
        print(f"  NULL text values: {null_text:,}")
        
        # Check indexes
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE tablename = 'reviews';
        """)
        index_count = cur.fetchone()[0]
        print(f"\nIndexes: {index_count}")
        
        if index_count < 9:
            print("  ⚠️  Expected 9 indexes (including primary key)")
        else:
            print("  ✅ All indexes present")
        
        # Check foreign key
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_constraint 
            WHERE conrelid = 'reviews'::regclass AND contype = 'f';
        """)
        fk_count = cur.fetchone()[0]
        
        if fk_count == 0:
            print("  ⚠️  Foreign key constraint not present")
        else:
            print("  ✅ Foreign key constraint present")
        
        # Validation
        print("\nValidation:")
        
        if total == EXPECTED_TOTAL_ROWS:
            print(f"  ✅ Row count matches expected ({EXPECTED_TOTAL_ROWS:,})")
        else:
            print(f"  ⚠️  Row count: {total:,} (expected {EXPECTED_TOTAL_ROWS:,})")
        
        if min_rating >= 0 and max_rating <= 5:
            print(f"  ✅ Rating range valid (0-5)")
        else:
            print(f"  ❌ Invalid rating range: {min_rating} - {max_rating}")
        
        if null_text == 0:
            print(f"  ✅ No NULL text values")
        else:
            print(f"  ⚠️  Found {null_text:,} NULL text values")
        
        print()
        print("=" * 80)
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        print(f"   Make sure PostgreSQL is running and database exists")
        print(f"   Create database: createdb {DB_NAME}")

def main():
    """Main verification"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "REVIEW DATA VERIFICATION" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Check command line args
    check_db = '--check-database' in sys.argv or '--db' in sys.argv
    
    # Verify Parquet files
    parquet_ok = verify_parquet_files()
    
    # Verify database if requested
    if check_db or (parquet_ok and DB_AVAILABLE):
        verify_database()
    
    print()
    if parquet_ok:
        print("✅ Verification complete - ready to load!")
    else:
        print("❌ Verification failed - fix issues before loading")
        sys.exit(1)

if __name__ == "__main__":
    main()

