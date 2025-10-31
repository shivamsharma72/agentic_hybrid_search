#!/usr/bin/env python3
"""
Complete Hierarchical Distribution Analysis

This script provides an ACCURATE picture of category distribution considering:
1. TRUE LEAVES (never parents): Final, specific categories
2. INTERMEDIATE LEAVES (both leaf & parent): Can be endpoints or have children
3. PURE PARENTS (never leaves): Always have children

Creates a comprehensive view of the hierarchy and distribution.

Author: AI Assistant
Date: October 31, 2025
"""

import psycopg2
import pandas as pd
import json
from collections import Counter, defaultdict
from datetime import datetime

# Configuration
DB_NAME = "amazon_electronics_rag"


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


def analyze_complete_hierarchy(conn):
    """Build complete category hierarchy with accurate classification."""
    print("\n" + "=" * 80)
    print("BUILDING COMPLETE CATEGORY HIERARCHY")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            categories
        FROM products
        WHERE categories IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    
    print(f"\n🔍 Processing {len(df):,} products...")
    
    # Data structures
    all_categories = set()
    leaf_occurrences = Counter()  # Categories appearing as leaf
    parent_categories = set()  # Categories with children
    category_children = defaultdict(set)  # Parent -> Children
    category_parents = defaultdict(set)  # Child -> Parents
    product_categories = {}  # ASIN -> full category path
    products_by_leaf = defaultdict(list)  # Leaf -> [ASINs]
    
    for idx, row in df.iterrows():
        asin = row['parent_asin']
        categories = row['categories']
        
        if categories is None:
            continue
        
        # Convert to list
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        if not isinstance(categories, list) or len(categories) == 0:
            continue
        
        # Clean categories
        categories = [c.strip() for c in categories if c and c.strip()]
        
        # Store product's full path
        product_categories[asin] = categories
        
        # Track all categories
        all_categories.update(categories)
        
        # Track leaf (last category)
        if len(categories) > 0:
            leaf = categories[-1]
            leaf_occurrences[leaf] += 1
            products_by_leaf[leaf].append(asin)
        
        # Track parent-child relationships
        for i in range(len(categories) - 1):
            parent = categories[i]
            child = categories[i + 1]
            parent_categories.add(parent)
            category_children[parent].add(child)
            category_parents[child].add(parent)
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Hierarchy built!")
    
    return {
        'all_categories': all_categories,
        'leaf_occurrences': leaf_occurrences,
        'parent_categories': parent_categories,
        'category_children': category_children,
        'category_parents': category_parents,
        'product_categories': product_categories,
        'products_by_leaf': products_by_leaf
    }


def classify_categories(hierarchy_data):
    """Classify all categories by type."""
    print("\n" + "=" * 80)
    print("CLASSIFYING ALL CATEGORIES")
    print("=" * 80)
    
    all_cats = hierarchy_data['all_categories']
    leaf_occ = hierarchy_data['leaf_occurrences']
    parent_cats = hierarchy_data['parent_categories']
    cat_children = hierarchy_data['category_children']
    
    # Classification
    true_leaves = {}  # Never parent
    intermediate = {}  # Both leaf and parent
    pure_parents = {}  # Never leaf
    
    for cat in all_cats:
        is_leaf = cat in leaf_occ
        is_parent = cat in parent_cats
        
        if is_leaf and not is_parent:
            true_leaves[cat] = {
                'product_count': leaf_occ[cat],
                'as_leaf': leaf_occ[cat],
                'children': []
            }
        elif is_leaf and is_parent:
            intermediate[cat] = {
                'product_count': leaf_occ[cat],
                'as_leaf': leaf_occ[cat],
                'children': list(cat_children[cat])
            }
        elif is_parent and not is_leaf:
            pure_parents[cat] = {
                'product_count': 0,
                'as_leaf': 0,
                'children': list(cat_children[cat])
            }
    
    print(f"\n📊 Category Classification:")
    print(f"{'Type':<25} {'Count':<10} {'Products (as leaf)'}")
    print("─" * 80)
    print(f"{'TRUE LEAVES':<25} {len(true_leaves):>8,}  {sum(c['as_leaf'] for c in true_leaves.values()):>15,}")
    print(f"{'INTERMEDIATE':<25} {len(intermediate):>8,}  {sum(c['as_leaf'] for c in intermediate.values()):>15,}")
    print(f"{'PURE PARENTS':<25} {len(pure_parents):>8,}  {'N/A':>15}")
    print(f"{'─' * 80}")
    print(f"{'TOTAL':<25} {len(all_cats):>8,}")
    
    return {
        'true_leaves': true_leaves,
        'intermediate': intermediate,
        'pure_parents': pure_parents
    }


def analyze_depth_distribution(hierarchy_data):
    """Analyze distribution by category depth."""
    print("\n" + "=" * 80)
    print("DEPTH DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    product_cats = hierarchy_data['product_categories']
    
    depth_dist = Counter()
    depth_by_type = defaultdict(lambda: {'true': 0, 'intermediate': 0})
    
    leaf_occ = hierarchy_data['leaf_occurrences']
    parent_cats = hierarchy_data['parent_categories']
    
    for asin, categories in product_cats.items():
        depth = len(categories)
        depth_dist[depth] += 1
        
        # Check if leaf is true or intermediate
        leaf = categories[-1] if categories else None
        if leaf:
            if leaf not in parent_cats:
                depth_by_type[depth]['true'] += 1
            else:
                depth_by_type[depth]['intermediate'] += 1
    
    print(f"\n📊 Products by Hierarchy Depth:")
    print(f"{'Depth':<8} {'Total':<12} {'True Leaf':<12} {'Intermediate':<12} {'%'}")
    print("─" * 80)
    
    total_products = sum(depth_dist.values())
    for depth in sorted(depth_dist.keys()):
        count = depth_dist[depth]
        true_count = depth_by_type[depth]['true']
        inter_count = depth_by_type[depth]['intermediate']
        pct = 100 * count / total_products
        
        print(f"{depth:<8} {count:>10,}  {true_count:>10,}  {inter_count:>10,}  {pct:>5.2f}%")


def analyze_subtree_sizes(hierarchy_data, classifications):
    """Analyze size of subtrees for intermediate categories."""
    print("\n" + "=" * 80)
    print("SUBTREE SIZE ANALYSIS (Intermediate Categories)")
    print("=" * 80)
    
    intermediate = classifications['intermediate']
    leaf_occ = hierarchy_data['leaf_occurrences']
    cat_children = hierarchy_data['category_children']
    
    # Calculate total products in each subtree
    def get_subtree_size(category, visited=None):
        """Recursively calculate products in category and all descendants."""
        if visited is None:
            visited = set()
        
        if category in visited:
            return 0
        visited.add(category)
        
        # Products directly in this category (as leaf)
        direct = leaf_occ.get(category, 0)
        
        # Products in children
        children_total = 0
        for child in cat_children.get(category, []):
            children_total += get_subtree_size(child, visited)
        
        return direct + children_total
    
    subtree_data = []
    for cat, info in intermediate.items():
        direct_products = info['as_leaf']
        children = info['children']
        
        # Calculate products in children
        children_products = 0
        for child in children:
            children_products += get_subtree_size(child)
        
        total_subtree = direct_products + children_products
        
        subtree_data.append({
            'category': cat,
            'direct': direct_products,
            'via_children': children_products,
            'total_subtree': total_subtree,
            'num_children': len(children),
            'pct_direct': 100 * direct_products / total_subtree if total_subtree > 0 else 0
        })
    
    # Sort by total subtree size
    subtree_data.sort(key=lambda x: x['total_subtree'], reverse=True)
    
    print(f"\nTop 30 Intermediate Categories by Subtree Size:")
    print(f"{'Category':<40} {'Direct':<10} {'Children':<10} {'Total':<10} {'% Direct'}")
    print("─" * 100)
    
    for i, data in enumerate(subtree_data[:30], 1):
        print(f"{data['category']:<40} {data['direct']:>8,}  {data['via_children']:>8,}  "
              f"{data['total_subtree']:>8,}  {data['pct_direct']:>6.1f}%")
    
    return subtree_data


def create_complete_distribution(hierarchy_data, classifications, subtree_data):
    """Create complete distribution view."""
    print("\n" + "=" * 80)
    print("COMPLETE DISTRIBUTION VIEW")
    print("=" * 80)
    
    true_leaves = classifications['true_leaves']
    intermediate = classifications['intermediate']
    
    # Combine all
    all_leaf_data = []
    
    # True leaves
    for cat, info in true_leaves.items():
        all_leaf_data.append({
            'category': cat,
            'type': 'TRUE_LEAF',
            'direct_products': info['as_leaf'],
            'subtree_products': info['as_leaf'],
            'num_children': 0,
            'pct_direct': 100.0
        })
    
    # Intermediate leaves - find in subtree data
    subtree_dict = {s['category']: s for s in subtree_data}
    for cat, info in intermediate.items():
        subtree_info = subtree_dict.get(cat, {})
        all_leaf_data.append({
            'category': cat,
            'type': 'INTERMEDIATE',
            'direct_products': info['as_leaf'],
            'subtree_products': subtree_info.get('total_subtree', info['as_leaf']),
            'num_children': len(info['children']),
            'pct_direct': subtree_info.get('pct_direct', 100.0)
        })
    
    # Sort by subtree size
    all_leaf_data.sort(key=lambda x: x['subtree_products'], reverse=True)
    
    print(f"\nTop 50 Categories (All Types, by Total Products):")
    print(f"{'Rank':<6} {'Category':<40} {'Type':<15} {'Direct':<10} {'Subtree':<10}")
    print("─" * 100)
    
    for i, data in enumerate(all_leaf_data[:50], 1):
        print(f"{i:<6} {data['category']:<40} {data['type']:<15} "
              f"{data['direct_products']:>8,}  {data['subtree_products']:>8,}")
    
    return all_leaf_data


def create_summary_stats(hierarchy_data, classifications, all_leaf_data):
    """Create comprehensive summary statistics."""
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    total_products = len(hierarchy_data['product_categories'])
    total_categories = len(hierarchy_data['all_categories'])
    
    true_leaves = classifications['true_leaves']
    intermediate = classifications['intermediate']
    pure_parents = classifications['pure_parents']
    
    true_leaf_products = sum(c['as_leaf'] for c in true_leaves.values())
    inter_leaf_products = sum(c['as_leaf'] for c in intermediate.values())
    
    print(f"\n{'Metric':<50} {'Value':<15} {'%'}")
    print("─" * 80)
    print(f"{'Total Products':<50} {total_products:>13,}  {'100.00%':>6}")
    print(f"{'Total Categories':<50} {total_categories:>13,}")
    print(f"{'─' * 80}")
    print(f"{'TRUE LEAF Categories':<50} {len(true_leaves):>13,}  {100*len(true_leaves)/total_categories:>5.2f}%")
    print(f"{'  Products with true leaf':<50} {true_leaf_products:>13,}  {100*true_leaf_products/total_products:>5.2f}%")
    print(f"{'─' * 80}")
    print(f"{'INTERMEDIATE Categories':<50} {len(intermediate):>13,}  {100*len(intermediate)/total_categories:>5.2f}%")
    print(f"{'  Products with intermediate leaf':<50} {inter_leaf_products:>13,}  {100*inter_leaf_products/total_products:>5.2f}%")
    print(f"{'─' * 80}")
    print(f"{'PURE PARENT Categories':<50} {len(pure_parents):>13,}  {100*len(pure_parents)/total_categories:>5.2f}%")
    print(f"{'  (Never appear as leaf)':<50} {'N/A':>13}")
    
    # Depth stats
    depths = [len(cats) for cats in hierarchy_data['product_categories'].values()]
    avg_depth = sum(depths) / len(depths) if depths else 0
    
    print(f"\n{'Hierarchy Depth Statistics:':<50}")
    print(f"{'  Minimum depth':<50} {min(depths):>13}")
    print(f"{'  Maximum depth':<50} {max(depths):>13}")
    print(f"{'  Average depth':<50} {avg_depth:>13.2f}")
    print(f"{'  Most common depth':<50} {Counter(depths).most_common(1)[0][0]:>13}")


def export_complete_distribution(all_leaf_data, subtree_data, hierarchy_data, classifications):
    """Export complete distribution data."""
    print("\n" + "=" * 80)
    print("EXPORTING COMPLETE DISTRIBUTION")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export complete leaf distribution
    df = pd.DataFrame(all_leaf_data)
    file1 = f"{base_path}/complete_leaf_distribution.csv"
    df.to_csv(file1, index=False)
    print(f"\n✅ Exported complete leaf distribution to:")
    print(f"   {file1}")
    
    # Export subtree analysis
    df2 = pd.DataFrame(subtree_data)
    file2 = f"{base_path}/intermediate_subtree_analysis.csv"
    df2.to_csv(file2, index=False)
    print(f"\n✅ Exported intermediate subtree analysis to:")
    print(f"   {file2}")
    
    # Export category hierarchy (parent-child relationships)
    cat_children = hierarchy_data['category_children']
    hierarchy_rows = []
    for parent, children in cat_children.items():
        for child in children:
            hierarchy_rows.append({
                'parent': parent,
                'child': child,
                'parent_type': 'INTERMEDIATE' if parent in classifications['intermediate'] else 'PURE_PARENT',
                'child_type': ('TRUE_LEAF' if child in classifications['true_leaves'] 
                              else 'INTERMEDIATE' if child in classifications['intermediate']
                              else 'PURE_PARENT')
            })
    
    df3 = pd.DataFrame(hierarchy_rows)
    file3 = f"{base_path}/complete_category_hierarchy.csv"
    df3.to_csv(file3, index=False)
    print(f"\n✅ Exported complete category hierarchy to:")
    print(f"   {file3}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("COMPLETE HIERARCHICAL DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nThis analysis considers:")
    print(f"  • TRUE LEAVES: Never parents (834 categories)")
    print(f"  • INTERMEDIATE: Both leaf AND parent (178 categories)")
    print(f"  • PURE PARENTS: Never leaves (71 categories)")
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Build complete hierarchy
        hierarchy_data = analyze_complete_hierarchy(conn)
        
        # Classify categories
        classifications = classify_categories(hierarchy_data)
        
        # Analyze depth distribution
        analyze_depth_distribution(hierarchy_data)
        
        # Analyze subtree sizes
        subtree_data = analyze_subtree_sizes(hierarchy_data, classifications)
        
        # Create complete distribution
        all_leaf_data = create_complete_distribution(hierarchy_data, classifications, subtree_data)
        
        # Summary stats
        create_summary_stats(hierarchy_data, classifications, all_leaf_data)
        
        # Export
        export_complete_distribution(all_leaf_data, subtree_data, hierarchy_data, classifications)
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"\nFiles created:")
        print(f"  • complete_leaf_distribution.csv (1,012 leaf categories)")
        print(f"  • intermediate_subtree_analysis.csv (178 intermediate)")
        print(f"  • complete_category_hierarchy.csv (parent-child relationships)")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

