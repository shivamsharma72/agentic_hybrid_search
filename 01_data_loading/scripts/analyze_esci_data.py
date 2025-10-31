"""
Analyze ESCI (E-commerce Search Classification Intelligence) Dataset
====================================================================
This script analyzes the ESCI benchmark data to understand:
- Query distribution
- Product categories
- Metadata characteristics
"""

import json
import csv
from collections import defaultdict, Counter
import pandas as pd

print("=" * 100)
print("ESCI DATASET ANALYSIS")
print("=" * 100)

# Paths
TEST_CSV = '../archive/processed_esci/test.csv'
METADATA_JSONL = '../archive/processed_esci/sampled_item_metadata_esci.jsonl'

# Step 1: Analyze test.csv (queries)
print("\n" + "=" * 100)
print("STEP 1: Analyzing Test Queries (test.csv)")
print("=" * 100)

try:
    df_test = pd.read_csv(TEST_CSV)
    
    print(f"\n📊 Query Statistics:")
    print(f"   Total queries: {len(df_test):,}")
    print(f"   Unique queries: {df_test['query'].nunique():,}")
    print(f"   Unique products: {df_test['item_id'].nunique():,}")
    print(f"   Avg query length: {df_test['query'].str.len().mean():.1f} characters")
    
    # Query length distribution
    query_lengths = df_test['query'].str.split().str.len()
    print(f"\n   Query word count distribution:")
    print(f"     Min: {query_lengths.min()} words")
    print(f"     Max: {query_lengths.max()} words")
    print(f"     Mean: {query_lengths.mean():.1f} words")
    print(f"     Median: {query_lengths.median():.1f} words")
    
    # Most common queries
    print(f"\n   Top 10 most frequent queries:")
    top_queries = df_test['query'].value_counts().head(10)
    for i, (query, count) in enumerate(top_queries.items(), 1):
        print(f"     {i:2d}. '{query}' ({count} times)")
    
    # Sample queries
    print(f"\n   Sample queries:")
    for i, query in enumerate(df_test['query'].sample(5).values, 1):
        print(f"     {i}. {query}")
    
except Exception as e:
    print(f"❌ Error reading test.csv: {e}")

# Step 2: Analyze metadata
print("\n" + "=" * 100)
print("STEP 2: Analyzing Product Metadata (sampled_item_metadata_esci.jsonl)")
print("=" * 100)

try:
    categories = Counter()
    metadata_lengths = []
    items_per_category = defaultdict(set)
    sample_items = []
    
    print("\n📂 Reading metadata file...")
    with open(METADATA_JSONL, 'r') as f:
        for i, line in enumerate(f, 1):
            if i % 100000 == 0:
                print(f"   Processed {i:,} lines...")
            
            try:
                data = json.loads(line)
                category = data.get('category', 'Unknown')
                item_id = data.get('item', '')
                metadata = data.get('metadata', '')
                
                categories[category] += 1
                items_per_category[category].add(item_id)
                metadata_lengths.append(len(metadata))
                
                if len(sample_items) < 5:
                    sample_items.append(data)
                    
            except json.JSONDecodeError:
                continue
    
    print(f"\n✅ Processed {i:,} metadata entries")
    
    print(f"\n📊 Metadata Statistics:")
    print(f"   Total metadata entries: {i:,}")
    print(f"   Unique categories: {len(categories)}")
    print(f"   Unique products: {sum(len(items) for items in items_per_category.values()):,}")
    
    print(f"\n   Metadata length distribution:")
    print(f"     Min: {min(metadata_lengths)} characters")
    print(f"     Max: {max(metadata_lengths)} characters")
    print(f"     Mean: {sum(metadata_lengths)/len(metadata_lengths):.1f} characters")
    print(f"     Median: {sorted(metadata_lengths)[len(metadata_lengths)//2]:.1f} characters")
    
    print(f"\n   Category Distribution:")
    print(f"   {'Category':<50} {'Entries':>10} {'Unique Items':>15}")
    print(f"   {'-'*50} {'-'*10} {'-'*15}")
    for category, count in categories.most_common():
        unique_items = len(items_per_category[category])
        print(f"   {category:<50} {count:>10,} {unique_items:>15,}")
    
    print(f"\n   Sample Metadata Entries:")
    for i, item in enumerate(sample_items, 1):
        print(f"\n   Sample {i}:")
        print(f"     Item ID: {item.get('item', 'N/A')}")
        print(f"     Category: {item.get('category', 'N/A')}")
        metadata_preview = item.get('metadata', '')[:200]
        print(f"     Metadata: {metadata_preview}...")
    
except Exception as e:
    print(f"❌ Error reading metadata: {e}")

# Step 3: Cross-reference analysis
print("\n" + "=" * 100)
print("STEP 3: Cross-Reference Analysis")
print("=" * 100)

try:
    # Check overlap between test queries and metadata
    test_items = set(df_test['item_id'].unique())
    metadata_items = set()
    
    with open(METADATA_JSONL, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                metadata_items.add(data.get('item', ''))
            except:
                continue
    
    overlap = test_items & metadata_items
    
    print(f"\n📊 Overlap Statistics:")
    print(f"   Products in test queries: {len(test_items):,}")
    print(f"   Products in metadata: {len(metadata_items):,}")
    print(f"   Overlap: {len(overlap):,} ({len(overlap)/len(test_items)*100:.1f}%)")
    print(f"   Missing from metadata: {len(test_items - metadata_items):,}")
    
except Exception as e:
    print(f"❌ Error in cross-reference: {e}")

# Step 4: Summary
print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)

print(f"""
ESCI Dataset Overview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Product search benchmark for evaluating retrieval systems

Test Set:
  • Queries: {len(df_test):,} search queries
  • Unique queries: {df_test['query'].nunique():,}
  • Products referenced: {len(test_items):,}
  • Avg query length: {df_test['query'].str.len().mean():.1f} characters

Metadata:
  • Total entries: {i:,}
  • Categories: {len(categories)}
  • Unique products: {len(metadata_items):,}
  • Avg metadata length: {sum(metadata_lengths)/len(metadata_lengths):.0f} characters

Coverage:
  • {len(overlap)/len(test_items)*100:.1f}% of test products have metadata

Use Case:
  • Benchmark for product search/retrieval systems
  • Evaluate dense retrieval (BLAIR, SimCSE) vs sparse (BM25)
  • Query-product relevance matching

Relevance to Your Project:
  • ✅ Can use BLAIR embeddings (same encoder)
  • ✅ Benchmark comparison for your RAG system
  • ✅ Product search component evaluation
  • ⚠️  Different task (search vs recommendation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("\n✅ Analysis complete!")

