#!/usr/bin/env python3
"""
Master Script to Run All Laptop Data Analyses
==============================================
This script orchestrates all 9 analysis modules in sequence.

Usage:
    python3 run_all_analyses.py [--skip-existing]
    
Options:
    --skip-existing: Skip analyses that already have output files
"""

import subprocess
import sys
import os
from datetime import datetime

ANALYSES = [
    {
        'id': '01',
        'name': 'Details Analysis',
        'folder': '01_details_analysis',
        'scripts': ['analyze_details.py', 'analyze_bestseller_rank.py'],
        'description': 'Analyze product specifications (JSONB details column)'
    },
    {
        'id': '02',
        'name': 'Store Analysis',
        'folder': '02_store_analysis',
        'scripts': ['analyze_stores.py'],
        'description': 'Analyze brands and sellers'
    },
    {
        'id': '03',
        'name': 'Categories Analysis',
        'folder': '03_categories_analysis',
        'scripts': ['analyze_categories.py'],
        'description': 'Analyze category hierarchy'
    },
    {
        'id': '04',
        'name': 'Main Category Analysis',
        'folder': '04_main_category_analysis',
        'scripts': ['analyze_main_category.py'],
        'description': 'Analyze top-level categories'
    },
    {
        'id': '05',
        'name': 'Description Analysis',
        'folder': '05_description_analysis',
        'scripts': ['analyze_descriptions.py'],
        'description': 'NLP analysis of product descriptions'
    },
    {
        'id': '06',
        'name': 'Features Analysis',
        'folder': '06_features_analysis',
        'scripts': ['analyze_features.py'],
        'description': 'Analyze product features'
    },
    {
        'id': '07',
        'name': 'Titles Analysis',
        'folder': '07_titles_analysis',
        'scripts': ['analyze_titles.py'],
        'description': 'Analyze product titles and naming'
    },
    {
        'id': '08',
        'name': 'Price & Rating Analysis',
        'folder': '08_price_rating_analysis',
        'scripts': ['analyze_price.py', 'analyze_ratings.py', 'analyze_price_rating_correlation.py'],
        'description': 'Analyze pricing and ratings correlation'
    },
    {
        'id': '09',
        'name': 'Reviews Analysis',
        'folder': '09_reviews_analysis',
        'scripts': ['analyze_review_content.py', 'analyze_review_sentiment.py', 'cross_analysis_with_products.py'],
        'description': 'Comprehensive review analysis and cross-validation'
    }
]

def print_banner():
    print("=" * 80)
    print("📊 LAPTOP DATA ANALYSIS - MASTER ORCHESTRATOR")
    print("=" * 80)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Analyses: {len(ANALYSES)}")
    print("\n")

def print_analysis_header(analysis):
    print("\n" + "=" * 80)
    print(f"[{analysis['id']}/09] {analysis['name']}")
    print("=" * 80)
    print(f"Description: {analysis['description']}")
    print(f"Folder: {analysis['folder']}")
    print(f"Scripts: {', '.join(analysis['scripts'])}")
    print()

def run_analysis(analysis, skip_existing=False):
    """Run all scripts for a given analysis"""
    folder = analysis['folder']
    
    # Check if folder exists
    if not os.path.exists(folder):
        print(f"⚠️  Folder not found: {folder}")
        print(f"   Creating folder...")
        os.makedirs(folder, exist_ok=True)
        os.makedirs(f"{folder}/visualizations", exist_ok=True)
        print(f"   ⏭️  Skipping (no scripts yet)")
        return False
    
    all_success = True
    for script in analysis['scripts']:
        script_path = os.path.join(folder, script)
        
        if not os.path.exists(script_path):
            print(f"⚠️  Script not found: {script}")
            print(f"   ⏭️  Skipping...")
            continue
        
        print(f"\n🔄 Running: {script}")
        print(f"   Working directory: {folder}/")
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, script],
                cwd=folder,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {script} completed successfully")
            else:
                print(f"❌ {script} failed with exit code {result.returncode}")
                all_success = False
                
        except Exception as e:
            print(f"❌ Error running {script}: {e}")
            all_success = False
    
    return all_success

def main():
    skip_existing = '--skip-existing' in sys.argv
    
    print_banner()
    
    results = {}
    start_time = datetime.now()
    
    for analysis in ANALYSES:
        print_analysis_header(analysis)
        
        try:
            success = run_analysis(analysis, skip_existing)
            results[analysis['id']] = {
                'name': analysis['name'],
                'success': success,
                'folder': analysis['folder']
            }
        except KeyboardInterrupt:
            print("\n\n⚠️  Analysis interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            results[analysis['id']] = {
                'name': analysis['name'],
                'success': False,
                'error': str(e)
            }
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    print("\n\n" + "=" * 80)
    print("📊 ANALYSIS COMPLETE - SUMMARY")
    print("=" * 80)
    print(f"\nTotal Time: {duration}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nResults:")
    
    successful = 0
    for analysis_id, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} [{analysis_id}] {result['name']}")
        if result['success']:
            successful += 1
    
    print(f"\nSuccess Rate: {successful}/{len(results)} analyses completed")
    print("=" * 80)

if __name__ == "__main__":
    main()

