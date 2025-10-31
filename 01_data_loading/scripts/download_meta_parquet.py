#!/usr/bin/env python3
"""
Download Amazon Electronics Metadata from Hugging Face
Source: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_Electronics
"""

import os
import requests
from tqdm import tqdm
import time

# Base URL for the parquet files
BASE_URL = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw_meta_Electronics/"

# List of all 10 parquet files (from the Hugging Face page)
PARQUET_FILES = [
    "full-00000-of-00010.parquet",  # 220 MB
    "full-00001-of-00010.parquet",  # 214 MB
    "full-00002-of-00010.parquet",  # 210 MB
    "full-00003-of-00010.parquet",  # 207 MB
    "full-00004-of-00010.parquet",  # 202 MB
    "full-00005-of-00010.parquet",  # 193 MB
    "full-00006-of-00010.parquet",  # 192 MB
    "full-00007-of-00010.parquet",  # 183 MB
    "full-00008-of-00010.parquet",  # 170 MB
    "full-00009-of-00010.parquet",  # 164 MB
]

# Output directory
OUTPUT_DIR = "raw_meta_Electronics"

def download_file(url, output_path):
    """
    Download a file with progress bar
    """
    try:
        # Stream the download
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download with progress bar
        with open(output_path, 'wb') as f, tqdm(
            desc=os.path.basename(output_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error downloading {output_path}: {e}")
        return False

def main():
    """
    Main download function
    """
    print("=" * 80)
    print("Amazon Electronics Metadata Downloader")
    print("Source: McAuley-Lab/Amazon-Reviews-2023")
    print("=" * 80)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\n📁 Output directory: {OUTPUT_DIR}/")
    
    # Calculate total size
    total_size_mb = 220 + 214 + 210 + 207 + 202 + 193 + 192 + 183 + 170 + 164
    print(f"📊 Total size: ~{total_size_mb} MB (~{total_size_mb/1024:.2f} GB)")
    print(f"📦 Files to download: {len(PARQUET_FILES)}")
    
    # Download each file
    print("\n" + "=" * 80)
    print("Starting downloads...")
    print("=" * 80 + "\n")
    
    successful = 0
    failed = 0
    
    for i, filename in enumerate(PARQUET_FILES, 1):
        url = BASE_URL + filename
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Check if file already exists
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ [{i}/{len(PARQUET_FILES)}] {filename} already exists ({file_size/1024/1024:.1f} MB)")
            successful += 1
            continue
        
        print(f"\n⬇️  [{i}/{len(PARQUET_FILES)}] Downloading {filename}...")
        
        # Download the file
        if download_file(url, output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ Downloaded successfully ({file_size/1024/1024:.1f} MB)")
            successful += 1
        else:
            failed += 1
        
        # Small delay between downloads to be respectful
        if i < len(PARQUET_FILES):
            time.sleep(1)
    
    # Summary
    print("\n" + "=" * 80)
    print("Download Summary")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{len(PARQUET_FILES)}")
    print(f"❌ Failed: {failed}/{len(PARQUET_FILES)}")
    
    if successful == len(PARQUET_FILES):
        print("\n🎉 All files downloaded successfully!")
        print(f"\n📁 Files location: {os.path.abspath(OUTPUT_DIR)}/")
        
        # Show how to read the files
        print("\n" + "=" * 80)
        print("How to read the parquet files:")
        print("=" * 80)
        print("""
import pandas as pd
import pyarrow.parquet as pq

# Read a single file
df = pd.read_parquet('raw_meta_Electronics/full-00000-of-00010.parquet')

# Or read all files at once
import glob
all_files = glob.glob('raw_meta_Electronics/*.parquet')
df_list = [pd.read_parquet(f) for f in all_files]
full_df = pd.concat(df_list, ignore_index=True)

print(f"Total products: {len(full_df)}")
print(full_df.head())
        """)
    else:
        print("\n⚠️  Some files failed to download. Please retry.")

if __name__ == "__main__":
    main()

