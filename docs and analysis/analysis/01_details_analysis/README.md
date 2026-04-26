# Details Column Analysis 📋

## Overview

This folder contains comprehensive analysis scripts for the `details` JSONB column in the `products_backup` (laptop) table. The `details` column stores structured technical specifications as key-value pairs.

## Analysis Scripts

### 1. **analyze_details.py** - Overview Analysis
High-level analysis of the details column structure and content.

**What it analyzes:**
- Most common specification keys across all products
- Coverage statistics (how many products have each key)
- RAM distribution (basic)
- Storage distribution (basic)

**Output:**
- `visualizations/top_specification_keys.png` - Bar chart of top 15 keys
- `visualizations/ram_distribution.png` - RAM sizes
- `visualizations/storage_distribution.png` - Storage types/sizes
- `details_summary.json` - Detailed statistics

**Run:**
```bash
python3 analyze_details.py
```

---

### 2. **analyze_technical_specs.py** - Deep Technical Dive
In-depth parsing and analysis of all laptop technical specifications.

**What it analyzes:**
- **RAM**: Size (GB), Type (DDR3/DDR4/DDR5), Speed (MHz)
- **Storage**: Type (SSD/HDD), Capacity (GB/TB)
- **Processor**: Brand (Intel/AMD/Apple), Series (Core i5/i7, Ryzen), Speed (GHz), Cores
- **Display**: Size (inches), Resolution (1080p/4K), Refresh Rate (Hz)
- **Graphics**: Type (Integrated/Dedicated), Brand (NVIDIA/AMD), VRAM (GB)
- **Operating System**: Windows, macOS, Linux, Chrome OS
- **Price Segments**: Budget (<$500), Mid-Range, Premium, High-End, Ultra ($2K+)
- **Spec Combinations**: Most common RAM + Storage + CPU combos

**Output:**
- `visualizations/ram_deep_analysis.png` - RAM size distribution & avg price by RAM
- `visualizations/storage_deep_analysis.png` - SSD vs HDD, capacity vs price
- `visualizations/processor_deep_analysis.png` - CPU brand & series distribution
- `visualizations/display_deep_analysis.png` - Screen sizes & resolutions
- `visualizations/graphics_deep_analysis.png` - GPU type distribution
- `visualizations/os_distribution.png` - Operating system breakdown
- `visualizations/price_segments.png` - Product distribution by price tier
- `technical_specs_summary.json` - Comprehensive statistics

**Run:**
```bash
python3 analyze_technical_specs.py
```

---

### 3. **analyze_bestseller_rank.py** - Best Seller Rank Analysis
Focused analysis of the "Best Sellers Rank" field within the details column.

**What it analyzes:**
- Rank distribution (overall and category-specific)
- Performance tiers: Top 100, Top 1K, Top 10K, etc.
- **Correlation with Price**: Do cheaper laptops rank better?
- **Correlation with Rating**: Do higher-rated laptops rank better?
- **Correlation with Review Count**: More reviews = better rank?
- **Top Brands in Bestsellers**: Which brands dominate the top 1,000?

**Output:**
- `visualizations/bestseller_rank_distribution.png` - Rank distribution histograms
- `visualizations/rank_vs_price.png` - Scatter plot & box plot by rank tier
- `visualizations/rank_vs_rating.png` - Scatter plot & box plot by rank tier
- `visualizations/rank_vs_reviews.png` - Scatter plot (log-log scale)
- `visualizations/top_brands_bestsellers.png` - Top 15 brands in bestsellers
- `bestseller_rank_summary.json` - Rank statistics & correlations

**Run:**
```bash
python3 analyze_bestseller_rank.py
```

---

## Key Insights You'll Gain

### Technical Specifications
- **Most common laptop configurations** (e.g., 8GB RAM + 256GB SSD + Intel Core i5)
- **Market trends**: SSD adoption rate, DDR4 vs DDR5, integrated vs dedicated graphics
- **Price-to-specs relationship**: How much does doubling RAM increase price?
- **Display trends**: Most popular screen sizes and resolutions
- **OS market share**: Windows vs macOS vs Linux vs Chrome OS

### Best Seller Rank
- **What makes a bestseller?** Correlation analysis reveals:
  - Is it low price? (rank vs price correlation)
  - Is it high quality? (rank vs rating correlation)
  - Is it popularity? (rank vs review count correlation)
- **Performance tiers**: Characteristics of top 100 vs top 1K vs rest
- **Brand dominance**: Which brands consistently rank in top tiers?

### Data Quality
- **Specification completeness**: Which specs are most often missing?
- **Key coverage**: How many products have RAM data? Storage? CPU?
- **Standardization issues**: Variations in how same specs are recorded

---

## Running All Analyses

To run all three analyses sequentially:

```bash
# Run overview
python3 analyze_details.py

# Run technical specs (deep dive)
python3 analyze_technical_specs.py

# Run bestseller rank
python3 analyze_bestseller_rank.py
```

Or create a simple shell script:
```bash
#!/bin/bash
echo "Running all details analyses..."
python3 analyze_details.py
python3 analyze_technical_specs.py
python3 analyze_bestseller_rank.py
echo "✅ All analyses complete! Check visualizations/ folder"
```

---

## Database Connection

All scripts will prompt for PostgreSQL credentials:
- **Database**: `amazon_electronics_rag`
- **Table**: `products_backup` (contains 5,369 laptop products)
- **User**: Your PostgreSQL username
- **Password**: Your PostgreSQL password (or press Enter if none)

---

## Output Structure

```
01_details_analysis/
├── analyze_details.py              # Overview script
├── analyze_technical_specs.py      # Deep technical analysis
├── analyze_bestseller_rank.py      # Bestseller rank analysis
├── README.md                        # This file
├── visualizations/                  # All generated charts
│   ├── top_specification_keys.png
│   ├── ram_distribution.png
│   ├── storage_distribution.png
│   ├── ram_deep_analysis.png
│   ├── storage_deep_analysis.png
│   ├── processor_deep_analysis.png
│   ├── display_deep_analysis.png
│   ├── graphics_deep_analysis.png
│   ├── os_distribution.png
│   ├── price_segments.png
│   ├── bestseller_rank_distribution.png
│   ├── rank_vs_price.png
│   ├── rank_vs_rating.png
│   ├── rank_vs_reviews.png
│   └── top_brands_bestsellers.png
├── details_summary.json             # Overview statistics
├── technical_specs_summary.json     # Technical specs statistics
└── bestseller_rank_summary.json     # Rank statistics & correlations
```

---

## Sample Findings (Example)

Based on similar laptop datasets, you might expect:

**Technical Specs:**
- 📊 **RAM**: 8GB (45%), 16GB (30%), 4GB (15%), 32GB+ (10%)
- 💿 **Storage**: SSD dominance (75%), with 256GB and 512GB most common
- 🔧 **CPU**: Intel (65%), AMD (25%), Apple (10%)
- 📺 **Display**: 15.6" (40%), 13.3" (25%), 14" (20%)
- 🎮 **Graphics**: Integrated (70%), Dedicated NVIDIA (20%), Dedicated AMD (10%)

**Best Seller Rank:**
- 📈 **Correlation (Rank vs Price)**: Moderate negative (-0.3 to -0.5)
  - Lower prices → Better ranks
- ⭐ **Correlation (Rank vs Rating)**: Weak negative (-0.1 to -0.2)
  - Higher ratings → Slightly better ranks
- 💬 **Correlation (Rank vs Reviews)**: Strong negative (-0.6 to -0.8)
  - More reviews → Much better ranks (social proof!)

---

## Dependencies

```bash
pip install psycopg2-binary pandas matplotlib seaborn numpy
```

---

## Troubleshooting

**Issue**: `psycopg2.OperationalError: could not connect to server`
- **Fix**: Ensure PostgreSQL is running: `brew services start postgresql`

**Issue**: `relation "products_backup" does not exist`
- **Fix**: This analysis uses the `products_backup` table. If your table is named differently (e.g., `products_laptop`), update the SQL queries in each script.

**Issue**: Scripts run but produce empty charts
- **Fix**: The `details` column might be NULL for many products. Check: `SELECT COUNT(*) FROM products_backup WHERE details IS NOT NULL;`

---

## Next Steps

After running these analyses, you'll have:
1. ✅ **Deep understanding** of laptop specifications in your dataset
2. ✅ **Visualizations** for reports and presentations
3. ✅ **Data quality insights** for cleaning/enrichment decisions
4. ✅ **Market insights** for recommendation system tuning

Use these insights to:
- **Improve search/filter**: Add facets for common specs (RAM, storage, CPU brand)
- **Enhance recommendations**: Consider bestseller rank as a relevance signal
- **Identify gaps**: Find under-represented categories (e.g., high-end gaming laptops)
- **Validate RAG outputs**: Cross-check AI-generated descriptions against real specs

---

## Questions?

This analysis is part of the **Graph-Assisted Hybrid RAG for Amazon Laptop Recommendations** project.

For more details, see:
- `../README.md` - Overview of all analyses
- `../02_store_analysis/` - Brand and vendor analysis
- `../08_price_rating_analysis/` - Price vs rating correlation
- `../09_reviews_analysis/` - Review sentiment and content analysis

