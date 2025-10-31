#!/usr/bin/env python3
"""
True Leaf vs Intermediate Leaf Analysis

This script distinguishes between:
1. TRUE LEAVES: Final categories that are NOT parents to other categories
2. INTERMEDIATE LEAVES: Categories that are leaf for some products but parent for others

Example: "Laptops" is a leaf for 17 products, but parent for 5,428 products!

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


def analyze_category_hierarchy(conn):
    """Analyze which categories are true leaves vs intermediate nodes."""
    print("\n" + "=" * 80)
    print("ANALYZING CATEGORY HIERARCHY")
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
    
    # Track all categories and their positions
    all_categories = set()
    leaf_categories = Counter()  # Categories that appear as final node
    parent_categories = set()  # Categories that have children
    category_children = defaultdict(set)  # Map parent -> children
    
    for idx, row in df.iterrows():
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
        
        # Add all categories to set
        for cat in categories:
            if cat and cat.strip():
                all_categories.add(cat.strip())
        
        # Track leaf (last category)
        leaf = categories[-1].strip()
        leaf_categories[leaf] += 1
        
        # Track parent-child relationships
        for i in range(len(categories) - 1):
            parent = categories[i].strip()
            child = categories[i + 1].strip()
            parent_categories.add(parent)
            category_children[parent].add(child)
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Analysis complete!")
    
    return all_categories, leaf_categories, parent_categories, category_children


def classify_leaves(all_categories, leaf_categories, parent_categories):
    """Classify categories into true leaves vs intermediate nodes."""
    print("\n" + "=" * 80)
    print("CLASSIFYING LEAVES")
    print("=" * 80)
    
    # True leaves: appear as leaf but NEVER as parent
    true_leaves = {}
    for cat, count in leaf_categories.items():
        if cat not in parent_categories:
            true_leaves[cat] = count
    
    # Intermediate leaves: appear as BOTH leaf AND parent
    intermediate_leaves = {}
    for cat, count in leaf_categories.items():
        if cat in parent_categories:
            intermediate_leaves[cat] = count
    
    # Pure parents: NEVER appear as leaf (always have children)
    pure_parents = parent_categories - set(leaf_categories.keys())
    
    print(f"\n📊 Classification:")
    print(f"{'Category Type':<30} {'Count':<10} {'Products as Leaf'}")
    print("─" * 80)
    print(f"{'TRUE LEAVES':<30} {len(true_leaves):>8,}  {sum(true_leaves.values()):>15,}")
    print(f"{'INTERMEDIATE LEAVES':<30} {len(intermediate_leaves):>8,}  {sum(intermediate_leaves.values()):>15,}")
    print(f"{'PURE PARENTS':<30} {len(pure_parents):>8,}  {'N/A':>15}")
    print(f"{'─' * 80}")
    print(f"{'TOTAL CATEGORIES':<30} {len(all_categories):>8,}")
    
    return true_leaves, intermediate_leaves, pure_parents


def analyze_intermediate_leaves(intermediate_leaves, category_children, leaf_categories):
    """Deep dive into intermediate leaves."""
    print("\n" + "=" * 80)
    print("INTERMEDIATE LEAVES ANALYSIS")
    print("=" * 80)
    
    print(f"\nThese categories act as BOTH leaf AND parent!")
    print(f"Example: 'Laptops' is:")
    print(f"  • Leaf for 17 products (no subcategory)")
    print(f"  • Parent for 5,428 products (has Traditional Laptops, 2-in-1, etc.)")
    
    print(f"\n{'Category':<40} {'As Leaf':<12} {'# Children':<12} {'Children'}")
    print("─" * 100)
    
    # Sort by leaf count
    sorted_intermediate = sorted(intermediate_leaves.items(), key=lambda x: x[1], reverse=True)
    
    for i, (cat, leaf_count) in enumerate(sorted_intermediate[:30], 1):
        children = category_children.get(cat, set())
        num_children = len(children)
        
        # Show first 3 children
        children_str = ', '.join(list(children)[:3])
        if num_children > 3:
            children_str += f", ... ({num_children - 3} more)"
        
        print(f"{cat:<40} {leaf_count:>10,}  {num_children:>10}  {children_str}")


def show_laptop_example(category_children, leaf_categories):
    """Show detailed example with Laptops category."""
    print("\n" + "=" * 80)
    print("EXAMPLE: 'LAPTOPS' CATEGORY")
    print("=" * 80)
    
    laptops_as_leaf = leaf_categories.get('Laptops', 0)
    laptops_children = category_children.get('Laptops', set())
    
    # Count products under each child
    total_under_children = 0
    for child in laptops_children:
        total_under_children += leaf_categories.get(child, 0)
    
    print(f"\n'Laptops' Category Breakdown:")
    print(f"{'─' * 80}")
    print(f"Products with 'Laptops' as LEAF (no subcategory):  {laptops_as_leaf:>6,}")
    print(f"Children categories under 'Laptops':                {len(laptops_children):>6}")
    print(f"Products under children (have subcategory):          {total_under_children:>6,}")
    print(f"{'─' * 80}")
    print(f"Total products mentioning 'Laptops':                 {laptops_as_leaf + total_under_children:>6,}")
    
    print(f"\nChildren of 'Laptops':")
    for child in sorted(laptops_children):
        count = leaf_categories.get(child, 0)
        print(f"  • {child:<40} {count:>6,} products")


def calculate_true_distribution(true_leaves, intermediate_leaves):
    """Calculate what happens if we only use true leaves."""
    print("\n" + "=" * 80)
    print("IMPACT OF USING ONLY TRUE LEAVES")
    print("=" * 80)
    
    total_true_leaf = sum(true_leaves.values())
    total_intermediate_leaf = sum(intermediate_leaves.values())
    total_all_leaves = total_true_leaf + total_intermediate_leaf
    
    print(f"\n📊 Product Distribution:")
    print(f"{'Metric':<50} {'Count':<12} {'%'}")
    print("─" * 80)
    print(f"{'Products with TRUE leaf':<50} {total_true_leaf:>10,}  {100*total_true_leaf/total_all_leaves:>5.2f}%")
    print(f"{'Products with INTERMEDIATE leaf':<50} {total_intermediate_leaf:>10,}  {100*total_intermediate_leaf/total_all_leaves:>5.2f}%")
    print(f"{'─' * 80}")
    print(f"{'Total':<50} {total_all_leaves:>10,}  {'100.00%':>6}")
    
    print(f"\n⚠️  If we ONLY use TRUE leaves:")
    print(f"   We'd lose {total_intermediate_leaf:,} products ({100*total_intermediate_leaf/total_all_leaves:.2f}%)")
    print(f"   These products have generic categories without specific subcategories")


def recommend_solution():
    """Recommend how to handle this in practice."""
    print("\n" + "=" * 80)
    print("RECOMMENDED SOLUTION")
    print("=" * 80)
    
    solution = """
🎯 PROBLEM STATEMENT:
────────────────────
Some categories like "Laptops" are:
• Leaf for some products (17 products end at "Laptops")
• Parent for other products (5,428 products have "Traditional Laptops", "2 in 1", etc.)

This creates ambiguity: Should we treat "Laptops" as a leaf or parent?

🎯 SOLUTION 1: USE LAST CATEGORY AS LEAF (Current Approach) ✅
──────────────────────────────────────────────────────────────

Keep the current approach: Use the LAST category in path as leaf.

Why?
• Simple and consistent
• Each product has EXACTLY one leaf (1:1 mapping)
• No special cases or exceptions
• Works for all 330,697 products

Result:
• Product A: [..., "Laptops"] → Leaf = "Laptops" (generic)
• Product B: [..., "Laptops", "Traditional Laptops"] → Leaf = "Traditional Laptops" (specific)

Pros:
✅ Simple implementation
✅ One-to-one mapping
✅ No data loss
✅ Works for 100% of products

Cons:
⚠️  Some leaves are more specific than others
⚠️  "Laptops" (17 products) mixed with "Traditional Laptops" (4,862 products)

🎯 SOLUTION 2: ADD LEAF_DEPTH COLUMN
────────────────────────────────────

Track how deep the leaf is in the hierarchy.

ALTER TABLE products ADD COLUMN leaf_depth INT;
UPDATE products SET leaf_depth = array_length(categories, 1);

Usage:
• leaf_depth = 5 → Very specific (Traditional Laptops)
• leaf_depth = 4 → Less specific (Laptops)
• leaf_depth = 3 → Generic (Computers & Tablets)

Filtering:
SELECT * FROM products 
WHERE leaf_category = 'Laptops'
AND leaf_depth >= 5;  -- Only products with specific subcategory

Pros:
✅ Can filter by specificity
✅ Distinguish generic vs specific
✅ Flexible querying

🎯 SOLUTION 3: NORMALIZE TO TRUE LEAVES (ADVANCED)
──────────────────────────────────────────────────

For products with intermediate leaves, promote them to a more specific category.

Example:
  Product: "Electronics > Computers > Laptops" (no subcategory)
  Issue:   "Laptops" is too generic
  
  Solution: Infer subcategory from other fields
  • Check title: "Dell Inspiron Traditional Laptop" → Assign "Traditional Laptops"
  • Check features: "2-in-1 convertible" → Assign "2 in 1 Laptops"
  • Check specs: If uncertain → Create "Other Laptops" category

Pros:
✅ All leaves are specific
✅ Better for recommendations
✅ Cleaner graph structure

Cons:
⚠️  Requires ML/rules to infer categories
⚠️  Risk of misclassification
⚠️  More complex

🎯 SOLUTION 4: TWO-TIER LEAF SYSTEM (RECOMMENDED FOR YOUR PROJECT)
──────────────────────────────────────────────────────────────────

Use TWO leaf fields:
1. leaf_category: Actual last category (current)
2. leaf_group: Canonical grouping for recommendations

Example:
  Product A: [..., "Laptops"]
    • leaf_category = "Laptops"
    • leaf_group = "Laptops (Unspecified)"
  
  Product B: [..., "Laptops", "Traditional Laptops"]
    • leaf_category = "Traditional Laptops"
    • leaf_group = "Traditional Laptops"

Implementation:
ALTER TABLE products ADD COLUMN leaf_group VARCHAR(255);

UPDATE products SET leaf_group = 
  CASE 
    WHEN leaf_category = 'Laptops' AND leaf_depth = 4 
      THEN 'Laptops (Unspecified)'
    ELSE leaf_category
  END;

Usage:
• Graph: Use leaf_group for Neo4j nodes (cleaner)
• Recommendations: Group by leaf_group (17 + 4,862 = 4,879 total laptops)
• Analytics: Use leaf_category for raw data

Pros:
✅ Clean separation of concerns
✅ Best for recommendations
✅ No data loss
✅ Flexible for different use cases

🎯 RECOMMENDED APPROACH:
───────────────────────

Start with SOLUTION 1 (current approach) for simplicity.

If you need more granularity later:
• Add SOLUTION 2 (leaf_depth) for filtering
• Add SOLUTION 4 (leaf_group) for recommendations

For your RAG + Graph project:
1. Keep current leaf_category (last category)
2. Add leaf_depth for filtering
3. In Neo4j, create nodes for both specific and generic categories
4. Connect generic "Laptops" node to specific "Traditional Laptops" nodes

Graph Structure:
  (Product A) -[:BELONGS_TO]-> (Laptops:Generic)
  (Product B) -[:BELONGS_TO]-> (Traditional Laptops:Specific)
  (Traditional Laptops) -[:CHILD_OF]-> (Laptops)
  
  This preserves hierarchy while keeping 1:1 product-to-leaf mapping!

════════════════════════════════════════════════════════════════════════════════
SUMMARY:
════════════════════════════════════════════════════════════════════════════════

✅ Current approach (last category as leaf) is CORRECT and SIMPLE
✅ Some leaves are intermediate nodes (both leaf and parent) - this is NORMAL
✅ Can enhance with leaf_depth or leaf_group if needed
✅ For graph: Use hierarchy relationships to connect generic and specific categories

Don't overcomplicate! Start simple, enhance if needed. 🎯
"""
    
    print(solution)


def export_results(true_leaves, intermediate_leaves, pure_parents, category_children):
    """Export analysis results."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export true leaves
    true_df = pd.DataFrame([
        {'category': cat, 'type': 'true_leaf', 'product_count': count, 'num_children': 0}
        for cat, count in sorted(true_leaves.items(), key=lambda x: x[1], reverse=True)
    ])
    
    # Export intermediate leaves
    intermediate_df = pd.DataFrame([
        {'category': cat, 'type': 'intermediate_leaf', 'product_count': count, 
         'num_children': len(category_children.get(cat, set()))}
        for cat, count in sorted(intermediate_leaves.items(), key=lambda x: x[1], reverse=True)
    ])
    
    # Combine
    all_leaves_df = pd.concat([true_df, intermediate_df], ignore_index=True)
    
    file_path = f"{base_path}/leaf_classification_analysis.csv"
    all_leaves_df.to_csv(file_path, index=False)
    
    print(f"\n✅ Exported {len(all_leaves_df):,} leaves to:")
    print(f"   {file_path}")
    
    # Export category hierarchy
    hierarchy_df = pd.DataFrame([
        {'parent': parent, 'child': child, 'products_in_child': true_leaves.get(child, 0) + intermediate_leaves.get(child, 0)}
        for parent, children in category_children.items()
        for child in children
    ])
    
    hierarchy_file = f"{base_path}/category_hierarchy.csv"
    hierarchy_df.to_csv(hierarchy_file, index=False)
    
    print(f"\n✅ Exported {len(hierarchy_df):,} parent-child relationships to:")
    print(f"   {hierarchy_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("TRUE vs INTERMEDIATE LEAF ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Analyze hierarchy
        all_categories, leaf_categories, parent_categories, category_children = analyze_category_hierarchy(conn)
        
        # Classify leaves
        true_leaves, intermediate_leaves, pure_parents = classify_leaves(all_categories, leaf_categories, parent_categories)
        
        # Analyze intermediate leaves
        analyze_intermediate_leaves(intermediate_leaves, category_children, leaf_categories)
        
        # Show laptop example
        show_laptop_example(category_children, leaf_categories)
        
        # Calculate impact
        calculate_true_distribution(true_leaves, intermediate_leaves)
        
        # Recommend solution
        recommend_solution()
        
        # Export results
        export_results(true_leaves, intermediate_leaves, pure_parents, category_children)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Total categories: {len(all_categories):,}")
        print(f"True leaves: {len(true_leaves):,} ({sum(true_leaves.values()):,} products)")
        print(f"Intermediate leaves: {len(intermediate_leaves):,} ({sum(intermediate_leaves.values()):,} products)")
        print(f"Pure parents: {len(pure_parents):,}")
        print(f"\nFiles created:")
        print(f"  • leaf_classification_analysis.csv")
        print(f"  • category_hierarchy.csv")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

