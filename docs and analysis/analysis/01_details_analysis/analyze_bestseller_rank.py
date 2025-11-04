#!/usr/bin/env python3
"""
Deep Analysis of Best Seller Rank in Product Details
====================================================
Analyzes the "Best Sellers Rank" field within the JSONB details column.

Key metrics:
- Rank distribution (overall and category-specific)
- Correlation with price, rating, review count
- Top 100, Top 1000 analysis
- Category-specific rankings
- What makes a bestseller?
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
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

print("=" * 80)
print("🏆 BEST SELLER RANK ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/8] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch products with bestseller rank
print("\n[2/8] Fetching products with bestseller rank...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        details,
        price,
        average_rating,
        rating_number,
        store
    FROM products_backup
    WHERE details IS NOT NULL
    AND details::text LIKE '%Best Sellers Rank%';
""")

products = cur.fetchall()
print(f"  ✅ Found {len(products):,} products with bestseller rank")

# Parse bestseller ranks
print("\n[3/8] Parsing bestseller rank data...")

def extract_ranks(details_json):
    """Extract all rank numbers and categories from details"""
    ranks = []
    
    if not details_json:
        return ranks
    
    for key, value in details_json.items():
        # Look for any key containing 'rank' (case insensitive)
        if 'rank' in key.lower():
            value_str = str(value)
            
            # Try multiple patterns to extract rank numbers
            # Pattern 1: "#45,921 in Electronics"
            matches = re.findall(r'#([\d,]+)\s+in\s+([^()\n]+?)(?:\s+\(|$)', value_str)
            for rank_str, category in matches:
                rank_num = int(rank_str.replace(',', ''))
                ranks.append({
                    'rank': rank_num,
                    'category': category.strip(),
                    'raw_text': value_str
                })
            
            # Pattern 2: Just numbers with commas (fallback)
            if not matches:
                rank_matches = re.findall(r'#?([\d,]+)', value_str)
                for rank_str in rank_matches:
                    # Only consider if it looks like a rank (> 100)
                    try:
                        rank_num = int(rank_str.replace(',', ''))
                        if rank_num >= 1:
                            # Try to find category nearby
                            category = 'Overall'
                            if 'electronics' in value_str.lower():
                                category = 'Electronics'
                            elif 'laptop' in value_str.lower() or 'computer' in value_str.lower():
                                category = 'Laptops & Computers'
                            
                            ranks.append({
                                'rank': rank_num,
                                'category': category,
                                'raw_text': value_str
                            })
                            break  # Only take first valid rank per field
                    except ValueError:
                        continue
    
    return ranks

rank_data = []
sample_printed = False

for parent_asin, title, details, price, rating, num_reviews, store in products:
    ranks = extract_ranks(details)
    
    # Print first sample for debugging
    if not sample_printed and ranks:
        print(f"\n  🔍 Sample rank data:")
        print(f"     ASIN: {parent_asin}")
        print(f"     Ranks found: {len(ranks)}")
        for r in ranks[:3]:
            print(f"       - Rank #{r['rank']:,} in {r['category']}")
        sample_printed = True
    
    for rank_info in ranks:
        rank_data.append({
            'asin': parent_asin,
            'title': title,
            'rank': rank_info['rank'],
            'category': rank_info['category'],
            'price': price,
            'rating': rating,
            'num_reviews': num_reviews,
            'store': store
        })

# Check if we found any ranks
if not rank_data:
    print(f"\n  ⚠️  WARNING: No rank data extracted!")
    print(f"  📋 Let's examine a sample 'details' field...")
    
    # Print a sample details structure
    for parent_asin, title, details, price, rating, num_reviews, store in products[:3]:
        print(f"\n  Sample ASIN: {parent_asin}")
        print(f"  Title: {title[:60]}...")
        print(f"  Details keys: {list(details.keys()) if details else 'None'}")
        if details:
            for key, value in list(details.items())[:5]:
                print(f"    - {key}: {str(value)[:80]}")
    
    print("\n" + "=" * 80)
    print("❌ ANALYSIS STOPPED: No bestseller rank data found")
    print("=" * 80)
    print("\nPossible reasons:")
    print("  1. The 'Best Sellers Rank' key might have a different name")
    print("  2. The rank format might be different than expected")
    print("  3. Very few products have rank data")
    print("\nPlease review the sample output above and update the extract_ranks() function.")
    print("=" * 80)
    
    cur.close()
    conn.close()
    exit(1)

df = pd.DataFrame(rank_data)
print(f"\n  ✅ Extracted {len(df):,} rank entries from {len(products):,} products")
print(f"  📊 Products with ranks: {df['asin'].nunique():,}")

# Analysis 1: Overall Rank Distribution
print("\n[4/8] Analyzing rank distributions...")

df_overall = df[df['category'].str.contains('Electronics', case=False, na=False)]
print(f"\n  📊 Overall Electronics Ranks: {len(df_overall):,} products")

if len(df_overall) > 0:
    print(f"     Best rank: #{df_overall['rank'].min():,}")
    print(f"     Worst rank: #{df_overall['rank'].max():,}")
    print(f"     Median rank: #{df_overall['rank'].median():,.0f}")
    print(f"     Mean rank: #{df_overall['rank'].mean():,.0f}")
    
    # Top performers
    top_100 = df_overall[df_overall['rank'] <= 100]
    top_1000 = df_overall[df_overall['rank'] <= 1000]
    top_10000 = df_overall[df_overall['rank'] <= 10000]
    
    print(f"\n  🏆 Performance Tiers:")
    print(f"     Top 100: {len(top_100):,} products ({len(top_100)/len(df_overall)*100:.1f}%)")
    print(f"     Top 1,000: {len(top_1000):,} products ({len(top_1000)/len(df_overall)*100:.1f}%)")
    print(f"     Top 10,000: {len(top_10000):,} products ({len(top_10000)/len(df_overall)*100:.1f}%)")

# Visualization 1: Rank Distribution
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(df_overall['rank'], bins=50, color='skyblue', edgecolor='black')
plt.xlabel('Best Seller Rank')
plt.ylabel('Number of Products')
plt.title('Distribution of Best Seller Ranks')
plt.yscale('log')

plt.subplot(1, 2, 2)
# Focus on top ranks
top_ranks = df_overall[df_overall['rank'] <= 50000]
plt.hist(top_ranks['rank'], bins=50, color='coral', edgecolor='black')
plt.xlabel('Best Seller Rank')
plt.ylabel('Number of Products')
plt.title('Distribution (Top 50,000 only)')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/bestseller_rank_distribution.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/bestseller_rank_distribution.png")

# Analysis 2: Rank vs Price
print("\n[5/8] Analyzing rank vs. price correlation...")
df_with_price = df_overall[df_overall['price'].notna()].copy()

if len(df_with_price) > 0:
    correlation = df_with_price['rank'].corr(df_with_price['price'])
    print(f"  📊 Correlation (Rank vs Price): {correlation:.3f}")
    
    # Price by rank tier
    df_with_price['rank_tier'] = pd.cut(df_with_price['rank'], 
                                         bins=[0, 100, 1000, 10000, 100000, float('inf')],
                                         labels=['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+'])
    
    print(f"\n  💰 Average Price by Rank Tier:")
    for tier in ['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+']:
        tier_data = df_with_price[df_with_price['rank_tier'] == tier]
        if len(tier_data) > 0:
            avg_price = tier_data['price'].mean()
            print(f"     {tier:10s} ${avg_price:7.2f} ({len(tier_data):,} products)")

# Visualization 2: Rank vs Price
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
# Scatter plot
sample_size = min(1000, len(df_with_price))
sample = df_with_price.sample(sample_size)
plt.scatter(sample['rank'], sample['price'], alpha=0.5, s=20)
plt.xlabel('Best Seller Rank')
plt.ylabel('Price ($)')
plt.title('Best Seller Rank vs. Price')
plt.xscale('log')

plt.subplot(1, 2, 2)
# Box plot by tier
df_with_price[df_with_price['rank_tier'].isin(['Top 100', 'Top 1K', 'Top 10K'])].boxplot(
    column='price', by='rank_tier', ax=plt.gca()
)
plt.xlabel('Rank Tier')
plt.ylabel('Price ($)')
plt.title('Price Distribution by Rank Tier')
plt.suptitle('')  # Remove default title

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rank_vs_price.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/rank_vs_price.png")

# Analysis 3: Rank vs Rating
print("\n[6/8] Analyzing rank vs. rating correlation...")
df_with_rating = df_overall[df_overall['rating'].notna()].copy()

if len(df_with_rating) > 0:
    correlation = df_with_rating['rank'].corr(df_with_rating['rating'])
    print(f"  📊 Correlation (Rank vs Rating): {correlation:.3f}")
    
    # Rating by rank tier
    df_with_rating['rank_tier'] = pd.cut(df_with_rating['rank'], 
                                          bins=[0, 100, 1000, 10000, 100000, float('inf')],
                                          labels=['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+'])
    
    print(f"\n  ⭐ Average Rating by Rank Tier:")
    for tier in ['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+']:
        tier_data = df_with_rating[df_with_rating['rank_tier'] == tier]
        if len(tier_data) > 0:
            avg_rating = tier_data['rating'].mean()
            print(f"     {tier:10s} {avg_rating:.2f} ⭐ ({len(tier_data):,} products)")

# Visualization 3: Rank vs Rating
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
# Scatter plot
sample_size = min(1000, len(df_with_rating))
sample = df_with_rating.sample(sample_size)
plt.scatter(sample['rank'], sample['rating'], alpha=0.5, s=20, c=sample['rating'], cmap='RdYlGn')
plt.colorbar(label='Rating')
plt.xlabel('Best Seller Rank')
plt.ylabel('Rating (1-5)')
plt.title('Best Seller Rank vs. Rating')
plt.xscale('log')

plt.subplot(1, 2, 2)
# Box plot by tier
df_with_rating[df_with_rating['rank_tier'].isin(['Top 100', 'Top 1K', 'Top 10K'])].boxplot(
    column='rating', by='rank_tier', ax=plt.gca()
)
plt.xlabel('Rank Tier')
plt.ylabel('Rating (1-5)')
plt.title('Rating Distribution by Rank Tier')
plt.suptitle('')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rank_vs_rating.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/rank_vs_rating.png")

# Analysis 4: Rank vs Review Count
print("\n[7/8] Analyzing rank vs. review count...")
df_with_reviews = df_overall[df_overall['num_reviews'].notna()].copy()

if len(df_with_reviews) > 0:
    correlation = df_with_reviews['rank'].corr(df_with_reviews['num_reviews'])
    print(f"  📊 Correlation (Rank vs Review Count): {correlation:.3f}")
    
    print(f"\n  💬 Average Reviews by Rank Tier:")
    df_with_reviews['rank_tier'] = pd.cut(df_with_reviews['rank'], 
                                           bins=[0, 100, 1000, 10000, 100000, float('inf')],
                                           labels=['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+'])
    
    for tier in ['Top 100', 'Top 1K', 'Top 10K', 'Top 100K', '100K+']:
        tier_data = df_with_reviews[df_with_reviews['rank_tier'] == tier]
        if len(tier_data) > 0:
            avg_reviews = tier_data['num_reviews'].mean()
            print(f"     {tier:10s} {avg_reviews:7.0f} reviews ({len(tier_data):,} products)")

# Visualization 4: Rank vs Review Count
plt.figure(figsize=(10, 6))
sample_size = min(1000, len(df_with_reviews))
sample = df_with_reviews.sample(sample_size)
plt.scatter(sample['rank'], sample['num_reviews'], alpha=0.5, s=20)
plt.xlabel('Best Seller Rank')
plt.ylabel('Number of Reviews')
plt.title('Best Seller Rank vs. Review Count')
plt.xscale('log')
plt.yscale('log')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/rank_vs_reviews.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/rank_vs_reviews.png")

# Analysis 5: Top Brands in Bestsellers
print("\n[8/8] Analyzing top brands in bestsellers...")
top_1000_products = df_overall[df_overall['rank'] <= 1000]

if len(top_1000_products) > 0 and top_1000_products['store'].notna().any():
    brand_counts = top_1000_products['store'].value_counts().head(15)
    
    print(f"\n  🏆 Top 15 Brands in Top 1,000 Bestsellers:")
    for i, (brand, count) in enumerate(brand_counts.items(), 1):
        pct = (count / len(top_1000_products)) * 100
        print(f"     {i:2d}. {brand:30s} {count:3d} ({pct:5.1f}%)")
    
    # Visualization: Top brands
    plt.figure(figsize=(12, 8))
    plt.barh(range(len(brand_counts)), brand_counts.values, color='gold')
    plt.yticks(range(len(brand_counts)), brand_counts.index)
    plt.xlabel('Number of Products in Top 1,000')
    plt.title('Top Brands in Best Sellers (Top 1,000)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/top_brands_bestsellers.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/top_brands_bestsellers.png")

# Save summary
summary = {
    'total_products_with_ranks': df['asin'].nunique(),
    'total_rank_entries': len(df),
    'overall_electronics_ranks': len(df_overall),
    'rank_statistics': {
        'min': int(df_overall['rank'].min()) if len(df_overall) > 0 else None,
        'max': int(df_overall['rank'].max()) if len(df_overall) > 0 else None,
        'median': float(df_overall['rank'].median()) if len(df_overall) > 0 else None,
        'mean': float(df_overall['rank'].mean()) if len(df_overall) > 0 else None
    },
    'top_performers': {
        'top_100': len(top_100) if 'top_100' in locals() else 0,
        'top_1000': len(top_1000) if 'top_1000' in locals() else 0,
        'top_10000': len(top_10000) if 'top_10000' in locals() else 0
    },
    'correlations': {
        'rank_vs_price': float(df_with_price['rank'].corr(df_with_price['price'])) if len(df_with_price) > 0 else None,
        'rank_vs_rating': float(df_with_rating['rank'].corr(df_with_rating['rating'])) if len(df_with_rating) > 0 else None,
        'rank_vs_reviews': float(df_with_reviews['rank'].corr(df_with_reviews['num_reviews'])) if len(df_with_reviews) > 0 else None
    }
}

with open('bestseller_rank_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\n✅ Saved summary: bestseller_rank_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ BESTSELLER RANK ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/bestseller_rank_distribution.png")
print(f"   • {OUTPUT_DIR}/rank_vs_price.png")
print(f"   • {OUTPUT_DIR}/rank_vs_rating.png")
print(f"   • {OUTPUT_DIR}/rank_vs_reviews.png")
print(f"   • {OUTPUT_DIR}/top_brands_bestsellers.png")
print(f"   • bestseller_rank_summary.json")
print("=" * 80)

