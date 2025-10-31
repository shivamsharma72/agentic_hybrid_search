#!/usr/bin/env python3
"""
Analyze Category Paths Frequency Distribution

This script analyzes the categories array field to find:
1. Most common category paths (full hierarchy)
2. Most common individual categories
3. Category depth distribution
4. Top leaf categories vs parent categories

Author: AI Assistant
Date: October 31, 2025
"""

import psycopg2
import pandas as pd
import json
from collections import Counter, defaultdict
from datetime import datetime

# Configuration
DB_NAME = "amazon_electronics_rag"


def connect_db():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user="shivamsharma",
            password="",
            host="localhost",
            port="5432"
        )
        print(f"✅ Connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise


def load_categories(conn):
    """Load all category data from database."""
    print("\n" + "=" * 80)
    print("LOADING CATEGORY DATA")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            categories,
            main_category
        FROM products
        WHERE categories IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\n✅ Loaded {len(df):,} products with categories")
    
    return df


def analyze_category_paths(df):
    """Analyze full category paths (hierarchies)."""
    print("\n" + "=" * 80)
    print("CATEGORY PATH ANALYSIS")
    print("=" * 80)
    
    path_counter = Counter()
    
    print(f"\n🔍 Processing {len(df):,} products...")
    
    for idx, row in df.iterrows():
        categories = row['categories']
        
        if categories is None:
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Create path string
        if isinstance(categories, list) and len(categories) > 0:
            path = " > ".join(categories)
            path_counter[path] += 1
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Found {len(path_counter):,} unique category paths")
    
    return path_counter


def analyze_individual_categories(df):
    """Analyze individual category terms (not full paths)."""
    print("\n" + "=" * 80)
    print("INDIVIDUAL CATEGORY ANALYSIS")
    print("=" * 80)
    
    category_counter = Counter()
    
    print(f"\n🔍 Extracting individual categories...")
    
    for idx, row in df.iterrows():
        categories = row['categories']
        
        if categories is None:
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Count each category individually
        if isinstance(categories, list):
            for category in categories:
                if category and category.strip():
                    category_counter[category.strip()] += 1
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Found {len(category_counter):,} unique individual categories")
    
    return category_counter


def analyze_category_depth(df):
    """Analyze depth of category hierarchies."""
    print("\n" + "=" * 80)
    print("CATEGORY DEPTH ANALYSIS")
    print("=" * 80)
    
    depth_counter = Counter()
    
    for categories in df['categories']:
        if categories is None:
            depth_counter[0] += 1
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Count depth
        if isinstance(categories, list):
            depth_counter[len(categories)] += 1
        else:
            depth_counter[1] += 1
    
    print(f"\n📊 Category Hierarchy Depth Distribution:")
    print(f"{'Depth':<10} {'Count':<12} {'%':<8} {'Bar'}")
    print("─" * 80)
    
    total = sum(depth_counter.values())
    for depth in sorted(depth_counter.keys()):
        count = depth_counter[depth]
        pct = 100 * count / total
        bar = '█' * int(pct / 2)
        print(f"{depth:<10} {count:>10,}  {pct:>6.2f}%  {bar}")


def analyze_leaf_categories(df):
    """Analyze leaf (final) categories in paths."""
    print("\n" + "=" * 80)
    print("LEAF CATEGORY ANALYSIS")
    print("=" * 80)
    
    leaf_counter = Counter()
    
    for categories in df['categories']:
        if categories is None:
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Get last category (leaf)
        if isinstance(categories, list) and len(categories) > 0:
            leaf = categories[-1].strip()
            leaf_counter[leaf] += 1
    
    print(f"\n✅ Found {len(leaf_counter):,} unique leaf categories")
    
    return leaf_counter


def analyze_root_categories(df):
    """Analyze root (first) categories in paths."""
    print("\n" + "=" * 80)
    print("ROOT CATEGORY ANALYSIS")
    print("=" * 80)
    
    root_counter = Counter()
    
    for categories in df['categories']:
        if categories is None:
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Get first category (root)
        if isinstance(categories, list) and len(categories) > 0:
            root = categories[0].strip()
            root_counter[root] += 1
    
    print(f"\n✅ Found {len(root_counter):,} unique root categories")
    
    return root_counter


def display_top_results(counter, title, top_n=50):
    """Display top N results from a counter."""
    print("\n" + "=" * 80)
    print(f"TOP {top_n} {title}")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Count':<12} {'%':<8} {title}")
    print("─" * 80)
    
    total = sum(counter.values())
    
    for i, (item, count) in enumerate(counter.most_common(top_n), 1):
        pct = 100 * count / total
        
        # Truncate long paths
        display_item = item
        if len(display_item) > 100:
            display_item = display_item[:97] + "..."
        
        print(f"{i:<6} {count:>10,}  {pct:>6.2f}%  {display_item}")


def export_results(path_counter, category_counter, leaf_counter, root_counter):
    """Export all results to CSV files."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export full paths
    paths_df = pd.DataFrame([
        {'path': path, 'count': count}
        for path, count in path_counter.most_common()
    ])
    paths_file = f"{base_path}/category_paths_frequency.csv"
    paths_df.to_csv(paths_file, index=False)
    print(f"\n✅ Exported {len(paths_df):,} category paths to:")
    print(f"   {paths_file}")
    
    # Export individual categories
    categories_df = pd.DataFrame([
        {'category': cat, 'count': count}
        for cat, count in category_counter.most_common()
    ])
    categories_file = f"{base_path}/individual_categories_frequency.csv"
    categories_df.to_csv(categories_file, index=False)
    print(f"\n✅ Exported {len(categories_df):,} individual categories to:")
    print(f"   {categories_file}")
    
    # Export leaf categories
    leaf_df = pd.DataFrame([
        {'leaf_category': leaf, 'count': count}
        for leaf, count in leaf_counter.most_common()
    ])
    leaf_file = f"{base_path}/leaf_categories_frequency.csv"
    leaf_df.to_csv(leaf_file, index=False)
    print(f"\n✅ Exported {len(leaf_df):,} leaf categories to:")
    print(f"   {leaf_file}")
    
    # Export root categories
    root_df = pd.DataFrame([
        {'root_category': root, 'count': count}
        for root, count in root_counter.most_common()
    ])
    root_file = f"{base_path}/root_categories_frequency.csv"
    root_df.to_csv(root_file, index=False)
    print(f"\n✅ Exported {len(root_df):,} root categories to:")
    print(f"   {root_file}")


def compare_with_main_category(df):
    """Compare categories array with main_category field."""
    print("\n" + "=" * 80)
    print("COMPARISON: CATEGORIES vs MAIN_CATEGORY")
    print("=" * 80)
    
    main_category_counter = Counter(df['main_category'].dropna())
    
    print(f"\n📊 Main Category Distribution:")
    print(f"{'Main Category':<30} {'Count':<12} {'%'}")
    print("─" * 80)
    
    total = sum(main_category_counter.values())
    for main_cat, count in main_category_counter.most_common(20):
        pct = 100 * count / total
        print(f"{main_cat:<30} {count:>10,}  {pct:>6.2f}%")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("CATEGORY PATH FREQUENCY ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect and load data
        conn = connect_db()
        df = load_categories(conn)
        
        # Analyze category depth
        analyze_category_depth(df)
        
        # Analyze full paths
        path_counter = analyze_category_paths(df)
        
        # Analyze individual categories
        category_counter = analyze_individual_categories(df)
        
        # Analyze leaf categories
        leaf_counter = analyze_leaf_categories(df)
        
        # Analyze root categories
        root_counter = analyze_root_categories(df)
        
        # Display top results
        display_top_results(path_counter, "CATEGORY PATHS", 50)
        display_top_results(category_counter, "INDIVIDUAL CATEGORIES", 50)
        display_top_results(leaf_counter, "LEAF CATEGORIES", 50)
        display_top_results(root_counter, "ROOT CATEGORIES", 30)
        
        # Compare with main_category
        compare_with_main_category(df)
        
        # Export results
        export_results(path_counter, category_counter, leaf_counter, root_counter)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Products analyzed: {len(df):,}")
        print(f"Unique category paths: {len(path_counter):,}")
        print(f"Unique individual categories: {len(category_counter):,}")
        print(f"Unique leaf categories: {len(leaf_counter):,}")
        print(f"Unique root categories: {len(root_counter):,}")
        print(f"\nFiles created:")
        print(f"  • category_paths_frequency.csv")
        print(f"  • individual_categories_frequency.csv")
        print(f"  • leaf_categories_frequency.csv")
        print(f"  • root_categories_frequency.csv")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

