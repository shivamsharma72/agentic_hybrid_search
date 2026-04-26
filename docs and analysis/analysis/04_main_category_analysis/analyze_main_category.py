#!/usr/bin/env python3
"""
Main Category Analysis for Laptop Products
==========================================
Analyzes the 'main_category' field which represents the primary product classification.

Key metrics:
- Distribution of main categories
- Main category vs price
- Main category vs quality
- Main category vs brand
- Comparison with leaf categories
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from collections import Counter

# Database configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

OUTPUT_DIR = "visualizations"
CSV_OUTPUT = "main_category_distribution.csv"

print("=" * 80)
print("📂 MAIN CATEGORY ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/8] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch all products
print("\n[2/8] Fetching products...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        main_category,
        price,
        average_rating,
        rating_number,
        store,
        categories
    FROM products_backup;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products")

# Create dataframe
df = pd.DataFrame(products, columns=[
    'asin', 'title', 'main_category', 'price', 'rating', 'num_reviews', 'store', 'categories'
])

# Analysis 1: Main Category Distribution
print("\n[3/8] Analyzing main category distribution...")

# Handle NULL values
df['main_category'] = df['main_category'].fillna('(Not Specified)')
main_cat_counts = df['main_category'].value_counts()

print(f"\n  📊 Main Category Distribution:")
print(f"  Total unique main categories: {len(main_cat_counts)}")

for i, (category, count) in enumerate(main_cat_counts.items(), 1):
    pct = (count / len(df)) * 100
    bar = '█' * int(pct / 2)
    print(f"     {i}. {category:50s} {count:5,} ({pct:6.2f}%) {bar}")

# Visualization 1: Main category distribution
plt.figure(figsize=(12, 6))
if len(main_cat_counts) <= 15:
    colors = plt.cm.Set3(range(len(main_cat_counts)))
    plt.bar(range(len(main_cat_counts)), main_cat_counts.values, color=colors, edgecolor='black')
    plt.xticks(range(len(main_cat_counts)), main_cat_counts.index, rotation=45, ha='right')
else:
    # Too many categories, show top 15
    top_cats = main_cat_counts.head(15)
    colors = plt.cm.Set3(range(len(top_cats)))
    plt.bar(range(len(top_cats)), top_cats.values, color=colors, edgecolor='black')
    plt.xticks(range(len(top_cats)), top_cats.index, rotation=45, ha='right')

plt.ylabel('Number of Products')
plt.title('Main Category Distribution')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/main_category_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/main_category_distribution.png")

# Analysis 2: Main Category vs Price
print("\n[4/8] Analyzing price by main category...")

df_with_price = df[df['price'].notna()].copy()
price_by_cat = df_with_price.groupby('main_category')['price'].agg(['mean', 'median', 'min', 'max', 'count'])
price_by_cat = price_by_cat.sort_values('mean', ascending=False)

print(f"\n  💰 Price Statistics by Main Category:")
for category, row in price_by_cat.iterrows():
    print(f"     {category:50s} ${row['mean']:7.2f} avg | ${row['median']:7.2f} med | n={int(row['count']):,}")

# Visualization 2: Price by category
if len(price_by_cat) > 0:
    plt.figure(figsize=(12, max(6, len(price_by_cat) * 0.4)))
    colors_price = plt.cm.RdYlGn_r(np.linspace(0, 1, len(price_by_cat)))
    plt.barh(range(len(price_by_cat)), price_by_cat['mean'], color=colors_price)
    plt.yticks(range(len(price_by_cat)), price_by_cat.index)
    plt.xlabel('Average Price ($)')
    plt.title('Average Price by Main Category')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_by_main_category.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/price_by_main_category.png")

# Analysis 3: Main Category vs Quality
print("\n[5/8] Analyzing quality by main category...")

df_with_rating = df[df['rating'].notna()].copy()
rating_by_cat = df_with_rating.groupby('main_category')['rating'].agg(['mean', 'median', 'count'])
rating_by_cat = rating_by_cat.sort_values('mean', ascending=False)

print(f"\n  ⭐ Quality (Rating) by Main Category:")
for category, row in rating_by_cat.iterrows():
    stars = '★' * int(row['mean']) + '☆' * (5 - int(row['mean']))
    print(f"     {category:50s} {row['mean']:.2f} {stars} (n={int(row['count']):,})")

# Visualization 3: Rating by category
if len(rating_by_cat) > 0:
    plt.figure(figsize=(12, max(6, len(rating_by_cat) * 0.4)))
    colors_rating = plt.cm.RdYlGn(rating_by_cat['mean'] / 5.0)
    plt.barh(range(len(rating_by_cat)), rating_by_cat['mean'], color=colors_rating)
    plt.yticks(range(len(rating_by_cat)), rating_by_cat.index)
    plt.xlabel('Average Rating (out of 5)')
    plt.title('Average Rating by Main Category')
    plt.xlim(0, 5.0)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/rating_by_main_category.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/rating_by_main_category.png")

# Analysis 4: Brand distribution by main category
print("\n[6/8] Analyzing top brands by main category...")

print(f"\n  🏪 Top Brands by Main Category:")
for category in main_cat_counts.head(5).index:
    cat_df = df[df['main_category'] == category]
    top_brands = cat_df['store'].value_counts().head(5)
    print(f"\n  {category}:")
    for brand, count in top_brands.items():
        pct = (count / len(cat_df)) * 100
        print(f"     • {brand:30s} {count:4,} ({pct:5.2f}%)")

# Analysis 5: Comparison with leaf categories
print("\n[7/8] Comparing main_category with leaf categories...")

# Extract leaf category from categories array
df['leaf_category'] = df['categories'].apply(lambda x: x[-1] if x and len(x) > 0 else None)

# Find mismatches
mismatches = df[df['main_category'] != df['leaf_category']]
match_rate = (1 - len(mismatches) / len(df)) * 100

print(f"\n  🔍 Main Category vs Leaf Category Alignment:")
print(f"     Match rate: {match_rate:.2f}%")
print(f"     Mismatches: {len(mismatches):,} products")

if len(mismatches) > 0:
    print(f"\n  📋 Top 10 Mismatch Patterns:")
    mismatch_patterns = Counter(zip(mismatches['main_category'], mismatches['leaf_category']))
    for i, ((main, leaf), count) in enumerate(mismatch_patterns.most_common(10), 1):
        print(f"     {i:2d}. Main: '{main}' ≠ Leaf: '{leaf}' ({count} products)")

# Analysis 6: Export CSV
print("\n[8/8] Generating main category CSV...")

# Prepare statistics
category_stats_list = []
for category in main_cat_counts.index:
    cat_products = df[df['main_category'] == category]
    
    stats = {
        'main_category': category,
        'product_count': len(cat_products),
        'market_share_pct': (len(cat_products) / len(df)) * 100,
        'avg_price': cat_products['price'].mean() if cat_products['price'].notna().any() else None,
        'median_price': cat_products['price'].median() if cat_products['price'].notna().any() else None,
        'min_price': cat_products['price'].min() if cat_products['price'].notna().any() else None,
        'max_price': cat_products['price'].max() if cat_products['price'].notna().any() else None,
        'avg_rating': cat_products['rating'].mean() if cat_products['rating'].notna().any() else None,
        'total_reviews': cat_products['num_reviews'].sum() if cat_products['num_reviews'].notna().any() else 0,
        'avg_reviews_per_product': cat_products['num_reviews'].mean() if cat_products['num_reviews'].notna().any() else None,
        'top_brands': ', '.join(cat_products['store'].value_counts().head(3).index.tolist()) if 'store' in cat_products.columns else None
    }
    
    category_stats_list.append(stats)

# Create DataFrame and save
category_df = pd.DataFrame(category_stats_list)
category_df = category_df.sort_values('product_count', ascending=False)
category_df.to_csv(CSV_OUTPUT, index=False)

print(f"  ✅ Saved: {CSV_OUTPUT}")
print(f"  📊 CSV contains {len(category_df):,} unique main categories")

# Save summary JSON
summary = {
    'total_products': len(df),
    'unique_main_categories': len(main_cat_counts),
    'main_category_distribution': main_cat_counts.to_dict(),
    'match_rate_with_leaf_category': float(match_rate),
    'mismatches_count': len(mismatches),
    'avg_price_by_category': price_by_cat['mean'].to_dict() if len(price_by_cat) > 0 else {},
    'avg_rating_by_category': rating_by_cat['mean'].to_dict() if len(rating_by_cat) > 0 else {}
}

with open('main_category_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"  ✅ Saved: main_category_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ MAIN CATEGORY ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/main_category_distribution.png")
print(f"   • {OUTPUT_DIR}/price_by_main_category.png")
print(f"   • {OUTPUT_DIR}/rating_by_main_category.png")
print(f"   • {CSV_OUTPUT} ⭐")
print(f"   • main_category_summary.json")
print("=" * 80)

