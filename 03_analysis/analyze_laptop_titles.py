#!/usr/bin/env python3
"""
Deep Analysis of Product Titles for Laptop Keywords

This script performs comprehensive analysis of product titles to identify laptops
by looking for COMBINATIONS of:
1. Brand names (Dell, HP, Lenovo, etc.)
2. Laptop-specific keywords (laptop, notebook, chromebook)
3. Technical specs (RAM, CPU, processor, SSD, etc.)

A product is only counted as a laptop if it has BOTH a brand AND a spec/keyword.

Author: AI Assistant
Date: October 31, 2025
"""

import psycopg2
import pandas as pd
import re
from collections import Counter, defaultdict
from datetime import datetime

# Configuration
DB_NAME = "amazon_electronics_rag"

# Laptop brands (comprehensive list)
LAPTOP_BRANDS = [
    # Major brands
    'dell', 'hp', 'lenovo', 'asus', 'acer', 'apple', 'microsoft', 'samsung',
    'toshiba', 'sony', 'msi', 'razer', 'alienware', 'lg', 'huawei',
    
    # Gaming/Performance brands
    'rog', 'predator', 'pavilion', 'inspiron', 'latitude', 'precision',
    'thinkpad', 'ideapad', 'vivobook', 'zenbook', 'chromebook', 'macbook',
    'surface', 'galaxy book', 'omen', 'envy', 'spectre', 'elitebook',
    
    # Other brands
    'gateway', 'panasonic', 'fujitsu', 'vaio', 'compaq', 'emachines',
    'chuwi', 'jumper', 'teclast', 'avita', 'evoo', 'motile', 'direkt-tek'
]

# Laptop type keywords (direct indicators)
LAPTOP_KEYWORDS = [
    'laptop', 'notebook', 'chromebook', 'ultrabook', 'netbook',
    'macbook', 'thinkpad', 'ideapad', 'vivobook', 'zenbook',
    '2-in-1', '2 in 1', 'convertible laptop', 'gaming laptop',
    'business laptop', 'student laptop', 'touchscreen laptop'
]

# Technical specs (must appear WITH a brand)
TECH_SPECS = {
    'ram': [
        r'\b\d+gb\s+ram\b', r'\b\d+gb\s+ddr\d?\b', r'\bramam\b',
        r'\b\d+gb\s+memory\b', r'\bmemory.*\d+gb\b'
    ],
    'storage': [
        r'\b\d+gb\s+ssd\b', r'\b\d+tb\s+ssd\b', r'\b\d+gb\s+hdd\b',
        r'\bssd\b', r'\bhard drive\b', r'\bemmc\b', r'\bnvme\b'
    ],
    'cpu': [
        r'\bintel\s+core\b', r'\bintel\s+celeron\b', r'\bintel\s+pentium\b',
        r'\bamd\s+ryzen\b', r'\bamd\s+athlon\b', r'\bcore\s+i[3579]\b',
        r'\bprocessor\b', r'\bcpu\b', r'\bghz\b'
    ],
    'screen': [
        r'\b1[0-9]\.\d+\s*inch\b', r'\b1[0-9]\s*"\b', r'\b1[0-9]inch\b',
        r'\bfhd\b', r'\b1080p\b', r'\b4k\b', r'\btouchscreen\b',
        r'\bips\b.*\bdisplay\b', r'\bretina\b'
    ],
    'os': [
        r'\bwindows\s+1[01]\b', r'\bwindows\s+11\b', r'\bwin\s+1[01]\b',
        r'\bchrome\s+os\b', r'\bmac\s+os\b', r'\bmacos\b'
    ]
}


def connect_db():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user="shivamsharma",
            password="",
            host="localhost",
            port="5432"
        )
        print(f"✅ Connected to database: {DB_NAME}")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise


def load_titles(conn):
    """Load all product titles from database."""
    print("\n" + "=" * 80)
    print("LOADING PRODUCT TITLES")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            title,
            main_category,
            categories,
            features_array,
            details
        FROM products
        WHERE title IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\n✅ Loaded {len(df):,} products with titles")
    
    return df


def analyze_title(title):
    """
    Analyze a single title for laptop indicators.
    Returns dict with findings.
    """
    title_lower = title.lower()
    
    findings = {
        'has_brand': False,
        'brands_found': [],
        'has_laptop_keyword': False,
        'laptop_keywords_found': [],
        'has_specs': False,
        'specs_found': [],
        'spec_types': set()
    }
    
    # Check for brands
    for brand in LAPTOP_BRANDS:
        if brand in title_lower:
            findings['has_brand'] = True
            findings['brands_found'].append(brand)
    
    # Check for laptop keywords
    for keyword in LAPTOP_KEYWORDS:
        if keyword in title_lower:
            findings['has_laptop_keyword'] = True
            findings['laptop_keywords_found'].append(keyword)
    
    # Check for tech specs
    for spec_type, patterns in TECH_SPECS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                findings['has_specs'] = True
                findings['spec_types'].add(spec_type)
                findings['specs_found'].append(pattern)
    
    return findings


def classify_laptops(df):
    """
    Classify products as laptops using strict criteria:
    Must have BOTH (brand OR laptop_keyword) AND specs
    """
    print("\n" + "=" * 80)
    print("CLASSIFYING LAPTOPS BY TITLE ANALYSIS")
    print("=" * 80)
    
    results = []
    
    # Tier 1: Direct laptop keywords (highest confidence)
    tier1_count = 0
    # Tier 2: Brand + Specs (high confidence)
    tier2_count = 0
    # Tier 3: Brand + Multiple specs (medium confidence)
    tier3_count = 0
    
    print("\n🔍 Analyzing titles...")
    
    for idx, row in df.iterrows():
        title = row['title']
        findings = analyze_title(title)
        
        is_laptop = False
        confidence = 'none'
        reason = ''
        
        # Tier 1: Has explicit laptop keyword
        if findings['has_laptop_keyword']:
            is_laptop = True
            confidence = 'high'
            reason = f"Laptop keyword: {findings['laptop_keywords_found'][0]}"
            tier1_count += 1
        
        # Tier 2: Brand + Specs (strict requirement)
        elif findings['has_brand'] and findings['has_specs']:
            is_laptop = True
            confidence = 'medium-high'
            reason = f"Brand ({findings['brands_found'][0]}) + Specs ({', '.join(findings['spec_types'])})"
            tier2_count += 1
        
        # Tier 3: Multiple specs without explicit brand (lower confidence)
        elif len(findings['spec_types']) >= 2:
            is_laptop = True
            confidence = 'medium'
            reason = f"Multiple specs: {', '.join(findings['spec_types'])}"
            tier3_count += 1
        
        if is_laptop:
            results.append({
                'parent_asin': row['parent_asin'],
                'title': title,
                'main_category': row['main_category'],
                'confidence': confidence,
                'reason': reason,
                'brands': ', '.join(findings['brands_found']) if findings['brands_found'] else 'N/A',
                'laptop_keywords': ', '.join(findings['laptop_keywords_found']) if findings['laptop_keywords_found'] else 'N/A',
                'spec_types': ', '.join(findings['spec_types']) if findings['spec_types'] else 'N/A'
            })
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"  Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Classification complete!")
    print(f"\n📊 Results by Tier:")
    print(f"   Tier 1 (Laptop keyword):         {tier1_count:>8,} products")
    print(f"   Tier 2 (Brand + Specs):          {tier2_count:>8,} products")
    print(f"   Tier 3 (Multiple specs):         {tier3_count:>8,} products")
    print(f"   {'─' * 50}")
    print(f"   Total Laptops Identified:        {len(results):>8,} products")
    
    return pd.DataFrame(results)


def analyze_brands(laptops_df):
    """Analyze laptop brands distribution."""
    print("\n" + "=" * 80)
    print("BRAND ANALYSIS")
    print("=" * 80)
    
    brand_counts = Counter()
    
    for brands_str in laptops_df['brands']:
        if brands_str != 'N/A':
            for brand in brands_str.split(', '):
                brand_counts[brand] += 1
    
    print(f"\n📊 Top 20 Laptop Brands:")
    print(f"{'Rank':<6} {'Brand':<20} {'Count':<10} {'%'}")
    print("─" * 80)
    
    total = sum(brand_counts.values())
    for i, (brand, count) in enumerate(brand_counts.most_common(20), 1):
        pct = 100 * count / total
        print(f"{i:<6} {brand.title():<20} {count:>8,}  {pct:>5.1f}%")


def analyze_specs(laptops_df):
    """Analyze technical specs distribution."""
    print("\n" + "=" * 80)
    print("TECHNICAL SPECS ANALYSIS")
    print("=" * 80)
    
    spec_counts = Counter()
    
    for specs_str in laptops_df['spec_types']:
        if specs_str != 'N/A':
            for spec in specs_str.split(', '):
                spec_counts[spec] += 1
    
    print(f"\n📊 Spec Types Found:")
    print(f"{'Spec Type':<20} {'Count':<10} {'% of Laptops'}")
    print("─" * 80)
    
    total_laptops = len(laptops_df)
    for spec, count in spec_counts.most_common():
        pct = 100 * count / total_laptops
        print(f"{spec.upper():<20} {count:>8,}  {pct:>5.1f}%")


def sample_laptops(laptops_df):
    """Show sample laptops from each tier."""
    print("\n" + "=" * 80)
    print("SAMPLE IDENTIFIED LAPTOPS")
    print("=" * 80)
    
    for confidence in ['high', 'medium-high', 'medium']:
        samples = laptops_df[laptops_df['confidence'] == confidence].head(3)
        
        if len(samples) > 0:
            print(f"\n{'─' * 80}")
            print(f"Confidence: {confidence.upper()}")
            print(f"{'─' * 80}")
            
            for i, row in enumerate(samples.iterrows(), 1):
                _, data = row
                print(f"\n{i}. ASIN: {data['parent_asin']}")
                print(f"   Title: {data['title'][:80]}...")
                print(f"   Reason: {data['reason']}")
                print(f"   Brands: {data['brands']}")
                print(f"   Specs: {data['spec_types']}")


def cross_validate(laptops_df, original_df):
    """Cross-validate with categories and features."""
    print("\n" + "=" * 80)
    print("CROSS-VALIDATION WITH OTHER FIELDS")
    print("=" * 80)
    
    # Merge with original data
    merged = laptops_df.merge(
        original_df[['parent_asin', 'categories', 'features_array', 'details']], 
        on='parent_asin'
    )
    
    # Check categories
    has_laptop_category = 0
    for cats in merged['categories']:
        if cats is not None:
            cats_str = ' '.join(cats).lower() if isinstance(cats, list) else str(cats).lower()
            if 'laptop' in cats_str or 'notebook' in cats_str:
                has_laptop_category += 1
    
    # Check features
    has_laptop_features = 0
    for feats in merged['features_array']:
        if feats is not None and len(feats) > 0:
            feats_str = ' '.join(feats).lower()
            if 'laptop' in feats_str or 'notebook' in feats_str:
                has_laptop_features += 1
    
    # Check details
    has_ram_in_details = 0
    for details in merged['details']:
        if details is not None and isinstance(details, dict):
            if 'RAM' in details or 'Processor Type' in details:
                has_ram_in_details += 1
    
    print(f"\n📊 Cross-Validation Results:")
    print(f"   Total laptops identified:             {len(merged):,}")
    print(f"   Also have 'Laptop' in categories:     {has_laptop_category:,} ({100*has_laptop_category/len(merged):.1f}%)")
    print(f"   Also have 'laptop' in features:       {has_laptop_features:,} ({100*has_laptop_features/len(merged):.1f}%)")
    print(f"   Also have RAM/CPU in details:         {has_ram_in_details:,} ({100*has_ram_in_details/len(merged):.1f}%)")


def export_results(laptops_df, output_file='laptop_titles_analysis.csv'):
    """Export identified laptops to CSV."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    output_path = f"/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis/{output_file}"
    
    # Export full results
    laptops_df.to_csv(output_path, index=False)
    print(f"\n✅ Exported {len(laptops_df):,} laptops to:")
    print(f"   {output_path}")
    
    # Export just ASINs for easy filtering
    asins_file = output_path.replace('.csv', '_asins_only.csv')
    laptops_df[['parent_asin', 'confidence']].to_csv(asins_file, index=False)
    print(f"\n✅ Exported ASINs to:")
    print(f"   {asins_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("DEEP LAPTOP TITLE ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nCriteria:")
    print(f"  • Must have BRAND + SPECS (strict requirement)")
    print(f"  • OR explicit laptop keyword")
    print(f"  • Checks {len(LAPTOP_BRANDS)} brands, {len(LAPTOP_KEYWORDS)} keywords, 5 spec types")
    
    try:
        # Connect and load data
        conn = connect_db()
        df = load_titles(conn)
        
        # Classify laptops
        laptops_df = classify_laptops(df)
        
        if len(laptops_df) == 0:
            print("\n⚠️  No laptops identified! Check criteria.")
            return
        
        # Analyze brands
        analyze_brands(laptops_df)
        
        # Analyze specs
        analyze_specs(laptops_df)
        
        # Show samples
        sample_laptops(laptops_df)
        
        # Cross-validate
        cross_validate(laptops_df, df)
        
        # Export results
        export_results(laptops_df)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Products analyzed: {len(df):,}")
        print(f"Laptops identified: {len(laptops_df):,} ({100*len(laptops_df)/len(df):.2f}%)")
        print(f"\nFiles created:")
        print(f"  • laptop_titles_analysis.csv (full details)")
        print(f"  • laptop_titles_analysis_asins_only.csv (just ASINs)")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

