import json
import gzip

print("=" * 100)
print("CHECKING 'bought_together' FIELD IN JSONL FILES")
print("=" * 100)

# Check meta_Electronics.jsonl.gz
print("\n📦 Analyzing: meta_Electronics.jsonl.gz")
print("-" * 100)

total_count = 0
has_bought_together = 0
non_null_bought_together = 0
sample_with_data = []

try:
    with gzip.open('meta_Electronics.jsonl.gz', 'rt', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    record = json.loads(line)
                    total_count += 1
                    
                    # Check if field exists
                    if 'bought_together' in record:
                        has_bought_together += 1
                        
                        # Check if it's not null/None
                        if record['bought_together'] is not None:
                            non_null_bought_together += 1
                            
                            # Collect first 5 samples with data
                            if len(sample_with_data) < 5:
                                sample_with_data.append({
                                    'parent_asin': record.get('parent_asin', 'Unknown'),
                                    'title': record.get('title', 'Unknown')[:80],
                                    'bought_together': record['bought_together']
                                })
                    
                    # Progress indicator
                    if line_num % 100000 == 0:
                        print(f"Processed {line_num:,} records... (Found {non_null_bought_together} with data)")
                
                except json.JSONDecodeError:
                    continue
    
    print(f"\n{'='*100}")
    print("RESULTS")
    print(f"{'='*100}")
    print(f"📊 Total records: {total_count:,}")
    print(f"📊 Records with 'bought_together' field: {has_bought_together:,} ({has_bought_together/total_count*100:.2f}%)")
    print(f"📊 Records with NON-NULL 'bought_together': {non_null_bought_together:,} ({non_null_bought_together/total_count*100:.2f}%)")
    
    if non_null_bought_together > 0:
        print(f"\n✅ GOOD NEWS: {non_null_bought_together:,} products have 'bought_together' data!")
        print(f"\n{'='*100}")
        print("SAMPLE RECORDS WITH 'bought_together' DATA")
        print(f"{'='*100}")
        
        for idx, sample in enumerate(sample_with_data, 1):
            print(f"\n[{idx}] Product: {sample['parent_asin']}")
            print(f"    Title: {sample['title']}")
            print(f"    Bought Together: {sample['bought_together']}")
    else:
        print(f"\n❌ NO DATA: All 'bought_together' fields are null/empty!")
    
except FileNotFoundError:
    print("❌ File 'meta_Electronics.jsonl.gz' not found!")
    print("Trying uncompressed version...")
    
    # Try uncompressed version
    try:
        with open('meta_Electronics.jsonl', 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        record = json.loads(line)
                        total_count += 1
                        
                        # Check if field exists
                        if 'bought_together' in record:
                            has_bought_together += 1
                            
                            # Check if it's not null/None
                            if record['bought_together'] is not None:
                                non_null_bought_together += 1
                                
                                # Collect first 5 samples with data
                                if len(sample_with_data) < 5:
                                    sample_with_data.append({
                                        'parent_asin': record.get('parent_asin', 'Unknown'),
                                        'title': record.get('title', 'Unknown')[:80],
                                        'bought_together': record['bought_together']
                                    })
                        
                        # Progress indicator
                        if line_num % 100000 == 0:
                            print(f"Processed {line_num:,} records... (Found {non_null_bought_together} with data)")
                    
                    except json.JSONDecodeError:
                        continue
        
        print(f"\n{'='*100}")
        print("RESULTS")
        print(f"{'='*100}")
        print(f"📊 Total records: {total_count:,}")
        print(f"📊 Records with 'bought_together' field: {has_bought_together:,} ({has_bought_together/total_count*100:.2f}%)")
        print(f"📊 Records with NON-NULL 'bought_together': {non_null_bought_together:,} ({non_null_bought_together/total_count*100:.2f}%)")
        
        if non_null_bought_together > 0:
            print(f"\n✅ GOOD NEWS: {non_null_bought_together:,} products have 'bought_together' data!")
            print(f"\n{'='*100}")
            print("SAMPLE RECORDS WITH 'bought_together' DATA")
            print(f"{'='*100}")
            
            for idx, sample in enumerate(sample_with_data, 1):
                print(f"\n[{idx}] Product: {sample['parent_asin']}")
                print(f"    Title: {sample['title']}")
                print(f"    Bought Together: {sample['bought_together']}")
        else:
            print(f"\n❌ NO DATA: All 'bought_together' fields are null/empty!")
    
    except FileNotFoundError:
        print("❌ File 'meta_Electronics.jsonl' not found either!")

print(f"\n{'='*100}")
print("✅ Analysis complete!")
print(f"{'='*100}")

