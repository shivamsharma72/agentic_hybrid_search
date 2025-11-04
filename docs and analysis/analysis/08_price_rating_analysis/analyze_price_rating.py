#!/usr/bin/env python3
"""
Price vs Rating Analysis for Laptop Products
============================================
Combined analysis of price and rating relationship, distribution, and patterns.

Key metrics:
- Price distribution and statistics
- Rating distribution and statistics
- Price-Rating correlation
- Price-Review Count correlation
- Rating-Review Count correlation
- Price tiers vs quality
- Value segments (price/quality matrix)
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from scipy import stats

# Database configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

OUTPUT_DIR = "visualizations"
CSV_OUTPUT = "price_rating_analysis.csv"

print("=" * 80)
print("💰⭐ PRICE vs RATING ANALYSIS")
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
print("\n[2/10] Fetching products...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        price,
        average_rating,
        rating_number,
        store
    FROM products_backup;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products")

# Create dataframe
df = pd.DataFrame(products, columns=['asin', 'title', 'price', 'rating', 'num_reviews', 'store'])

# Analysis 1: Price Distribution
print("\n[3/10] Analyzing price distribution...")

df_with_price = df[df['price'].notna()].copy()

price_stats = {
    'count': len(df_with_price),
    'mean': df_with_price['price'].mean(),
    'median': df_with_price['price'].median(),
    'std': df_with_price['price'].std(),
    'min': df_with_price['price'].min(),
    'max': df_with_price['price'].max(),
    'q25': df_with_price['price'].quantile(0.25),
    'q75': df_with_price['price'].quantile(0.75)
}

print(f"\n  💰 Price Statistics:")
print(f"     Products with price: {price_stats['count']:,} ({price_stats['count']/len(df)*100:.2f}%)")
print(f"     Mean: ${price_stats['mean']:.2f}")
print(f"     Median: ${price_stats['median']:.2f}")
print(f"     Std Dev: ${price_stats['std']:.2f}")
print(f"     Range: ${price_stats['min']:.2f} - ${price_stats['max']:.2f}")
print(f"     25th percentile: ${price_stats['q25']:.2f}")
print(f"     75th percentile: ${price_stats['q75']:.2f}")

# Price categories
df_with_price['price_tier'] = pd.cut(
    df_with_price['price'],
    bins=[0, 400, 700, 1000, 1500, float('inf')],
    labels=['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']
)

print(f"\n  📊 Price Tier Distribution:")
for tier in ['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']:
    count = (df_with_price['price_tier'] == tier).sum()
    pct = (count / len(df_with_price)) * 100
    print(f"     {tier:25s} {count:4,} ({pct:5.2f}%)")

# Visualization 1: Price distribution
plt.figure(figsize=(14, 6))

plt.subplot(1, 3, 1)
plt.hist(df_with_price['price'], bins=50, color='green', edgecolor='black', alpha=0.7)
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.title('Price Distribution')
plt.axvline(price_stats['mean'], color='red', linestyle='--', label=f'Mean: ${price_stats["mean"]:.0f}')
plt.axvline(price_stats['median'], color='blue', linestyle='--', label=f'Median: ${price_stats["median"]:.0f}')
plt.legend()

plt.subplot(1, 3, 2)
plt.hist(df_with_price['price'], bins=50, color='green', edgecolor='black', alpha=0.7)
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.title('Price Distribution (Zoomed to $2000)')
plt.xlim(0, 2000)
plt.axvline(price_stats['median'], color='blue', linestyle='--')

plt.subplot(1, 3, 3)
tier_counts = df_with_price['price_tier'].value_counts()
colors = ['#90EE90', '#87CEEB', '#FFD700', '#FF8C00', '#FF4500']
plt.bar(range(len(tier_counts)), tier_counts.values, color=colors)
plt.xticks(range(len(tier_counts)), tier_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Products')
plt.title('Products by Price Tier')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/price_distribution.png")

# Analysis 2: Rating Distribution
print("\n[4/10] Analyzing rating distribution...")

df_with_rating = df[df['rating'].notna()].copy()

rating_stats = {
    'count': len(df_with_rating),
    'mean': df_with_rating['rating'].mean(),
    'median': df_with_rating['rating'].median(),
    'std': df_with_rating['rating'].std(),
    'min': df_with_rating['rating'].min(),
    'max': df_with_rating['rating'].max()
}

print(f"\n  ⭐ Rating Statistics:")
print(f"     Products with rating: {rating_stats['count']:,} ({rating_stats['count']/len(df)*100:.2f}%)")
print(f"     Mean: {rating_stats['mean']:.2f}⭐")
print(f"     Median: {rating_stats['median']:.2f}⭐")
print(f"     Std Dev: {rating_stats['std']:.2f}")
print(f"     Range: {rating_stats['min']:.2f} - {rating_stats['max']:.2f}")

# Rating categories
df_with_rating['rating_category'] = pd.cut(
    df_with_rating['rating'],
    bins=[0, 3.0, 3.5, 4.0, 4.5, 5.0],
    labels=['Poor (<3.0)', 'Fair (3.0-3.5)', 'Good (3.5-4.0)', 'Very Good (4.0-4.5)', 'Excellent (4.5+)']
)

print(f"\n  📊 Rating Distribution:")
for cat in ['Poor (<3.0)', 'Fair (3.0-3.5)', 'Good (3.5-4.0)', 'Very Good (4.0-4.5)', 'Excellent (4.5+)']:
    count = (df_with_rating['rating_category'] == cat).sum()
    pct = (count / len(df_with_rating)) * 100
    print(f"     {cat:25s} {count:4,} ({pct:5.2f}%)")

# Visualization 2: Rating distribution
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.hist(df_with_rating['rating'], bins=50, color='gold', edgecolor='black', alpha=0.7)
plt.xlabel('Rating (out of 5)')
plt.ylabel('Frequency')
plt.title('Rating Distribution')
plt.axvline(rating_stats['mean'], color='red', linestyle='--', label=f'Mean: {rating_stats["mean"]:.2f}⭐')
plt.axvline(rating_stats['median'], color='blue', linestyle='--', label=f'Median: {rating_stats["median"]:.2f}⭐')
plt.legend()

plt.subplot(1, 2, 2)
cat_counts = df_with_rating['rating_category'].value_counts()
colors = ['#ff6b6b', '#ffa500', '#ffd700', '#90EE90', '#00ff00']
plt.bar(range(len(cat_counts)), cat_counts.values, color=colors)
plt.xticks(range(len(cat_counts)), cat_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Products')
plt.title('Products by Rating Category')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rating_distribution.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/rating_distribution.png")

# Analysis 3: Price vs Rating Correlation
print("\n[5/10] Analyzing price vs rating correlation...")

df_both = df[(df['price'].notna()) & (df['rating'].notna())].copy()

if len(df_both) > 0:
    correlation = df_both['price'].corr(df_both['rating'])
    spearman_corr = stats.spearmanr(df_both['price'], df_both['rating'])[0]
    
    print(f"\n  📊 Price vs Rating Correlation:")
    print(f"     Pearson: {correlation:.3f}")
    print(f"     Spearman: {spearman_corr:.3f}")
    
    # Average rating by price tier
    print(f"\n  ⭐ Average Rating by Price Tier:")
    df_both['price_tier'] = pd.cut(
        df_both['price'],
        bins=[0, 400, 700, 1000, 1500, float('inf')],
        labels=['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']
    )
    
    for tier in ['Budget (<$400)', 'Mid-Range ($400-$700)', 'Upper-Mid ($700-$1K)', 'Premium ($1K-$1.5K)', 'Luxury ($1.5K+)']:
        tier_data = df_both[df_both['price_tier'] == tier]
        if len(tier_data) > 0:
            avg_rating = tier_data['rating'].mean()
            stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
            print(f"     {tier:25s} {avg_rating:.2f} {stars} (n={len(tier_data):,})")

# Visualization 3: Price vs Rating scatter
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sample_size = min(2000, len(df_both))
sample = df_both.sample(sample_size)
plt.scatter(sample['price'], sample['rating'], alpha=0.5, s=20, c=sample['rating'], cmap='RdYlGn')
plt.colorbar(label='Rating')
plt.xlabel('Price ($)')
plt.ylabel('Rating (out of 5)')
plt.title(f'Price vs Rating (Pearson: {correlation:.3f})')
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
df_both.boxplot(column='rating', by='price_tier', ax=plt.gca())
plt.xlabel('Price Tier')
plt.ylabel('Rating (out of 5)')
plt.title('Rating Distribution by Price Tier')
plt.suptitle('')
plt.xticks(rotation=15, ha='right')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_vs_rating.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/price_vs_rating.png")

# Analysis 4: Review Count Distribution
print("\n[6/10] Analyzing review count distribution...")

df_with_reviews = df[df['num_reviews'].notna()].copy()

review_stats = {
    'count': len(df_with_reviews),
    'mean': df_with_reviews['num_reviews'].mean(),
    'median': df_with_reviews['num_reviews'].median(),
    'max': df_with_reviews['num_reviews'].max(),
    'total': df_with_reviews['num_reviews'].sum()
}

print(f"\n  💬 Review Count Statistics:")
print(f"     Products with reviews: {review_stats['count']:,}")
print(f"     Total reviews: {int(review_stats['total']):,}")
print(f"     Mean per product: {review_stats['mean']:.0f}")
print(f"     Median per product: {review_stats['median']:.0f}")
print(f"     Max reviews: {int(review_stats['max']):,}")

# Analysis 5: Price vs Review Count
print("\n[7/10] Analyzing price vs review count...")

df_price_reviews = df[(df['price'].notna()) & (df['num_reviews'].notna())].copy()

if len(df_price_reviews) > 0:
    corr_price_reviews = df_price_reviews['price'].corr(df_price_reviews['num_reviews'])
    print(f"\n  📊 Price vs Review Count Correlation: {corr_price_reviews:.3f}")

# Visualization 4: Price vs Review Count
plt.figure(figsize=(10, 6))
sample = df_price_reviews.sample(min(1000, len(df_price_reviews)))
plt.scatter(sample['price'], sample['num_reviews'], alpha=0.5, s=20)
plt.xlabel('Price ($)')
plt.ylabel('Number of Reviews')
plt.title(f'Price vs Review Count (Correlation: {corr_price_reviews:.3f})')
plt.yscale('log')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_vs_reviews.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/price_vs_reviews.png")

# Analysis 6: Rating vs Review Count
print("\n[8/10] Analyzing rating vs review count...")

df_rating_reviews = df[(df['rating'].notna()) & (df['num_reviews'].notna())].copy()

if len(df_rating_reviews) > 0:
    corr_rating_reviews = df_rating_reviews['rating'].corr(df_rating_reviews['num_reviews'])
    print(f"\n  📊 Rating vs Review Count Correlation: {corr_rating_reviews:.3f}")

# Visualization 5: Rating vs Review Count
plt.figure(figsize=(10, 6))
sample = df_rating_reviews.sample(min(1000, len(df_rating_reviews)))
plt.scatter(sample['rating'], sample['num_reviews'], alpha=0.5, s=20, c=sample['rating'], cmap='RdYlGn')
plt.colorbar(label='Rating')
plt.xlabel('Rating (out of 5)')
plt.ylabel('Number of Reviews')
plt.title(f'Rating vs Review Count (Correlation: {corr_rating_reviews:.3f})')
plt.yscale('log')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rating_vs_reviews.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/rating_vs_reviews.png")

# Analysis 7: Price-Quality Matrix (Value Segments)
print("\n[9/10] Creating price-quality value matrix...")

df_matrix = df[(df['price'].notna()) & (df['rating'].notna())].copy()

# Categorize
df_matrix['price_segment'] = pd.cut(
    df_matrix['price'],
    bins=[0, 500, 1000, float('inf')],
    labels=['Budget', 'Mid-Range', 'Premium']
)

df_matrix['quality_segment'] = pd.cut(
    df_matrix['rating'],
    bins=[0, 3.5, 4.0, 5.0],
    labels=['Standard', 'Good', 'Excellent']
)

# Create matrix
matrix = pd.crosstab(df_matrix['price_segment'], df_matrix['quality_segment'])
print(f"\n  🎯 Price-Quality Matrix (Product Count):")
print(matrix)

# Value segments
print(f"\n  💎 Value Segments:")
segments = {
    'Best Value': df_matrix[(df_matrix['price'] < 500) & (df_matrix['rating'] >= 4.0)],
    'Premium Value': df_matrix[(df_matrix['price'].between(500, 1000)) & (df_matrix['rating'] >= 4.0)],
    'Overpriced': df_matrix[(df_matrix['price'] > 1000) & (df_matrix['rating'] < 3.5)],
    'Budget Gems': df_matrix[(df_matrix['price'] < 500) & (df_matrix['rating'] >= 4.5)]
}

for segment_name, segment_df in segments.items():
    count = len(segment_df)
    pct = (count / len(df_matrix)) * 100
    if count > 0:
        avg_price = segment_df['price'].mean()
        avg_rating = segment_df['rating'].mean()
        print(f"     {segment_name:20s} {count:4,} products ({pct:5.2f}%) - ${avg_price:.0f} avg, {avg_rating:.2f}⭐ avg")

# Visualization 6: Price-Quality Matrix
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
sns.heatmap(matrix, annot=True, fmt='d', cmap='YlGnBu', cbar_kws={'label': 'Product Count'})
plt.title('Price-Quality Matrix (Product Count)')
plt.xlabel('Quality Segment')
plt.ylabel('Price Segment')

plt.subplot(1, 2, 2)
# Scatter with density
sample = df_matrix.sample(min(2000, len(df_matrix)))
plt.scatter(sample['rating'], sample['price'], alpha=0.3, s=20, c=sample['price'], cmap='viridis')
plt.colorbar(label='Price ($)')
plt.xlabel('Rating (out of 5)')
plt.ylabel('Price ($)')
plt.title('Price vs Quality Scatter')
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_quality_matrix.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/price_quality_matrix.png")

# Analysis 8: Export
print("\n[10/10] Generating summary...")

summary_data = {
    'metric': [
        'Total Products',
        'Products with Price',
        'Products with Rating',
        'Avg Price',
        'Median Price',
        'Avg Rating',
        'Correlation (Price-Rating)',
        'Correlation (Price-Reviews)',
        'Correlation (Rating-Reviews)'
    ],
    'value': [
        len(df),
        len(df_with_price),
        len(df_with_rating),
        f"${price_stats['mean']:.2f}",
        f"${price_stats['median']:.2f}",
        f"{rating_stats['mean']:.2f}⭐",
        f"{correlation:.3f}" if 'correlation' in locals() else 'N/A',
        f"{corr_price_reviews:.3f}" if 'corr_price_reviews' in locals() else 'N/A',
        f"{corr_rating_reviews:.3f}" if 'corr_rating_reviews' in locals() else 'N/A'
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(CSV_OUTPUT, index=False)
print(f"  ✅ Saved: {CSV_OUTPUT}")

# Save JSON
summary_json = {
    'price_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                         for k, v in price_stats.items()},
    'rating_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                          for k, v in rating_stats.items()},
    'review_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                          for k, v in review_stats.items()},
    'correlations': {
        'price_rating_pearson': float(correlation) if 'correlation' in locals() else None,
        'price_rating_spearman': float(spearman_corr) if 'spearman_corr' in locals() else None,
        'price_reviews': float(corr_price_reviews) if 'corr_price_reviews' in locals() else None,
        'rating_reviews': float(corr_rating_reviews) if 'corr_rating_reviews' in locals() else None
    },
    'value_segments': {name: len(seg) for name, seg in segments.items()}
}

with open('price_rating_summary.json', 'w') as f:
    json.dump(summary_json, f, indent=2)
print(f"  ✅ Saved: price_rating_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ PRICE vs RATING ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/price_distribution.png")
print(f"   • {OUTPUT_DIR}/rating_distribution.png")
print(f"   • {OUTPUT_DIR}/price_vs_rating.png")
print(f"   • {OUTPUT_DIR}/price_vs_reviews.png")
print(f"   • {OUTPUT_DIR}/rating_vs_reviews.png")
print(f"   • {OUTPUT_DIR}/price_quality_matrix.png")
print(f"   • {CSV_OUTPUT}")
print(f"   • price_rating_summary.json")
print("=" * 80)

