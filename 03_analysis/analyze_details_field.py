#!/usr/bin/env python3
"""
Analyze the 'details' JSONB field in the products table.

This script performs comprehensive analysis of product specifications stored
in the details JSONB field, including:
- Key frequency analysis
- Value type distribution
- Common specification patterns
- Category-specific details
- Data quality metrics
"""

import psycopg2
import json
from collections import Counter, defaultdict
from typing import Dict, List, Any
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


def analyze_details_overview(conn):
    """Get overview statistics of the details field."""
    print("=" * 80)
    print("1. DETAILS FIELD OVERVIEW")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Total products with details
        cur.execute("""
            SELECT 
                COUNT(*) as total_products,
                COUNT(details) as products_with_details,
                COUNT(*) - COUNT(details) as products_without_details,
                ROUND(100.0 * COUNT(details) / COUNT(*), 2) as coverage_pct
            FROM products;
        """)
        
        result = cur.fetchone()
        print(f"\nTotal Products: {result[0]:,}")
        print(f"Products with Details: {result[1]:,}")
        print(f"Products without Details: {result[2]:,}")
        print(f"Coverage: {result[3]}%")
        
        # Average number of keys per product - simpler approach
        cur.execute("""
            SELECT 
                AVG(key_count)::numeric(10,2) as avg_keys,
                MIN(key_count) as min_keys,
                MAX(key_count) as max_keys,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY key_count)::numeric(10,2) as median_keys
            FROM (
                SELECT COUNT(*) as key_count
                FROM products, jsonb_object_keys(details)
                WHERE details IS NOT NULL AND details != 'null'::jsonb
                GROUP BY parent_asin
            ) key_counts;
        """)
        
        result = cur.fetchone()
        if result and result[0]:
            print(f"\nAverage Keys per Product: {result[0]:.2f}")
            print(f"Min Keys: {result[1]}")
            print(f"Max Keys: {result[2]}")
            print(f"Median Keys: {result[3]:.2f}")


def analyze_key_frequency(conn, limit=50):
    """Analyze the most common keys in details."""
    print("\n" + "=" * 80)
    print("2. TOP KEYS IN DETAILS FIELD")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get all unique keys and their frequencies
        cur.execute("""
            SELECT 
                key,
                COUNT(*) as frequency,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM products WHERE details IS NOT NULL), 2) as pct
            FROM products, jsonb_each(details)
            WHERE details IS NOT NULL
            GROUP BY key
            ORDER BY frequency DESC
            LIMIT %s;
        """, (limit,))
        
        results = cur.fetchall()
        
        print(f"\n{'Rank':<6} {'Key':<40} {'Frequency':<12} {'Coverage':<10}")
        print("-" * 80)
        for i, (key, freq, pct) in enumerate(results, 1):
            print(f"{i:<6} {key:<40} {freq:>10,}  {pct:>8}%")
        
        return results


def analyze_key_patterns(conn):
    """Analyze patterns in key names."""
    print("\n" + "=" * 80)
    print("3. KEY NAME PATTERNS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get all unique keys
        cur.execute("""
            SELECT DISTINCT key
            FROM products, jsonb_each(details)
            WHERE details IS NOT NULL;
        """)
        
        keys = [row[0] for row in cur.fetchall()]
        
        # Analyze patterns
        patterns = {
            'Contains "size"': [k for k in keys if 'size' in k.lower()],
            'Contains "weight"': [k for k in keys if 'weight' in k.lower()],
            'Contains "color"': [k for k in keys if 'color' in k.lower()],
            'Contains "power"': [k for k in keys if 'power' in k.lower()],
            'Contains "battery"': [k for k in keys if 'battery' in k.lower()],
            'Contains "connectivity"': [k for k in keys if 'connect' in k.lower()],
            'Contains "material"': [k for k in keys if 'material' in k.lower()],
            'Contains "dimension"': [k for k in keys if 'dimension' in k.lower()],
            'All caps (acronyms)': [k for k in keys if k.isupper() and len(k) > 1],
            'Has spaces': [k for k in keys if ' ' in k],
        }
        
        print(f"\n{'Pattern':<30} {'Count':<10} {'Examples (first 5)'}")
        print("-" * 80)
        for pattern_name, matches in patterns.items():
            examples = ', '.join(matches[:5]) if matches else 'None'
            if len(examples) > 40:
                examples = examples[:37] + '...'
            print(f"{pattern_name:<30} {len(matches):<10} {examples}")
        
        print(f"\nTotal Unique Keys: {len(keys):,}")


def analyze_value_types(conn):
    """Analyze the types of values in details."""
    print("\n" + "=" * 80)
    print("4. VALUE CONTENT ANALYSIS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Sample products to analyze value content
        cur.execute("""
            SELECT details
            FROM products
            WHERE details IS NOT NULL 
                AND details != 'null'::jsonb
                AND jsonb_typeof(details) = 'object'
            LIMIT 10000;
        """)
        
        results = cur.fetchall()
        
        value_lengths = []
        value_types = Counter()
        numeric_keys = set()
        text_keys = set()
        
        for (details_json,) in results:
            if not details_json:
                continue
                
            for key, value in details_json.items():
                value_str = str(value)
                value_lengths.append(len(value_str))
                
                # Classify value type
                if value_str.replace('.', '').replace('-', '').isdigit():
                    value_types['numeric'] += 1
                    numeric_keys.add(key)
                elif len(value_str) < 50:
                    value_types['short_text'] += 1
                    text_keys.add(key)
                elif len(value_str) < 200:
                    value_types['medium_text'] += 1
                    text_keys.add(key)
                else:
                    value_types['long_text'] += 1
                    text_keys.add(key)
        
        print(f"\nAnalyzed {len(results):,} products")
        print(f"\nValue Type Distribution:")
        print(f"  Numeric values: {value_types['numeric']:,} ({100*value_types['numeric']/sum(value_types.values()):.1f}%)")
        print(f"  Short text (<50 chars): {value_types['short_text']:,} ({100*value_types['short_text']/sum(value_types.values()):.1f}%)")
        print(f"  Medium text (50-200 chars): {value_types['medium_text']:,} ({100*value_types['medium_text']/sum(value_types.values()):.1f}%)")
        print(f"  Long text (>200 chars): {value_types['long_text']:,} ({100*value_types['long_text']/sum(value_types.values()):.1f}%)")
        
        print(f"\nValue Length Statistics:")
        print(f"  Average: {sum(value_lengths)/len(value_lengths):.1f} characters")
        print(f"  Min: {min(value_lengths)} characters")
        print(f"  Max: {max(value_lengths)} characters")
        print(f"  Median: {sorted(value_lengths)[len(value_lengths)//2]} characters")


def analyze_by_category(conn):
    """Analyze details by product category."""
    print("\n" + "=" * 80)
    print("5. CATEGORY-SPECIFIC DETAILS ANALYSIS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get top categories
        cur.execute("""
            SELECT 
                main_category,
                COUNT(*) as product_count
            FROM products
            WHERE main_category IS NOT NULL
            GROUP BY main_category
            ORDER BY product_count DESC
            LIMIT 10;
        """)
        
        top_categories = cur.fetchall()
        
        print(f"\n{'Category':<40} {'Products':<12} {'Top 5 Keys'}")
        print("-" * 120)
        
        for category, count in top_categories:
            # Get top keys for this category
            cur.execute("""
                SELECT 
                    key,
                    COUNT(*) as freq
                FROM products, jsonb_each(details)
                WHERE details IS NOT NULL 
                    AND main_category = %s
                GROUP BY key
                ORDER BY freq DESC
                LIMIT 5;
            """, (category,))
            
            top_keys = [row[0] for row in cur.fetchall()]
            keys_str = ', '.join(top_keys) if top_keys else 'None'
            if len(keys_str) > 60:
                keys_str = keys_str[:57] + '...'
            
            print(f"{category[:38]:<40} {count:>10,}  {keys_str}")


def analyze_specific_keys(conn):
    """Analyze specific important keys in detail."""
    print("\n" + "=" * 80)
    print("6. DETAILED ANALYSIS OF IMPORTANT KEYS")
    print("=" * 80)
    
    important_keys = [
        'Brand', 'Manufacturer', 'Model', 'Color', 'Size',
        'Weight', 'Dimensions', 'Material', 'Connectivity Technology',
        'Power Source', 'Battery Life', 'Wattage', 'Voltage'
    ]
    
    with conn.cursor() as cur:
        results = []
        
        for key in important_keys:
            # Count products with this key
            cur.execute("""
                SELECT COUNT(*)
                FROM products
                WHERE details ? %s;
            """, (key,))
            
            count = cur.fetchone()[0]
            
            if count > 0:
                # Get sample values
                cur.execute("""
                    SELECT DISTINCT details ->> %s as value
                    FROM products
                    WHERE details ? %s
                    LIMIT 5;
                """, (key, key))
                
                sample_values = [row[0] for row in cur.fetchall() if row[0]]
                results.append((key, count, sample_values))
        
        print(f"\n{'Key':<30} {'Count':<12} {'Sample Values'}")
        print("-" * 100)
        
        for key, count, samples in sorted(results, key=lambda x: x[1], reverse=True):
            samples_str = ', '.join([s[:20] for s in samples[:3]])
            if len(samples_str) > 50:
                samples_str = samples_str[:47] + '...'
            print(f"{key:<30} {count:>10,}  {samples_str}")


def sample_details_records(conn, n=10):
    """Show sample details records from different categories."""
    print("\n" + "=" * 80)
    print("7. SAMPLE DETAILS RECORDS")
    print("=" * 80)
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                parent_asin,
                title,
                main_category,
                details
            FROM products
            WHERE details IS NOT NULL 
                AND details != 'null'::jsonb
                AND jsonb_typeof(details) = 'object'
            ORDER BY RANDOM()
            LIMIT %s;
        """, (n,))
        
        results = cur.fetchall()
        
        for i, (asin, title, category, details) in enumerate(results, 1):
            print(f"\n{i}. ASIN: {asin}")
            print(f"   Title: {title[:70]}...")
            print(f"   Category: {category}")
            print(f"   Details ({len(details)} keys):")
            
            # Show first 10 key-value pairs
            for j, (key, value) in enumerate(list(details.items())[:10], 1):
                value_str = str(value)
                if len(value_str) > 60:
                    value_str = value_str[:57] + '...'
                print(f"      {key}: {value_str}")
            
            if len(details) > 10:
                print(f"      ... and {len(details) - 10} more keys")


def export_analysis(conn, output_file='details_analysis.csv'):
    """Export details key frequency to CSV."""
    print("\n" + "=" * 80)
    print("8. EXPORTING ANALYSIS TO CSV")
    print("=" * 80)
    
    with conn.cursor() as cur:
        # Get all keys with their frequencies (simplified - no sample values for performance)
        cur.execute("""
            SELECT 
                key,
                COUNT(*) as frequency,
                COUNT(DISTINCT parent_asin) as unique_products,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM products WHERE details IS NOT NULL), 2) as coverage_pct
            FROM products, jsonb_each(details)
            WHERE details IS NOT NULL
            GROUP BY key
            ORDER BY frequency DESC;
        """)
        
        results = cur.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            'key', 'frequency', 'unique_products', 'coverage_pct'
        ])
        
        # Export to CSV
        output_path = f"/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/{output_file}"
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ Exported {len(df):,} unique keys to: {output_file}")
        print(f"   Location: {output_path}")
        
        # Show summary
        print(f"\nSummary:")
        print(f"  Total unique keys: {len(df):,}")
        print(f"  Keys in >50% of products: {len(df[df['coverage_pct'] > 50]):,}")
        print(f"  Keys in >10% of products: {len(df[df['coverage_pct'] > 10]):,}")
        print(f"  Keys in <1% of products: {len(df[df['coverage_pct'] < 1]):,}")


def main():
    """Run all analyses."""
    print("\n" + "=" * 80)
    print("PRODUCT DETAILS FIELD ANALYSIS")
    print("Database: amazon_electronics_rag")
    print("Table: products")
    print("Field: details (JSONB)")
    print("=" * 80)
    
    conn = connect_db()
    
    try:
        analyze_details_overview(conn)
        analyze_key_frequency(conn, limit=50)
        analyze_key_patterns(conn)
        analyze_value_types(conn)
        analyze_by_category(conn)
        analyze_specific_keys(conn)
        sample_details_records(conn, n=5)
        export_analysis(conn)
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()

