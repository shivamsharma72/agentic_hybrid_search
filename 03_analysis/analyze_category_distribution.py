#!/usr/bin/env python3
"""
Complete Category Distribution Analysis

This script analyzes:
1. How many products have categories vs don't have categories
2. Distribution of products across all category nodes
3. Whether categories add up to total products
4. What main_category tells us vs categories array
5. Coverage and overlaps

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


def analyze_coverage(conn):
    """Analyze how many products have categories."""
    print("\n" + "=" * 80)
    print("CATEGORY COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Total products
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products;")
    total_products = cur.fetchone()[0]
    
    # Products with categories
    cur.execute("SELECT COUNT(*) FROM products WHERE categories IS NOT NULL;")
    with_categories = cur.fetchone()[0]
    
    # Products without categories
    without_categories = total_products - with_categories
    
    # Products with main_category
    cur.execute("SELECT COUNT(*) FROM products WHERE main_category IS NOT NULL;")
    with_main_category = cur.fetchone()[0]
    
    # Products with BOTH
    cur.execute("""
        SELECT COUNT(*) FROM products 
        WHERE categories IS NOT NULL AND main_category IS NOT NULL;
    """)
    with_both = cur.fetchone()[0]
    
    # Products with EITHER
    cur.execute("""
        SELECT COUNT(*) FROM products 
        WHERE categories IS NOT NULL OR main_category IS NOT NULL;
    """)
    with_either = cur.fetchone()[0]
    
    # Products with NEITHER
    with_neither = total_products - with_either
    
    print(f"\n📊 Coverage Statistics:")
    print(f"{'Metric':<40} {'Count':<12} {'%'}")
    print("─" * 80)
    print(f"{'Total Products':<40} {total_products:>10,}  {'100.0%':>6}")
    print(f"{'─' * 80}")
    print(f"{'Products WITH categories':<40} {with_categories:>10,}  {100*with_categories/total_products:>5.2f}%")
    print(f"{'Products WITHOUT categories':<40} {without_categories:>10,}  {100*without_categories/total_products:>5.2f}%")
    print(f"{'─' * 80}")
    print(f"{'Products WITH main_category':<40} {with_main_category:>10,}  {100*with_main_category/total_products:>5.2f}%")
    print(f"{'Products WITH categories array':<40} {with_categories:>10,}  {100*with_categories/total_products:>5.2f}%")
    print(f"{'Products WITH BOTH':<40} {with_both:>10,}  {100*with_both/total_products:>5.2f}%")
    print(f"{'Products WITH EITHER':<40} {with_either:>10,}  {100*with_either/total_products:>5.2f}%")
    print(f"{'Products WITH NEITHER':<40} {with_neither:>10,}  {100*with_neither/total_products:>5.2f}%")
    
    cur.close()
    
    return {
        'total': total_products,
        'with_categories': with_categories,
        'without_categories': without_categories,
        'with_main_category': with_main_category,
        'with_both': with_both,
        'with_either': with_either,
        'with_neither': with_neither
    }


def analyze_category_nodes(conn):
    """Analyze distribution across all category nodes."""
    print("\n" + "=" * 80)
    print("CATEGORY NODE DISTRIBUTION")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            categories
        FROM products
        WHERE categories IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Count products per category node
    category_counts = Counter()
    
    print(f"\n🔍 Processing {len(df):,} products with categories...")
    
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
        
        # Count each category node
        if isinstance(categories, list):
            for category in categories:
                if category and category.strip():
                    category_counts[category.strip()] += 1
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Found {len(category_counts):,} unique category nodes")
    
    # Calculate total occurrences
    total_occurrences = sum(category_counts.values())
    
    print(f"\n📊 Total category occurrences: {total_occurrences:,}")
    print(f"   Average categories per product: {total_occurrences / len(df):.2f}")
    
    return category_counts, total_occurrences, len(df)


def analyze_main_category(conn):
    """Analyze main_category distribution."""
    print("\n" + "=" * 80)
    print("MAIN_CATEGORY DISTRIBUTION")
    print("=" * 80)
    
    query = """
        SELECT 
            main_category,
            COUNT(*) as count
        FROM products
        WHERE main_category IS NOT NULL
        GROUP BY main_category
        ORDER BY count DESC;
    """
    
    df = pd.read_sql_query(query, conn)
    
    total = df['count'].sum()
    
    print(f"\n📊 Main Category Distribution:")
    print(f"{'Main Category':<40} {'Count':<12} {'%'}")
    print("─" * 80)
    
    for _, row in df.head(30).iterrows():
        count = row['count']
        main_cat = row['main_category']
        pct = 100 * count / total
        print(f"{main_cat:<40} {count:>10,}  {pct:>5.2f}%")
    
    print(f"\n✅ Total unique main_category values: {len(df)}")
    print(f"   Total products with main_category: {total:,}")
    
    return df


def compare_categories_vs_main(conn):
    """Compare categories array vs main_category."""
    print("\n" + "=" * 80)
    print("CATEGORIES vs MAIN_CATEGORY COMPARISON")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            categories,
            main_category
        FROM products
        WHERE main_category IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    
    print(f"\n🔍 Analyzing {len(df):,} products with main_category...")
    
    # Check if main_category appears in categories array
    main_in_categories = 0
    main_not_in_categories = 0
    categories_more_specific = 0
    
    for idx, row in df.iterrows():
        main_cat = row['main_category']
        categories = row['categories']
        
        if categories is None:
            main_not_in_categories += 1
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Check if main_category is in categories array
        if isinstance(categories, list):
            cat_str = ' '.join(categories).lower()
            if main_cat.lower() in cat_str:
                main_in_categories += 1
                if len(categories) > 1:
                    categories_more_specific += 1
            else:
                main_not_in_categories += 1
    
    total = len(df)
    
    print(f"\n📊 Comparison Results:")
    print(f"{'Metric':<50} {'Count':<12} {'%'}")
    print("─" * 80)
    print(f"{'Main category FOUND in categories array':<50} {main_in_categories:>10,}  {100*main_in_categories/total:>5.2f}%")
    print(f"{'Main category NOT in categories array':<50} {main_not_in_categories:>10,}  {100*main_not_in_categories/total:>5.2f}%")
    print(f"{'Categories array more specific than main':<50} {categories_more_specific:>10,}  {100*categories_more_specific/total:>5.2f}%")


def check_category_math(coverage_stats, category_counts, total_occurrences, products_with_cats):
    """Check if category counts add up correctly."""
    print("\n" + "=" * 80)
    print("CATEGORY MATH VERIFICATION")
    print("=" * 80)
    
    total_products = coverage_stats['total']
    with_cats = coverage_stats['with_categories']
    without_cats = coverage_stats['without_categories']
    
    print(f"\n🔢 Do the numbers add up?")
    print(f"{'─' * 80}")
    
    # Check 1: Products with + without = total
    sum_coverage = with_cats + without_cats
    match1 = "✅" if sum_coverage == total_products else "❌"
    print(f"\n1. Coverage Check:")
    print(f"   With categories: {with_cats:,}")
    print(f"   Without categories: {without_cats:,}")
    print(f"   Sum: {sum_coverage:,}")
    print(f"   Total products: {total_products:,}")
    print(f"   Match: {match1} ({sum_coverage == total_products})")
    
    # Check 2: Average categories per product
    avg_cats = total_occurrences / products_with_cats if products_with_cats > 0 else 0
    print(f"\n2. Category Occurrences:")
    print(f"   Total category occurrences: {total_occurrences:,}")
    print(f"   Products with categories: {products_with_cats:,}")
    print(f"   Average categories per product: {avg_cats:.2f}")
    print(f"   (Expected: 4-5 based on depth analysis)")
    
    # Check 3: Category node distribution
    print(f"\n3. Category Node Distribution:")
    print(f"   Unique category nodes: {len(category_counts):,}")
    print(f"   Most common node: {category_counts.most_common(1)[0][0]}")
    print(f"   Most common count: {category_counts.most_common(1)[0][1]:,}")
    print(f"   Least common count: {category_counts.most_common()[-1][1]:,}")
    
    # Important note
    print(f"\n📝 Important Note:")
    print(f"   Category nodes DON'T add up to total products because:")
    print(f"   • Each product can have MULTIPLE categories (avg {avg_cats:.2f})")
    print(f"   • Category nodes count OCCURRENCES, not unique products")
    print(f"   • Example: A product with 5 categories contributes to 5 different nodes")
    print(f"   • Total occurrences ({total_occurrences:,}) >> Total products ({total_products:,})")


def display_top_category_nodes(category_counts, n=50):
    """Display top N category nodes by product count."""
    print("\n" + "=" * 80)
    print(f"TOP {n} CATEGORY NODES (By Product Count)")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Count':<12} {'%':<8} {'Category Node'}")
    print("─" * 80)
    
    total_occurrences = sum(category_counts.values())
    
    for i, (category, count) in enumerate(category_counts.most_common(n), 1):
        pct = 100 * count / total_occurrences
        
        # Truncate long category names
        display_cat = category
        if len(display_cat) > 60:
            display_cat = display_cat[:57] + "..."
        
        print(f"{i:<6} {count:>10,}  {pct:>6.2f}%  {display_cat}")


def export_results(category_counts, main_category_df, coverage_stats):
    """Export results to CSV."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export category node distribution
    cat_df = pd.DataFrame([
        {'category_node': cat, 'product_count': count}
        for cat, count in category_counts.most_common()
    ])
    cat_file = f"{base_path}/category_node_distribution.csv"
    cat_df.to_csv(cat_file, index=False)
    print(f"\n✅ Exported {len(cat_df):,} category nodes to:")
    print(f"   {cat_file}")
    
    # Export main_category distribution
    main_file = f"{base_path}/main_category_distribution.csv"
    main_category_df.to_csv(main_file, index=False)
    print(f"\n✅ Exported {len(main_category_df):,} main categories to:")
    print(f"   {main_file}")
    
    # Export coverage summary
    coverage_df = pd.DataFrame([coverage_stats])
    coverage_file = f"{base_path}/category_coverage_summary.csv"
    coverage_df.to_csv(coverage_file, index=False)
    print(f"\n✅ Exported coverage summary to:")
    print(f"   {coverage_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("COMPLETE CATEGORY DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Analyze coverage
        coverage_stats = analyze_coverage(conn)
        
        # Analyze category nodes
        category_counts, total_occurrences, products_with_cats = analyze_category_nodes(conn)
        
        # Display top category nodes
        display_top_category_nodes(category_counts, 50)
        
        # Analyze main_category
        main_category_df = analyze_main_category(conn)
        
        # Compare categories vs main_category
        compare_categories_vs_main(conn)
        
        # Check if math adds up
        check_category_math(coverage_stats, category_counts, total_occurrences, products_with_cats)
        
        # Export results
        export_results(category_counts, main_category_df, coverage_stats)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Total products: {coverage_stats['total']:,}")
        print(f"Products with categories: {coverage_stats['with_categories']:,} ({100*coverage_stats['with_categories']/coverage_stats['total']:.2f}%)")
        print(f"Unique category nodes: {len(category_counts):,}")
        print(f"Total category occurrences: {total_occurrences:,}")
        print(f"Average categories per product: {total_occurrences/products_with_cats:.2f}")
        print(f"\nFiles created:")
        print(f"  • category_node_distribution.csv")
        print(f"  • main_category_distribution.csv")
        print(f"  • category_coverage_summary.csv")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

