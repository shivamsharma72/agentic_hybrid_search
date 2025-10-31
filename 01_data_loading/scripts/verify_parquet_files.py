#!/usr/bin/env python3
"""
Verify Parquet Files - Quick check of all parquet files
"""

import pyarrow.parquet as pq
import os
from pathlib import Path
import sys

def main():
    print("=" * 70)
    print("   PARQUET FILES VERIFICATION")
    print("=" * 70)
    
    base_dir = Path(__file__).parent.parent
    
    # Product parquet files
    product_dir = base_dir / "data/processed/raw_meta_Electronics"
    print(f"\n📦 PRODUCT PARQUET FILES")
    print(f"   Location: {product_dir}")
    
    if product_dir.exists():
        product_files = sorted(product_dir.glob("*.parquet"))
        if product_files:
            total_products = 0
            total_size = 0
            
            for file in product_files:
                try:
                    table = pq.read_table(file)
                    num_rows = len(table)
                    total_products += num_rows
                    size_mb = file.stat().st_size / (1024 * 1024)
                    total_size += size_mb
                    print(f"   ✅ {file.name}: {num_rows:,} rows, {size_mb:.2f} MB")
                except Exception as e:
                    print(f"   ❌ {file.name}: ERROR - {e}")
            
            print(f"\n   Total: {len(product_files)} files, {total_products:,} products, {total_size:.2f} MB")
            
            # Check expected count
            expected_products = 348_228
            if total_products == expected_products:
                print(f"   ✅ Product count matches expected: {expected_products:,}")
            else:
                diff = abs(total_products - expected_products)
                print(f"   ⚠️  Product count mismatch: expected {expected_products:,}, got {total_products:,} (diff: {diff:,})")
        else:
            print("   ❌ No parquet files found")
    else:
        print(f"   ❌ Directory not found: {product_dir}")
    
    # Review parquet files
    review_dir = base_dir / "data/processed/reviews_Electronics"
    print(f"\n📝 REVIEW PARQUET FILES")
    print(f"   Location: {review_dir}")
    
    if review_dir.exists():
        review_files = sorted(review_dir.glob("*.parquet"))
        if review_files:
            total_reviews = 0
            total_size = 0
            
            for file in review_files:
                try:
                    table = pq.read_table(file)
                    num_rows = len(table)
                    total_reviews += num_rows
                    size_mb = file.stat().st_size / (1024 * 1024)
                    total_size += size_mb
                    print(f"   ✅ {file.name}: {num_rows:,} rows, {size_mb:.2f} MB")
                except Exception as e:
                    print(f"   ❌ {file.name}: ERROR - {e}")
            
            print(f"\n   Total: {len(review_files)} files, {total_reviews:,} reviews, {total_size:.2f} GB")
            
            # Check expected count
            expected_reviews = 37_512_193
            expected_files = 10
            
            if len(review_files) == expected_files:
                print(f"   ✅ File count matches expected: {expected_files}")
            else:
                print(f"   ⚠️  File count mismatch: expected {expected_files}, got {len(review_files)}")
            
            if total_reviews == expected_reviews:
                print(f"   ✅ Review count matches expected: {expected_reviews:,}")
            else:
                diff = abs(total_reviews - expected_reviews)
                print(f"   ⚠️  Review count mismatch: expected {expected_reviews:,}, got {total_reviews:,} (diff: {diff:,})")
        else:
            print("   ❌ No parquet files found")
    else:
        print(f"   ❌ Directory not found: {review_dir}")
    
    # Whitelist files
    print(f"\n🗂️  WHITELIST FILES")
    logs_dir = base_dir / "logs"
    
    electronics_pkl = logs_dir / "electronics_products_whitelist.pkl"
    fivecore_pkl = logs_dir / "unique_asins_whitelist.pkl"
    
    if electronics_pkl.exists():
        import pickle
        with open(electronics_pkl, 'rb') as f:
            electronics_asins = pickle.load(f)
        size_kb = electronics_pkl.stat().st_size / 1024
        print(f"   ✅ electronics_products_whitelist.pkl: {len(electronics_asins):,} ASINs, {size_kb:.2f} KB")
        
        expected_whitelist = 348_228
        if len(electronics_asins) == expected_whitelist:
            print(f"      ✅ Matches expected: {expected_whitelist:,}")
        else:
            print(f"      ⚠️  Expected {expected_whitelist:,}, got {len(electronics_asins):,}")
    else:
        print(f"   ❌ electronics_products_whitelist.pkl not found")
    
    if fivecore_pkl.exists():
        import pickle
        with open(fivecore_pkl, 'rb') as f:
            fivecore_asins = pickle.load(f)
        size_kb = fivecore_pkl.stat().st_size / 1024
        print(f"   ✅ unique_asins_whitelist.pkl: {len(fivecore_asins):,} ASINs, {size_kb:.2f} KB")
    else:
        print(f"   ❌ unique_asins_whitelist.pkl not found")
    
    print("\n" + "=" * 70)
    print("   VERIFICATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()

