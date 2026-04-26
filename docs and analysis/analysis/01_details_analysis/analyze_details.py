#!/usr/bin/env python3
"""
Analysis of Details Column (JSONB) in Products Table
====================================================
This script analyzes the laptop specifications stored in the 'details' JSONB column.

Key metrics:
- Most common specification keys (RAM, Storage, Processor, etc.)
- Value distributions for each key
- Missing/incomplete specifications
- Specification trends
"""

import psycopg2
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import numpy as np

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
print("📊 LAPTOP DETAILS ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/6] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch all details
print("\n[2/6] Fetching product details...")
cur.execute("""
    SELECT 
        parent_asin,
        title,
        details,
        price,
        average_rating,
        rating_number
    FROM products_backup
    WHERE details IS NOT NULL;
""")

products = cur.fetchall()
print(f"  ✅ Loaded {len(products):,} products with details")

# Parse details
print("\n[3/6] Parsing JSONB details...")
all_keys = Counter()
key_values = defaultdict(list)
products_data = []

for parent_asin, title, details_json, price, rating, num_reviews in products:
    if details_json:
        for key, value in details_json.items():
            all_keys[key] += 1
            key_values[key].append(str(value))
            
        products_data.append({
            'asin': parent_asin,
            'title': title,
            'details': details_json,
            'price': price,
            'rating': rating,
            'num_reviews': num_reviews
        })

print(f"  ✅ Found {len(all_keys)} unique specification keys")

# Analysis 1: Most common keys
print("\n[4/6] Analyzing specification keys...")
print("\n  📋 Top 20 Most Common Specification Keys:")
for i, (key, count) in enumerate(all_keys.most_common(20), 1):
    pct = (count / len(products)) * 100
    print(f"     {i:2d}. {key:40s} {count:5,} products ({pct:5.1f}%)")

# Visualization 1: Top specification keys
plt.figure(figsize=(12, 8))
top_keys = all_keys.most_common(15)
keys, counts = zip(*top_keys)
plt.barh(range(len(keys)), counts, color='steelblue')
plt.yticks(range(len(keys)), keys)
plt.xlabel('Number of Products')
plt.title('Top 15 Specification Keys in Laptop Details')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/top_specification_keys.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/top_specification_keys.png")

# Analysis 2: RAM Distribution
print("\n[5/6] Analyzing RAM specifications...")
ram_key = None
for key in all_keys.keys():
    if 'ram' in key.lower() or 'memory' in key.lower():
        ram_key = key
        break

if ram_key:
    ram_values = [v for v in key_values[ram_key]]
    ram_counter = Counter(ram_values)
    print(f"\n  💾 RAM Distribution (Key: '{ram_key}'):")
    for ram, count in ram_counter.most_common(10):
        pct = (count / len(ram_values)) * 100
        print(f"     {ram:30s} {count:5,} ({pct:5.1f}%)")
    
    # Visualization: RAM distribution
    plt.figure(figsize=(10, 6))
    top_ram = ram_counter.most_common(10)
    rams, counts = zip(*top_ram)
    plt.bar(range(len(rams)), counts, color='coral')
    plt.xticks(range(len(rams)), rams, rotation=45, ha='right')
    plt.ylabel('Number of Products')
    plt.title('RAM Distribution in Laptops')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/ram_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/ram_distribution.png")

# Analysis 3: Storage Distribution
print("\n[6/6] Analyzing Storage specifications...")
storage_key = None
for key in all_keys.keys():
    if 'storage' in key.lower() or 'hard drive' in key.lower() or 'ssd' in key.lower():
        storage_key = key
        break

if storage_key:
    storage_values = [v for v in key_values[storage_key]]
    storage_counter = Counter(storage_values)
    print(f"\n  💿 Storage Distribution (Key: '{storage_key}'):")
    for storage, count in storage_counter.most_common(10):
        pct = (count / len(storage_values)) * 100
        print(f"     {storage:40s} {count:5,} ({pct:5.1f}%)")
    
    # Visualization: Storage distribution
    plt.figure(figsize=(12, 6))
    top_storage = storage_counter.most_common(10)
    storages, counts = zip(*top_storage)
    plt.bar(range(len(storages)), counts, color='lightgreen')
    plt.xticks(range(len(storages)), storages, rotation=45, ha='right')
    plt.ylabel('Number of Products')
    plt.title('Storage Distribution in Laptops')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/storage_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/storage_distribution.png")

# Save summary statistics
summary = {
    'total_products_analyzed': len(products),
    'unique_specification_keys': len(all_keys),
    'top_20_keys': [{'key': k, 'count': c, 'percentage': (c/len(products))*100} 
                     for k, c in all_keys.most_common(20)],
    'coverage_statistics': {
        key: {
            'products_with_key': count,
            'coverage_percentage': (count/len(products))*100
        }
        for key, count in all_keys.most_common(10)
    }
}

with open('details_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\n✅ Saved summary: details_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ DETAILS ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files:")
print(f"   • {OUTPUT_DIR}/top_specification_keys.png")
print(f"   • {OUTPUT_DIR}/ram_distribution.png")
print(f"   • {OUTPUT_DIR}/storage_distribution.png")
print(f"   • details_summary.json")
print("=" * 80)

