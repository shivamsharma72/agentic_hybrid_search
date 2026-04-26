#!/usr/bin/env python3
"""
Leaf Node Distribution Analysis

This script analyzes leaf nodes (final category in each path) to:
1. Check if leaf nodes add up to total products with categories
2. Understand the distribution of products across leaf nodes
3. Explain why leaf nodes are important for graph construction

Author: AI Assistant
Date: October 31, 2025
"""

import psycopg2
import pandas as pd
import json
from collections import Counter
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


def analyze_leaf_nodes(conn):
    """Analyze leaf node distribution."""
    print("\n" + "=" * 80)
    print("LEAF NODE ANALYSIS")
    print("=" * 80)
    
    query = """
        SELECT 
            parent_asin,
            categories
        FROM products
        WHERE categories IS NOT NULL;
    """
    
    df = pd.read_sql_query(query, conn)
    
    print(f"\n🔍 Processing {len(df):,} products with categories...")
    
    leaf_counter = Counter()
    products_per_leaf = {}  # Store actual product ASINs for each leaf
    products_with_leaf = set()
    products_without_leaf = []
    
    for idx, row in df.iterrows():
        asin = row['parent_asin']
        categories = row['categories']
        
        if categories is None:
            products_without_leaf.append(asin)
            continue
        
        # Convert to list if needed
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = [categories]
        
        # Get leaf (last category)
        if isinstance(categories, list) and len(categories) > 0:
            leaf = categories[-1].strip()
            leaf_counter[leaf] += 1
            products_with_leaf.add(asin)
            
            # Store ASIN for this leaf
            if leaf not in products_per_leaf:
                products_per_leaf[leaf] = []
            products_per_leaf[leaf].append(asin)
        else:
            products_without_leaf.append(asin)
        
        # Progress
        if (idx + 1) % 50000 == 0:
            print(f"   Processed {idx + 1:,} / {len(df):,} products...")
    
    print(f"\n✅ Analysis complete!")
    
    return leaf_counter, products_per_leaf, products_with_leaf, products_without_leaf, len(df)


def verify_leaf_coverage(leaf_counter, products_with_leaf, products_without_leaf, total_with_cats):
    """Verify if leaf nodes add up to total products."""
    print("\n" + "=" * 80)
    print("LEAF NODE COVERAGE VERIFICATION")
    print("=" * 80)
    
    # Sum of all leaf node counts
    total_leaf_counts = sum(leaf_counter.values())
    
    # Number of unique products with leaf nodes
    unique_products_with_leaf = len(products_with_leaf)
    
    # Number of products without leaf
    num_without_leaf = len(products_without_leaf)
    
    print(f"\n📊 Coverage Check:")
    print(f"{'Metric':<50} {'Count':<12} {'%'}")
    print("─" * 80)
    print(f"{'Total products with categories':<50} {total_with_cats:>10,}  {'100.0%':>6}")
    print(f"{'─' * 80}")
    print(f"{'Products with leaf node':<50} {unique_products_with_leaf:>10,}  {100*unique_products_with_leaf/total_with_cats:>5.2f}%")
    print(f"{'Products without leaf node':<50} {num_without_leaf:>10,}  {100*num_without_leaf/total_with_cats:>5.2f}%")
    print(f"{'─' * 80}")
    print(f"{'Sum (with + without)':<50} {unique_products_with_leaf + num_without_leaf:>10,}  {100*(unique_products_with_leaf + num_without_leaf)/total_with_cats:>5.2f}%")
    
    # Verification
    sum_check = unique_products_with_leaf + num_without_leaf
    match = "✅" if sum_check == total_with_cats else "❌"
    
    print(f"\n🔢 Verification:")
    print(f"   Total products with categories: {total_with_cats:,}")
    print(f"   Products with leaf + without:   {sum_check:,}")
    print(f"   Match: {match} ({sum_check == total_with_cats})")
    
    # Leaf counts vs unique products
    print(f"\n📊 Leaf Node Math:")
    print(f"   Total leaf node counts:         {total_leaf_counts:,}")
    print(f"   Unique products with leaf:      {unique_products_with_leaf:,}")
    print(f"   Ratio:                          {total_leaf_counts / unique_products_with_leaf:.2f}:1")
    
    # Important insight
    if total_leaf_counts == unique_products_with_leaf:
        print(f"\n✅ IMPORTANT: Leaf counts = Unique products!")
        print(f"   This means: Each product has EXACTLY ONE leaf node! ✅")
        print(f"   Why? Leaf is the LAST/FINAL category in the path.")
    else:
        print(f"\n⚠️  Leaf counts ({total_leaf_counts:,}) ≠ Unique products ({unique_products_with_leaf:,})")
        print(f"   Difference: {abs(total_leaf_counts - unique_products_with_leaf):,}")


def analyze_leaf_distribution(leaf_counter, products_per_leaf):
    """Analyze distribution of products across leaf nodes."""
    print("\n" + "=" * 80)
    print("LEAF NODE DISTRIBUTION")
    print("=" * 80)
    
    total_products = sum(leaf_counter.values())
    
    print(f"\n📊 Statistics:")
    print(f"   Unique leaf nodes:      {len(leaf_counter):,}")
    print(f"   Total products:         {total_products:,}")
    print(f"   Avg products per leaf:  {total_products / len(leaf_counter):.2f}")
    print(f"   Max products in a leaf: {max(leaf_counter.values()):,} ({leaf_counter.most_common(1)[0][0]})")
    print(f"   Min products in a leaf: {min(leaf_counter.values()):,}")
    
    # Distribution buckets
    buckets = {
        'Large (10,000+)': 0,
        'Medium (1,000-9,999)': 0,
        'Small (100-999)': 0,
        'Tiny (10-99)': 0,
        'Single digit (1-9)': 0
    }
    
    for count in leaf_counter.values():
        if count >= 10000:
            buckets['Large (10,000+)'] += 1
        elif count >= 1000:
            buckets['Medium (1,000-9,999)'] += 1
        elif count >= 100:
            buckets['Small (100-999)'] += 1
        elif count >= 10:
            buckets['Tiny (10-99)'] += 1
        else:
            buckets['Single digit (1-9)'] += 1
    
    print(f"\n📊 Leaf Size Distribution:")
    print(f"{'Size Category':<30} {'Count':<10} {'%'}")
    print("─" * 80)
    
    for category, count in buckets.items():
        pct = 100 * count / len(leaf_counter)
        print(f"{category:<30} {count:>8}  {pct:>5.1f}%")


def display_top_leaf_nodes(leaf_counter, n=50):
    """Display top N leaf nodes."""
    print("\n" + "=" * 80)
    print(f"TOP {n} LEAF NODES (By Product Count)")
    print("=" * 80)
    
    print(f"\n{'Rank':<6} {'Count':<12} {'%':<8} {'Leaf Node'}")
    print("─" * 80)
    
    total = sum(leaf_counter.values())
    
    for i, (leaf, count) in enumerate(leaf_counter.most_common(n), 1):
        pct = 100 * count / total
        
        # Truncate long names
        display_leaf = leaf
        if len(display_leaf) > 60:
            display_leaf = display_leaf[:57] + "..."
        
        print(f"{i:<6} {count:>10,}  {pct:>6.2f}%  {display_leaf}")


def explain_leaf_importance():
    """Explain why leaf nodes are important."""
    print("\n" + "=" * 80)
    print("WHY LEAF NODES MATTER FOR YOUR PROJECT")
    print("=" * 80)
    
    explanation = """
🎯 REASON 1: ONE-TO-ONE MAPPING
──────────────────────────────
Each product has EXACTLY ONE leaf node (its final, most specific category).

Example:
  Product: Dell Laptop
  Categories: ["Electronics", "Computers", "Laptops", "Traditional Laptops"]
                ↓              ↓           ↓         ↓
              Parent        Parent       Parent    LEAF ✅
  
  This product contributes to:
  • 4 parent nodes (Electronics, Computers, Laptops)
  • 1 LEAF node (Traditional Laptops)
  
  ✅ Leaf = Most specific classification
  ✅ No overlap (product can't be in 2 leaf nodes)
  ✅ Clean, unique assignment

🎯 REASON 2: GRAPH CONSTRUCTION
────────────────────────────────
Leaf nodes are PERFECT for building your Neo4j graph!

Why?
• Clear node identity: Each product belongs to ONE leaf
• No ambiguity: Product → Leaf is 1:1 relationship
• Easy edges: Can connect products within same leaf
• Similarity: Products in same leaf are inherently similar

Example Graph Structure:
  (Product1) -[:BELONGS_TO]-> (Traditional Laptops) <-[:BELONGS_TO]- (Product2)
  (Product1) -[:SIMILAR_TO]-> (Product2)  [same leaf = similar]
  
  Leaf node becomes a HUB for connecting related products!

🎯 REASON 3: RECOMMENDATION LOGIC
──────────────────────────────────
Leaf nodes enable powerful recommendation patterns!

1. Same-Leaf Recommendations:
   User views "Traditional Laptops" → Show other "Traditional Laptops"
   
2. Cross-Leaf Recommendations:
   User views "Traditional Laptops" → Show "2 in 1 Laptops" (sibling leaf)
   
3. Parent-to-Children:
   User browses "Laptops" → Show all children (Traditional, 2-in-1, Gaming)
   
4. Hierarchical Filtering:
   Filter by parent + rank by leaf similarity

🎯 REASON 4: EXPLAINABILITY
───────────────────────────
Leaf nodes make recommendations EXPLAINABLE!

Example:
  "We recommend this laptop because:"
  ✅ "Both are Traditional Laptops" (same leaf)
  ✅ "Both have similar specs" (RAM, CPU in graph)
  ✅ "Other users who bought Traditional Laptops also liked this"
  
  VS just embeddings:
  ❌ "Similarity score: 0.87" (not explainable!)

🎯 REASON 5: GNN TRAINING
─────────────────────────
Graph Neural Networks benefit from leaf structure!

Message Passing:
  • Nodes (Products) aggregate info from neighbors
  • Leaf creates natural neighborhoods
  • Products in same leaf share information
  • Parent nodes aggregate from multiple leaves
  
  Traditional Laptops (Leaf)
         ↓
      [Laptop1, Laptop2, Laptop3] ← Same leaf, share features
         ↓
  GNN learns: "These products are similar"

🎯 REASON 6: FILTERING & INDEXING
──────────────────────────────────
Leaf nodes optimize database queries!

Current approach: Check entire category array
  WHERE 'laptop' IN ANY(categories)  → Scans 4-5 values per product
  
Leaf approach: Check single value
  WHERE leaf_category = 'Traditional Laptops'  → Scans 1 value per product
  
  ✅ Faster queries
  ✅ Simpler indexes
  ✅ Better cache utilization

🎯 REASON 7: BALANCED DISTRIBUTION
────────────────────────────────────
Leaf nodes show TRUE product distribution!

Parent nodes are OVERLAPPING:
  "Electronics" → 330K products
  "Computers" → 141K products
  Add them? 471K! But we only have 348K total!
  
Leaf nodes are NON-OVERLAPPING:
  "Traditional Laptops" → 4,862
  "2 in 1 Laptops" → 566
  "Cases" → 20,168
  Add them? Equals total products with categories! ✅

🎯 REASON 8: USER EXPERIENCE
────────────────────────────
Leaf nodes match how users think!

User search: "I want a traditional laptop"
  ✅ Matches leaf: "Traditional Laptops"
  ❌ Doesn't match parent: "Laptops" (too broad)
  ❌ Doesn't match path: "Electronics > Computers > ..." (too complex)
  
  Leaf = Natural language of product types!

════════════════════════════════════════════════════════════════════════════════
SUMMARY: Why You NEED Leaf Node Analysis
════════════════════════════════════════════════════════════════════════════════

✅ One-to-One: Each product has exactly one leaf (clean assignment)
✅ Graph: Perfect for Neo4j nodes and relationships
✅ Recommendations: Enables same-leaf and cross-leaf suggestions
✅ Explainable: Makes recommendations understandable
✅ GNN: Natural neighborhoods for message passing
✅ Performance: Faster queries and indexing
✅ Distribution: Shows true product spread (no overlap)
✅ UX: Matches user mental model

For your RAG + Graph + GNN project, leaf nodes are ESSENTIAL! 🎯
"""
    
    print(explanation)


def export_results(leaf_counter, products_per_leaf):
    """Export leaf node analysis."""
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)
    
    base_path = "/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project/03_analysis"
    
    # Export leaf distribution
    leaf_df = pd.DataFrame([
        {'leaf_node': leaf, 'product_count': count}
        for leaf, count in leaf_counter.most_common()
    ])
    leaf_file = f"{base_path}/leaf_node_distribution.csv"
    leaf_df.to_csv(leaf_file, index=False)
    print(f"\n✅ Exported {len(leaf_df):,} leaf nodes to:")
    print(f"   {leaf_file}")
    
    # Export summary stats
    summary = {
        'total_leaf_nodes': len(leaf_counter),
        'total_products': sum(leaf_counter.values()),
        'avg_products_per_leaf': sum(leaf_counter.values()) / len(leaf_counter),
        'max_products': max(leaf_counter.values()),
        'min_products': min(leaf_counter.values()),
        'top_leaf': leaf_counter.most_common(1)[0][0],
        'top_leaf_count': leaf_counter.most_common(1)[0][1]
    }
    
    summary_df = pd.DataFrame([summary])
    summary_file = f"{base_path}/leaf_node_summary.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"\n✅ Exported summary stats to:")
    print(f"   {summary_file}")


def main():
    """Main execution function."""
    start_time = datetime.now()
    
    print("\n" + "=" * 80)
    print("LEAF NODE DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Analyze leaf nodes
        leaf_counter, products_per_leaf, products_with_leaf, products_without_leaf, total_with_cats = analyze_leaf_nodes(conn)
        
        # Verify coverage
        verify_leaf_coverage(leaf_counter, products_with_leaf, products_without_leaf, total_with_cats)
        
        # Analyze distribution
        analyze_leaf_distribution(leaf_counter, products_per_leaf)
        
        # Display top leaf nodes
        display_top_leaf_nodes(leaf_counter, 50)
        
        # Explain importance
        explain_leaf_importance()
        
        # Export results
        export_results(leaf_counter, products_per_leaf)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Total products with categories: {total_with_cats:,}")
        print(f"Unique leaf nodes: {len(leaf_counter):,}")
        print(f"Products with leaf: {len(products_with_leaf):,}")
        print(f"Leaf coverage: {100*len(products_with_leaf)/total_with_cats:.2f}%")
        print(f"\nFiles created:")
        print(f"  • leaf_node_distribution.csv")
        print(f"  • leaf_node_summary.csv")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

