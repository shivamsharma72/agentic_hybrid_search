#!/usr/bin/env python3
"""
Script to create a focused EDA notebook for Headphones category
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = [
    # Title
    ('markdown', '# 🎧 Headphones Market Analysis - Deep Dive EDA\n\n**Amazon Electronics - Headphones Segment**  \n**Date:** October 29, 2025'),
    
    # Setup
    ('markdown', '## Setup & Imports'),
    ('code', '''import pandas as pd
import numpy as np
import psycopg2
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')
print("✅ Libraries loaded!")'''),
    
    # Load Data
    ('markdown', '## 1. Load Headphones Data'),
    ('code', '''conn = psycopg2.connect(
    host="localhost",
    database="amazon_electronics_rag",
    user="shivamsharma",
    port="5432"
)

# Get all headphone-related categories
query = """
SELECT main_category, COUNT(*) as count 
FROM products 
WHERE main_category ILIKE '%headphone%' 
   OR main_category ILIKE '%audio%'
   OR main_category ILIKE '%earbud%'
GROUP BY main_category
ORDER BY count DESC;
"""

categories = pd.read_sql_query(query, conn)
print("🎧 Headphone-related categories:\\n")
print(categories)
print(f"\\nTotal categories: {len(categories)}")'''),
    
    ('code', '''# Load all headphone products
# Based on the categories found above, adjust the filter
query = """
SELECT parent_asin, title, description, features, average_rating, 
       rating_number, price, main_category, store, images, blair_embedding
FROM products 
WHERE main_category IN (
    'Headphones', 'Home Audio & Theater', 'Portable Audio & Accessories',
    'Earbud Headphones', 'Over-Ear Headphones', 'On-Ear Headphones',
    'In-Ear Headphones'
)
OR title ILIKE '%headphone%'
OR title ILIKE '%earbud%'
OR title ILIKE '%earphone%'
OR title ILIKE '%airpod%';
"""

df = pd.read_sql_query(query, conn)
conn.close()

print(f"✅ Loaded {len(df):,} headphone products")
print(f"   Columns: {df.shape[1]}")
print(f"\\nCategory breakdown:")
print(df['main_category'].value_counts().head(10))'''),
    
    # Filter to actual headphones
    ('markdown', '## 2. Filter to Pure Headphone Products'),
    ('code', '''# Filter by title keywords to ensure we only get actual headphones
headphone_keywords = ['headphone', 'earbud', 'earphone', 'airpod', 'earpiece', 
                      'in-ear', 'over-ear', 'on-ear', 'bluetooth headset']

def is_headphone(title):
    title_lower = str(title).lower()
    return any(keyword in title_lower for keyword in headphone_keywords)

df['is_headphone'] = df['title'].apply(is_headphone)
df_hp = df[df['is_headphone']].copy()

print(f"📊 Filtered to {len(df_hp):,} pure headphone products")
print(f"   Removed {len(df) - len(df_hp):,} non-headphone products")
print(f"\\nPrice data: {df_hp['price'].notna().sum():,} products ({df_hp['price'].notna().sum()/len(df_hp)*100:.1f}%)")
print(f"Rating data: {df_hp['average_rating'].notna().sum():,} products ({df_hp['average_rating'].notna().sum()/len(df_hp)*100:.1f}%)")'''),
    
    # Feature Engineering
    ('markdown', '## 3. Feature Engineering for Headphones'),
    ('code', '''print("🔧 Creating headphone-specific features...\\n")

# Price segments
df_hp['price_segment'] = pd.cut(
    df_hp['price'], 
    bins=[0, 20, 50, 100, 200, 1000], 
    labels=['Budget (<$20)', 'Entry ($20-50)', 'Mid-Range ($50-100)', 
            'Premium ($100-200)', 'Luxury (>$200)']
)

# Rating tiers
df_hp['rating_tier'] = pd.cut(
    df_hp['average_rating'],
    bins=[0, 3.5, 4.0, 4.5, 5.0],
    labels=['Below Avg (<3.5)', 'Average (3.5-4.0)', 'Good (4.0-4.5)', 'Excellent (4.5-5.0)']
)

# Review volume
df_hp['review_volume'] = pd.cut(
    df_hp['rating_number'],
    bins=[-1, 50, 200, 1000, 100000],
    labels=['Low (<50)', 'Medium (50-200)', 'High (200-1K)', 'Very High (>1K)']
)

# Headphone type detection
def detect_type(title):
    title_lower = str(title).lower()
    if 'wireless' in title_lower or 'bluetooth' in title_lower:
        return 'Wireless'
    elif 'wired' in title_lower or 'cable' in title_lower:
        return 'Wired'
    else:
        return 'Unknown'

def detect_form_factor(title):
    title_lower = str(title).lower()
    if 'earbud' in title_lower or 'in-ear' in title_lower or 'airpod' in title_lower:
        return 'Earbuds/In-Ear'
    elif 'over-ear' in title_lower or 'over ear' in title_lower:
        return 'Over-Ear'
    elif 'on-ear' in title_lower or 'on ear' in title_lower:
        return 'On-Ear'
    else:
        return 'Unknown'

df_hp['connectivity'] = df_hp['title'].apply(detect_type)
df_hp['form_factor'] = df_hp['title'].apply(detect_form_factor)

# Brand extraction
df_hp['brand'] = df_hp['title'].str.split().str[0]

# Popularity score
scaler = MinMaxScaler()
df_hp['popularity_score'] = (
    scaler.fit_transform(df_hp[['rating_number']].fillna(0)) * 0.6 +
    scaler.fit_transform(df_hp[['average_rating']].fillna(0)) * 0.4
).flatten()

# Value score (lower price per rating = better value)
df_hp['value_score'] = df_hp['price'] / (df_hp['average_rating'] + 0.01)

print("✅ Created features:")
print("   • price_segment, rating_tier, review_volume")
print("   • connectivity (Wireless/Wired)")
print("   • form_factor (Earbuds/Over-Ear/On-Ear)")
print("   • popularity_score, value_score")
print(f"\\n📊 Dataset now has {df_hp.shape[1]} columns")'''),
    
    # Overview Stats
    ('markdown', '## 4. Market Overview Statistics'),
    ('code', '''print("="*70)
print("🎧 HEADPHONES MARKET OVERVIEW")
print("="*70)
print(f"Total Products: {len(df_hp):,}")
print(f"\\nPRICE:")
print(f"  • Median: ${df_hp['price'].median():.2f}")
print(f"  • Mean: ${df_hp['price'].mean():.2f}")
print(f"  • Range: ${df_hp['price'].min():.2f} - ${df_hp['price'].max():.2f}")
print(f"\\nRATINGS:")
print(f"  • Average: {df_hp['average_rating'].mean():.2f}★")
print(f"  • Median reviews: {df_hp['rating_number'].median():.0f}")
print(f"  • Products with 4.5+★: {len(df_hp[df_hp['average_rating'] >= 4.5]):,} ({len(df_hp[df_hp['average_rating'] >= 4.5])/len(df_hp)*100:.1f}%)")
print(f"\\nCONNECTIVITY:")
print(df_hp['connectivity'].value_counts())
print(f"\\nFORM FACTOR:")
print(df_hp['form_factor'].value_counts())
print(f"\\nTOP 5 BRANDS:")
print(df_hp['brand'].value_counts().head(5))
print("="*70)'''),
    
    # Price Analysis
    ('markdown', '## 5. Price Segment Analysis'),
    ('code', '''fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Products per price segment
price_counts = df_hp['price_segment'].value_counts().sort_index()
axes[0,0].bar(range(len(price_counts)), price_counts.values, color='teal', edgecolor='black')
axes[0,0].set_xticks(range(len(price_counts)))
axes[0,0].set_xticklabels(price_counts.index, rotation=45, ha='right')
axes[0,0].set_ylabel('Number of Products')
axes[0,0].set_title('Headphones by Price Segment', fontweight='bold', fontsize=12)
axes[0,0].grid(axis='y', alpha=0.3)

# Rating by price segment
price_rating = df_hp.groupby('price_segment')['average_rating'].mean().sort_index()
axes[0,1].plot(range(len(price_rating)), price_rating.values, marker='o', linewidth=3, markersize=10, color='red')
axes[0,1].set_xticks(range(len(price_rating)))
axes[0,1].set_xticklabels(price_rating.index, rotation=45, ha='right')
axes[0,1].set_ylabel('Average Rating')
axes[0,1].set_title('Rating by Price Segment', fontweight='bold', fontsize=12)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_ylim([3.5, 4.5])

# Price distribution
valid_prices = df_hp['price'].dropna()
axes[1,0].hist(valid_prices, bins=50, color='purple', alpha=0.7, edgecolor='black')
axes[1,0].set_xlabel('Price ($)')
axes[1,0].set_ylabel('Frequency')
axes[1,0].set_title('Price Distribution', fontweight='bold', fontsize=12)
axes[1,0].axvline(valid_prices.median(), color='red', linestyle='--', linewidth=2, label=f'Median: ${valid_prices.median():.2f}')
axes[1,0].legend()
axes[1,0].grid(axis='y', alpha=0.3)

# Reviews by price segment
price_reviews = df_hp.groupby('price_segment')['rating_number'].median().sort_index()
axes[1,1].bar(range(len(price_reviews)), price_reviews.values, color='orange', edgecolor='black')
axes[1,1].set_xticks(range(len(price_reviews)))
axes[1,1].set_xticklabels(price_reviews.index, rotation=45, ha='right')
axes[1,1].set_ylabel('Median Review Count')
axes[1,1].set_title('Review Volume by Price', fontweight='bold', fontsize=12)
axes[1,1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\\n💰 Most common: {price_counts.idxmax()} ({price_counts.max():,} products)")
print(f"⭐ Highest rated: {price_rating.idxmax()} ({price_rating.max():.2f}★)")
print(f"📈 Most reviewed: {price_reviews.idxmax()} ({price_reviews.max():.0f} median reviews)")'''),
    
    # Connectivity Analysis
    ('markdown', '## 6. Wireless vs Wired Analysis'),
    ('code', '''# Compare wireless vs wired
conn_data = df_hp[df_hp['connectivity'].isin(['Wireless', 'Wired'])].copy()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Count
conn_counts = conn_data['connectivity'].value_counts()
axes[0,0].bar(conn_counts.index, conn_counts.values, color=['blue', 'green'], edgecolor='black')
axes[0,0].set_ylabel('Number of Products')
axes[0,0].set_title('Product Count: Wireless vs Wired', fontweight='bold', fontsize=12)
axes[0,0].grid(axis='y', alpha=0.3)

# Price comparison
conn_data.boxplot(column='price', by='connectivity', ax=axes[0,1])
axes[0,1].set_title('Price Distribution: Wireless vs Wired', fontweight='bold', fontsize=12)
axes[0,1].set_xlabel('Connectivity')
axes[0,1].set_ylabel('Price ($)')
plt.sca(axes[0,1])
plt.xticks(rotation=0)

# Rating comparison
conn_ratings = conn_data.groupby('connectivity')['average_rating'].mean()
axes[1,0].bar(conn_ratings.index, conn_ratings.values, color=['blue', 'green'], edgecolor='black')
axes[1,0].set_ylabel('Average Rating')
axes[1,0].set_title('Average Rating: Wireless vs Wired', fontweight='bold', fontsize=12)
axes[1,0].set_ylim([3.5, 4.5])
axes[1,0].grid(axis='y', alpha=0.3)

# Review volume
conn_reviews = conn_data.groupby('connectivity')['rating_number'].median()
axes[1,1].bar(conn_reviews.index, conn_reviews.values, color=['blue', 'green'], edgecolor='black')
axes[1,1].set_ylabel('Median Review Count')
axes[1,1].set_title('Review Volume: Wireless vs Wired', fontweight='bold', fontsize=12)
axes[1,1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

print("\\n📊 WIRELESS vs WIRED COMPARISON:")
for conn_type in ['Wireless', 'Wired']:
    data = conn_data[conn_data['connectivity'] == conn_type]
    print(f"\\n{conn_type}:")
    print(f"  • Count: {len(data):,}")
    print(f"  • Median Price: ${data['price'].median():.2f}")
    print(f"  • Avg Rating: {data['average_rating'].mean():.2f}★")
    print(f"  • Median Reviews: {data['rating_number'].median():.0f}")'''),
    
    # Form Factor Analysis
    ('markdown', '## 7. Form Factor Analysis (Earbuds vs Over-Ear vs On-Ear)'),
    ('code', '''# Filter known form factors
ff_data = df_hp[df_hp['form_factor'] != 'Unknown'].copy()

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# Count
ff_counts = ff_data['form_factor'].value_counts()
axes[0,0].barh(range(len(ff_counts)), ff_counts.values, color='coral', edgecolor='black')
axes[0,0].set_yticks(range(len(ff_counts)))
axes[0,0].set_yticklabels(ff_counts.index)
axes[0,0].set_xlabel('Number of Products')
axes[0,0].set_title('Product Count by Form Factor', fontweight='bold', fontsize=12)
axes[0,0].invert_yaxis()
axes[0,0].grid(axis='x', alpha=0.3)

# Price by form factor
ff_price = ff_data.groupby('form_factor')['price'].median().sort_values(ascending=False)
axes[0,1].barh(range(len(ff_price)), ff_price.values, color='gold', edgecolor='black')
axes[0,1].set_yticks(range(len(ff_price)))
axes[0,1].set_yticklabels(ff_price.index)
axes[0,1].set_xlabel('Median Price ($)')
axes[0,1].set_title('Price by Form Factor', fontweight='bold', fontsize=12)
axes[0,1].invert_yaxis()
axes[0,1].grid(axis='x', alpha=0.3)

# Rating by form factor
ff_rating = ff_data.groupby('form_factor')['average_rating'].mean().sort_values(ascending=False)
axes[1,0].barh(range(len(ff_rating)), ff_rating.values, color='lightblue', edgecolor='black')
axes[1,0].set_yticks(range(len(ff_rating)))
axes[1,0].set_yticklabels(ff_rating.index)
axes[1,0].set_xlabel('Average Rating')
axes[1,0].set_title('Rating by Form Factor', fontweight='bold', fontsize=12)
axes[1,0].invert_yaxis()
axes[1,0].set_xlim([3.5, 4.5])
axes[1,0].grid(axis='x', alpha=0.3)

# Review volume
ff_reviews = ff_data.groupby('form_factor')['rating_number'].median().sort_values(ascending=False)
axes[1,1].barh(range(len(ff_reviews)), ff_reviews.values, color='lightgreen', edgecolor='black')
axes[1,1].set_yticks(range(len(ff_reviews)))
axes[1,1].set_yticklabels(ff_reviews.index)
axes[1,1].set_xlabel('Median Review Count')
axes[1,1].set_title('Review Volume by Form Factor', fontweight='bold', fontsize=12)
axes[1,1].invert_yaxis()
axes[1,1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.show()

print("\\n🎧 FORM FACTOR COMPARISON:")
for ff in ff_counts.index:
    data = ff_data[ff_data['form_factor'] == ff]
    print(f"\\n{ff}:")
    print(f"  • Count: {len(data):,}")
    print(f"  • Median Price: ${data['price'].median():.2f}")
    print(f"  • Avg Rating: {data['average_rating'].mean():.2f}★")
    print(f"  • Median Reviews: {data['rating_number'].median():.0f}")'''),
    
    # Top Brands
    ('markdown', '## 8. Top Brands Analysis'),
    ('code', '''top_brands = df_hp['brand'].value_counts().head(20)

fig, axes = plt.subplots(1, 2, figsize=(18, 6))

# Top 20 brands by count
axes[0].barh(range(len(top_brands)), top_brands.values, color='darkblue', edgecolor='black')
axes[0].set_yticks(range(len(top_brands)))
axes[0].set_yticklabels(top_brands.index)
axes[0].set_xlabel('Number of Products')
axes[0].set_title('Top 20 Headphone Brands', fontweight='bold', fontsize=12)
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3)

# Top brands by rating (min 20 products)
brand_stats = df_hp.groupby('brand').agg({
    'average_rating': 'mean',
    'parent_asin': 'count',
    'price': 'median'
}).rename(columns={'parent_asin': 'count'})
brand_stats = brand_stats[brand_stats['count'] >= 20]
top_rated_brands = brand_stats.nlargest(20, 'average_rating')

axes[1].barh(range(len(top_rated_brands)), top_rated_brands['average_rating'].values, color='green', edgecolor='black')
axes[1].set_yticks(range(len(top_rated_brands)))
axes[1].set_yticklabels(top_rated_brands.index)
axes[1].set_xlabel('Average Rating')
axes[1].set_title('Top 20 Brands by Rating (≥20 products)', fontweight='bold', fontsize=12)
axes[1].invert_yaxis()
axes[1].set_xlim([4.0, 4.8])
axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\\n🏆 Most products: {top_brands.index[0]} ({top_brands.values[0]:,})")
print(f"🌟 Highest rated: {top_rated_brands.index[0]} ({top_rated_brands.iloc[0]['average_rating']:.2f}★)")
print(f"🏷️  Total brands: {df_hp['brand'].nunique():,}")'''),
    
    # TF-IDF Keywords
    ('markdown', '## 9. Headphone-Specific Keywords (TF-IDF)'),
    ('code', '''print("📝 Analyzing headphone keywords...\\n")

titles = df_hp['title'].fillna('').str.lower()
tfidf = TfidfVectorizer(max_features=50, stop_words='english', ngram_range=(1, 2))
tfidf_matrix = tfidf.fit_transform(titles)

feature_names = tfidf.get_feature_names_out()
tfidf_scores = tfidf_matrix.sum(axis=0).A1
top_terms = sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)[:20]

print("Top 20 Headphone-Specific Keywords:\\n")
for i, (term, score) in enumerate(top_terms, 1):
    print(f"{i:2d}. {term:30s} {score:10,.1f}")

terms, scores = zip(*top_terms[:15])
plt.figure(figsize=(12, 7))
plt.barh(range(len(terms)), scores, color='purple', edgecolor='black')
plt.yticks(range(len(terms)), terms)
plt.xlabel('TF-IDF Score')
plt.title('Top 15 Headphone Keywords', fontweight='bold', fontsize=14)
plt.gca().invert_yaxis()
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()'''),
    
    # Best Value
    ('markdown', '## 10. Best Value Headphones'),
    ('code', '''# Find best value headphones (high rating, low price per rating)
high_rated_hp = df_hp[df_hp['average_rating'] >= 4.0].copy()
best_value_hp = high_rated_hp.nsmallest(20, 'value_score')[['title', 'price', 'average_rating', 'rating_number', 'connectivity', 'value_score']]

plt.figure(figsize=(14, 8))
plt.barh(range(len(best_value_hp)), best_value_hp['value_score'].values, color='green', edgecolor='black')
plt.yticks(range(len(best_value_hp)), [t[:50] + '...' for t in best_value_hp['title']])
plt.xlabel('Value Score (Lower = Better)')
plt.title('Top 20 Best Value Headphones (Rating ≥ 4.0★)', fontweight='bold', fontsize=14)
plt.gca().invert_yaxis()
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()

print("\\n💎 TOP 5 BEST VALUE HEADPHONES:\\n")
for i, (idx, row) in enumerate(best_value_hp.head(5).iterrows(), 1):
    print(f"{i}. {row['title'][:60]}...")
    print(f"   Price: ${row['price']:.2f} | Rating: {row['average_rating']:.2f}★ | Reviews: {row['rating_number']:,}")
    print(f"   Type: {row['connectivity']} | Value Score: {row['value_score']:.2f}")
    print()'''),
    
    # Most Popular
    ('markdown', '## 11. Most Popular Headphones'),
    ('code', '''top_popular_hp = df_hp.nlargest(20, 'popularity_score')[['title', 'popularity_score', 'average_rating', 'rating_number', 'price', 'connectivity']]

plt.figure(figsize=(14, 8))
plt.barh(range(len(top_popular_hp)), top_popular_hp['popularity_score'].values, color='red', edgecolor='black')
plt.yticks(range(len(top_popular_hp)), [t[:50] + '...' for t in top_popular_hp['title']])
plt.xlabel('Popularity Score')
plt.title('Top 20 Most Popular Headphones', fontweight='bold', fontsize=14)
plt.gca().invert_yaxis()
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()

print("\\n🌟 TOP 5 MOST POPULAR HEADPHONES:\\n")
for i, (idx, row) in enumerate(top_popular_hp.head(5).iterrows(), 1):
    print(f"{i}. {row['title'][:60]}...")
    print(f"   Price: ${row['price']:.2f} | Rating: {row['average_rating']:.2f}★ | Reviews: {row['rating_number']:,}")
    print(f"   Type: {row['connectivity']} | Popularity: {row['popularity_score']:.3f}")
    print()'''),
    
    # Export
    ('markdown', '## 12. Export Results & Summary'),
    ('code', '''print("💾 Exporting results...\\n")

# Export enhanced dataset
export_cols = ['parent_asin', 'title', 'price', 'average_rating', 'rating_number',
               'price_segment', 'connectivity', 'form_factor', 'brand',
               'popularity_score', 'value_score']
df_hp[export_cols].to_csv('headphones_analysis.csv', index=False)
print("✅ headphones_analysis.csv")

# Top brands
top_brands.to_csv('headphones_top_brands.csv')
print("✅ headphones_top_brands.csv")

# Best value list
best_value_hp.to_csv('headphones_best_value.csv', index=False)
print("✅ headphones_best_value.csv")

# Summary report
summary = f"""
{'='*70}
🎧 HEADPHONES MARKET ANALYSIS SUMMARY
{'='*70}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

OVERVIEW:
• Total Products: {len(df_hp):,}
• With Price Data: {df_hp['price'].notna().sum():,} ({df_hp['price'].notna().sum()/len(df_hp)*100:.1f}%)
• With Ratings: {df_hp['average_rating'].notna().sum():,} ({df_hp['average_rating'].notna().sum()/len(df_hp)*100:.1f}%)

PRICING:
• Median Price: ${df_hp['price'].median():.2f}
• Mean Price: ${df_hp['price'].mean():.2f}
• Price Range: ${df_hp['price'].min():.2f} - ${df_hp['price'].max():.2f}
• Most Common Segment: {df_hp['price_segment'].value_counts().index[0]}

QUALITY:
• Average Rating: {df_hp['average_rating'].mean():.2f}★
• Products ≥4.5★: {len(df_hp[df_hp['average_rating'] >= 4.5]):,} ({len(df_hp[df_hp['average_rating'] >= 4.5])/len(df_hp)*100:.1f}%)
• Median Reviews: {df_hp['rating_number'].median():.0f}

CONNECTIVITY:
• Wireless: {len(df_hp[df_hp['connectivity'] == 'Wireless']):,}
• Wired: {len(df_hp[df_hp['connectivity'] == 'Wired']):,}
• Wireless Premium: ${df_hp[df_hp['connectivity'] == 'Wireless']['price'].median():.2f} median

FORM FACTOR:
{df_hp['form_factor'].value_counts().to_string()}

TOP BRANDS:
{df_hp['brand'].value_counts().head(5).to_string()}

KEY INSIGHTS:
1. Budget segment (<$20) has {price_counts.values[0]:,} products
2. Wireless headphones dominate the market
3. Earbuds/In-Ear is the most popular form factor
4. {top_brands.index[0]} has the most products ({top_brands.values[0]:,})
5. Best value: {best_value_hp.iloc[0]['title'][:50]}...

{'='*70}
"""

with open('headphones_summary.txt', 'w') as f:
    f.write(summary)
print("✅ headphones_summary.txt")

print("\\n" + summary)
print("\\n✅ Analysis complete! All files exported.")'''),
]

# Add cells to notebook
for cell_type, content in cells:
    if cell_type == 'markdown':
        nb['cells'].append(nbf.v4.new_markdown_cell(content))
    else:
        nb['cells'].append(nbf.v4.new_code_cell(content))

# Save notebook
with open('headphones_eda.ipynb', 'w') as f:
    nbf.write(nb, f)

print('✅ Created: headphones_eda.ipynb')
print('📁 Location: eda/headphones_eda.ipynb')
print('\\n👉 Open in Jupyter at: http://localhost:8890')
print('\\n📊 This notebook will analyze:')
print('   • Price segments & trends')
print('   • Wireless vs Wired comparison')
print('   • Form factors (Earbuds/Over-Ear/On-Ear)')
print('   • Top brands & ratings')
print('   • Best value products')
print('   • Most popular headphones')
print('   • Headphone-specific keywords')

