#!/usr/bin/env python3
"""
Export Products from PostgreSQL to Parquet
Exports all 348K filtered Electronics products to a single Parquet file
"""

import psycopg2
import pandas as pd
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Configuration
DB_NAME = "amazon_electronics_rag"
OUTPUT_FILE = Path(__file__).parent / "products_all_columns.parquet"
CHUNK_SIZE = 50000  # Read in chunks to manage memory

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(f"dbname={DB_NAME}")
        print(f"✅ Connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise

def export_products_to_parquet():
    """Export all products to a single Parquet file"""
    
    print("=" * 80)
    print("EXPORT PRODUCTS TO PARQUET")
    print("=" * 80)
    print()
    
    start_time = datetime.now()
    
    # Connect to database
    conn = connect_db()
    
    # Get total count
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products;")
    total_count = cur.fetchone()[0]
    print(f"📊 Total products to export: {total_count:,}")
    print()
    
    # SQL query to export all columns
    # Note: We'll convert special types to formats Parquet can handle
    query = """
    SELECT 
        parent_asin,
        title,
        description,
        features,
        average_rating,
        rating_number,
        price,
        main_category,
        categories,  -- PostgreSQL array
        store,
        details,     -- JSONB -> will convert to JSON string
        images,      -- JSONB -> will convert to JSON string
        videos,      -- JSONB -> will convert to JSON string
        blair_embedding,  -- VECTOR -> will convert to array
        created_at,
        updated_at
    FROM products
    ORDER BY parent_asin;
    """
    
    print("🔄 Reading data from PostgreSQL...")
    
    # Read in chunks and collect
    chunks = []
    offset = 0
    
    while offset < total_count:
        chunk_query = f"""
        SELECT 
            parent_asin,
            title,
            description,
            features,
            average_rating,
            rating_number,
            price,
            main_category,
            categories,
            store,
            details,
            images,
            videos,
            blair_embedding,
            created_at,
            updated_at
        FROM products
        ORDER BY parent_asin
        OFFSET {offset} LIMIT {CHUNK_SIZE};
        """
        
        # Read chunk
        df_chunk = pd.read_sql_query(chunk_query, conn)
        
        if len(df_chunk) == 0:
            break
        
        chunks.append(df_chunk)
        offset += CHUNK_SIZE
        
        print(f"   Read {offset:,} / {total_count:,} products ({offset/total_count*100:.1f}%)")
    
    # Combine all chunks
    print("\n🔗 Combining chunks...")
    df = pd.concat(chunks, ignore_index=True)
    
    print(f"✅ Loaded {len(df):,} products into DataFrame")
    print()
    
    # Process special columns for Parquet compatibility
    print("🔧 Processing special columns...")
    
    # 1. Convert PostgreSQL arrays to Python lists (if not already)
    if 'categories' in df.columns:
        df['categories'] = df['categories'].apply(
            lambda x: x if isinstance(x, list) else (list(x) if x is not None else [])
        )
    
    # 2. Convert JSONB to JSON strings
    for col in ['details', 'images', 'videos']:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if x is not None and not pd.isna(x) else None
            )
    
    # 3. Convert vector(768) to list of floats
    if 'blair_embedding' in df.columns:
        def convert_vector(vec):
            if vec is None or pd.isna(vec):
                return None
            if isinstance(vec, str):
                # Parse string representation: "[0,0,0,...]"
                vec = vec.strip('[]').split(',')
                return [float(v) for v in vec]
            elif isinstance(vec, (list, np.ndarray)):
                return [float(v) for v in vec]
            return None
        
        df['blair_embedding'] = df['blair_embedding'].apply(convert_vector)
    
    # 4. Handle any remaining NaN/None values
    df = df.replace({np.nan: None})
    
    print("✅ Column processing complete")
    print()
    
    # Display DataFrame info
    print("📊 DataFrame Info:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print()
    
    print("Column Details:")
    for col in df.columns:
        non_null = df[col].notna().sum()
        null_count = len(df) - non_null
        print(f"   {col:20} - {non_null:,} non-null, {null_count:,} null")
    print()
    
    # Export to Parquet
    print(f"💾 Exporting to Parquet: {OUTPUT_FILE.name}")
    
    df.to_parquet(
        OUTPUT_FILE,
        engine='pyarrow',
        compression='snappy',  # Good balance of speed and compression
        index=False
    )
    
    # Get file size
    file_size_mb = OUTPUT_FILE.stat().st_size / 1024**2
    
    print(f"✅ Export complete!")
    print()
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("=" * 80)
    print("EXPORT SUMMARY")
    print("=" * 80)
    print(f"Output file: {OUTPUT_FILE}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Total products: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Speed: {len(df)/duration:.0f} products/sec")
    print()
    
    # Verify the file
    print("🔍 Verifying Parquet file...")
    df_verify = pd.read_parquet(OUTPUT_FILE)
    print(f"✅ Verification passed: {len(df_verify):,} products")
    print()
    
    # Sample data
    print("📋 Sample Data (first 3 products):")
    print(df_verify[['parent_asin', 'title', 'main_category', 'average_rating', 'price']].head(3).to_string())
    print()
    
    print("=" * 80)
    print("✅ SUCCESS! Products exported to Parquet")
    print("=" * 80)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    try:
        export_products_to_parquet()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

