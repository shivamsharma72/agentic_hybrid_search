# Store/Brand Analysis 🏪

## Overview

This folder contains comprehensive analysis of laptop brands/vendors in the Amazon dataset, revealing market concentration, pricing strategies, quality positioning, and competitive dynamics across 113 unique stores.

---

## Files in This Folder

### 📊 Analysis Script
- **`analyze_store.py`** - Main analysis script
  - Analyzes 113 unique brands across 5,455 products
  - Generates 7 visualizations
  - Exports detailed CSV with all brand statistics
  - Creates JSON summary file

### 📄 Reports & Data
- **`STORE_ANALYSIS_REPORT.md`** ⭐ - **Comprehensive 11-section analysis report**
  - Executive summary with key findings
  - Market concentration analysis (top 10 brands = 85% market share)
  - Price positioning strategies (Budget to Luxury tiers)
  - Quality rankings (Microsoft leads at 4.33⭐)
  - Popularity metrics (HP and ASUS lead with 191K reviews each)
  - Price-quality matrix and strategic positioning
  - Portfolio size analysis
  - Data quality issues identified
  - Market insights and recommendations

- **`store_distribution.csv`** - **Detailed brand statistics** (113 brands)
  - Columns: store, product_count, market_share_pct, avg_price, median_price, min_price, max_price, avg_rating, total_reviews, avg_reviews_per_product, price_tier, portfolio_size

- **`store_summary.json`** - Aggregated statistics and key metrics

### 📈 Visualizations (7 charts)
All saved in `visualizations/` folder:
1. **top_stores_by_count.png** - Top 20 brands by product count
2. **market_concentration.png** - Cumulative market share curve
3. **brand_price_positioning.png** - Average price by brand (color-coded by tier)
4. **brand_quality_ratings.png** - Average rating by brand
5. **brand_popularity_reviews.png** - Total reviews by brand
6. **price_quality_matrix.png** - Scatter plot: price vs quality vs popularity
7. **portfolio_distribution.png** - Brand distribution by portfolio size

---

## Key Findings

### 🏆 Market Leaders (Top 5)
1. **ASUS** - 848 products (15.55%) - Widest range
2. **HP** - 763 products (13.99%) - Mass market leader
3. **Amazon Renewed** - 743 products (13.62%) - Refurbished giant
4. **Lenovo** - 699 products (12.81%) - Business to consumer
5. **Dell** - 544 products (9.97%) - Full spectrum

### 💰 Price Positioning
- **Luxury ($1.5K+)**: Razer ($1,849), Gigabyte ($1,586), Alienware ($1,567)
- **Premium ($1K-$1.5K)**: MSI, Apple, LG
- **Upper-Mid ($700-$1K)**: Microsoft, ASUS
- **Mid-Range ($400-$700)**: Dell, Lenovo, HP, Acer
- **Budget (<$400)**: Amazon Renewed ($300), SAMSUNG, HEWLETT PACKARD

### ⭐ Quality Champions
1. **Microsoft** - 4.33⭐ (Premium positioning justified)
2. **LG** - 4.15⭐ (High-quality alternative)
3. **Amazon Renewed** - 3.93⭐ (Best value)
4. **HP** - 3.91⭐ (Reliable mid-range)
5. **MSI** - 3.85⭐ (Gaming quality)

### 💬 Popularity Leaders (Total Reviews)
1. **HP** - 191,403 reviews (250.9 avg/product)
2. **ASUS** - 191,311 reviews (225.6 avg/product)
3. **Amazon Renewed** - 156,922 reviews (211.2 avg/product)
4. **Lenovo** - 143,068 reviews (204.7 avg/product)
5. **Acer** - 111,326 reviews (465.8 avg/product) 🔥 Highest engagement!

### 📊 Market Concentration
- **Top 10 brands** → 85.52% of products
- **Top 20 brands** → 95.00% of products
- **Top 50 brands** → 98.61% of products

This is a **highly concentrated oligopoly** - major brands dominate!

---

## Running the Analysis

### Prerequisites
```bash
pip install psycopg2-binary pandas matplotlib seaborn numpy
```

### Execution
```bash
cd /path/to/analysis/02_store_analysis
python3 analyze_store.py
```

The script will:
1. Prompt for PostgreSQL credentials
2. Connect to `products_backup` table
3. Analyze all 113 brands
4. Generate 7 visualizations
5. Export `store_distribution.csv` with detailed statistics
6. Create `store_summary.json`

**Runtime**: ~30-60 seconds

---

## Output Structure

```
02_store_analysis/
├── analyze_store.py                    # Analysis script
├── STORE_ANALYSIS_REPORT.md            # Comprehensive report ⭐
├── README.md                           # This file
├── store_distribution.csv              # All brand statistics ⭐
├── store_summary.json                  # Aggregated metrics
└── visualizations/
    ├── top_stores_by_count.png
    ├── market_concentration.png
    ├── brand_price_positioning.png
    ├── brand_quality_ratings.png
    ├── brand_popularity_reviews.png
    ├── price_quality_matrix.png
    └── portfolio_distribution.png
```

---

## Using the CSV Data

### Example: Find Budget Brands with Good Quality

```python
import pandas as pd

df = pd.read_csv('store_distribution.csv')

# Budget brands (avg price < $400) with rating > 3.8
budget_quality = df[(df['avg_price'] < 400) & (df['avg_rating'] > 3.8)]
print(budget_quality[['store', 'avg_price', 'avg_rating', 'product_count']])
```

**Output**:
```
              store  avg_price  avg_rating  product_count
Amazon Renewed      300.09        3.93            743
```

### Example: Find Most Popular Gaming Brands

```python
# Gaming brands (avg price > $1000) sorted by total reviews
gaming = df[df['avg_price'] > 1000].sort_values('total_reviews', ascending=False)
print(gaming[['store', 'avg_price', 'total_reviews']].head())
```

---

## Insights for Different Audiences

### 👨‍💼 For Business Analysts
- **Market concentration analysis**: Understand competitive dynamics
- **Price-quality positioning**: Identify strategic gaps
- **Portfolio strategies**: Compare specialist vs diversified approaches
- **Brand performance metrics**: Quality, popularity, pricing

### 🛒 For Consumers
- **Best value brands**: HP ($561, 3.91⭐), Amazon Renewed ($300, 3.93⭐)
- **Quality leaders**: Microsoft (4.33⭐), LG (4.15⭐)
- **Avoid**: Sony (3.38⭐), Gateway (3.50⭐)

### 🔬 For Data Scientists
- **Clean CSV data**: Ready for ML, clustering, segmentation
- **Feature engineering**: Use brand as categorical feature
- **Price prediction**: Brand is strong price predictor
- **Recommendation systems**: Brand affinity, quality-price trade-offs

### 📊 For Researchers
- **Market structure**: Oligopoly characteristics, concentration ratios
- **Brand equity**: Quality premium analysis (Microsoft, Apple)
- **Refurbished market**: Amazon Renewed as case study
- **Data quality**: Brand name inconsistencies for data cleaning research

---

## Data Quality Issues

### ⚠️ Issues Identified
1. **Case inconsistency**: "acer" vs "Acer" (359 vs 239 products)
2. **Case inconsistency**: "msi" vs "MSI" (94 vs 126 products)
3. **Duplicate brands**: HP vs HEWLETT PACKARD (763 vs 26 products)

### ✅ Potential Fixes
```python
# Normalize brand names
df['store_normalized'] = df['store'].str.title()

# After normalization:
# Acer: 598 products combined (moves from #6/#7 to #3!)
# MSI: 220 products combined (4.03% market share)
```

---

## Advanced Analysis Ideas

### 1. Time Series Analysis
If temporal data available:
- Brand market share evolution
- Price trends by brand
- Quality improvement/decline over time

### 2. Brand Clustering
```python
from sklearn.cluster import KMeans

features = df[['avg_price', 'avg_rating', 'product_count', 'total_reviews']]
kmeans = KMeans(n_clusters=5)
df['brand_cluster'] = kmeans.fit_predict(features)
# Identify brand archetypes
```

### 3. Competitive Analysis
- Brand substitution analysis
- Price elasticity by brand
- Quality sensitivity analysis

### 4. Portfolio Optimization
- Optimal product count per brand
- Diversification vs specialization trade-offs

---

## Integration with RAG System

### Use Cases

**1. Brand-aware Search**
```python
# Query: "Best HP laptop under $600"
# Filter: store='HP', price<600, sort by rating
```

**2. Brand Recommendations**
```python
# If user likes ASUS mid-range → Recommend similar brands:
# Lenovo, Dell (similar price-quality profile)
```

**3. Quality Guarantees**
```python
# Surface high-quality brands first:
# Priority: Microsoft (4.33) > LG (4.15) > Amazon Renewed (3.93)
```

**4. Price Guidance**
```python
# User asks: "Is $1,200 expensive for an HP laptop?"
# Answer: HP avg = $561, median = $475
# → Yes, $1,200 is above 75th percentile for HP
```

---

## Next Steps

After reviewing this analysis:

1. ✅ **Clean data**: Normalize brand names (acer→Acer, msi→MSI)
2. ✅ **Integrate findings**: Use in RAG system for brand-aware responses
3. ✅ **Expand analysis**: 
   - Cross-reference with categories (gaming brands in gaming category?)
   - Analyze brand-specific features (ASUS ROG, Dell XPS, etc.)
4. ✅ **Update regularly**: Track brand performance changes

---

## Questions Answered

✅ **Which brands dominate the market?**
- Top 5: ASUS (15.55%), HP (13.99%), Amazon Renewed (13.62%), Lenovo (12.81%), Dell (9.97%)

✅ **What's the best value brand?**
- **Amazon Renewed**: $300 avg, 3.93⭐, 211 reviews/product
- **HP**: $561 avg, 3.91⭐, 250 reviews/product

✅ **Which premium brands are worth it?**
- **Microsoft**: 4.33⭐ at $900 avg - Quality justified
- **LG**: 4.15⭐ at $1,162 avg - Premium quality

✅ **Which brands have quality issues?**
- Sony (3.38⭐), HEWLETT PACKARD (3.38⭐), Gateway (3.50⭐), Toshiba (3.53⭐)

✅ **Gaming laptop leaders?**
- Razer ($1,849), Alienware ($1,567), MSI ($1,360-$1,485)

✅ **Is the market concentrated?**
- **Yes**: Top 10 brands = 85.52% market share (oligopoly)

---

## Contact & Contributions

This analysis is part of the **Amazon Laptop RAG System** project.

For questions or suggestions:
- Open an issue in the project repository
- Review the comprehensive `STORE_ANALYSIS_REPORT.md` for detailed insights

---

**Last Updated**: November 4, 2025  
**Data Source**: PostgreSQL `products_backup` table (5,455 laptops, 113 brands)  
**Analysis Tool**: `analyze_store.py` v1.0

