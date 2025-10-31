#!/usr/bin/env python3
"""
Setup script to create Products EDA Jupyter Notebook
"""

import nbformat as nbf

# Create a new notebook
nb = nbf.v4.new_notebook()

# Add cells
cells = []

# Title
cells.append(nbf.v4.new_markdown_cell("""# 📊 Amazon Electronics Products - Exploratory Data Analysis

**Dataset:** 348,228 Electronics Products  
**Database:** PostgreSQL (amazon_electronics_rag)  
**Date:** October 29, 2025

---"""))

# Setup
cells.append(nbf.v4.new_markdown_cell("## Setup & Imports"))

cells.append(nbf.v4.new_code_cell("""# Core libraries
import pandas as pd
import numpy as np
import psycopg2
import json
from datetime import datetime

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Text analysis
from wordcloud import WordCloud
from collections import Counter
import re

# Statistical analysis
from scipy import stats
from scipy.stats import pearsonr, spearmanr

# Settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)

print("✅ Imports complete!")"""))

# Database connection
cells.append(nbf.v4.new_markdown_cell("## Database Connection"))

cells.append(nbf.v4.new_code_cell("""# Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname="amazon_electronics_rag",
        user="shivamsharma",
        host="localhost",
        port="5432"
    )

# Test connection
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM products;")
total_products = cur.fetchone()[0]
cur.close()
conn.close()

print(f"✅ Connected to database")
print(f"📦 Total products: {total_products:,}")"""))

# Phase 1
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 1: Basic Dataset Overview"))
cells.append(nbf.v4.new_markdown_cell("## 1.1 Load Data"))

cells.append(nbf.v4.new_code_cell("""# Load full dataset
query = \"\"\"
SELECT 
    parent_asin,
    title,
    description,
    features,
    price,
    average_rating,
    rating_number,
    main_category,
    store,
    images,
    videos,
    CASE WHEN blair_embedding IS NOT NULL THEN TRUE ELSE FALSE END as has_embedding,
    created_at
FROM products;
\"\"\"

print("Loading data from PostgreSQL...")
df = pd.read_sql_query(query, get_connection())
print(f"✅ Loaded {len(df):,} products")
df.head()"""))

cells.append(nbf.v4.new_markdown_cell("## 1.2 Dataset Info"))

cells.append(nbf.v4.new_code_cell("""print("="*80)
print("DATASET OVERVIEW")
print("="*80)
print(f"Rows: {df.shape[0]:,}")
print(f"Columns: {df.shape[1]}")
print(f"\\nMemory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print(f"\\nColumn Types:")
print(df.dtypes)
print(f"\\nBasic Statistics:")
df.describe()"""))

cells.append(nbf.v4.new_markdown_cell("## 1.3 Missing Data"))

cells.append(nbf.v4.new_code_cell("""# Missing data analysis
missing_df = pd.DataFrame({
    'Column': df.columns,
    'Missing Count': df.isnull().sum(),
    'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
}).sort_values('Missing %', ascending=False)

print("="*80)
print("MISSING DATA ANALYSIS")
print("="*80)
print(missing_df.to_string(index=False))

# Visualize
fig, ax = plt.subplots(figsize=(12, 6))
missing_df.plot(x='Column', y='Missing %', kind='barh', ax=ax, color='coral')
ax.set_xlabel('Missing %')
ax.set_title('Missing Data by Column')
plt.tight_layout()
plt.show()"""))

# Phase 2
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 2: Category Analysis"))
cells.append(nbf.v4.new_markdown_cell("## 2.1 Main Category Distribution"))

cells.append(nbf.v4.new_code_cell("""# Top 20 categories
category_counts = df['main_category'].value_counts().head(20)

print("="*80)
print("TOP 20 CATEGORIES")
print("="*80)
for i, (cat, count) in enumerate(category_counts.items(), 1):
    pct = count / len(df) * 100
    print(f"{i:2}. {cat:35} {count:8,} ({pct:5.2f}%)")

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

category_counts.plot(kind='barh', ax=ax1, color='steelblue')
ax1.set_xlabel('Number of Products')
ax1.set_title('Top 20 Categories')
ax1.invert_yaxis()

category_counts.head(10).plot(kind='pie', ax=ax2, autopct='%1.1f%%')
ax2.set_ylabel('')
ax2.set_title('Top 10 Categories')

plt.tight_layout()
plt.show()"""))

# Phase 3 - Price
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 3: Price Analysis"))
cells.append(nbf.v4.new_markdown_cell("## 3.1 Price Distribution"))

cells.append(nbf.v4.new_code_cell("""# Price statistics
price_data = df[df['price'].notna()]['price']

print("="*80)
print("PRICE STATISTICS")
print("="*80)
print(f"Products with price: {len(price_data):,} ({len(price_data)/len(df)*100:.1f}%)")
print(f"\\nStatistics:")
print(price_data.describe())

# Visualize
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# All prices
axes[0,0].hist(price_data, bins=50, color='skyblue', edgecolor='black')
axes[0,0].set_xlabel('Price ($)')
axes[0,0].set_title('Price Distribution (All)')
axes[0,0].axvline(price_data.median(), color='red', linestyle='--', label=f'Median: ${price_data.median():.2f}')
axes[0,0].legend()

# Under $500
price_under_500 = price_data[price_data <= 500]
axes[0,1].hist(price_under_500, bins=50, color='lightgreen', edgecolor='black')
axes[0,1].set_xlabel('Price ($)')
axes[0,1].set_title('Price Distribution (Under $500)')

# Box plot
axes[1,0].boxplot(price_data, vert=False)
axes[1,0].set_xlabel('Price ($)')
axes[1,0].set_title('Price Box Plot')

# Log scale
axes[1,1].hist(np.log10(price_data[price_data > 0]), bins=50, color='coral', edgecolor='black')
axes[1,1].set_xlabel('Log10(Price)')
axes[1,1].set_title('Price Distribution (Log Scale)')

plt.tight_layout()
plt.show()"""))

# Phase 4 - Ratings
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 4: Rating Analysis"))
cells.append(nbf.v4.new_markdown_cell("## 4.1 Rating Distribution"))

cells.append(nbf.v4.new_code_cell("""# Rating statistics
rating_data = df[df['average_rating'].notna()]['average_rating']

print("="*80)
print("RATING STATISTICS")
print("="*80)
print(f"Products with ratings: {len(rating_data):,} ({len(rating_data)/len(df)*100:.1f}%)")
print(f"\\nStatistics:")
print(rating_data.describe())

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

axes[0].hist(rating_data, bins=50, color='gold', edgecolor='black')
axes[0].set_xlabel('Average Rating')
axes[0].set_title('Rating Distribution')
axes[0].axvline(rating_data.mean(), color='red', linestyle='--', label=f'Mean: {rating_data.mean():.2f}★')
axes[0].legend()

rating_bins = pd.cut(rating_data, bins=[0, 2, 3, 4, 4.5, 5], labels=['<2★', '2-3★', '3-4★', '4-4.5★', '4.5-5★'])
rating_bin_counts = rating_bins.value_counts().sort_index()
axes[1].bar(range(len(rating_bin_counts)), rating_bin_counts.values, color='orange')
axes[1].set_xticks(range(len(rating_bin_counts)))
axes[1].set_xticklabels(rating_bin_counts.index)
axes[1].set_title('Products by Rating Range')

plt.tight_layout()
plt.show()"""))

# Phase 5 - Text
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 5: Text Analysis"))
cells.append(nbf.v4.new_markdown_cell("## 5.1 Title Analysis"))

cells.append(nbf.v4.new_code_cell("""# Title lengths
df['title_length'] = df['title'].str.len()

print("="*80)
print("TITLE ANALYSIS")
print("="*80)
print(f"Average title length: {df['title_length'].mean():.1f} characters")
print(f"Median: {df['title_length'].median():.1f}")

# Most common words
all_titles = ' '.join(df['title'].dropna().astype(str))
words = re.findall(r'\\b\\w{4,}\\b', all_titles.lower())
word_counts = Counter(words).most_common(30)

print("\\nTop 30 Words in Titles:")
for i, (word, count) in enumerate(word_counts, 1):
    print(f"{i:2}. {word:20} {count:8,}")

# Plot
fig, ax = plt.subplots(figsize=(12, 5))
df['title_length'].hist(bins=50, ax=ax, color='skyblue', edgecolor='black')
ax.set_xlabel('Title Length')
ax.set_title('Title Length Distribution')
plt.tight_layout()
plt.show()"""))

# Phase 6 - Correlations
cells.append(nbf.v4.new_markdown_cell("---\n\n# Phase 6: Correlations"))
cells.append(nbf.v4.new_markdown_cell("## 6.1 Price vs Rating"))

cells.append(nbf.v4.new_code_cell("""# Price vs Rating correlation
price_rating_df = df[(df['price'].notna()) & (df['average_rating'].notna())].copy()

pearson_corr, _ = pearsonr(price_rating_df['price'], price_rating_df['average_rating'])

print("="*80)
print("PRICE vs RATING")
print("="*80)
print(f"Pearson correlation: {pearson_corr:.4f}")
print(f"Sample size: {len(price_rating_df):,}")

# Scatter plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.scatter(price_rating_df['price'], price_rating_df['average_rating'], alpha=0.3, s=10)
ax.set_xlabel('Price ($)')
ax.set_ylabel('Rating')
ax.set_title(f'Price vs Rating (r = {pearson_corr:.4f})')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""))

# Summary
cells.append(nbf.v4.new_markdown_cell("---\n\n# Summary"))

cells.append(nbf.v4.new_code_cell("""# Export summary
summary = {
    'Total Products': len(df),
    'Unique Categories': df['main_category'].nunique(),
    'Products with Price': df['price'].notna().sum(),
    'Avg Price': df['price'].mean(),
    'Products with Rating': df['average_rating'].notna().sum(),
    'Avg Rating': df['average_rating'].mean(),
    'Products with Embeddings': df['has_embedding'].sum()
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('products_eda_summary.csv', index=False)

print("="*80)
print("EDA COMPLETE!")
print("="*80)
for key, value in summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:.2f}")
    else:
        print(f"{key}: {value:,}")"""))

# Add all cells to notebook
nb['cells'] = cells

# Write notebook
with open('products_eda.ipynb', 'w') as f:
    nbf.write(nb, f)

print("✅ Notebook created: products_eda.ipynb")
