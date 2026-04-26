#!/usr/bin/env python3
"""
Store/Brand Analysis for Laptop Products
========================================
Analyzes the 'store' column which represents brands and vendors.

Key metrics:
- Brand distribution (market share)
- Brand vs price positioning (budget/premium brands)
- Brand vs quality (average ratings)
- Brand vs popularity (review counts)
- Brand specialization vs diversification
- Top brands by bestseller presence
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from collections import Counter, defaultdict

# Database configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

OUTPUT_DIR = "visualizations"
CSV_OUTPUT = "store_distribution.csv"

print("=" * 80)
print("🏪 STORE/BRAND ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/10] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch all products
print("\n[2/10] Fetching all laptop products...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        store,
        price,
        average_rating,
        rating_number,
        main_category,
        categories
    FROM products_backup
    WHERE store IS NOT NULL;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products with store data")

# Create dataframe
df = pd.DataFrame(products, columns=[
    'asin', 'title', 'store', 'price', 'rating', 'num_reviews', 'main_category', 'categories'
])

# Analysis 1: Store Distribution
print("\n[3/10] Analyzing store distribution...")

store_counts = df['store'].value_counts()
total_products = len(df)

print(f"\n  🏪 Total Unique Stores/Brands: {len(store_counts):,}")
print(f"  📦 Total Products: {total_products:,}")
print(f"\n  🏆 Top 20 Stores by Product Count:")

for i, (store, count) in enumerate(store_counts.head(20).items(), 1):
    pct = (count / total_products) * 100
    print(f"     {i:2d}. {store:35s} {count:5,} products ({pct:5.2f}%)")

# Visualization 1: Top stores
plt.figure(figsize=(14, 8))
top_stores = store_counts.head(20)
colors = plt.cm.viridis(np.linspace(0, 1, len(top_stores)))
plt.barh(range(len(top_stores)), top_stores.values, color=colors)
plt.yticks(range(len(top_stores)), top_stores.index)
plt.xlabel('Number of Products')
plt.title('Top 20 Stores/Brands by Product Count')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_stores_by_count.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/top_stores_by_count.png")

# Analysis 2: Store Concentration
print("\n[4/10] Analyzing market concentration...")

# Calculate cumulative market share
store_counts_sorted = store_counts.sort_values(ascending=False)
cumulative_pct = (store_counts_sorted.cumsum() / total_products * 100)

# Find concentration metrics
top_10_share = cumulative_pct.iloc[:10].iloc[-1]
top_20_share = cumulative_pct.iloc[:20].iloc[-1]
top_50_share = cumulative_pct.iloc[:50].iloc[-1] if len(cumulative_pct) >= 50 else 100
top_100_share = cumulative_pct.iloc[:100].iloc[-1] if len(cumulative_pct) >= 100 else 100

print(f"\n  📊 Market Concentration:")
print(f"     Top 10 stores control:  {top_10_share:5.2f}% of products")
print(f"     Top 20 stores control:  {top_20_share:5.2f}% of products")
print(f"     Top 50 stores control:  {top_50_share:5.2f}% of products")
print(f"     Top 100 stores control: {top_100_share:5.2f}% of products")

# Visualization 2: Cumulative market share
plt.figure(figsize=(12, 6))
plt.plot(range(1, min(101, len(cumulative_pct)+1)), cumulative_pct.iloc[:100], linewidth=2, color='blue')
plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% Market Share')
plt.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='80% Market Share')
plt.xlabel('Number of Top Stores')
plt.ylabel('Cumulative Market Share (%)')
plt.title('Cumulative Market Share by Top Stores')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/market_concentration.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/market_concentration.png")

# Analysis 3: Brand vs Price
print("\n[5/10] Analyzing brand pricing strategies...")

# Calculate average price per brand (top 20 brands)
top_20_brands = store_counts.head(20).index
df_top_brands = df[df['store'].isin(top_20_brands) & df['price'].notna()].copy()

brand_price_stats = df_top_brands.groupby('store')['price'].agg(['mean', 'median', 'min', 'max', 'count'])
brand_price_stats = brand_price_stats.sort_values('mean', ascending=False)

print(f"\n  💰 Top 20 Brands - Price Positioning:")
print(f"  {'Brand':<35s} {'Avg Price':>10s} {'Median':>10s} {'Products':>10s}")
print("  " + "-" * 68)
for brand, row in brand_price_stats.head(20).iterrows():
    print(f"  {brand:<35s} ${row['mean']:>9.2f} ${row['median']:>9.2f} {int(row['count']):>10,}")

# Categorize brands by price positioning
brand_price_stats['price_tier'] = pd.cut(
    brand_price_stats['mean'],
    bins=[0, 400, 700, 1000, 1500, float('inf')],
    labels=['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']
)

print(f"\n  🎯 Brand Price Positioning (Top 20):")
for tier in ['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']:
    tier_brands = brand_price_stats[brand_price_stats['price_tier'] == tier]
    if len(tier_brands) > 0:
        print(f"     {tier:25s} {len(tier_brands):2d} brands: {', '.join(tier_brands.index.tolist())}")

# Visualization 3: Brand vs Average Price
plt.figure(figsize=(14, 8))
brand_price_sorted = brand_price_stats.sort_values('mean', ascending=True)
colors_price = ['green' if x < 400 else 'blue' if x < 700 else 'orange' if x < 1000 else 'red' if x < 1500 else 'purple' 
                for x in brand_price_sorted['mean']]
plt.barh(range(len(brand_price_sorted)), brand_price_sorted['mean'], color=colors_price)
plt.yticks(range(len(brand_price_sorted)), brand_price_sorted.index)
plt.xlabel('Average Price ($)')
plt.title('Average Price by Brand (Top 20 Brands)')
plt.axvline(x=400, color='green', linestyle='--', alpha=0.5, label='Budget threshold')
plt.axvline(x=700, color='blue', linestyle='--', alpha=0.5, label='Mid-range threshold')
plt.axvline(x=1000, color='orange', linestyle='--', alpha=0.5, label='Upper-mid threshold')
plt.legend()
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/brand_price_positioning.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/brand_price_positioning.png")

# Analysis 4: Brand vs Quality (Rating)
print("\n[6/10] Analyzing brand quality (ratings)...")

df_with_rating = df[df['store'].isin(top_20_brands) & df['rating'].notna()].copy()
brand_rating_stats = df_with_rating.groupby('store')['rating'].agg(['mean', 'median', 'count'])
brand_rating_stats = brand_rating_stats.sort_values('mean', ascending=False)

print(f"\n  ⭐ Top 20 Brands - Quality Rankings:")
print(f"  {'Brand':<35s} {'Avg Rating':>12s} {'Products':>10s}")
print("  " + "-" * 58)
for brand, row in brand_rating_stats.head(20).iterrows():
    stars = '★' * int(row['mean']) + '☆' * (5 - int(row['mean']))
    print(f"  {brand:<35s} {row['mean']:>6.2f} {stars:>5s} {int(row['count']):>10,}")

# Visualization 4: Brand vs Rating
plt.figure(figsize=(14, 8))
brand_rating_sorted = brand_rating_stats.sort_values('mean', ascending=True)
colors_rating = plt.cm.RdYlGn(brand_rating_sorted['mean'] / 5.0)
plt.barh(range(len(brand_rating_sorted)), brand_rating_sorted['mean'], color=colors_rating)
plt.yticks(range(len(brand_rating_sorted)), brand_rating_sorted.index)
plt.xlabel('Average Rating (out of 5)')
plt.title('Average Rating by Brand (Top 20 Brands)')
plt.xlim(3.0, 5.0)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/brand_quality_ratings.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/brand_quality_ratings.png")

# Analysis 5: Brand vs Popularity (Review Count)
print("\n[7/10] Analyzing brand popularity (review counts)...")

df_with_reviews = df[df['store'].isin(top_20_brands) & df['num_reviews'].notna()].copy()
brand_review_stats = df_with_reviews.groupby('store')['num_reviews'].agg(['sum', 'mean', 'median', 'count'])
brand_review_stats = brand_review_stats.sort_values('sum', ascending=False)

print(f"\n  💬 Top 20 Brands - Popularity (Total Reviews):")
print(f"  {'Brand':<35s} {'Total Reviews':>14s} {'Avg/Product':>12s}")
print("  " + "-" * 62)
for brand, row in brand_review_stats.head(20).iterrows():
    print(f"  {brand:<35s} {int(row['sum']):>14,} {row['mean']:>12.1f}")

# Visualization 5: Brand vs Total Reviews
plt.figure(figsize=(14, 8))
top_review_brands = brand_review_stats.head(20).sort_values('sum', ascending=True)
plt.barh(range(len(top_review_brands)), top_review_brands['sum'], color='teal')
plt.yticks(range(len(top_review_brands)), top_review_brands.index)
plt.xlabel('Total Reviews')
plt.title('Total Reviews by Brand (Top 20 Brands)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/brand_popularity_reviews.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/brand_popularity_reviews.png")

# Analysis 6: Price vs Quality Matrix
print("\n[8/10] Creating price-quality matrix...")

# Merge price and rating data for top brands
price_quality_df = df_top_brands.groupby('store').agg({
    'price': 'mean',
    'rating': 'mean',
    'num_reviews': 'sum'
}).dropna()

# Categorize brands
price_quality_df['price_category'] = pd.cut(
    price_quality_df['price'],
    bins=[0, 700, 1200, float('inf')],
    labels=['Budget', 'Mid-Range', 'Premium']
)

price_quality_df['quality_category'] = pd.cut(
    price_quality_df['rating'],
    bins=[0, 4.0, 4.3, 5.0],
    labels=['Standard', 'Good', 'Excellent']
)

print(f"\n  🎯 Price-Quality Matrix:")
matrix = pd.crosstab(price_quality_df['price_category'], price_quality_df['quality_category'])
print(matrix)

# Visualization 6: Price-Quality Scatter
plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    price_quality_df['price'],
    price_quality_df['rating'],
    s=price_quality_df['num_reviews'] / 100,  # Size by popularity
    alpha=0.6,
    c=price_quality_df['rating'],
    cmap='RdYlGn',
    edgecolors='black',
    linewidth=0.5
)

# Add brand labels for notable ones
for brand in price_quality_df.index[:10]:
    plt.annotate(
        brand,
        (price_quality_df.loc[brand, 'price'], price_quality_df.loc[brand, 'rating']),
        fontsize=8,
        alpha=0.7
    )

plt.colorbar(scatter, label='Average Rating')
plt.xlabel('Average Price ($)')
plt.ylabel('Average Rating')
plt.title('Brand Positioning: Price vs Quality\n(Bubble size = Total Reviews)')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_quality_matrix.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/price_quality_matrix.png")

# Analysis 7: Product Portfolio Size
print("\n[9/10] Analyzing brand portfolio sizes...")

# Categorize brands by portfolio size
portfolio_distribution = pd.cut(
    store_counts,
    bins=[0, 5, 10, 20, 50, float('inf')],
    labels=['Specialist (1-5)', 'Small (6-10)', 'Medium (11-20)', 'Large (21-50)', 'Mega (51+)']
).value_counts().sort_index()

print(f"\n  📦 Brand Portfolio Distribution:")
for category, count in portfolio_distribution.items():
    pct = (count / len(store_counts)) * 100
    print(f"     {category:20s} {count:4d} brands ({pct:5.2f}%)")

# Visualization 7: Portfolio Distribution
plt.figure(figsize=(10, 6))
plt.pie(
    portfolio_distribution.values,
    labels=portfolio_distribution.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=plt.cm.Set3(range(len(portfolio_distribution)))
)
plt.title('Brand Distribution by Portfolio Size')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/portfolio_distribution.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/portfolio_distribution.png")

# Analysis 8: Export CSV with all stores
print("\n[10/10] Generating comprehensive store CSV...")

# Create detailed store statistics
store_stats = []
for store in store_counts.index:
    store_products = df[df['store'] == store]
    
    stats = {
        'store': store,
        'product_count': len(store_products),
        'market_share_pct': (len(store_products) / total_products) * 100,
        'avg_price': store_products['price'].mean() if store_products['price'].notna().any() else None,
        'median_price': store_products['price'].median() if store_products['price'].notna().any() else None,
        'min_price': store_products['price'].min() if store_products['price'].notna().any() else None,
        'max_price': store_products['price'].max() if store_products['price'].notna().any() else None,
        'avg_rating': store_products['rating'].mean() if store_products['rating'].notna().any() else None,
        'total_reviews': store_products['num_reviews'].sum() if store_products['num_reviews'].notna().any() else 0,
        'avg_reviews_per_product': store_products['num_reviews'].mean() if store_products['num_reviews'].notna().any() else None
    }
    
    # Determine price tier
    if stats['avg_price']:
        if stats['avg_price'] < 400:
            stats['price_tier'] = 'Budget'
        elif stats['avg_price'] < 700:
            stats['price_tier'] = 'Mid-Range'
        elif stats['avg_price'] < 1000:
            stats['price_tier'] = 'Upper-Mid'
        elif stats['avg_price'] < 1500:
            stats['price_tier'] = 'Premium'
        else:
            stats['price_tier'] = 'Luxury'
    else:
        stats['price_tier'] = 'Unknown'
    
    # Determine portfolio size category
    if stats['product_count'] <= 5:
        stats['portfolio_size'] = 'Specialist'
    elif stats['product_count'] <= 10:
        stats['portfolio_size'] = 'Small'
    elif stats['product_count'] <= 20:
        stats['portfolio_size'] = 'Medium'
    elif stats['product_count'] <= 50:
        stats['portfolio_size'] = 'Large'
    else:
        stats['portfolio_size'] = 'Mega'
    
    store_stats.append(stats)

# Create DataFrame and save
store_df = pd.DataFrame(store_stats)
store_df = store_df.sort_values('product_count', ascending=False)
store_df.to_csv(CSV_OUTPUT, index=False)

print(f"  ✅ Saved: {CSV_OUTPUT}")
print(f"  📊 CSV contains {len(store_df):,} unique stores with detailed statistics")

# Preview the CSV
print(f"\n  📄 CSV Preview (Top 10 stores):")
print(store_df.head(10).to_string(index=False))

# Save summary JSON
summary = {
    'total_stores': len(store_counts),
    'total_products': total_products,
    'top_10_market_share': float(top_10_share),
    'top_20_market_share': float(top_20_share),
    'top_20_stores': store_counts.head(20).to_dict(),
    'portfolio_distribution': portfolio_distribution.to_dict(),
    'price_tiers': store_df['price_tier'].value_counts().to_dict(),
    'avg_price_by_tier': store_df.groupby('price_tier')['avg_price'].mean().to_dict()
}

with open('store_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\n  ✅ Saved: store_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ STORE/BRAND ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/top_stores_by_count.png")
print(f"   • {OUTPUT_DIR}/market_concentration.png")
print(f"   • {OUTPUT_DIR}/brand_price_positioning.png")
print(f"   • {OUTPUT_DIR}/brand_quality_ratings.png")
print(f"   • {OUTPUT_DIR}/brand_popularity_reviews.png")
print(f"   • {OUTPUT_DIR}/price_quality_matrix.png")
print(f"   • {OUTPUT_DIR}/portfolio_distribution.png")
print(f"   • {CSV_OUTPUT} ⭐ (Detailed store statistics)")
print(f"   • store_summary.json")
print("=" * 80)

