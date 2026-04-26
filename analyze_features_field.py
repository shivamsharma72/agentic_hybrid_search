#!/usr/bin/env python3
"""
Analyze the 'features' TEXT field in the products table.

This script performs comprehensive analysis of product features stored
in the features TEXT field, including:
- Coverage and length statistics
- Common feature patterns
- Feature extraction and parsing
- Category-specific features
- Comparison with details field
"""

import psycopg2
import re
from collections import Counter, defaultdict
from typing import List, Dict, Any
import pandas as pd


def connect_db():
    """Connect to PostgreSQL database."""
    return psycopg2.connect(
        dbname="amazon_electronics_rag",
        user="shivamsharma",
        password="",
        host="localhost",
        port="5432"
    )


def analyze_features_overview(conn):
    """Get overview statistics of the features field."""
    print("=" * 80)
    print("1. FEATURES FIELD OVERVIEW")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Total products with features
        cur.execute("""
            SELECT 
                COUNT(*) as total_products,
                COUNT(features) as products_with_features,
                COUNT(*) - COUNT(features) as products_without_features,
                ROUND(100.0 * COUNT(features) / COUNT(*), 2) as coverage_pct
            FROM products;
        """)
        
        result = cur.fetchone()
        print(f"\nTotal Products: {result[0]:,}")
        print(f"Products with Features: {result[1]:,}")
        print(f"Products without Features: {result[2]:,}")
        print(f"Coverage: {result[3]}%")
        
        # Length statistics
        cur.execute("""
            SELECT 
                AVG(LENGTH(features))::int as avg_length,
                MIN(LENGTH(features)) as min_length,
                MAX(LENGTH(features)) as max_length,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY LENGTH(features))::int as median_length
            FROM products
            WHERE features IS NOT NULL AND features != '';
        """)
        
        result = cur.fetchone()
        print(f"\nFeatures Text Length (characters):")
        print(f"  Average: {result[0]:,} characters")
        print(f"  Min: {result[1]:,} characters")
        print(f"  Max: {result[2]:,} characters")
        print(f"  Median: {result[3]:,} characters")


def sample_features_by_category(conn):
    """Show sample features from different categories."""
    print("\n" + "=" * 80)
    print("2. SAMPLE FEATURES BY CATEGORY")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get samples from different categories
        cur.execute("""
            SELECT DISTINCT ON (main_category)
                parent_asin,
                title,
                main_category,
                features
            FROM products
            WHERE features IS NOT NULL 
                AND features != ''
                AND main_category IN ('Computers', 'Home Audio & Theater', 'Cell Phones & Accessories', 
                                     'Camera & Photo', 'Car Electronics')
            ORDER BY main_category, RANDOM()
            LIMIT 5;
        """)
        
        results = cur.fetchall()
        
        for i, (asin, title, category, features) in enumerate(results, 1):
            print(f"\n{i}. {category}")
            print(f"   ASIN: {asin}")
            print(f"   Title: {title[:60]}...")
            print(f"   Features Length: {len(features):,} characters")
            print(f"   First 300 characters:")
            print(f"   {features[:300]}...")


def analyze_feature_structure(conn):
    """Analyze the structure of features text."""
    print("\n" + "=" * 80)
    print("3. FEATURES TEXT STRUCTURE ANALYSIS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Sample features to analyze structure
        cur.execute("""
            SELECT features
            FROM products
            WHERE features IS NOT NULL 
                AND features != ''
            ORDER BY RANDOM()
            LIMIT 1000;
        """)
        
        features_samples = [row[0] for row in cur.fetchall()]
        
        # Analyze patterns
        has_bullets = 0
        has_newlines = 0
        has_numbers = 0
        has_sentences = 0
        avg_bullets_per_product = []
        
        for features in features_samples:
            # Check for bullet points or list markers
            if '•' in features or '●' in features or '◦' in features:
                has_bullets += 1
            
            # Check for newlines (line breaks)
            if '\n' in features:
                has_newlines += 1
                # Count number of lines
                lines = [line.strip() for line in features.split('\n') if line.strip()]
                avg_bullets_per_product.append(len(lines))
            
            # Check for numbered lists (1., 2., etc.)
            if re.search(r'\d+\.', features):
                has_numbers += 1
            
            # Check for sentence structure (periods)
            if '. ' in features:
                has_sentences += 1
        
        print(f"\nStructure Patterns (sample of 1,000 products):")
        print(f"  Has bullet points (•, ●, ◦): {has_bullets} ({100*has_bullets/1000:.1f}%)")
        print(f"  Has newlines (\\n): {has_newlines} ({100*has_newlines/1000:.1f}%)")
        print(f"  Has numbered lists (1., 2.): {has_numbers} ({100*has_numbers/1000:.1f}%)")
        print(f"  Has sentence structure: {has_sentences} ({100*has_sentences/1000:.1f}%)")
        
        if avg_bullets_per_product:
            print(f"\nAverage number of feature lines: {sum(avg_bullets_per_product)/len(avg_bullets_per_product):.1f}")


def extract_common_keywords(conn, limit=50):
    """Extract common keywords/phrases from features."""
    print("\n" + "=" * 80)
    print("4. COMMON KEYWORDS IN FEATURES")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Sample features
        cur.execute("""
            SELECT features
            FROM products
            WHERE features IS NOT NULL 
                AND features != ''
            ORDER BY RANDOM()
            LIMIT 10000;
        """)
        
        features_samples = [row[0] for row in cur.fetchall()]
        
        # Extract keywords (words that appear frequently)
        word_counter = Counter()
        
        for features in features_samples:
            # Convert to lowercase and split into words
            words = re.findall(r'\b[a-z]{4,}\b', features.lower())
            word_counter.update(words)
        
        # Filter out common stop words
        stop_words = {'with', 'from', 'this', 'that', 'have', 'for', 'and', 'the', 'are', 'not', 
                     'but', 'can', 'all', 'your', 'when', 'use', 'you', 'how', 'will', 'more',
                     'also', 'into', 'about', 'them', 'than', 'been', 'has', 'had', 'was', 'were'}
        
        filtered_words = {word: count for word, count in word_counter.items() 
                         if word not in stop_words}
        
        print(f"\nTop {limit} Keywords (from 10,000 products):")
        print(f"{'Rank':<6} {'Keyword':<20} {'Frequency':<12}")
        print("-" * 80)
        
        for i, (word, count) in enumerate(sorted(filtered_words.items(), 
                                                 key=lambda x: x[1], 
                                                 reverse=True)[:limit], 1):
            print(f"{i:<6} {word:<20} {count:>10,}")


def analyze_by_category(conn):
    """Analyze features by product category."""
    print("\n" + "=" * 80)
    print("5. FEATURES BY CATEGORY")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get average length by category
        cur.execute("""
            SELECT 
                main_category,
                COUNT(*) as product_count,
                COUNT(features) as with_features,
                ROUND(100.0 * COUNT(features) / COUNT(*), 2) as coverage_pct,
                AVG(LENGTH(features))::int as avg_length
            FROM products
            WHERE main_category IS NOT NULL
            GROUP BY main_category
            HAVING COUNT(*) > 1000
            ORDER BY product_count DESC
            LIMIT 15;
        """)
        
        results = cur.fetchall()
        
        print(f"\n{'Category':<35} {'Products':<12} {'Coverage':<10} {'Avg Length':<12}")
        print("-" * 80)
        
        for category, count, with_features, coverage, avg_len in results:
            print(f"{category[:33]:<35} {count:>10,}  {coverage:>7}%  {avg_len:>10,}")


def compare_with_details(conn):
    """Compare features field with details field."""
    print("\n" + "=" * 80)
    print("6. COMPARISON: FEATURES vs DETAILS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Products with both
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(features) as has_features,
                COUNT(details) as has_details,
                COUNT(CASE WHEN features IS NOT NULL AND details IS NOT NULL THEN 1 END) as has_both,
                COUNT(CASE WHEN features IS NULL AND details IS NULL THEN 1 END) as has_neither
            FROM products;
        """)
        
        result = cur.fetchone()
        total, has_features, has_details, has_both, has_neither = result
        
        print(f"\nOverlap Analysis:")
        print(f"  Total products: {total:,}")
        print(f"  Have features: {has_features:,} ({100*has_features/total:.1f}%)")
        print(f"  Have details: {has_details:,} ({100*has_details/total:.1f}%)")
        print(f"  Have BOTH: {has_both:,} ({100*has_both/total:.1f}%)")
        print(f"  Have NEITHER: {has_neither:,} ({100*has_neither/total:.1f}%)")


def extract_feature_list_sample(conn):
    """Extract and parse a sample of feature lists."""
    print("\n" + "=" * 80)
    print("7. PARSED FEATURE LISTS (SAMPLES)")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get products with features
        cur.execute("""
            SELECT parent_asin, title, features
            FROM products
            WHERE features IS NOT NULL 
                AND features != ''
                AND LENGTH(features) > 100
            ORDER BY RANDOM()
            LIMIT 3;
        """)
        
        results = cur.fetchall()
        
        for i, (asin, title, features) in enumerate(results, 1):
            print(f"\n{i}. ASIN: {asin}")
            print(f"   Title: {title[:70]}...")
            print(f"   Parsed Features:")
            
            # Try to split into individual features
            # Features might be separated by newlines, bullets, or numbers
            feature_lines = []
            
            if '\n' in features:
                # Split by newlines
                feature_lines = [line.strip() for line in features.split('\n') if line.strip()]
            elif '•' in features or '●' in features:
                # Split by bullets
                feature_lines = re.split(r'[•●◦]', features)
                feature_lines = [line.strip() for line in feature_lines if line.strip()]
            else:
                # Try splitting by sentences
                feature_lines = [s.strip() for s in features.split('. ') if s.strip()]
            
            # Show first 10 features
            for j, feature in enumerate(feature_lines[:10], 1):
                if len(feature) > 80:
                    feature = feature[:77] + "..."
                print(f"      {j:2}. {feature}")
            
            if len(feature_lines) > 10:
                print(f"      ... and {len(feature_lines) - 10} more features")


def export_analysis(conn, output_file='features_analysis.csv'):
    """Export features analysis to CSV."""
    print("\n" + "=" * 80)
    print("8. EXPORTING ANALYSIS TO CSV")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get features statistics by product
        cur.execute("""
            SELECT 
                parent_asin,
                main_category,
                LENGTH(features) as feature_length,
                CASE 
                    WHEN features LIKE '%\n%' THEN 'newline_separated'
                    WHEN features LIKE '%•%' OR features LIKE '%●%' THEN 'bullet_points'
                    WHEN features ~ '\d+\.' THEN 'numbered_list'
                    ELSE 'paragraph'
                END as format_type
            FROM products
            WHERE features IS NOT NULL AND features != ''
            LIMIT 10000;
        """)
        
        results = cur.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            'parent_asin', 'main_category', 'feature_length', 'format_type'
        ])
        
        # Export to CSV
        output_path = f"/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/{output_file}"
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ Exported {len(df):,} product features to: {output_file}")
        print(f"   Location: {output_path}")
        
        # Show summary
        print(f"\nFormat Type Distribution:")
        format_counts = df['format_type'].value_counts()
        for format_type, count in format_counts.items():
            print(f"  {format_type}: {count:,} ({100*count/len(df):.1f}%)")
        
        print(f"\nLength Statistics:")
        print(f"  Average: {df['feature_length'].mean():.0f} characters")
        print(f"  Median: {df['feature_length'].median():.0f} characters")
        print(f"  Min: {df['feature_length'].min()} characters")
        print(f"  Max: {df['feature_length'].max():,} characters")


def main():
    """Run all analyses."""
    print("\n" + "=" * 80)
    print("PRODUCT FEATURES FIELD ANALYSIS")
    print("Database: amazon_electronics_rag")
    print("Table: products")
    print("Field: features (TEXT)")
    print("=" * 80)
    
    conn = connect_db()
    
    try:
        analyze_features_overview(conn)
        sample_features_by_category(conn)
        analyze_feature_structure(conn)
        extract_common_keywords(conn, limit=50)
        analyze_by_category(conn)
        compare_with_details(conn)
        extract_feature_list_sample(conn)
        export_analysis(conn)
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()

