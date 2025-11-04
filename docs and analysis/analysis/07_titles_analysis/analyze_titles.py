#!/usr/bin/env python3
"""
Product Titles Analysis for Laptop Products
===========================================
Analyzes product title patterns, structure, and information content.

Key metrics:
- Title length distribution
- Common keywords and brands in titles
- Information density (specs in titles)
- Title structure patterns
- Correlation with price/rating
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
CSV_OUTPUT = "titles_analysis.csv"

print("=" * 80)
print("📝 PRODUCT TITLES ANALYSIS")
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

# Analysis 1: Title Length
print("\n[3/8] Analyzing title lengths...")

df['title_length'] = df['title'].str.len()
df['word_count'] = df['title'].str.split().str.len()

length_stats = {
    'mean_chars': df['title_length'].mean(),
    'median_chars': df['title_length'].median(),
    'max_chars': df['title_length'].max(),
    'min_chars': df['title_length'].min(),
    'mean_words': df['word_count'].mean(),
    'median_words': df['word_count'].median()
}

print(f"\n  📏 Title Length Statistics:")
print(f"     Mean: {length_stats['mean_chars']:.0f} chars, {length_stats['mean_words']:.1f} words")
print(f"     Median: {length_stats['median_chars']:.0f} chars, {length_stats['median_words']:.0f} words")
print(f"     Range: {length_stats['min_chars']:.0f} - {length_stats['max_chars']:.0f} chars")

# Categorize by length
df['length_category'] = pd.cut(
    df['title_length'],
    bins=[0, 50, 100, 150, 200, float('inf')],
    labels=['Very Short (<50)', 'Short (50-100)', 'Medium (100-150)', 'Long (150-200)', 'Very Long (200+)']
)

print(f"\n  📊 Title Length Categories:")
for cat in ['Very Short (<50)', 'Short (50-100)', 'Medium (100-150)', 'Long (150-200)', 'Very Long (200+)']:
    count = (df['length_category'] == cat).sum()
    pct = (count / len(df)) * 100
    print(f"     {cat:25s} {count:5,} ({pct:5.2f}%)")

# Visualization 1: Length distribution
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.hist(df['title_length'], bins=50, color='steelblue', edgecolor='black')
plt.xlabel('Title Length (characters)')
plt.ylabel('Number of Products')
plt.title('Distribution of Title Lengths')
plt.axvline(length_stats['mean_chars'], color='red', linestyle='--', label=f'Mean: {length_stats["mean_chars"]:.0f}')
plt.axvline(length_stats['median_chars'], color='green', linestyle='--', label=f'Median: {length_stats["median_chars"]:.0f}')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.subplot(1, 2, 2)
cat_counts = df['length_category'].value_counts()
colors = ['#ff9999', '#ffcc99', '#99ccff', '#99ff99', '#cc99ff']
plt.bar(range(len(cat_counts)), cat_counts.values, color=colors)
plt.xticks(range(len(cat_counts)), cat_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Products')
plt.title('Products by Title Length Category')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/title_length_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/title_length_distribution.png")

# Analysis 2: Common Keywords
print("\n[4/8] Analyzing common keywords in titles...")

# Extract keywords
all_words = []
for title in df['title']:
    words = re.findall(r'\b[a-z]{3,}\b', str(title).lower())
    all_words.extend(words)

# Filter stop words
stop_words = {'the', 'and', 'for', 'with', 'inch', 'full', 'home', 'new', 'laptop', 
              'notebook', 'computer', 'windows', 'edition', 'version', 'model', 'brand'}

filtered_words = [w for w in all_words if w not in stop_words]
word_counts = Counter(filtered_words)

print(f"\n  🔤 Top 25 Keywords in Titles:")
for i, (word, count) in enumerate(word_counts.most_common(25), 1):
    pct = (count / len(df)) * 100
    print(f"     {i:2d}. {word:20s} {count:5,} ({pct:5.2f}% of products)")

# Visualization 2: Top keywords
plt.figure(figsize=(14, 10))
top_words = word_counts.most_common(25)
words, counts = zip(*top_words)
colors = plt.cm.viridis(np.linspace(0, 1, len(words)))
plt.barh(range(len(words)), counts, color=colors)
plt.yticks(range(len(words)), words, fontsize=9)
plt.xlabel('Frequency in Titles')
plt.title('Top 25 Keywords in Product Titles')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_title_keywords.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_title_keywords.png")

# Analysis 3: Specs in Titles
print("\n[5/8] Detecting specs mentioned in titles...")

# Define spec patterns
specs = {
    'Brand': ['hp', 'dell', 'lenovo', 'asus', 'acer', 'apple', 'msi', 'samsung', 'toshiba'],
    'Processor': ['intel', 'core', 'i3', 'i5', 'i7', 'i9', 'ryzen', 'amd', 'celeron', 'pentium'],
    'RAM': ['4gb', '8gb', '12gb', '16gb', '32gb', '64gb'],
    'Storage': ['128gb', '256gb', '512gb', '1tb', '2tb', 'ssd', 'hdd'],
    'Screen Size': ['11', '13', '14', '15', '17'],
    'Resolution': ['hd', '1080p', '4k', 'uhd', 'fhd'],
    'OS': ['windows', 'chrome', 'chromebook', 'macos'],
    'Type': ['2-in-1', 'touchscreen', 'gaming', 'business', 'ultrabook']
}

spec_mentions = {spec: 0 for spec in specs}
for spec_type, keywords in specs.items():
    for title in df['title']:
        title_lower = str(title).lower()
        if any(keyword in title_lower for keyword in keywords):
            spec_mentions[spec_type] += 1

# Sort by frequency
sorted_specs = sorted(spec_mentions.items(), key=lambda x: x[1], reverse=True)

print(f"\n  🔧 Spec Types in Titles (% of products):")
for spec_type, count in sorted_specs:
    pct = (count / len(df)) * 100
    print(f"     {spec_type:15s} {count:5,} ({pct:5.2f}%)")

# Visualization 3: Specs in titles
plt.figure(figsize=(10, 6))
spec_types, spec_counts = zip(*sorted_specs)
colors_spec = plt.cm.Set3(range(len(spec_types)))
plt.barh(range(len(spec_types)), spec_counts, color=colors_spec)
plt.yticks(range(len(spec_types)), spec_types)
plt.xlabel('Number of Products Mentioning')
plt.title('Specification Types Mentioned in Titles')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/specs_in_titles.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/specs_in_titles.png")

# Analysis 4: Title Length vs Price
print("\n[6/8] Analyzing title length vs price...")

df_with_price = df[df['price'].notna()].copy()

if len(df_with_price) > 0:
    correlation = df_with_price['title_length'].corr(df_with_price['price'])
    print(f"\n  📊 Correlation (Title Length vs Price): {correlation:.3f}")
    
    print(f"\n  💰 Average Price by Title Length:")
    for cat in ['Very Short (<50)', 'Short (50-100)', 'Medium (100-150)', 'Long (150-200)', 'Very Long (200+)']:
        cat_data = df_with_price[df_with_price['length_category'] == cat]
        if len(cat_data) > 0:
            avg_price = cat_data['price'].mean()
            print(f"     {cat:25s} ${avg_price:7.2f}")

# Visualization 4: Length vs Price
plt.figure(figsize=(10, 6))
sample_size = min(1000, len(df_with_price))
sample = df_with_price.sample(sample_size)
plt.scatter(sample['title_length'], sample['price'], alpha=0.5, s=20)
plt.xlabel('Title Length (characters)')
plt.ylabel('Price ($)')
plt.title(f'Title Length vs Price (Correlation: {correlation:.3f})')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/title_length_vs_price.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/title_length_vs_price.png")

# Analysis 5: Title Length vs Rating
print("\n[7/8] Analyzing title length vs rating...")

df_with_rating = df[df['rating'].notna()].copy()

if len(df_with_rating) > 0:
    correlation_rating = df_with_rating['title_length'].corr(df_with_rating['rating'])
    print(f"\n  📊 Correlation (Title Length vs Rating): {correlation_rating:.3f}")
    
    print(f"\n  ⭐ Average Rating by Title Length:")
    for cat in ['Very Short (<50)', 'Short (50-100)', 'Medium (100-150)', 'Long (150-200)', 'Very Long (200+)']:
        cat_data = df_with_rating[df_with_rating['length_category'] == cat]
        if len(cat_data) > 0:
            avg_rating = cat_data['rating'].mean()
            stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
            print(f"     {cat:25s} {avg_rating:.2f} {stars}")

# Analysis 6: Brand Analysis
print("\n[8/8] Analyzing title length by brand...")

top_brands = df['store'].value_counts().head(10).index
brand_title_stats = []

for brand in top_brands:
    brand_df = df[df['store'] == brand]
    if len(brand_df) > 0:
        brand_title_stats.append({
            'brand': brand,
            'products': len(brand_df),
            'avg_title_length': brand_df['title_length'].mean(),
            'median_title_length': brand_df['title_length'].median()
        })

brand_title_df = pd.DataFrame(brand_title_stats).sort_values('avg_title_length', ascending=False)

print(f"\n  🏪 Top 10 Brands - Title Length:")
for _, row in brand_title_df.iterrows():
    print(f"     {row['brand']:30s} {row['avg_title_length']:6.0f} chars avg (n={row['products']:,})")

# Visualization 5: Brand comparison
plt.figure(figsize=(12, 6))
plt.barh(range(len(brand_title_df)), brand_title_df['avg_title_length'], color='coral')
plt.yticks(range(len(brand_title_df)), brand_title_df['brand'])
plt.xlabel('Average Title Length (characters)')
plt.title('Average Title Length by Top 10 Brands')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/title_length_by_brand.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/title_length_by_brand.png")

# Export CSV
summary_data = {
    'metric': [
        'Total Products',
        'Avg Length (chars)',
        'Avg Length (words)',
        'Median Length (chars)',
        'Max Length',
        'Correlation with Price',
        'Correlation with Rating'
    ],
    'value': [
        len(df),
        f"{length_stats['mean_chars']:.0f}",
        f"{length_stats['mean_words']:.1f}",
        f"{length_stats['median_chars']:.0f}",
        f"{length_stats['max_chars']:.0f}",
        f"{correlation:.3f}" if 'correlation' in locals() else 'N/A',
        f"{correlation_rating:.3f}" if 'correlation_rating' in locals() else 'N/A'
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(CSV_OUTPUT, index=False)
print(f"\n  ✅ Saved: {CSV_OUTPUT}")

# Save JSON summary
summary_json = {
    'length_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                          for k, v in length_stats.items()},
    'top_25_keywords': {k: int(v) for k, v in word_counts.most_common(25)},
    'spec_mentions': {k: int(v) for k, v in spec_mentions.items()},
    'correlation_with_price': float(correlation) if 'correlation' in locals() else None,
    'correlation_with_rating': float(correlation_rating) if 'correlation_rating' in locals() else None,
    'brand_statistics': [{k: int(v) if isinstance(v, (np.int64, np.int32)) else float(v) if isinstance(v, (np.float64, np.float32)) else v 
                          for k, v in record.items()} for record in brand_title_df.to_dict('records')]
}

with open('titles_summary.json', 'w') as f:
    json.dump(summary_json, f, indent=2)
print(f"  ✅ Saved: titles_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ TITLES ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/title_length_distribution.png")
print(f"   • {OUTPUT_DIR}/top_title_keywords.png")
print(f"   • {OUTPUT_DIR}/specs_in_titles.png")
print(f"   • {OUTPUT_DIR}/title_length_vs_price.png")
print(f"   • {OUTPUT_DIR}/title_length_by_brand.png")
print(f"   • {CSV_OUTPUT}")
print(f"   • titles_summary.json")
print("=" * 80)

