"""
Extract Unique Product ASINs from 5-Core CSV
==============================================
This script reads the Electronics_pureid_5core.csv file and extracts
all unique parent_asin values to create a whitelist for filtering
the product metadata from parquet files.

Input: Electronics_pureid_5core.csv (15M reviews)
Output: Set of unique parent_asin values
"""

import csv
import pickle
from datetime import datetime

print("=" * 100)
print("EXTRACTING UNIQUE PRODUCT ASINs FROM 5-CORE CSV")
print("=" * 100)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Path to CSV file
csv_file = '../data/raw/Electronics_pureid_5core.csv'

# Set to store unique parent_asin values
unique_asins = set()
total_reviews = 0

print("📂 Reading CSV file...")
print(f"   File: {csv_file}\n")

try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, 1):
            total_reviews += 1
            
            # Extract parent_asin
            parent_asin = row['parent_asin']
            unique_asins.add(parent_asin)
            
            # Progress indicator
            if row_num % 1000000 == 0:
                print(f"   Processed {row_num:,} reviews... (Unique products: {len(unique_asins):,})")
    
    print(f"\n✅ CSV processing complete!")
    
    # Results
    print(f"\n{'='*100}")
    print("RESULTS")
    print(f"{'='*100}")
    print(f"📊 Total reviews in 5-core:        {total_reviews:,}")
    print(f"📊 Unique products (parent_asin):  {len(unique_asins):,}")
    print(f"📊 Avg reviews per product:        {total_reviews/len(unique_asins):.1f}")
    
    # Save to pickle for fast loading
    output_file = '../logs/unique_asins_whitelist.pkl'
    with open(output_file, 'wb') as f:
        pickle.dump(unique_asins, f)
    
    print(f"\n💾 Whitelist saved to: {output_file}")
    print(f"   File size: {len(pickle.dumps(unique_asins)) / (1024*1024):.2f} MB")
    
    # Sample ASINs
    print(f"\n🔍 Sample ASINs (first 10):")
    for i, asin in enumerate(list(unique_asins)[:10], 1):
        print(f"   {i}. {asin}")
    
    print(f"\n{'='*100}")
    print(f"✅ Extraction complete!")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}")
    
    # Write summary to log file
    with open('../logs/extract_asins_summary.txt', 'w') as f:
        f.write(f"Unique ASIN Extraction Summary\n")
        f.write(f"==============================\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total reviews: {total_reviews:,}\n")
        f.write(f"Unique products: {len(unique_asins):,}\n")
        f.write(f"Avg reviews per product: {total_reviews/len(unique_asins):.1f}\n")
    
    print(f"\n📄 Summary saved to: logs/extract_asins_summary.txt")

except FileNotFoundError:
    print(f"❌ ERROR: File not found: {csv_file}")
    print(f"   Please ensure Electronics_pureid_5core.csv is in the project root directory.")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

