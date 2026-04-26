#!/usr/bin/env python3
"""
Deep Technical Specifications Analysis
======================================
In-depth analysis of laptop technical specifications from the details JSONB column.

Focus areas:
- RAM configurations (frequency, type, upgradeability)
- Storage (type, capacity, speed)
- Processor (brand, generation, cores, speed)
- Display (size, resolution, refresh rate, panel type)
- Graphics (integrated vs dedicated, VRAM)
- Battery life
- Connectivity (ports, WiFi, Bluetooth)
- Operating system
- Weight and dimensions
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
print("🔧 TECHNICAL SPECIFICATIONS DEEP ANALYSIS")
print("=" * 80)

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print("\n[1/12] Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("  ✅ Connected!")

# Fetch all laptop products with details
print("\n[2/12] Fetching all laptop products...")
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
    WHERE details IS NOT NULL;
""")

products = cur.fetchall()
print(f"  ✅ Fetched {len(products):,} products")

# Parse all technical specifications
print("\n[3/12] Parsing technical specifications...")

def parse_ram_details(details):
    """Extract detailed RAM information"""
    ram_info = {}
    
    for key, value in details.items():
        key_lower = key.lower()
        value_str = str(value).lower()
        
        # RAM size
        if 'ram' in key_lower or 'memory' in key_lower:
            size_match = re.search(r'(\d+)\s*(gb|mb)', value_str)
            if size_match:
                ram_info['size_gb'] = int(size_match.group(1)) if 'gb' in size_match.group(2) else int(size_match.group(1)) / 1024
            
            # RAM type
            if 'ddr' in value_str:
                type_match = re.search(r'ddr\s*(\d+[a-z]*)', value_str)
                if type_match:
                    ram_info['type'] = f"DDR{type_match.group(1).upper()}"
            
            # RAM speed
            speed_match = re.search(r'(\d+)\s*mhz', value_str)
            if speed_match:
                ram_info['speed_mhz'] = int(speed_match.group(1))
    
    return ram_info

def parse_storage_details(details):
    """Extract detailed storage information"""
    storage_info = {}
    
    for key, value in details.items():
        key_lower = key.lower()
        value_str = str(value).lower()
        
        # Storage type
        if any(x in value_str for x in ['ssd', 'solid state', 'nvme', 'hdd', 'hard disk']):
            if 'ssd' in value_str or 'solid state' in value_str or 'nvme' in value_str:
                storage_info['type'] = 'SSD'
            elif 'hdd' in value_str or 'hard disk' in value_str:
                storage_info['type'] = 'HDD'
        
        # Storage capacity
        if any(x in key_lower for x in ['storage', 'hard', 'ssd', 'drive']):
            # Look for TB or GB
            size_match = re.search(r'(\d+)\s*(tb|gb)', value_str)
            if size_match:
                capacity = int(size_match.group(1))
                if 'tb' in size_match.group(2):
                    storage_info['capacity_gb'] = capacity * 1024
                else:
                    storage_info['capacity_gb'] = capacity
    
    return storage_info

def parse_processor_details(details):
    """Extract processor information"""
    processor_info = {}
    
    for key, value in details.items():
        key_lower = key.lower()
        value_str = str(value).lower()
        
        if any(x in key_lower for x in ['processor', 'cpu', 'chipset']):
            # Brand
            if 'intel' in value_str:
                processor_info['brand'] = 'Intel'
            elif 'amd' in value_str:
                processor_info['brand'] = 'AMD'
            elif 'apple' in value_str or 'm1' in value_str or 'm2' in value_str:
                processor_info['brand'] = 'Apple'
            
            # Generation/Model
            if 'core i' in value_str:
                gen_match = re.search(r'core\s*i(\d)', value_str)
                if gen_match:
                    processor_info['series'] = f"Core i{gen_match.group(1)}"
                
                # Generation number
                gen_num_match = re.search(r'(\d{4,5})', value_str)
                if gen_num_match:
                    processor_info['model_number'] = gen_num_match.group(1)
            
            elif 'ryzen' in value_str:
                ryzen_match = re.search(r'ryzen\s*(\d)', value_str)
                if ryzen_match:
                    processor_info['series'] = f"Ryzen {ryzen_match.group(1)}"
            
            # Speed
            speed_match = re.search(r'(\d+\.?\d*)\s*ghz', value_str)
            if speed_match:
                processor_info['speed_ghz'] = float(speed_match.group(1))
            
            # Cores
            cores_match = re.search(r'(\d+)[-\s]*core', value_str)
            if cores_match:
                processor_info['cores'] = int(cores_match.group(1))
    
    return processor_info

def parse_display_details(details):
    """Extract display information"""
    display_info = {}
    
    for key, value in details.items():
        key_lower = key.lower()
        value_str = str(value).lower()
        
        if any(x in key_lower for x in ['display', 'screen', 'resolution']):
            # Screen size
            size_match = re.search(r'(\d+\.?\d*)\s*["\']?\s*inch', value_str)
            if size_match:
                display_info['size_inches'] = float(size_match.group(1))
            
            # Resolution
            if 'full hd' in value_str or '1920' in value_str or '1080p' in value_str:
                display_info['resolution'] = '1920x1080'
            elif '4k' in value_str or '3840' in value_str or '2160p' in value_str:
                display_info['resolution'] = '3840x2160'
            elif '2k' in value_str or '2560' in value_str or '1440p' in value_str:
                display_info['resolution'] = '2560x1440'
            elif 'hd' in value_str or '1366' in value_str:
                display_info['resolution'] = '1366x768'
            
            # Refresh rate
            refresh_match = re.search(r'(\d+)\s*hz', value_str)
            if refresh_match:
                display_info['refresh_hz'] = int(refresh_match.group(1))
    
    return display_info

def parse_graphics_details(details):
    """Extract graphics information"""
    graphics_info = {}
    
    for key, value in details.items():
        key_lower = key.lower()
        value_str = str(value).lower()
        
        if any(x in key_lower for x in ['graphics', 'gpu', 'video']):
            # Type
            if any(x in value_str for x in ['nvidia', 'geforce', 'rtx', 'gtx']):
                graphics_info['type'] = 'Dedicated (NVIDIA)'
            elif 'amd' in value_str and 'radeon' in value_str:
                graphics_info['type'] = 'Dedicated (AMD)'
            elif any(x in value_str for x in ['integrated', 'intel', 'iris', 'uhd']):
                graphics_info['type'] = 'Integrated'
            
            # VRAM
            vram_match = re.search(r'(\d+)\s*gb', value_str)
            if vram_match and graphics_info.get('type', '').startswith('Dedicated'):
                graphics_info['vram_gb'] = int(vram_match.group(1))
    
    return graphics_info

def parse_operating_system(details):
    """Extract OS information"""
    for key, value in details.items():
        value_str = str(value).lower()
        
        if 'windows' in value_str:
            if '11' in value_str:
                return 'Windows 11'
            elif '10' in value_str:
                return 'Windows 10'
            return 'Windows'
        elif 'mac' in value_str or 'os x' in value_str or 'macos' in value_str:
            return 'macOS'
        elif 'linux' in value_str or 'ubuntu' in value_str:
            return 'Linux'
        elif 'chrome' in value_str:
            return 'Chrome OS'
    
    return None

# Parse all products
parsed_data = []

for parent_asin, title, details, price, rating, num_reviews, store in products:
    if not details:
        continue
    
    ram = parse_ram_details(details)
    storage = parse_storage_details(details)
    processor = parse_processor_details(details)
    display = parse_display_details(details)
    graphics = parse_graphics_details(details)
    os = parse_operating_system(details)
    
    parsed_data.append({
        'asin': parent_asin,
        'title': title,
        'price': price,
        'rating': rating,
        'num_reviews': num_reviews,
        'store': store,
        'ram_size': ram.get('size_gb'),
        'ram_type': ram.get('type'),
        'ram_speed': ram.get('speed_mhz'),
        'storage_type': storage.get('type'),
        'storage_capacity': storage.get('capacity_gb'),
        'cpu_brand': processor.get('brand'),
        'cpu_series': processor.get('series'),
        'cpu_speed': processor.get('speed_ghz'),
        'cpu_cores': processor.get('cores'),
        'display_size': display.get('size_inches'),
        'display_resolution': display.get('resolution'),
        'display_refresh': display.get('refresh_hz'),
        'graphics_type': graphics.get('type'),
        'graphics_vram': graphics.get('vram_gb'),
        'os': os
    })

df = pd.DataFrame(parsed_data)
print(f"  ✅ Parsed {len(df):,} products")

# Analysis 1: RAM Analysis
print("\n[4/12] Analyzing RAM configurations...")
ram_analysis = df[df['ram_size'].notna()]
print(f"  📊 Products with RAM data: {len(ram_analysis):,}")

if len(ram_analysis) > 0:
    print(f"\n  💾 RAM Size Distribution:")
    ram_counts = ram_analysis['ram_size'].value_counts().sort_index()
    for size, count in ram_counts.items():
        pct = (count / len(ram_analysis)) * 100
        print(f"     {size:5.0f} GB: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n  💾 RAM Type Distribution:")
    if ram_analysis['ram_type'].notna().any():
        ram_type_counts = ram_analysis['ram_type'].value_counts()
        for ram_type, count in ram_type_counts.items():
            pct = (count / len(ram_analysis[ram_analysis['ram_type'].notna()])) * 100
            print(f"     {ram_type:10s} {count:4d} ({pct:5.1f}%)")

# Visualization 1: RAM
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# RAM size distribution
ram_counts_plot = ram_analysis['ram_size'].value_counts().sort_index()
axes[0].bar(range(len(ram_counts_plot)), ram_counts_plot.values, color='steelblue')
axes[0].set_xticks(range(len(ram_counts_plot)))
axes[0].set_xticklabels([f"{int(x)} GB" for x in ram_counts_plot.index])
axes[0].set_ylabel('Number of Products')
axes[0].set_title('RAM Size Distribution')
axes[0].grid(axis='y', alpha=0.3)

# RAM vs Price
ram_price_data = ram_analysis[ram_analysis['price'].notna()]
if len(ram_price_data) > 0:
    ram_price_avg = ram_price_data.groupby('ram_size')['price'].mean().sort_index()
    axes[1].bar(range(len(ram_price_avg)), ram_price_avg.values, color='coral')
    axes[1].set_xticks(range(len(ram_price_avg)))
    axes[1].set_xticklabels([f"{int(x)} GB" for x in ram_price_avg.index])
    axes[1].set_ylabel('Average Price ($)')
    axes[1].set_title('Average Price by RAM Size')
    axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/ram_deep_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n  ✅ Saved: {OUTPUT_DIR}/ram_deep_analysis.png")

# Analysis 2: Storage Analysis
print("\n[5/12] Analyzing storage configurations...")
storage_analysis = df[df['storage_capacity'].notna()]
print(f"  📊 Products with storage data: {len(storage_analysis):,}")

if len(storage_analysis) > 0:
    print(f"\n  💿 Storage Type Distribution:")
    if storage_analysis['storage_type'].notna().any():
        storage_type_counts = storage_analysis['storage_type'].value_counts()
        for storage_type, count in storage_type_counts.items():
            pct = (count / len(storage_analysis[storage_analysis['storage_type'].notna()])) * 100
            print(f"     {storage_type:10s} {count:4d} ({pct:5.1f}%)")
    
    print(f"\n  💿 Storage Capacity Distribution:")
    storage_capacity_counts = storage_analysis['storage_capacity'].value_counts().sort_index()
    for capacity, count in storage_capacity_counts.head(10).items():
        pct = (count / len(storage_analysis)) * 100
        if capacity >= 1024:
            print(f"     {capacity/1024:5.1f} TB: {count:4d} ({pct:5.1f}%)")
        else:
            print(f"     {capacity:5.0f} GB: {count:4d} ({pct:5.1f}%)")

# Visualization 2: Storage
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Storage type
if storage_analysis['storage_type'].notna().any():
    storage_type_counts = storage_analysis['storage_type'].value_counts()
    axes[0].pie(storage_type_counts.values, labels=storage_type_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Storage Type Distribution')

# Storage capacity vs price
storage_price_data = storage_analysis[storage_analysis['price'].notna()]
if len(storage_price_data) > 0:
    # Group capacities
    storage_price_data = storage_price_data.copy()
    storage_price_data['capacity_label'] = storage_price_data['storage_capacity'].apply(
        lambda x: f"{int(x)} GB" if x < 1024 else f"{x/1024:.1f} TB"
    )
    storage_price_avg = storage_price_data.groupby('capacity_label')['price'].mean().head(10)
    axes[1].barh(range(len(storage_price_avg)), storage_price_avg.values, color='green')
    axes[1].set_yticks(range(len(storage_price_avg)))
    axes[1].set_yticklabels(storage_price_avg.index)
    axes[1].set_xlabel('Average Price ($)')
    axes[1].set_title('Average Price by Storage Capacity (Top 10)')
    axes[1].grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/storage_deep_analysis.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/storage_deep_analysis.png")

# Analysis 3: Processor Analysis
print("\n[6/12] Analyzing processor configurations...")
cpu_analysis = df[df['cpu_brand'].notna()]
print(f"  📊 Products with CPU data: {len(cpu_analysis):,}")

if len(cpu_analysis) > 0:
    print(f"\n  🔧 CPU Brand Distribution:")
    cpu_brand_counts = cpu_analysis['cpu_brand'].value_counts()
    for brand, count in cpu_brand_counts.items():
        pct = (count / len(cpu_analysis)) * 100
        print(f"     {brand:10s} {count:4d} ({pct:5.1f}%)")
    
    print(f"\n  🔧 Top CPU Series:")
    if cpu_analysis['cpu_series'].notna().any():
        cpu_series_counts = cpu_analysis['cpu_series'].value_counts().head(10)
        for series, count in cpu_series_counts.items():
            pct = (count / len(cpu_analysis[cpu_analysis['cpu_series'].notna()])) * 100
            print(f"     {series:15s} {count:4d} ({pct:5.1f}%)")

# Visualization 3: Processor
plt.figure(figsize=(12, 6))

# CPU brand distribution
cpu_brand_counts = cpu_analysis['cpu_brand'].value_counts()
plt.subplot(1, 2, 1)
plt.pie(cpu_brand_counts.values, labels=cpu_brand_counts.index, autopct='%1.1f%%', startangle=90)
plt.title('CPU Brand Distribution')

# CPU series (top 10)
if cpu_analysis['cpu_series'].notna().any():
    plt.subplot(1, 2, 2)
    cpu_series_counts = cpu_analysis['cpu_series'].value_counts().head(10)
    plt.barh(range(len(cpu_series_counts)), cpu_series_counts.values, color='purple')
    plt.yticks(range(len(cpu_series_counts)), cpu_series_counts.index)
    plt.xlabel('Number of Products')
    plt.title('Top 10 CPU Series')
    plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/processor_deep_analysis.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/processor_deep_analysis.png")

# Analysis 4: Display Analysis
print("\n[7/12] Analyzing display configurations...")
display_analysis = df[df['display_size'].notna()]
print(f"  📊 Products with display data: {len(display_analysis):,}")

if len(display_analysis) > 0:
    print(f"\n  📺 Display Size Distribution:")
    display_size_counts = display_analysis['display_size'].value_counts().sort_index()
    for size, count in display_size_counts.items():
        pct = (count / len(display_analysis)) * 100
        print(f"     {size:4.1f}\": {count:4d} ({pct:5.1f}%)")
    
    print(f"\n  📺 Resolution Distribution:")
    if display_analysis['display_resolution'].notna().any():
        resolution_counts = display_analysis['display_resolution'].value_counts()
        for resolution, count in resolution_counts.items():
            pct = (count / len(display_analysis[display_analysis['display_resolution'].notna()])) * 100
            print(f"     {resolution:15s} {count:4d} ({pct:5.1f}%)")

# Visualization 4: Display
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Display size distribution
display_size_counts = display_analysis['display_size'].value_counts().sort_index()
axes[0].bar(range(len(display_size_counts)), display_size_counts.values, color='teal')
axes[0].set_xticks(range(len(display_size_counts)))
axes[0].set_xticklabels([f"{x:.1f}\"" for x in display_size_counts.index], rotation=45)
axes[0].set_ylabel('Number of Products')
axes[0].set_title('Display Size Distribution')
axes[0].grid(axis='y', alpha=0.3)

# Resolution distribution
if display_analysis['display_resolution'].notna().any():
    resolution_counts = display_analysis['display_resolution'].value_counts()
    axes[1].barh(range(len(resolution_counts)), resolution_counts.values, color='orange')
    axes[1].set_yticks(range(len(resolution_counts)))
    axes[1].set_yticklabels(resolution_counts.index)
    axes[1].set_xlabel('Number of Products')
    axes[1].set_title('Display Resolution Distribution')
    axes[1].gca().invert_yaxis()

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/display_deep_analysis.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/display_deep_analysis.png")

# Analysis 5: Graphics Analysis
print("\n[8/12] Analyzing graphics configurations...")
graphics_analysis = df[df['graphics_type'].notna()]
print(f"  📊 Products with graphics data: {len(graphics_analysis):,}")

if len(graphics_analysis) > 0:
    print(f"\n  🎮 Graphics Type Distribution:")
    graphics_type_counts = graphics_analysis['graphics_type'].value_counts()
    for graphics_type, count in graphics_type_counts.items():
        pct = (count / len(graphics_analysis)) * 100
        print(f"     {graphics_type:25s} {count:4d} ({pct:5.1f}%)")

# Visualization 5: Graphics
plt.figure(figsize=(10, 6))
if len(graphics_analysis) > 0:
    graphics_type_counts = graphics_analysis['graphics_type'].value_counts()
    plt.pie(graphics_type_counts.values, labels=graphics_type_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Graphics Type Distribution')
    plt.savefig(f'{OUTPUT_DIR}/graphics_deep_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/graphics_deep_analysis.png")

# Analysis 6: Operating System
print("\n[9/12] Analyzing operating systems...")
os_analysis = df[df['os'].notna()]
print(f"  📊 Products with OS data: {len(os_analysis):,}")

if len(os_analysis) > 0:
    print(f"\n  💻 Operating System Distribution:")
    os_counts = os_analysis['os'].value_counts()
    for os_name, count in os_counts.items():
        pct = (count / len(os_analysis)) * 100
        print(f"     {os_name:15s} {count:4d} ({pct:5.1f}%)")

# Visualization 6: Operating System
plt.figure(figsize=(10, 6))
if len(os_analysis) > 0:
    os_counts = os_analysis['os'].value_counts()
    plt.pie(os_counts.values, labels=os_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Operating System Distribution')
    plt.savefig(f'{OUTPUT_DIR}/os_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {OUTPUT_DIR}/os_distribution.png")

# Analysis 7: Price segments by specs
print("\n[10/12] Analyzing price segments...")
price_segment_analysis = df[df['price'].notna()].copy()

if len(price_segment_analysis) > 0:
    # Create price segments
    price_segment_analysis['price_segment'] = pd.cut(
        price_segment_analysis['price'],
        bins=[0, 500, 1000, 1500, 2000, float('inf')],
        labels=['Budget (<$500)', 'Mid-Range ($500-$1K)', 'Premium ($1K-$1.5K)', 'High-End ($1.5K-$2K)', 'Ultra ($2K+)']
    )
    
    print(f"\n  💰 Product Distribution by Price Segment:")
    segment_counts = price_segment_analysis['price_segment'].value_counts()
    for segment, count in segment_counts.items():
        pct = (count / len(price_segment_analysis)) * 100
        print(f"     {segment:25s} {count:4d} ({pct:5.1f}%)")

# Visualization 7: Price segments
plt.figure(figsize=(12, 6))
segment_counts = price_segment_analysis['price_segment'].value_counts()
colors = ['green', 'blue', 'orange', 'red', 'purple']
plt.bar(range(len(segment_counts)), segment_counts.values, color=colors)
plt.xticks(range(len(segment_counts)), segment_counts.index, rotation=15)
plt.ylabel('Number of Products')
plt.title('Product Distribution by Price Segment')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/price_segments.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Saved: {OUTPUT_DIR}/price_segments.png")

# Analysis 8: Spec combinations
print("\n[11/12] Analyzing common specification combinations...")
spec_combos = df[
    df['ram_size'].notna() & 
    df['storage_capacity'].notna() & 
    df['cpu_brand'].notna()
].copy()

if len(spec_combos) > 0:
    spec_combos['spec_combo'] = spec_combos.apply(
        lambda x: f"{int(x['ram_size'])}GB RAM + {int(x['storage_capacity'])}GB {x['storage_type'] or 'Storage'} + {x['cpu_brand']}",
        axis=1
    )
    
    print(f"\n  🔧 Top 15 Specification Combinations:")
    combo_counts = spec_combos['spec_combo'].value_counts().head(15)
    for i, (combo, count) in enumerate(combo_counts.items(), 1):
        pct = (count / len(spec_combos)) * 100
        print(f"     {i:2d}. {combo:60s} {count:3d} ({pct:4.1f}%)")

# Save detailed summary
print("\n[12/12] Generating detailed summary...")
summary = {
    'total_products': len(df),
    'ram_analysis': {
        'products_with_data': len(df[df['ram_size'].notna()]),
        'most_common_size': int(df[df['ram_size'].notna()]['ram_size'].mode()[0]) if len(df[df['ram_size'].notna()]) > 0 else None,
        'size_distribution': df['ram_size'].value_counts().to_dict() if df['ram_size'].notna().any() else {}
    },
    'storage_analysis': {
        'products_with_data': len(df[df['storage_capacity'].notna()]),
        'ssd_percentage': float((df['storage_type'] == 'SSD').sum() / len(df[df['storage_type'].notna()]) * 100) if df['storage_type'].notna().any() else 0,
        'most_common_capacity': int(df[df['storage_capacity'].notna()]['storage_capacity'].mode()[0]) if len(df[df['storage_capacity'].notna()]) > 0 else None
    },
    'processor_analysis': {
        'products_with_data': len(df[df['cpu_brand'].notna()]),
        'brand_distribution': df['cpu_brand'].value_counts().to_dict() if df['cpu_brand'].notna().any() else {}
    },
    'display_analysis': {
        'products_with_data': len(df[df['display_size'].notna()]),
        'most_common_size': float(df[df['display_size'].notna()]['display_size'].mode()[0]) if len(df[df['display_size'].notna()]) > 0 else None,
        'resolution_distribution': df['display_resolution'].value_counts().to_dict() if df['display_resolution'].notna().any() else {}
    },
    'graphics_analysis': {
        'products_with_data': len(df[df['graphics_type'].notna()]),
        'type_distribution': df['graphics_type'].value_counts().to_dict() if df['graphics_type'].notna().any() else {}
    },
    'os_analysis': {
        'products_with_data': len(df[df['os'].notna()]),
        'distribution': df['os'].value_counts().to_dict() if df['os'].notna().any() else {}
    }
}

with open('technical_specs_summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=int)
print(f"  ✅ Saved summary: technical_specs_summary.json")

# Close connection
cur.close()
conn.close()

print("\n" + "=" * 80)
print("✅ TECHNICAL SPECIFICATIONS ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📁 Output files in {OUTPUT_DIR}/:")
print(f"   • ram_deep_analysis.png")
print(f"   • storage_deep_analysis.png")
print(f"   • processor_deep_analysis.png")
print(f"   • display_deep_analysis.png")
print(f"   • graphics_deep_analysis.png")
print(f"   • os_distribution.png")
print(f"   • price_segments.png")
print(f"   • technical_specs_summary.json")
print("=" * 80)

