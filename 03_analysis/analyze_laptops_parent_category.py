#!/usr/bin/env python3
"""
Analyze Products Under "Laptops" Parent Category

This script analyzes all products that have "Laptops" as a parent category
to understand what subcategories and product types exist.

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


def load_laptop_parent_products(conn):
    """Load all products that have 'Laptops' in their category path."""
    print("\n" + "=" * 80)
    print("LOADING PRODUCTS WITH 'LAPTOPS' PARENT CATEGORY")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            title,
            categories,
            main_category,
            price,
            average_rating,
            rating_number,
            details
        FROM products
        WHERE EXISTS (
            SELECT 1 FROM unnest(categories) AS cat 
            WHERE cat = 'Laptops'
        );
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\n✅ Loaded {len(df):,} products with 'Laptops' parent category")
    
    return df


def extract_category_paths(df):
    """Extract full category paths and subcategories after 'Laptops'."""
    print("\n" + "=" * 80)
    print("EXTRACTING CATEGORY PATHS")
    print("=" * 80)
    
    full_paths = Counter()
    subcategories_after_laptops = Counter()
    leaf_categories = Counter()
    
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
        
        # Full path
        if isinstance(categories, list) and len(categories) > 0:
            path = " > ".join(categories)
            full_paths[path] += 1
            
            # Get leaf category
            leaf = categories[-1].strip()
            leaf_categories[leaf] += 1
            
            # Find subcategories after "Laptops"
            try:
                laptop_idx = categories.index('Laptops')
                if laptop_idx < len(categories) - 1:
                    # Get next category after Laptops
                    next_cat = categories[laptop_idx + 1].strip()
                    subcategories_after_laptops[next_cat] += 1
            except ValueError:
                pass  # 'Laptops' not found
    
    print(f"\n✅ Found:")
    print(f"   {len(full_paths):,} unique full paths")
    print(f"   {len(subcategories_after_laptops):,} unique subcategories after 'Laptops'")
    print(f"   {len(leaf_categories):,} unique leaf categories")
    
    return full_paths, subcategories_after_laptops, leaf_categories


def analyze_laptop_types(df):
    """Analyze different laptop types based on title and categories."""
    print("\n" + "=" * 80)
    print("LAPTOP TYPE ANALYSIS")
    print("=" * 80)
    
    laptop_types = {
        'Traditional Laptops': 0,
        'Gaming Laptops': 0,
        'Chromebooks': 0,
        '2-in-1 Laptops': 0,
        'Business Laptops': 0,
        'Student Laptops': 0,
        'Ultrabooks': 0,
        'MacBooks': 0,
        'Netbooks': 0,
        'Accessories (Cases, Bags)': 0,
        'Other': 0
    }
    
    for idx, row in df.iterrows():
        title = row['title'].lower() if row['title'] else ''
        categories = row['categories']
        
        # Convert categories to string for searching
        cat_str = ''
        if categories is not None:
            if isinstance(categories, str):
                cat_str = categories.lower()
            elif isinstance(categories, list):
                cat_str = ' '.join(categories).lower()
        
        # Classify by category first
        if 'traditional laptops' in cat_str:
            laptop_types['Traditional Laptops'] += 1
        elif 'gaming' in cat_str or 'gaming' in title:
            laptop_types['Gaming Laptops'] += 1
        elif 'chromebook' in cat_str or 'chromebook' in title:
            laptop_types['Chromebooks'] += 1
        elif '2 in 1' in cat_str or '2-in-1' in title or 'convertible' in title:
            laptop_types['2-in-1 Laptops'] += 1
        elif 'business' in title:
            laptop_types['Business Laptops'] += 1
        elif 'student' in title:
            laptop_types['Student Laptops'] += 1
        elif 'ultrabook' in cat_str or 'ultrabook' in title:
            laptop_types['Ultrabooks'] += 1
        elif 'macbook' in title:
            laptop_types['MacBooks'] += 1
        elif 'netbook' in cat_str or 'netbook' in title:
            laptop_types['Netbooks'] += 1
        elif any(word in title for word in ['case', 'bag', 'sleeve', 'backpack', 'stand', 'charger', 'adapter']):
            laptop_types['Accessories (Cases, Bags)'] += 1
        else:
            laptop_types['Other'] += 1
    
    print(f"\n📊 Laptop Type Distribution:")
    print(f"{'Type':<35} {'Count':<10} {'%'}")
    print("─" * 80)
    
    total = sum(laptop_types.values())
    for laptop_type, count in sorted(laptop_types.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / total if total > 0 else 0
        print(f"{laptop_type:<35} {count:>8,}  {pct:>5.1f}%")


def analyze_specs_coverage(df):
    """Analyze how many have specs in details."""
    print("\n" + "=" * 80)
    print("SPECS COVERAGE ANALYSIS")
    print("=" * 80)
    
    has_ram = 0
    has_processor = 0
    has_screen = 0
    has_storage = 0
    has_os = 0
    has_any_spec = 0
    has_all_specs = 0
    
    for details in df['details']:
        if details is None or not isinstance(details, dict):
            continue
        
        ram = details.get('RAM') or details.get('RAM Memory Installed Size')
        processor = details.get('Processor') or details.get('Processor Type')
        screen = details.get('Screen Size') or details.get('Standing screen display size')
        storage = details.get('Hard Drive') or details.get('Hard Disk Size')
        os = details.get('Operating System')
        
        if ram: has_ram += 1
        if processor: has_processor += 1
        if screen: has_screen += 1
        if storage: has_storage += 1
        if os: has_os += 1
        
        if any([ram, processor, screen, storage, os]):
            has_any_spec += 1
        
        if all([ram, processor, screen, storage, os]):
            has_all_specs += 1
    
    total = len(df)
    
    print(f"\n📊 Spec Coverage:")
    print(f"{'Spec Type':<25} {'Count':<10} {'%'}")
    print("─" * 80)
    print(f"{'Has any spec':<25} {has_any_spec:>8,}  {100*has_any_spec/total:>5.1f}%")
    print(f"{'Has all 5 specs':<25} {has_all_specs:>8,}  {100*has_all_specs/total:>5.1f}%")
    print(f"{'─' * 80}")
    print(f"{'RAM':<25} {has_ram:>8,}  {100*has_ram/total:>5.1f}%")
    print(f"{'Processor':<25} {has_processor:>8,}  {100*has_processor/total:>5.1f}%")
    print(f"{'Screen Size':<25} {has_screen:>8,}  {100*has_screen/total:>5.1f}%")
    print(f"{'Storage':<25} {has_storage:>8,}  {100*has_storage/total:>5.1f}%")
    print(f"{'Operating System':<25} {has_os:>8,}  {100*has_os/total:>5.1f}%")


def show_samples(df, subcategories):
    """Show sample products from each subcategory."""
    print("\n" + "=" * 80)
    print("SAMPLE PRODUCTS BY SUBCATEGORY")
    print("=" * 80)
    
    for subcat, count in subcategories.most_common(10):
        print(f"\n{'─' * 80}")
        print(f"Subcategory: {subcat} ({count:,} products)")
        print(f"{'─' * 80}")
        
        # Find products in this subcategory
        samples = []
        for idx, row in df.iterrows():
            categories = row['categories']
            if categories is None:
                continue
            
            if isinstance(categories, str):
                try:
                    categories = json.loads(categories)
                except:
                    categories = [categories]
            
            if isinstance(categories, list) and subcat in categories:
                samples.append(row)
                if len(samples) >= 3:
                    break
        
        # Display samples
        for i, sample in enumerate(samples, 1):
            print(f"\n{i}. ASIN: {sample['parent_asin']}")
            title = sample['title'][:80] + "..." if len(sample['title']) > 80 else sample['title']
            print(f"   Title: {title}")
            print(f"   Price: ${sample['price']}")
            print(f"   Rating: {sample['average_rating']} ({sample['rating_number']:,} reviews)")


def display_top_results(counter, title, top_n=30):
    """Display top N results."""
    print("\n" + "=" * 80)
    print(f"TOP {top_n} {title}")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Count':<12} {'%':<8} {title}")
    print("─" * 80)
    
    total = sum(counter.values())
    
    for i, (item, count) in enumerate(counter.most_common(top_n), 1):
        pct = 100 * count / total
        
        # Truncate long items
        display_item = item
        if len(display_item) > 90:
            display_item = display_item[:87] + "..."
        
        print(f"{i:<6} {count:>10,}  {pct:>6.2f}%  {display_item}")


def export_results(df, full_paths, subcategories, leaf_categories):
    """Export results to CSV."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export products
    products_file = f"{base_path}/laptops_parent_category_products.csv"
    export_df = df.copy()
    export_df['categories'] = export_df['categories'].apply(
        lambda x: json.dumps(x) if isinstance(x, list) else x
    )
    export_df['details'] = export_df['details'].apply(
        lambda x: json.dumps(x) if isinstance(x, dict) else None
    )
    export_df.to_csv(products_file, index=False)
    print(f"\n✅ Exported {len(df):,} products to:")
    print(f"   {products_file}")
    
    # Export subcategories
    subcat_df = pd.DataFrame([
        {'subcategory': cat, 'count': count}
        for cat, count in subcategories.most_common()
    ])
    subcat_file = f"{base_path}/laptops_subcategories.csv"
    subcat_df.to_csv(subcat_file, index=False)
    print(f"\n✅ Exported {len(subcat_df):,} subcategories to:")
    print(f"   {subcat_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("ANALYSIS: PRODUCTS UNDER 'LAPTOPS' PARENT CATEGORY")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect and load data
        conn = connect_db()
        df = load_laptop_parent_products(conn)
        
        # Extract category information
        full_paths, subcategories, leaf_categories = extract_category_paths(df)
        
        # Display results
        display_top_results(full_paths, "CATEGORY PATHS", 30)
        display_top_results(subcategories, "SUBCATEGORIES AFTER 'LAPTOPS'", 20)
        display_top_results(leaf_categories, "LEAF CATEGORIES", 30)
        
        # Analyze laptop types
        analyze_laptop_types(df)
        
        # Analyze specs coverage
        analyze_specs_coverage(df)
        
        # Show samples
        show_samples(df, subcategories)
        
        # Export results
        export_results(df, full_paths, subcategories, leaf_categories)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Products with 'Laptops' parent: {len(df):,}")
        print(f"Unique full paths: {len(full_paths):,}")
        print(f"Unique subcategories: {len(subcategories):,}")
        print(f"Unique leaf categories: {len(leaf_categories):,}")
        print(f"\nFiles created:")
        print(f"  • laptops_parent_category_products.csv")
        print(f"  • laptops_subcategories.csv")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

