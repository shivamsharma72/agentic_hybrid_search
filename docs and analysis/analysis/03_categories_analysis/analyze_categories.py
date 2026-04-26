#!/usr/bin/env python3
"""
Categories Analysis for Laptop Products
========================================
Analyzes the 'categories' array column which contains hierarchical category paths.

Key metrics:
- Category hierarchy depth and structure
- Most common category paths
- Leaf categories (most specific)
- Root categories (most general)
- Category co-occurrence
- Product distribution across categories
- Category-price relationships
- Category-quality relationships
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from collections import Counter, defaultdict
from itertools import combinations

# Database configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

OUTPUT_DIR = "visualizations"
CSV_OUTPUT = "category_distribution.csv"

print("=" * 80)
print("📁 CATEGORIES ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/12] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch all products with categories
print("\n[2/12] Fetching products with categories...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        categories,
        main_category,
        price,
        average_rating,
        rating_number,
        store
    FROM products_backup
    WHERE categories IS NOT NULL AND array_length(categories, 1) > 0;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products with category data")

# Parse categories
print("\n[3/12] Parsing category hierarchies...")

all_categories = []
category_paths = []
leaf_categories = Counter()
root_categories = Counter()
depth_distribution = Counter()
products_data = []

for parent_asin, title, categories, main_category, price, rating, num_reviews, store in products:
    if categories and len(categories) > 0:
        # Store full path
        category_path = ' > '.join(categories)
        category_paths.append(category_path)
        
        # Extract root (first) and leaf (last) categories
        root = categories[0]
        leaf = categories[-1]
        
        root_categories[root] += 1
        leaf_categories[leaf] += 1
        depth_distribution[len(categories)] += 1
        
        # Store all categories
        all_categories.extend(categories)
        
        products_data.append({
            'asin': parent_asin,
            'title': title,
            'categories': categories,
            'category_path': category_path,
            'root_category': root,
            'leaf_category': leaf,
            'depth': len(categories),
            'main_category': main_category,
            'price': price,
            'rating': rating,
            'num_reviews': num_reviews,
            'store': store
        })

df = pd.DataFrame(products_data)
all_categories_counter = Counter(all_categories)

print(f"  ✅ Analyzed {len(products_data):,} products")
print(f"  📊 Unique categories found: {len(all_categories_counter):,}")
print(f"  📊 Unique category paths: {len(set(category_paths)):,}")

# Analysis 1: Category Hierarchy Depth
print("\n[4/12] Analyzing category hierarchy depth...")

print(f"\n  📏 Category Depth Distribution:")
for depth in sorted(depth_distribution.keys()):
    count = depth_distribution[depth]
    pct = (count / len(df)) * 100
    bar = '█' * int(pct / 2)
    print(f"     Depth {depth}: {count:5,} products ({pct:5.2f}%) {bar}")

avg_depth = df['depth'].mean()
median_depth = df['depth'].median()
print(f"\n  📊 Average depth: {avg_depth:.2f}")
print(f"  📊 Median depth: {median_depth:.0f}")

# Visualization 1: Depth distribution
plt.figure(figsize=(10, 6))
depths = sorted(depth_distribution.keys())
counts = [depth_distribution[d] for d in depths]
plt.bar(depths, counts, color='steelblue', edgecolor='black')
plt.xlabel('Category Hierarchy Depth')
plt.ylabel('Number of Products')
plt.title('Distribution of Category Hierarchy Depth')
plt.xticks(depths)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/category_depth_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/category_depth_distribution.png")

# Analysis 2: Root Categories
print("\n[5/12] Analyzing root categories...")

print(f"\n  🌳 Top 20 Root Categories:")
for i, (category, count) in enumerate(root_categories.most_common(20), 1):
    pct = (count / len(df)) * 100
    print(f"     {i:2d}. {category:50s} {count:5,} ({pct:5.2f}%)")

# Visualization 2: Top root categories
plt.figure(figsize=(14, 8))
top_roots = root_categories.most_common(15)
roots, counts = zip(*top_roots)
colors = plt.cm.tab20(range(len(roots)))
plt.barh(range(len(roots)), counts, color=colors)
plt.yticks(range(len(roots)), roots)
plt.xlabel('Number of Products')
plt.title('Top 15 Root Categories')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_root_categories.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_root_categories.png")

# Analysis 3: Leaf Categories
print("\n[6/12] Analyzing leaf categories (most specific)...")

print(f"\n  🍃 Top 20 Leaf Categories:")
for i, (category, count) in enumerate(leaf_categories.most_common(20), 1):
    pct = (count / len(df)) * 100
    print(f"     {i:2d}. {category:50s} {count:5,} ({pct:5.2f}%)")

# Visualization 3: Top leaf categories
plt.figure(figsize=(14, 10))
top_leaves = leaf_categories.most_common(20)
leaves, counts = zip(*top_leaves)
colors = plt.cm.viridis(np.linspace(0, 1, len(leaves)))
plt.barh(range(len(leaves)), counts, color=colors)
plt.yticks(range(len(leaves)), leaves, fontsize=9)
plt.xlabel('Number of Products')
plt.title('Top 20 Leaf Categories (Most Specific)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_leaf_categories.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_leaf_categories.png")

# Analysis 4: Most Common Category Paths
print("\n[7/12] Analyzing complete category paths...")

path_counter = Counter(category_paths)
print(f"\n  🛤️  Top 15 Complete Category Paths:")
for i, (path, count) in enumerate(path_counter.most_common(15), 1):
    pct = (count / len(df)) * 100
    # Truncate long paths for display
    display_path = path if len(path) <= 80 else path[:77] + "..."
    print(f"     {i:2d}. {display_path:80s} {count:4,} ({pct:5.2f}%)")

# Analysis 5: Most Frequent Categories (at any level)
print("\n[8/12] Analyzing most frequent categories (all levels)...")

print(f"\n  📊 Top 20 Most Frequent Categories (at any hierarchy level):")
for i, (category, count) in enumerate(all_categories_counter.most_common(20), 1):
    pct = (count / sum(all_categories_counter.values())) * 100
    print(f"     {i:2d}. {category:50s} {count:5,} ({pct:5.2f}%)")

# Visualization 4: Most frequent categories
plt.figure(figsize=(14, 8))
top_all = all_categories_counter.most_common(20)
cats, counts = zip(*top_all)
plt.barh(range(len(cats)), counts, color='coral')
plt.yticks(range(len(cats)), cats, fontsize=9)
plt.xlabel('Frequency (across all hierarchy levels)')
plt.title('Top 20 Most Frequent Categories')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/most_frequent_categories.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/most_frequent_categories.png")

# Analysis 6: Category vs Price
print("\n[9/12] Analyzing category-price relationships...")

# Top leaf categories with price data
df_with_price = df[df['price'].notna()].copy()
leaf_price_stats = df_with_price.groupby('leaf_category')['price'].agg(['mean', 'median', 'count'])
leaf_price_stats = leaf_price_stats[leaf_price_stats['count'] >= 20]  # At least 20 products
leaf_price_stats = leaf_price_stats.sort_values('mean', ascending=False)

print(f"\n  💰 Top 10 Most Expensive Leaf Categories (avg price):")
for category, row in leaf_price_stats.head(10).iterrows():
    print(f"     {category:50s} ${row['mean']:7.2f} (n={int(row['count']):3d})")

print(f"\n  💰 Top 10 Most Affordable Leaf Categories (avg price):")
for category, row in leaf_price_stats.tail(10).iterrows():
    print(f"     {category:50s} ${row['mean']:7.2f} (n={int(row['count']):3d})")

# Visualization 5: Category price comparison
plt.figure(figsize=(14, 8))
top_price_cats = leaf_price_stats.head(15).sort_values('mean', ascending=True)
colors_price = plt.cm.RdYlGn_r(np.linspace(0, 1, len(top_price_cats)))
plt.barh(range(len(top_price_cats)), top_price_cats['mean'], color=colors_price)
plt.yticks(range(len(top_price_cats)), top_price_cats.index, fontsize=9)
plt.xlabel('Average Price ($)')
plt.title('Top 15 Most Expensive Leaf Categories')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/category_price_comparison.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/category_price_comparison.png")

# Analysis 7: Category vs Quality
print("\n[10/12] Analyzing category-quality relationships...")

df_with_rating = df[df['rating'].notna()].copy()
leaf_rating_stats = df_with_rating.groupby('leaf_category')['rating'].agg(['mean', 'median', 'count'])
leaf_rating_stats = leaf_rating_stats[leaf_rating_stats['count'] >= 20]
leaf_rating_stats = leaf_rating_stats.sort_values('mean', ascending=False)

print(f"\n  ⭐ Top 10 Highest Rated Leaf Categories:")
for category, row in leaf_rating_stats.head(10).iterrows():
    stars = '★' * int(row['mean']) + '☆' * (5 - int(row['mean']))
    print(f"     {category:50s} {row['mean']:.2f} {stars} (n={int(row['count']):3d})")

print(f"\n  ⭐ Top 10 Lowest Rated Leaf Categories:")
for category, row in leaf_rating_stats.tail(10).iterrows():
    stars = '★' * int(row['mean']) + '☆' * (5 - int(row['mean']))
    print(f"     {category:50s} {row['mean']:.2f} {stars} (n={int(row['count']):3d})")

# Visualization 6: Category quality comparison
plt.figure(figsize=(14, 8))
top_rating_cats = leaf_rating_stats.head(15).sort_values('mean', ascending=True)
colors_rating = plt.cm.RdYlGn(top_rating_cats['mean'] / 5.0)
plt.barh(range(len(top_rating_cats)), top_rating_cats['mean'], color=colors_rating)
plt.yticks(range(len(top_rating_cats)), top_rating_cats.index, fontsize=9)
plt.xlabel('Average Rating (out of 5)')
plt.title('Top 15 Highest Rated Leaf Categories')
plt.xlim(3.0, 5.0)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/category_quality_comparison.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/category_quality_comparison.png")

# Analysis 8: Category Co-occurrence
print("\n[11/12] Analyzing category co-occurrence patterns...")

# Find categories that frequently appear together in paths
category_pairs = Counter()
for categories in df['categories']:
    if len(categories) >= 2:
        # Get all pairs in the path
        for pair in combinations(categories, 2):
            category_pairs[pair] += 1

print(f"\n  🔗 Top 15 Category Pairs (co-occurrence):")
for i, (pair, count) in enumerate(category_pairs.most_common(15), 1):
    pct = (count / len(df)) * 100
    print(f"     {i:2d}. {pair[0]:40s} + {pair[1]:40s} = {count:4,} ({pct:5.2f}%)")

# Analysis 9: Export CSV
print("\n[12/12] Generating category distribution CSV...")

# Prepare leaf category statistics
leaf_stats_list = []
for leaf_cat in leaf_categories.most_common():
    category_name, product_count = leaf_cat
    
    # Get products in this leaf category
    cat_products = df[df['leaf_category'] == category_name]
    
    stats = {
        'category': category_name,
        'product_count': product_count,
        'market_share_pct': (product_count / len(df)) * 100,
        'avg_price': cat_products['price'].mean() if cat_products['price'].notna().any() else None,
        'median_price': cat_products['price'].median() if cat_products['price'].notna().any() else None,
        'min_price': cat_products['price'].min() if cat_products['price'].notna().any() else None,
        'max_price': cat_products['price'].max() if cat_products['price'].notna().any() else None,
        'avg_rating': cat_products['rating'].mean() if cat_products['rating'].notna().any() else None,
        'total_reviews': cat_products['num_reviews'].sum() if cat_products['num_reviews'].notna().any() else 0,
        'avg_reviews_per_product': cat_products['num_reviews'].mean() if cat_products['num_reviews'].notna().any() else None,
        'top_brands': ', '.join(cat_products['store'].value_counts().head(3).index.tolist()) if 'store' in cat_products.columns else None
    }
    
    leaf_stats_list.append(stats)

# Create DataFrame and save
category_df = pd.DataFrame(leaf_stats_list)
category_df = category_df.sort_values('product_count', ascending=False)
category_df.to_csv(CSV_OUTPUT, index=False)

print(f"  ✅ Saved: {CSV_OUTPUT}")
print(f"  📊 CSV contains {len(category_df):,} unique leaf categories with detailed statistics")

# Preview
print(f"\n  📄 CSV Preview (Top 10 categories):")
print(category_df.head(10)[['category', 'product_count', 'avg_price', 'avg_rating']].to_string(index=False))

# Save summary JSON
summary = {
    'total_products': len(df),
    'unique_categories': len(all_categories_counter),
    'unique_category_paths': len(set(category_paths)),
    'unique_leaf_categories': len(leaf_categories),
    'unique_root_categories': len(root_categories),
    'avg_hierarchy_depth': float(avg_depth),
    'median_hierarchy_depth': int(median_depth),
    'depth_distribution': {str(k): v for k, v in depth_distribution.items()},
    'top_20_root_categories': dict(root_categories.most_common(20)),
    'top_20_leaf_categories': dict(leaf_categories.most_common(20)),
    'top_15_category_paths': dict(path_counter.most_common(15)),
    'top_20_all_categories': dict(all_categories_counter.most_common(20))
}

with open('category_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\n  ✅ Saved: category_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ CATEGORIES ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/category_depth_distribution.png")
print(f"   • {OUTPUT_DIR}/top_root_categories.png")
print(f"   • {OUTPUT_DIR}/top_leaf_categories.png")
print(f"   • {OUTPUT_DIR}/most_frequent_categories.png")
print(f"   • {OUTPUT_DIR}/category_price_comparison.png")
print(f"   • {OUTPUT_DIR}/category_quality_comparison.png")
print(f"   • {CSV_OUTPUT} ⭐ (Detailed category statistics)")
print(f"   • category_summary.json")
print("=" * 80)

