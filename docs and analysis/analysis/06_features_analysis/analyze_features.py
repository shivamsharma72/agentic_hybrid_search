#!/usr/bin/env python3
"""
Features Analysis for Laptop Products
======================================
Analyzes product features (bullet points in text and array formats).

Key metrics:
- Coverage and completeness
- Number of features per product
- Common feature themes
- Feature quality indicators
- Price/rating correlation with feature count/quality
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
CSV_OUTPUT = "features_analysis.csv"

print("=" * 80)
print("✨ FEATURES ANALYSIS")
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
        features,
        features_array,
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
    'asin', 'title', 'features', 'features_array', 'price', 'rating', 'num_reviews', 'store'
])

# Analysis 1: Coverage
print("\n[3/10] Analyzing features coverage...")

total = len(df)
has_feat = df['features'].notna().sum()
has_feat_array = df['features_array'].notna().sum()
has_non_empty_feat = df[df['features'].notna() & (df['features'].str.len() > 0)].shape[0]

coverage_stats = {
    'total_products': total,
    'has_features_text': has_feat,
    'has_features_array': has_feat_array,
    'has_non_empty_text': has_non_empty_feat,
    'coverage_pct_text': (has_feat / total) * 100,
    'coverage_pct_array': (has_feat_array / total) * 100
}

print(f"\n  📊 Coverage Statistics:")
print(f"     Total products: {total:,}")
print(f"     Has features (text): {has_feat:,} ({coverage_stats['coverage_pct_text']:.2f}%)")
print(f"     Has features_array: {has_feat_array:,} ({coverage_stats['coverage_pct_array']:.2f}%)")
print(f"     Non-empty text: {has_non_empty_feat:,}")

# Missing features
missing = df[df['features'].isna() | (df['features'].str.len() == 0)]
print(f"\n  ⚠️  Missing/empty features: {len(missing):,} ({len(missing)/total*100:.2f}%)")
if len(missing) > 0:
    print(f"     Top brands with missing features:")
    missing_brands = missing['store'].value_counts().head(5)
    for brand, count in missing_brands.items():
        print(f"       • {brand}: {count}")

# Analysis 2: Features Array Statistics
print("\n[4/10] Analyzing features_array...")

df['feature_count'] = df['features_array'].apply(lambda x: len(x) if x and isinstance(x, list) else 0)
df_with_features = df[df['feature_count'] > 0].copy()

if len(df_with_features) > 0:
    count_stats = {
        'mean': df_with_features['feature_count'].mean(),
        'median': df_with_features['feature_count'].median(),
        'min': df_with_features['feature_count'].min(),
        'max': df_with_features['feature_count'].max(),
        'std': df_with_features['feature_count'].std()
    }
    
    print(f"\n  📋 Features Count Statistics:")
    print(f"     Mean: {count_stats['mean']:.2f} features")
    print(f"     Median: {count_stats['median']:.0f} features")
    print(f"     Min: {count_stats['min']:.0f} features")
    print(f"     Max: {count_stats['max']:.0f} features")
    print(f"     Std Dev: {count_stats['std']:.2f}")
    
    # Categorize by feature count
    df_with_features['feature_category'] = pd.cut(
        df_with_features['feature_count'],
        bins=[0, 3, 5, 7, 10, float('inf')],
        labels=['Minimal (1-3)', 'Standard (4-5)', 'Good (6-7)', 'Detailed (8-10)', 'Extensive (10+)']
    )
    
    print(f"\n  📊 Products by Feature Count:")
    for cat in ['Minimal (1-3)', 'Standard (4-5)', 'Good (6-7)', 'Detailed (8-10)', 'Extensive (10+)']:
        count = (df_with_features['feature_category'] == cat).sum()
        pct = (count / len(df_with_features)) * 100
        print(f"     {cat:20s} {count:5,} ({pct:5.2f}%)")

# Visualization 1: Feature count distribution
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.hist(df_with_features['feature_count'], bins=range(0, int(count_stats['max'])+2), 
         color='steelblue', edgecolor='black')
plt.xlabel('Number of Features')
plt.ylabel('Number of Products')
plt.title('Distribution of Feature Counts')
plt.axvline(count_stats['mean'], color='red', linestyle='--', label=f'Mean: {count_stats["mean"]:.1f}')
plt.axvline(count_stats['median'], color='green', linestyle='--', label=f'Median: {count_stats["median"]:.0f}')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.subplot(1, 2, 2)
cat_counts = df_with_features['feature_category'].value_counts()
colors = ['#ff9999', '#ffcc99', '#99ccff', '#99ff99', '#cc99ff']
plt.bar(range(len(cat_counts)), cat_counts.values, color=colors)
plt.xticks(range(len(cat_counts)), cat_counts.index, rotation=15, ha='right')
plt.ylabel('Number of Products')
plt.title('Products by Feature Count Category')
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/feature_count_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/feature_count_distribution.png")

# Analysis 3: Common Feature Themes/Keywords
print("\n[5/10] Analyzing common feature keywords...")

# Extract all features from arrays
all_features = []
for feat_array in df_with_features['features_array']:
    if feat_array and isinstance(feat_array, list):
        all_features.extend(feat_array)

# Extract keywords
all_words = []
for feature in all_features:
    if feature:
        words = re.findall(r'\b[a-z]{4,}\b', str(feature).lower())
        all_words.extend(words)

# Filter stop words
stop_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'more', 'about', 'also', 
              'their', 'which', 'there', 'these', 'been', 'other', 'into', 'such', 'than'}

filtered_words = [w for w in all_words if w not in stop_words]
word_counts = Counter(filtered_words)

print(f"\n  🔤 Top 25 Keywords in Features:")
for i, (word, count) in enumerate(word_counts.most_common(25), 1):
    pct = (count / len(filtered_words)) * 100
    print(f"     {i:2d}. {word:20s} {count:7,} ({pct:4.2f}%)")

# Visualization 2: Top keywords
plt.figure(figsize=(14, 10))
top_words = word_counts.most_common(25)
words, counts = zip(*top_words)
colors = plt.cm.plasma(np.linspace(0, 1, len(words)))
plt.barh(range(len(words)), counts, color=colors)
plt.yticks(range(len(words)), words, fontsize=9)
plt.xlabel('Frequency')
plt.title('Top 25 Keywords in Product Features')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_feature_keywords.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_feature_keywords.png")

# Analysis 4: Feature Themes Detection
print("\n[6/10] Detecting feature themes...")

# Define theme keywords
themes = {
    'Processor/CPU': ['processor', 'intel', 'core', 'amd', 'ryzen', 'ghz', 'cpu'],
    'Memory/RAM': ['memory', 'ram', 'ddr3', 'ddr4', 'ddr5'],
    'Storage': ['storage', 'hard', 'drive', 'ssd', 'nvme', 'emmc'],
    'Display': ['display', 'screen', 'resolution', 'inch', 'full'],
    'Graphics': ['graphics', 'nvidia', 'geforce', 'radeon', 'gpu', 'video'],
    'Battery': ['battery', 'hours', 'life', 'charging'],
    'Connectivity': ['wifi', 'bluetooth', 'wireless', 'ports', 'hdmi', 'usb'],
    'Operating System': ['windows', 'chrome', 'linux', 'macos'],
    'Design': ['thin', 'light', 'portable', 'design', 'aluminum']
}

# Count theme mentions
theme_counts = {theme: 0 for theme in themes}
for feature in all_features:
    if feature:
        feature_lower = str(feature).lower()
        for theme, keywords in themes.items():
            if any(keyword in feature_lower for keyword in keywords):
                theme_counts[theme] += 1

# Sort by count
sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)

print(f"\n  🎨 Feature Themes (% of products mentioning):")
for theme, count in sorted_themes:
    pct = (count / len(df_with_features)) * 100
    print(f"     {theme:20s} {count:5,} ({pct:5.2f}%)")

# Visualization 3: Theme distribution
plt.figure(figsize=(10, 6))
themes_list, counts_list = zip(*sorted_themes)
colors_theme = plt.cm.Set3(range(len(themes_list)))
plt.barh(range(len(themes_list)), counts_list, color=colors_theme)
plt.yticks(range(len(themes_list)), themes_list)
plt.xlabel('Number of Mentions')
plt.title('Feature Themes Distribution')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/feature_themes.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/feature_themes.png")

# Analysis 5: Feature Count vs Price
print("\n[7/10] Analyzing feature count vs price...")

df_price_feat = df_with_features[df_with_features['price'].notna()].copy()

if len(df_price_feat) > 0:
    correlation = df_price_feat['feature_count'].corr(df_price_feat['price'])
    print(f"\n  📊 Correlation (Feature Count vs Price): {correlation:.3f}")
    
    print(f"\n  💰 Average Price by Feature Count:")
    for cat in ['Minimal (1-3)', 'Standard (4-5)', 'Good (6-7)', 'Detailed (8-10)', 'Extensive (10+)']:
        cat_data = df_price_feat[df_price_feat['feature_category'] == cat]
        if len(cat_data) > 0:
            avg_price = cat_data['price'].mean()
            print(f"     {cat:20s} ${avg_price:7.2f}")

# Visualization 4: Feature count vs price
plt.figure(figsize=(10, 6))
sample_size = min(1000, len(df_price_feat))
sample = df_price_feat.sample(sample_size)
plt.scatter(sample['feature_count'], sample['price'], alpha=0.5, s=20)
plt.xlabel('Number of Features')
plt.ylabel('Price ($)')
plt.title(f'Feature Count vs Price (Correlation: {correlation:.3f})')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/feature_count_vs_price.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/feature_count_vs_price.png")

# Analysis 6: Feature Count vs Rating
print("\n[8/10] Analyzing feature count vs rating...")

df_rating_feat = df_with_features[df_with_features['rating'].notna()].copy()

if len(df_rating_feat) > 0:
    correlation_rating = df_rating_feat['feature_count'].corr(df_rating_feat['rating'])
    print(f"\n  📊 Correlation (Feature Count vs Rating): {correlation_rating:.3f}")
    
    print(f"\n  ⭐ Average Rating by Feature Count:")
    for cat in ['Minimal (1-3)', 'Standard (4-5)', 'Good (6-7)', 'Detailed (8-10)', 'Extensive (10+)']:
        cat_data = df_rating_feat[df_rating_feat['feature_category'] == cat]
        if len(cat_data) > 0:
            avg_rating = cat_data['rating'].mean()
            stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
            print(f"     {cat:20s} {avg_rating:.2f} {stars}")

# Analysis 7: Brand Analysis
print("\n[9/10] Analyzing feature count by brand...")

top_brands = df['store'].value_counts().head(10).index
brand_feat_stats = []

for brand in top_brands:
    brand_df = df_with_features[df_with_features['store'] == brand]
    if len(brand_df) > 0:
        brand_feat_stats.append({
            'brand': brand,
            'products': len(brand_df),
            'avg_feature_count': brand_df['feature_count'].mean(),
            'median_feature_count': brand_df['feature_count'].median()
        })

brand_feat_df = pd.DataFrame(brand_feat_stats).sort_values('avg_feature_count', ascending=False)

print(f"\n  🏪 Top 10 Brands - Feature Count:")
for _, row in brand_feat_df.iterrows():
    print(f"     {row['brand']:30s} {row['avg_feature_count']:4.1f} features avg (n={row['products']:,})")

# Visualization 5: Brand comparison
plt.figure(figsize=(12, 6))
plt.barh(range(len(brand_feat_df)), brand_feat_df['avg_feature_count'], color='teal')
plt.yticks(range(len(brand_feat_df)), brand_feat_df['brand'])
plt.xlabel('Average Number of Features')
plt.title('Average Feature Count by Top 10 Brands')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/feature_count_by_brand.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/feature_count_by_brand.png")

# Analysis 8: Export CSV
print("\n[10/10] Generating summary CSV...")

summary_data = {
    'metric': [
        'Total Products',
        'Has Features',
        'Coverage %',
        'Avg Feature Count',
        'Median Feature Count',
        'Max Feature Count',
        'Correlation with Price',
        'Correlation with Rating'
    ],
    'value': [
        total,
        has_feat,
        f"{coverage_stats['coverage_pct_text']:.2f}%",
        f"{count_stats['mean']:.2f}",
        f"{count_stats['median']:.0f}",
        f"{count_stats['max']:.0f}",
        f"{correlation:.3f}" if 'correlation' in locals() else 'N/A',
        f"{correlation_rating:.3f}" if 'correlation_rating' in locals() else 'N/A'
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv(CSV_OUTPUT, index=False)
print(f"  ✅ Saved: {CSV_OUTPUT}")

# Save JSON summary
summary_json = {
    'coverage': {k: int(v) if isinstance(v, (np.int64, np.int32)) else float(v) if isinstance(v, (np.float64, np.float32)) else v 
                 for k, v in coverage_stats.items()},
    'count_statistics': {k: float(v) if isinstance(v, (np.float64, np.float32, np.int64, np.int32)) else v 
                         for k, v in count_stats.items()} if 'count_stats' in locals() else {},
    'top_25_keywords': {k: int(v) for k, v in word_counts.most_common(25)},
    'feature_themes': {k: int(v) for k, v in theme_counts.items()},
    'correlation_with_price': float(correlation) if 'correlation' in locals() else None,
    'correlation_with_rating': float(correlation_rating) if 'correlation_rating' in locals() else None,
    'brand_statistics': [{k: int(v) if isinstance(v, (np.int64, np.int32)) else float(v) if isinstance(v, (np.float64, np.float32)) else v 
                          for k, v in record.items()} for record in brand_feat_df.to_dict('records')] if not brand_feat_df.empty else []
}

with open('features_summary.json', 'w') as f:
    json.dump(summary_json, f, indent=2)
print(f"  ✅ Saved: features_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ FEATURES ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/feature_count_distribution.png")
print(f"   • {OUTPUT_DIR}/top_feature_keywords.png")
print(f"   • {OUTPUT_DIR}/feature_themes.png")
print(f"   • {OUTPUT_DIR}/feature_count_vs_price.png")
print(f"   • {OUTPUT_DIR}/feature_count_by_brand.png")
print(f"   • {CSV_OUTPUT}")
print(f"   • features_summary.json")
print("=" * 80)

