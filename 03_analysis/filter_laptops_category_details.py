#!/usr/bin/env python3
"""
Filter Laptops Based on Categories + Details (JSONB)

This script identifies laptops using:
1. Categories field (must contain laptop-related keywords)
2. Details field (JSONB) - must have laptop-specific specs

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

# Category keywords for laptops
CATEGORY_KEYWORDS = [
    'laptop', 'laptops', 'notebook', 'notebooks', 'chromebook', 'chromebooks',
    'ultrabook', 'ultrabooks', 'netbook', 'netbooks', 'macbook', 'macbooks',
    '2-in-1', 'convertible', 'gaming laptop', 'business laptop'
]

# Details keys that indicate laptop specs (JSONB keys)
LAPTOP_SPEC_KEYS = {
    # Direct laptop indicators
    'RAM', 'RAM Memory Installed Size', 'RAM Size', 'System RAM', 'Memory RAM',
    
    # CPU indicators
    'Processor', 'Processor Type', 'Processor Brand', 'Processor Speed', 
    'CPU Model', 'CPU Speed', 'Processor Count', 'Processor Model',
    
    # Screen indicators
    'Screen Size', 'Display Size', 'Display Resolution Maximum', 
    'Screen Resolution', 'Display Type',
    
    # Storage indicators
    'Hard Drive', 'Hard Drive Size', 'Hard Disk Size', 'Flash Memory Size',
    'Hard Drive Interface', 'SSD Capacity',
    
    # Graphics indicators
    'Graphics Card Description', 'Graphics Coprocessor', 'Graphics Card Ram Size',
    'GPU', 'Graphics Card',
    
    # Operating System
    'Operating System', 'OS', 'Software Included',
    
    # Other laptop-specific
    'Battery Life', 'Batteries', 'Number of USB 2.0 Ports', 'Number of USB 3.0 Ports',
    'Wireless Type', 'Connectivity', 'Keyboard Description',
    'Standing screen display size', 'Computer Memory Type'
}


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


def filter_by_category(conn):
    """Filter products that have laptop keywords in categories."""
    print("\n" + "=" * 80)
    print("STEP 1: FILTER BY CATEGORIES")
    print("=" * 80)
    
    # Build ILIKE conditions for categories array
    category_conditions = []
    for keyword in CATEGORY_KEYWORDS:
        # Check if keyword exists in any element of categories array
        category_conditions.append(f"EXISTS (SELECT 1 FROM unnest(categories) AS cat WHERE cat ILIKE '%{keyword}%')")
    
    query = f"""
        SELECT 
            parent_asin,
            title,
            main_category,
            categories,
            details,
            price,
            average_rating,
            rating_number
        FROM products
        WHERE 
            categories IS NOT NULL
            AND ({' OR '.join(category_conditions)});
    """
    
    print(f"\n🔍 Searching for products with laptop-related categories...")
    print(f"   Keywords: {', '.join(CATEGORY_KEYWORDS[:5])}...")
    
    df = pd.read_sql_query(query, conn)
    
    print(f"\n✅ Found {len(df):,} products with laptop-related categories")
    
    return df


def analyze_categories(df):
    """Analyze which category keywords are most common."""
    print("\n" + "=" * 80)
    print("CATEGORY KEYWORD ANALYSIS")
    print("=" * 80)
    
    keyword_counts = Counter()
    
    for categories in df['categories']:
        if categories is None:
            continue
        
        # Convert to string for searching
        cats_str = ' '.join(categories).lower() if isinstance(categories, list) else str(categories).lower()
        
        for keyword in CATEGORY_KEYWORDS:
            if keyword.lower() in cats_str:
                keyword_counts[keyword] += 1
    
    print(f"\n📊 Category Keywords Found:")
    print(f"{'Keyword':<25} {'Count':<10} {'%'}")
    print("─" * 80)
    
    total = len(df)
    for keyword, count in keyword_counts.most_common():
        pct = 100 * count / total
        print(f"{keyword:<25} {count:>8,}  {pct:>5.1f}%")


def filter_by_details(df):
    """Filter products that have laptop specs in details JSONB."""
    print("\n" + "=" * 80)
    print("STEP 2: FILTER BY DETAILS (JSONB)")
    print("=" * 80)
    
    laptops = []
    
    print(f"\n🔍 Checking {len(df):,} products for laptop specs in details...")
    
    for idx, row in df.iterrows():
        details = row['details']
        
        if details is None or not isinstance(details, dict):
            continue
        
        # Check if any laptop spec key exists in details
        found_keys = []
        for key in LAPTOP_SPEC_KEYS:
            if key in details and details[key] is not None:
                found_keys.append(key)
        
        # Require at least 1 laptop spec key
        if len(found_keys) > 0:
            laptops.append({
                'parent_asin': row['parent_asin'],
                'title': row['title'],
                'main_category': row['main_category'],
                'categories': row['categories'],
                'details': row['details'],
                'price': row['price'],
                'average_rating': row['average_rating'],
                'rating_number': row['rating_number'],
                'spec_keys_found': len(found_keys),
                'spec_keys': ', '.join(found_keys[:5])  # First 5 keys
            })
        
        # Progress
        if (idx + 1) % 5000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    laptops_df = pd.DataFrame(laptops)
    
    print(f"\n✅ Found {len(laptops_df):,} products with laptop specs in details")
    print(f"   (Filtered from {len(df):,} category-matched products)")
    print(f"   Success rate: {100 * len(laptops_df) / len(df):.1f}%")
    
    return laptops_df


def analyze_spec_keys(laptops_df):
    """Analyze which spec keys are most common."""
    print("\n" + "=" * 80)
    print("DETAILS SPEC KEYS ANALYSIS")
    print("=" * 80)
    
    key_counts = Counter()
    
    for details in laptops_df['details']:
        if details is None or not isinstance(details, dict):
            continue
        
        for key in details.keys():
            if key in LAPTOP_SPEC_KEYS:
                key_counts[key] += 1
    
    print(f"\n📊 Top 30 Laptop Spec Keys Found:")
    print(f"{'Spec Key':<40} {'Count':<10} {'%'}")
    print("─" * 80)
    
    total = len(laptops_df)
    for i, (key, count) in enumerate(key_counts.most_common(30), 1):
        pct = 100 * count / total
        print(f"{i:>2}. {key:<37} {count:>8,}  {pct:>5.1f}%")


def analyze_spec_combinations(laptops_df):
    """Analyze common combinations of specs."""
    print("\n" + "=" * 80)
    print("SPEC COMBINATION ANALYSIS")
    print("=" * 80)
    
    # Define key spec categories
    spec_categories = {
        'RAM': ['RAM', 'RAM Memory Installed Size', 'RAM Size', 'System RAM', 'Memory RAM', 'Computer Memory Type'],
        'CPU': ['Processor', 'Processor Type', 'Processor Brand', 'Processor Speed', 'CPU Model', 'CPU Speed'],
        'Screen': ['Screen Size', 'Display Size', 'Display Resolution Maximum', 'Standing screen display size'],
        'Storage': ['Hard Drive', 'Hard Drive Size', 'Hard Disk Size', 'Flash Memory Size', 'SSD Capacity'],
        'OS': ['Operating System', 'OS', 'Software Included'],
        'Graphics': ['Graphics Card Description', 'Graphics Coprocessor', 'Graphics Card Ram Size']
    }
    
    # Count products with each spec category
    spec_presence = defaultdict(int)
    spec_combinations = Counter()
    
    for details in laptops_df['details']:
        if details is None or not isinstance(details, dict):
            continue
        
        present_specs = []
        
        for spec_name, spec_keys in spec_categories.items():
            for key in spec_keys:
                if key in details:
                    present_specs.append(spec_name)
                    spec_presence[spec_name] += 1
                    break  # Only count once per category
        
        # Record combination
        if present_specs:
            combo = tuple(sorted(present_specs))
            spec_combinations[combo] += 1
    
    print(f"\n📊 Spec Category Coverage:")
    print(f"{'Category':<15} {'Count':<10} {'%'}")
    print("─" * 80)
    
    total = len(laptops_df)
    for spec, count in sorted(spec_presence.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / total
        print(f"{spec:<15} {count:>8,}  {pct:>5.1f}%")
    
    print(f"\n📊 Top 10 Spec Combinations:")
    print(f"{'Combination':<50} {'Count':<10} {'%'}")
    print("─" * 80)
    
    for combo, count in spec_combinations.most_common(10):
        combo_str = ' + '.join(combo)
        pct = 100 * count / total
        print(f"{combo_str:<50} {count:>8,}  {pct:>5.1f}%")


def show_samples(laptops_df):
    """Show sample laptops with their specs."""
    print("\n" + "=" * 80)
    print("SAMPLE IDENTIFIED LAPTOPS")
    print("=" * 80)
    
    # Show top 5 by spec_keys_found
    samples = laptops_df.nlargest(5, 'spec_keys_found')
    
    for i, (_, row) in enumerate(samples.iterrows(), 1):
        print(f"\n{'─' * 80}")
        print(f"{i}. {row['parent_asin']}")
        print(f"   Title: {row['title'][:70]}...")
        print(f"   Main Category: {row['main_category']}")
        print(f"   Spec Keys Found: {row['spec_keys_found']}")
        print(f"   Price: ${row['price']}")
        print(f"   Rating: {row['average_rating']} ({row['rating_number']:,} reviews)")
        
        # Show some specs
        details = row['details']
        if isinstance(details, dict):
            print(f"   Sample Specs:")
            for key in ['RAM', 'Processor', 'Screen Size', 'Operating System', 'Hard Drive'][:3]:
                if key in details:
                    value = details[key]
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + '...'
                    print(f"      • {key}: {value}")


def compare_with_title_analysis(conn, laptops_df):
    """Compare with previous title-based analysis."""
    print("\n" + "=" * 80)
    print("COMPARISON WITH TITLE ANALYSIS")
    print("=" * 80)
    
    # Get title analysis ASINs
    try:
        title_df = pd.read_csv('/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis/laptop_titles_analysis_asins_only.csv')
        
        category_details_asins = set(laptops_df['parent_asin'])
        title_asins = set(title_df['parent_asin'])
        
        overlap = category_details_asins.intersection(title_asins)
        only_category_details = category_details_asins - title_asins
        only_title = title_asins - category_details_asins
        
        print(f"\n📊 Comparison:")
        print(f"   Category + Details:        {len(category_details_asins):>8,}")
        print(f"   Title Analysis:            {len(title_asins):>8,}")
        print(f"   {'─' * 50}")
        print(f"   Overlap (Both methods):    {len(overlap):>8,} ({100*len(overlap)/len(category_details_asins):.1f}%)")
        print(f"   Only Category + Details:   {len(only_category_details):>8,}")
        print(f"   Only Title:                {len(only_title):>8,}")
        
    except FileNotFoundError:
        print("\n⚠️  Title analysis file not found, skipping comparison")


def export_results(laptops_df):
    """Export results to CSV."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    output_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis/laptops_category_details.csv"
    
    # Export full results
    export_df = laptops_df.copy()
    # Convert details to JSON string for CSV
    export_df['details'] = export_df['details'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else None)
    export_df['categories'] = export_df['categories'].apply(lambda x: json.dumps(x) if isinstance(x, list) else None)
    
    export_df.to_csv(output_path, index=False)
    print(f"\n✅ Exported {len(laptops_df):,} laptops to:")
    print(f"   {output_path}")
    
    # Export just ASINs
    asins_file = output_path.replace('.csv', '_asins_only.csv')
    laptops_df[['parent_asin', 'spec_keys_found']].to_csv(asins_file, index=False)
    print(f"\n✅ Exported ASINs to:")
    print(f"   {asins_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("LAPTOP FILTERING: CATEGORIES + DETAILS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nMethod:")
    print(f"  • Step 1: Filter by categories (laptop keywords)")
    print(f"  • Step 2: Validate with details JSONB (has laptop specs)")
    print(f"  • Requires BOTH conditions")
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Step 1: Filter by categories
        category_df = filter_by_category(conn)
        
        if len(category_df) == 0:
            print("\n⚠️  No products found with laptop categories!")
            return
        
        # Analyze categories
        analyze_categories(category_df)
        
        # Step 2: Filter by details
        laptops_df = filter_by_details(category_df)
        
        if len(laptops_df) == 0:
            print("\n⚠️  No products found with laptop specs in details!")
            return
        
        # Analyze spec keys
        analyze_spec_keys(laptops_df)
        
        # Analyze spec combinations
        analyze_spec_combinations(laptops_df)
        
        # Show samples
        show_samples(laptops_df)
        
        # Compare with title analysis
        compare_with_title_analysis(conn, laptops_df)
        
        # Export results
        export_results(laptops_df)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Products with laptop categories: {len(category_df):,}")
        print(f"Laptops with specs in details:   {len(laptops_df):,}")
        print(f"Success rate: {100 * len(laptops_df) / len(category_df):.1f}%")
        print(f"\nFiles created:")
        print(f"  • laptops_category_details.csv (full details)")
        print(f"  • laptops_category_details_asins_only.csv (just ASINs)")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

