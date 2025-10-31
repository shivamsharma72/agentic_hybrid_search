# 📊 Amazon Electronics Products - Exploratory Data Analysis

This folder contains **comprehensive in-depth EDA** of the 348,228 Electronics products from the PostgreSQL database.

## What's Inside

- **products_eda.ipynb** - Complete EDA notebook with advanced analysis
- **requirements.txt** - Python dependencies
- **Exported files** (generated after running notebook):
  - `products_enhanced_sample.csv` - Top 10K products with new features
  - `category_analysis.csv` - Detailed per-category statistics
  - `top_brands.csv` - Brand analysis
  - `anomalies_and_insights.xlsx` - Outliers and special products
  - `eda_summary_report.txt` - Text summary of key findings

## Setup

```bash
cd eda
pip install -r requirements.txt
```

## Run the Analysis

```bash
jupyter notebook products_eda.ipynb
```

**Important:** After running Cell 2 (package installation), restart the kernel before running Cell 3!

## Analysis Includes

### 📈 Basic Analysis

1. **Dataset Overview** - Basic statistics and structure
2. **Missing Data Analysis** - Data completeness insights
3. **Categorical Analysis** - Categories, stores, and distributions
4. **Numerical Analysis** - Price and rating patterns
5. **Text Analysis** - Title, description, and features insights
6. **Cross-Feature Analysis** - Relationships between variables

### 🔬 Advanced Analysis (NEW!)

7. **Feature Engineering** - 15+ new derived features
   - Price segments, rating categories, review volume
   - Popularity score, price-per-rating (value metric)
   - Text length features, brand extraction
8. **Advanced Price Analysis** - Price segment trends
9. **Brand Analysis** - Top brands by count and rating
10. **TF-IDF Analysis** - Most important keywords across products
11. **Category Deep Dive** - Per-category detailed metrics
12. **Correlation Matrix** - Feature relationships
13. **Popularity & Value Analysis** - Best value products, popular items
14. **Anomaly Detection** - Outliers, suspicious patterns, viral products
15. **Embedding Analysis** - BLAIR-RoBERTa embedding statistics
16. **RAG System Recommendations** - Segment-based insights for the chatbot

## New Features Created

The notebook creates 15+ new features that can be used in your RAG system:

- `price_segment` - Budget, Low, Mid, Mid-High, High, Premium
- `rating_category` - Poor, Below Avg, Average, Good, Excellent
- `review_volume` - Very Low, Low, Medium, High, Very High
- `popularity_score` - Composite metric (60% reviews, 40% rating)
- `price_per_rating` - Value metric (lower is better)
- `potential_brand` - Extracted from title
- `title_length`, `description_length`, `features_count`
- `has_description`, `has_features`, `has_videos`, `has_images`
- `image_count`, `title_word_count`

## Key Insights for RAG System

✅ Use `popularity_score` for ranking recommendations  
✅ Filter by `price_segment` for budget-aware queries  
✅ Use `rating_category` for quality filtering  
✅ Leverage `potential_brand` for brand-specific queries  
✅ Cross-reference with review data for deeper insights

## Database Connection

The notebook connects to:

- **Database:** `amazon_electronics_rag`
- **Host:** `localhost`
- **Port:** `5432`
- **User:** `shivamsharma`

## Files Generated

After running the notebook, you'll get:

- `products_enhanced_sample.csv` - Enhanced dataset sample (10K products with new features)
- `category_analysis.csv` - Category-level analysis
- `top_brands.csv` - Brand rankings
- `anomalies_and_insights.xlsx` - Anomaly detection results (expensive, viral, best value products)
- `eda_summary_report.txt` - Comprehensive summary report
- `products_eda_summary.csv` - Quick summary statistics

## Visualizations

The notebook includes **50+ visualizations**:

- Distribution plots (price, rating, popularity)
- Category comparisons
- Brand analysis charts
- TF-IDF keyword rankings
- Correlation heatmaps
- Embedding analysis plots
- Outlier detection (box plots)
- Trend analysis across price segments

## Performance

- **Runtime:** ~5-10 minutes (depending on system)
- **Memory:** ~1-2 GB required
- **Embedding Analysis:** Analyzes 10K product embeddings for performance

---

**Created:** October 29, 2025  
**Dataset Size:** 348,228 products  
**Categories:** 35  
**Embeddings:** BLAIR-RoBERTa (768 dimensions)
