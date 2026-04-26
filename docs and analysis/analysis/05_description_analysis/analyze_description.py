#!/usr/bin/env python3
"""
Description Analysis for Laptop Products
=========================================
Analyzes product descriptions (text and array formats).

Key metrics:
- Coverage and completeness
- Text length distribution
- Common keywords and themes
- Description quality indicators
- Price/rating correlation with description quality
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from collections import Counter
import re

# Database configuration
DB_CONFIG = {
    'dbname': 'amazon_electronics_rag',
    'user': input('PostgreSQL username: '),
    'password': input('PostgreSQL password (press Enter if none): ') or '',
    'host': 'localhost',
    'port': 5432
}

OUTPUT_DIR = "visualizations"
CSV_OUTPUT = "description_analysis.csv"

print("=" * 80)
print("📝 DESCRIPTION ANALYSIS")
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
        description,
        description_array,
        price,
        average_rating,
        rating_number,
        store
    FROM products_backup;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products")

# Create dataframe
df = pd.DataFrame(products, columns=[
    'asin', 'title', 'description', 'description_array', 'price', 'rating', 'num_reviews', 'store'
])

# Analysis 1: Coverage
print("\n[3/10] Analyzing description coverage...")

total = len(df)
has_desc = df['description'].notna().sum()
has_desc_array = df['description_array'].notna().sum()
has_non_empty_desc = df[df['description'].notna() & (df['description'].str.len() > 0)].shape[0]

coverage_stats = {
    'total_products': total,
    'has_description_text': has_desc,
    'has_description_array': has_desc_array,
    'has_non_empty_text': has_non_empty_desc,
    'coverage_pct_text': (has_desc / total) * 100,
    'coverage_pct_array': (has_desc_array / total) * 100
}

print(f"\n  📊 Coverage Statistics:")
print(f"     Total products: {total:,}")
print(f"     Has description (text): {has_desc:,} ({coverage_stats['coverage_pct_text']:.2f}%)")
print(f"     Has description_array: {has_desc_array:,} ({coverage_stats['coverage_pct_array']:.2f}%)")
print(f"     Non-empty text: {has_non_empty_desc:,}")

# Missing descriptions
missing = df[df['description'].isna() | (df['description'].str.len() == 0)]
print(f"\n  ⚠️  Missing/empty descriptions: {len(missing):,} ({len(missing)/total*100:.2f}%)")
if len(missing) > 0:
    print(f"     Top brands with missing descriptions:")
    missing_brands = missing['store'].value_counts().head(5)
    for brand, count in missing_brands.items():
        print(f"       • {brand}: {count}")

# Analysis 2: Length Distribution
print("\n[4/10] Analyzing description length...")

df['desc_length'] = df['description'].str.len()
df_with_desc = df[df['desc_length'].notna() & (df['desc_length'] > 0)].copy()

length_stats = {
    'mean': df_with_desc['desc_length'].mean(),
    'median': df_with_desc['desc_length'].median(),
    'min': df_with_desc['desc_length'].min(),
    'max': df_with_desc['desc_length'].max(),
    'std': df_with_desc['desc_length'].std()
}

print(f"\n  📏 Length Statistics:")
print(f"     Mean: {length_stats['mean']:.0f} chars")
print(f"     Median: {length_stats['median']:.0f} chars")
print(f"     Min: {length_stats['min']:.0f} chars")
print(f"     Max: {length_stats['max']:.0f} chars")
print(f"     Std Dev: {length_stats['std']:.0f} chars")

# Categorize by length
df_with_desc['desc_category'] = pd.cut(
    df_with_desc['desc_length'],
    bins=[0, 200, 500, 1000, 2000, float('inf')],
    labels=['Very Short (<200)', 'Short (200-500)', 'Medium (500-1K)', 'Long (1K-2K)', 'Very Long (2K+)']
)

print(f"\n  📊 Description Length Categories:")
for cat in ['Very Short (<200)', 'Short (200-500)', 'Medium (500-1K)', 'Long (1K-2K)', 'Very Long (2K+)']:
    count = (df_with_desc['desc_category'] == cat).sum()
    pct = (count / len(df_with_desc)) * 100
    print(f"     {cat:20s} {count:5,} ({pct:5.2f}%)")

# Visualization 1: Length distribution
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(df_with_desc['desc_length'], bins=50, color='steelblue', edgecolor='black')
plt.xlabel('Description Length (characters)')
plt.ylabel('Number of Products')
plt.title('Distribution of Description Lengths')
plt.axvline(length_stats['mean'], color='red', linestyle='--', label=f'Mean: {length_stats["mean"]:.0f}')
plt.axvline(length_stats['median'], color='green', linestyle='--', label=f'Median: {length_stats["median"]:.0f}')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.subplot(1, 2, 2)
cat_counts = df_with_desc['desc_category'].value_counts()
colors = ['#ff9999', '#ffcc99', '#99ccff', '#99ff99', '#cc99ff']
plt.bar(range(len(cat_counts)), cat_counts.values, color=colors)
plt.xticks(range(len(cat_counts)), cat_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Products')
plt.title('Products by Description Length Category')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/description_length_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/description_length_distribution.png")

# Analysis 3: Array Statistics
print("\n[5/10] Analyzing description_array...")

df['array_length'] = df['description_array'].apply(lambda x: len(x) if x and isinstance(x, list) else 0)
df_with_array = df[df['array_length'] > 0].copy()

if len(df_with_array) > 0:
    print(f"\n  📋 Description Array Statistics:")
    print(f"     Avg items per array: {df_with_array['array_length'].mean():.2f}")
    print(f"     Median items: {df_with_array['array_length'].median():.0f}")
    print(f"     Max items: {df_with_array['array_length'].max():.0f}")
    print(f"     Min items: {df_with_array['array_length'].min():.0f}")

# Analysis 4: Keyword Analysis
print("\n[6/10] Analyzing common keywords...")

# Extract keywords from descriptions
all_words = []
for desc in df_with_desc['description'].dropna():
    # Simple word extraction (lowercase, alphanumeric only)
    words = re.findall(r'\b[a-z]{4,}\b', desc.lower())
    all_words.extend(words)

# Common words (excluding stop words)
stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'more', 'about', 'also', 
              'their', 'which', 'there', 'these', 'been', 'other', 'into', 'such', 'than', 
              'them', 'only', 'over', 'some', 'when', 'very', 'even', 'just', 'they', 'what',
              'makes', 'made', 'like', 'features', 'feature', 'includes', 'include'}

filtered_words = [w for w in all_words if w not in stop_words]
word_counts = Counter(filtered_words)

print(f"\n  🔤 Top 20 Keywords in Descriptions:")
for i, (word, count) in enumerate(word_counts.most_common(20), 1):
    pct = (count / len(filtered_words)) * 100
    print(f"     {i:2d}. {word:20s} {count:6,} ({pct:4.2f}%)")

# Visualization 2: Top keywords
plt.figure(figsize=(12, 8))
top_words = word_counts.most_common(20)
words, counts = zip(*top_words)
colors = plt.cm.viridis(np.linspace(0, 1, len(words)))
plt.barh(range(len(words)), counts, color=colors)
plt.yticks(range(len(words)), words)
plt.xlabel('Frequency')
plt.title('Top 20 Keywords in Product Descriptions')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_description_keywords.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_description_keywords.png")

# Analysis 5: Description Quality vs Price
print("\n[7/10] Analyzing description quality vs price...")

df_price_desc = df_with_desc[df_with_desc['price'].notna()].copy()

if len(df_price_desc) > 0:
    # Correlation
    correlation = df_price_desc['desc_length'].corr(df_price_desc['price'])
    print(f"\n  📊 Correlation (Length vs Price): {correlation:.3f}")
    
    # Average price by description category
    print(f"\n  💰 Average Price by Description Length:")
    for cat in ['Very Short (<200)', 'Short (200-500)', 'Medium (500-1K)', 'Long (1K-2K)', 'Very Long (2K+)']:
        cat_data = df_price_desc[df_price_desc['desc_category'] == cat]
        if len(cat_data) > 0:
            avg_price = cat_data['price'].mean()
            print(f"     {cat:20s} ${avg_price:7.2f}")

# Visualization 3: Length vs Price
plt.figure(figsize=(10, 6))
sample_size = min(1000, len(df_price_desc))
sample = df_price_desc.sample(sample_size)
plt.scatter(sample['desc_length'], sample['price'], alpha=0.5, s=20)
plt.xlabel('Description Length (characters)')
plt.ylabel('Price ($)')
plt.title(f'Description Length vs Price (Correlation: {correlation:.3f})')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/description_length_vs_price.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/description_length_vs_price.png")

# Analysis 6: Description Quality vs Rating
print("\n[8/10] Analyzing description quality vs rating...")

df_rating_desc = df_with_desc[df_with_desc['rating'].notna()].copy()

if len(df_rating_desc) > 0:
    correlation = df_rating_desc['desc_length'].corr(df_rating_desc['rating'])
    print(f"\n  📊 Correlation (Length vs Rating): {correlation:.3f}")
    
    print(f"\n  ⭐ Average Rating by Description Length:")
    for cat in ['Very Short (<200)', 'Short (200-500)', 'Medium (500-1K)', 'Long (1K-2K)', 'Very Long (2K+)']:
        cat_data = df_rating_desc[df_rating_desc['desc_category'] == cat]
        if len(cat_data) > 0:
            avg_rating = cat_data['rating'].mean()
            stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
            print(f"     {cat:20s} {avg_rating:.2f} {stars}")

# Analysis 7: Brand Analysis
print("\n[9/10] Analyzing description quality by brand...")

top_brands = df['store'].value_counts().head(10).index
brand_desc_stats = []

for brand in top_brands:
    brand_df = df_with_desc[df_with_desc['store'] == brand]
    if len(brand_df) > 0:
        brand_desc_stats.append({
            'brand': brand,
            'products': len(brand_df),
            'avg_desc_length': brand_df['desc_length'].mean(),
            'median_desc_length': brand_df['desc_length'].median()
        })

brand_desc_df = pd.DataFrame(brand_desc_stats).sort_values('avg_desc_length', ascending=False)

print(f"\n  🏪 Top 10 Brands - Description Length:")
for _, row in brand_desc_df.iterrows():
    print(f"     {row['brand']:30s} {row['avg_desc_length']:6.0f} chars avg (n={row['products']:,})")

# Visualization 4: Brand comparison
plt.figure(figsize=(12, 6))
plt.barh(range(len(brand_desc_df)), brand_desc_df['avg_desc_length'], color='coral')
plt.yticks(range(len(brand_desc_df)), brand_desc_df['brand'])
plt.xlabel('Average Description Length (characters)')
plt.title('Average Description Length by Top 10 Brands')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/description_length_by_brand.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/description_length_by_brand.png")

# Analysis 8: Export CSV
print("\n[10/10] Generating summary CSV...")

summary_data = {
    'metric': [
        'Total Products',
        'Has Description',
        'Coverage %',
        'Avg Length',
        'Median Length',
        'Max Length',
        'Correlation with Price',
        'Correlation with Rating'
    ],
    'value': [
        total,
        has_desc,
        f"{coverage_stats['coverage_pct_text']:.2f}%",
        f"{length_stats['mean']:.0f}",
        f"{length_stats['median']:.0f}",
        f"{length_stats['max']:.0f}",
        f"{correlation:.3f}" if 'correlation' in locals() else 'N/A',
        f"{df_rating_desc['desc_length'].corr(df_rating_desc['rating']):.3f}" if len(df_rating_desc) > 0 else 'N/A'
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(CSV_OUTPUT, index=False)
print(f"  ✅ Saved: {CSV_OUTPUT}")

# Save JSON summary
summary_json = {
    'coverage': {k: int(v) if isinstance(v, (np.int64, np.int32)) else float(v) if isinstance(v, (np.float64, np.float32)) else v 
                 for k, v in coverage_stats.items()},
    'length_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                          for k, v in length_stats.items()},
    'top_20_keywords': {k: int(v) for k, v in word_counts.most_common(20)},
    'correlation_with_price': float(correlation) if 'correlation' in locals() else None,
    'correlation_with_rating': float(df_rating_desc['desc_length'].corr(df_rating_desc['rating'])) if len(df_rating_desc) > 0 else None,
    'brand_statistics': [{k: int(v) if isinstance(v, (np.int64, np.int32)) else float(v) if isinstance(v, (np.float64, np.float32)) else v 
                          for k, v in record.items()} for record in brand_desc_df.to_dict('records')]
}

with open('description_summary.json', 'w') as f:
    json.dump(summary_json, f, indent=2)
print(f"  ✅ Saved: description_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DESCRIPTION ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/description_length_distribution.png")
print(f"   • {OUTPUT_DIR}/top_description_keywords.png")
print(f"   • {OUTPUT_DIR}/description_length_vs_price.png")
print(f"   • {OUTPUT_DIR}/description_length_by_brand.png")
print(f"   • {CSV_OUTPUT}")
print(f"   • description_summary.json")
print("=" * 80)

