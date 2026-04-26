#!/usr/bin/env python3
"""
Comprehensive Analysis of FEATURES ARRAY in Parquet Files

This script performs in-depth analysis of product features stored as arrays
in the original Parquet files, similar to the details JSONB analysis.

Analysis includes:
- Coverage and length statistics
- Individual feature extraction
- Common keywords and patterns
- Category-specific features
- Feature structure analysis (bullets, specs, etc.)
- Laptop-specific feature detection
- Export to CSV for further analysis
"""

import pandas as pd
import numpy as np
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any
import glob
import os


PARQUET_DIR = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/data/processed/raw_meta_Electronics"
OUTPUT_DIR = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project"


def load_all_parquet_files(sample_size=None):
    """Load all Parquet files (or sample if specified)."""
    print("=" * 80)
    print("LOADING PARQUET FILES")
    print("=" * 80)
    
    parquet_files = sorted(glob.glob(os.path.join(PARQUET_DIR, "full-*.parquet")))
    print(f"\nFound {len(parquet_files)} Parquet files")
    
    dfs = []
    total_rows = 0
    
    for i, file in enumerate(parquet_files, 1):
        print(f"\nLoading file {i}/{len(parquet_files)}: {os.path.basename(file)}")
        df = pd.read_parquet(file)
        rows = len(df)
        total_rows += rows
        print(f"  Rows: {rows:,}")
        
        dfs.append(df)
        
        # If sampling, stop after reaching sample size
        if sample_size and total_rows >= sample_size:
            print(f"\n✓ Reached sample size: {total_rows:,} products")
            break
    
    print(f"\n✓ Total products loaded: {total_rows:,}")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    if sample_size and len(combined_df) > sample_size:
        combined_df = combined_df.sample(n=sample_size, random_state=42)
        print(f"✓ Sampled down to: {len(combined_df):,} products")
    
    return combined_df


def analyze_features_overview(df):
    """Get overview statistics of the features field."""
    print("\n" + "=" * 80)
    print("1. FEATURES ARRAY OVERVIEW")
    print("=" * 80)
    
    # Total products with features
    total_products = len(df)
    
    # Check which have non-empty features
    has_features = df['features'].apply(
        lambda x: isinstance(x, np.ndarray) and len(x) > 0
    ).sum()
    
    print(f"\nTotal Products Analyzed: {total_products:,}")
    print(f"Products with Features: {has_features:,}")
    print(f"Products without Features: {total_products - has_features:,}")
    print(f"Coverage: {100 * has_features / total_products:.2f}%")
    
    # Length statistics
    feature_lengths = df['features'].apply(
        lambda x: len(x) if isinstance(x, np.ndarray) else 0
    )
    
    non_empty_lengths = feature_lengths[feature_lengths > 0]
    
    if len(non_empty_lengths) > 0:
        print(f"\nFeatures Array Length (when non-empty):")
        print(f"  Average: {non_empty_lengths.mean():.1f} features per product")
        print(f"  Median: {non_empty_lengths.median():.0f} features per product")
        print(f"  Min: {non_empty_lengths.min()} features")
        print(f"  Max: {non_empty_lengths.max()} features")
        print(f"  25th percentile: {non_empty_lengths.quantile(0.25):.0f}")
        print(f"  75th percentile: {non_empty_lengths.quantile(0.75):.0f}")


def extract_all_features(df):
    """Extract all individual features from all products."""
    print("\n" + "=" * 80)
    print("2. EXTRACTING ALL INDIVIDUAL FEATURES")
    print("=" * 80)
    
    all_features = []
    feature_metadata = []  # (asin, category, feature)
    
    print("\nProcessing products...")
    for idx, row in df.iterrows():
        if isinstance(row['features'], np.ndarray) and len(row['features']) > 0:
            for feature in row['features']:
                feature_str = str(feature).strip()
                if feature_str:
                    all_features.append(feature_str)
                    feature_metadata.append({
                        'asin': row['parent_asin'],
                        'category': row['main_category'],
                        'feature': feature_str
                    })
        
        if (idx + 1) % 50000 == 0:
            print(f"  Processed {idx + 1:,} products...")
    
    print(f"\n✓ Total individual features extracted: {len(all_features):,}")
    print(f"✓ Unique features: {len(set(all_features)):,}")
    
    return all_features, feature_metadata


def analyze_feature_lengths(all_features):
    """Analyze the length of individual feature strings."""
    print("\n" + "=" * 80)
    print("3. FEATURE STRING LENGTH ANALYSIS")
    print("=" * 80)
    
    lengths = [len(f) for f in all_features]
    
    print(f"\nFeature String Lengths:")
    print(f"  Average: {np.mean(lengths):.1f} characters")
    print(f"  Median: {np.median(lengths):.0f} characters")
    print(f"  Min: {min(lengths)} characters")
    print(f"  Max: {max(lengths)} characters")
    
    # Categorize by length
    very_short = sum(1 for l in lengths if l < 20)  # UPC codes, weights
    short = sum(1 for l in lengths if 20 <= l < 50)  # Brief specs
    medium = sum(1 for l in lengths if 50 <= l < 150)  # Sentences
    long = sum(1 for l in lengths if 150 <= l < 300)  # Paragraphs
    very_long = sum(1 for l in lengths if l >= 300)  # Long descriptions
    
    total = len(lengths)
    print(f"\nLength Distribution:")
    print(f"  Very Short (<20 chars):     {very_short:>8,}  ({100*very_short/total:>5.1f}%)")
    print(f"  Short (20-50 chars):        {short:>8,}  ({100*short/total:>5.1f}%)")
    print(f"  Medium (50-150 chars):      {medium:>8,}  ({100*medium/total:>5.1f}%)")
    print(f"  Long (150-300 chars):       {long:>8,}  ({100*long/total:>5.1f}%)")
    print(f"  Very Long (>=300 chars):    {very_long:>8,}  ({100*very_long/total:>5.1f}%)")


def analyze_feature_patterns(all_features, sample_size=100000):
    """Analyze common patterns in features."""
    print("\n" + "=" * 80)
    print("4. FEATURE PATTERN ANALYSIS")
    print("=" * 80)
    
    # Sample for performance
    if len(all_features) > sample_size:
        sample_features = np.random.choice(all_features, sample_size, replace=False)
        print(f"\nAnalyzing sample of {sample_size:,} features")
    else:
        sample_features = all_features
        print(f"\nAnalyzing all {len(all_features):,} features")
    
    # Pattern detection
    patterns = {
        'has_colon': 0,  # "Brand: Sony"
        'has_bullets': 0,  # Contains •, ●, ◦
        'starts_with_number': 0,  # "1. Feature"
        'contains_specs': 0,  # RAM, CPU, GB, etc.
        'contains_dimensions': 0,  # inches, cm, mm
        'contains_weight': 0,  # lbs, kg, ounces
        'contains_upc': 0,  # UPC codes
        'all_caps': 0,  # ALL CAPS
        'contains_url': 0,  # URLs
        'question_mark': 0,  # Questions
    }
    
    spec_keywords = ['ram', 'cpu', 'processor', 'ghz', 'gb', 'tb', 'mb', 'cores', 'intel', 'amd']
    dimension_keywords = ['inch', 'inches', 'cm', 'mm', 'feet', 'foot']
    weight_keywords = ['lbs', 'pounds', 'kg', 'ounces', 'oz', 'grams']
    
    for feature in sample_features:
        feature_lower = feature.lower()
        
        if ':' in feature:
            patterns['has_colon'] += 1
        
        if any(bullet in feature for bullet in ['•', '●', '◦', '■', '▪']):
            patterns['has_bullets'] += 1
        
        if re.match(r'^\d+\.', feature.strip()):
            patterns['starts_with_number'] += 1
        
        if any(kw in feature_lower for kw in spec_keywords):
            patterns['contains_specs'] += 1
        
        if any(kw in feature_lower for kw in dimension_keywords):
            patterns['contains_dimensions'] += 1
        
        if any(kw in feature_lower for kw in weight_keywords):
            patterns['contains_weight'] += 1
        
        if 'upc' in feature_lower or re.search(r'\d{12,}', feature):
            patterns['contains_upc'] += 1
        
        if feature.isupper() and len(feature.split()) > 2:
            patterns['all_caps'] += 1
        
        if 'http' in feature_lower or 'www.' in feature_lower:
            patterns['contains_url'] += 1
        
        if '?' in feature:
            patterns['question_mark'] += 1
    
    print(f"\nPattern Frequencies:")
    total = len(sample_features)
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern:30} {count:>8,}  ({100*count/total:>5.1f}%)")


def extract_common_keywords(all_features, top_n=100):
    """Extract most common keywords from features."""
    print("\n" + "=" * 80)
    print("5. COMMON KEYWORDS IN FEATURES")
    print("=" * 80)
    
    # Sample for performance
    sample_size = min(200000, len(all_features))
    sample_features = np.random.choice(all_features, sample_size, replace=False)
    
    print(f"\nAnalyzing {sample_size:,} features for keywords...")
    
    word_counter = Counter()
    
    for feature in sample_features:
        # Extract words (alphanumeric, 3+ chars)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', feature.lower())
        word_counter.update(words)
    
    # Filter stop words
    stop_words = {
        'the', 'and', 'with', 'for', 'from', 'this', 'that', 'have', 'are', 'not',
        'but', 'can', 'all', 'your', 'when', 'use', 'you', 'how', 'will', 'more',
        'also', 'into', 'about', 'than', 'been', 'has', 'had', 'was', 'were', 'their',
        'what', 'which', 'who', 'would', 'make', 'like', 'time', 'just', 'know', 'take',
        'people', 'year', 'them', 'see', 'other', 'could', 'there', 'some', 'her',
        'only', 'its', 'over', 'think', 'also', 'back', 'after', 'our', 'work', 'first',
        'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
        'most', 'designed', 'made', 'used', 'compatible', 'compatible', 'high', 'quality'
    }
    
    filtered_words = {word: count for word, count in word_counter.items() 
                     if word not in stop_words and len(word) > 3}
    
    print(f"\nTop {top_n} Keywords:")
    print(f"{'Rank':<6} {'Keyword':<25} {'Frequency':<12} {'% of Features'}")
    print("-" * 80)
    
    top_keywords = []
    for i, (word, count) in enumerate(sorted(filtered_words.items(), 
                                             key=lambda x: x[1], 
                                             reverse=True)[:top_n], 1):
        pct = 100 * count / sample_size
        print(f"{i:<6} {word:<25} {count:>10,}  {pct:>6.2f}%")
        top_keywords.append((word, count, pct))
    
    return top_keywords


def analyze_by_category(df):
    """Analyze features by product category."""
    print("\n" + "=" * 80)
    print("6. FEATURES BY CATEGORY")
    print("=" * 80)
    
    # Group by category
    category_stats = []
    
    for category in df['main_category'].value_counts().head(20).index:
        cat_df = df[df['main_category'] == category]
        
        # Count products with features
        has_features = cat_df['features'].apply(
            lambda x: isinstance(x, np.ndarray) and len(x) > 0
        ).sum()
        
        # Average length
        feature_lengths = cat_df['features'].apply(
            lambda x: len(x) if isinstance(x, np.ndarray) else 0
        )
        avg_length = feature_lengths[feature_lengths > 0].mean() if has_features > 0 else 0
        
        category_stats.append({
            'category': category,
            'total_products': len(cat_df),
            'with_features': has_features,
            'coverage_pct': 100 * has_features / len(cat_df),
            'avg_features': avg_length
        })
    
    # Sort by total products
    category_stats.sort(key=lambda x: x['total_products'], reverse=True)
    
    print(f"\n{'Category':<35} {'Products':<12} {'Coverage':<10} {'Avg Features':<12}")
    print("-" * 80)
    
    for stat in category_stats:
        print(f"{stat['category'][:33]:<35} {stat['total_products']:>10,}  "
              f"{stat['coverage_pct']:>7.1f}%  {stat['avg_features']:>10.1f}")
    
    return category_stats


def sample_features_by_category(df, categories=['Computers', 'Home Audio & Theater', 
                                               'Cell Phones & Accessories', 'Camera & Photo']):
    """Show sample features from different categories."""
    print("\n" + "=" * 80)
    print("7. SAMPLE FEATURES BY CATEGORY")
    print("=" * 80)
    
    for category in categories:
        cat_df = df[df['main_category'] == category]
        
        # Get products with features
        with_features = cat_df[cat_df['features'].apply(
            lambda x: isinstance(x, np.ndarray) and len(x) > 3
        )]
        
        if len(with_features) == 0:
            continue
        
        # Sample one product
        sample = with_features.iloc[0]
        
        print(f"\n{'─' * 80}")
        print(f"Category: {category}")
        print(f"{'─' * 80}")
        print(f"ASIN: {sample['parent_asin']}")
        print(f"Title: {sample['title'][:70]}...")
        print(f"Number of Features: {len(sample['features'])}")
        
        print(f"\nFeatures:")
        for i, feature in enumerate(sample['features'][:8], 1):
            feature_str = str(feature)
            if len(feature_str) > 90:
                feature_str = feature_str[:87] + "..."
            print(f"  [{i}] {feature_str}")
        
        if len(sample['features']) > 8:
            print(f"  ... and {len(sample['features']) - 8} more features")


def identify_laptop_features(feature_metadata):
    """Identify laptop-specific features and keywords."""
    print("\n" + "=" * 80)
    print("8. LAPTOP-SPECIFIC FEATURE ANALYSIS")
    print("=" * 80)
    
    # Laptop indicators
    laptop_keywords = {
        'hardware': ['ram', 'cpu', 'processor', 'graphics', 'gpu', 'memory', 'storage', 
                    'hard drive', 'ssd', 'hdd', 'cores', 'ghz', 'intel', 'amd', 'nvidia'],
        'display': ['screen', 'display', 'resolution', 'monitor', 'lcd', 'led', 'ips', 
                   'touchscreen', 'retina'],
        'os': ['windows', 'macos', 'mac os', 'chrome os', 'chromebook', 'linux', 'ubuntu'],
        'laptop_types': ['laptop', 'notebook', 'ultrabook', 'chromebook', 'macbook', 
                        'thinkpad', 'gaming laptop', '2-in-1'],
        'battery': ['battery', 'battery life', 'hours battery', 'mah', 'wh'],
        'connectivity': ['wifi', 'bluetooth', 'usb', 'hdmi', 'thunderbolt', 'usb-c', 'ethernet'],
        'build': ['aluminum', 'metal', 'plastic', 'weight', 'thin', 'portable', 'lightweight']
    }
    
    # Count features by category
    laptop_feature_counts = defaultdict(lambda: defaultdict(int))
    
    print("\nScanning features for laptop indicators...")
    
    for item in feature_metadata:
        feature_lower = item['feature'].lower()
        
        for category, keywords in laptop_keywords.items():
            for keyword in keywords:
                if keyword in feature_lower:
                    laptop_feature_counts[category][keyword] += 1
    
    # Display results
    print("\nLaptop-Related Keywords by Category:")
    print("=" * 80)
    
    for category, keywords in laptop_feature_counts.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        for keyword, count in sorted_keywords[:10]:
            print(f"  {keyword:30} {count:>8,} occurrences")


def export_features_analysis(df, all_features, top_keywords, output_file='features_parquet_analysis.csv'):
    """Export detailed analysis to CSV."""
    print("\n" + "=" * 80)
    print("9. EXPORTING ANALYSIS TO CSV")
    print("=" * 80)
    
    # Create analysis dataframe
    analysis_data = []
    
    # Sample features with metadata
    sample_size = min(50000, len(all_features))
    print(f"\nPreparing {sample_size:,} sample features for export...")
    
    sample_indices = np.random.choice(len(all_features), sample_size, replace=False)
    
    for idx in sample_indices:
        feature = all_features[idx]
        
        analysis_data.append({
            'feature': feature,
            'length': len(feature),
            'word_count': len(feature.split()),
            'has_colon': ':' in feature,
            'has_specs': any(kw in feature.lower() for kw in ['ram', 'cpu', 'gb', 'ghz']),
            'has_dimensions': any(kw in feature.lower() for kw in ['inch', 'cm', 'mm']),
            'is_laptop_related': any(kw in feature.lower() for kw in 
                                    ['laptop', 'notebook', 'ram', 'cpu', 'windows', 'macos'])
        })
    
    analysis_df = pd.DataFrame(analysis_data)
    
    output_path = os.path.join(OUTPUT_DIR, output_file)
    analysis_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Exported {len(analysis_df):,} features to: {output_file}")
    print(f"   Location: {output_path}")
    
    # Show summary
    print(f"\nExport Summary:")
    print(f"  Total features: {len(analysis_df):,}")
    print(f"  With specs: {analysis_df['has_specs'].sum():,} ({100*analysis_df['has_specs'].mean():.1f}%)")
    print(f"  Laptop-related: {analysis_df['is_laptop_related'].sum():,} ({100*analysis_df['is_laptop_related'].mean():.1f}%)")
    print(f"  Avg length: {analysis_df['length'].mean():.1f} characters")


def main():
    """Run all analyses."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE FEATURES ARRAY ANALYSIS (PARQUET)")
    print("Database: Parquet Files (1.8M products)")
    print("Field: features (numpy.ndarray)")
    print("=" * 80)
    
    # Load data (sample for performance)
    print("\n⚠️  Loading sample of 200,000 products for analysis...")
    print("   (Full 1.8M would take ~30 minutes)")
    df = load_all_parquet_files(sample_size=200000)
    
    # Run analyses
    analyze_features_overview(df)
    
    all_features, feature_metadata = extract_all_features(df)
    
    analyze_feature_lengths(all_features)
    
    analyze_feature_patterns(all_features)
    
    top_keywords = extract_common_keywords(all_features, top_n=100)
    
    analyze_by_category(df)
    
    sample_features_by_category(df)
    
    identify_laptop_features(feature_metadata)
    
    export_features_analysis(df, all_features, top_keywords)
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Review features_parquet_analysis.csv")
    print("  2. Use insights for laptop identification")
    print("  3. Decide on PostgreSQL array column strategy")
    print("=" * 80)


if __name__ == "__main__":
    main()

