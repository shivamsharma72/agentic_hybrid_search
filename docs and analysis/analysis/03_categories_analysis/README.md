# Categories Analysis 📁

## Overview
Analysis of category hierarchies across 5,455 laptop products, revealing an extremely standardized structure with only 2 primary categories.

---

## Key Findings

### 📊 Category Structure
- **Root**: 100% "Electronics"
- **Main Types**: Traditional Laptops (89.1%) | 2-in-1 Laptops (10.4%)
- **Hierarchy Depth**: 5 levels (99.5% consistent)
- **Total Unique Categories**: Only 14

### 💰 Price & Quality
- **Traditional**: $595 avg, 3.80⭐
- **2-in-1**: $588 avg, 3.79⭐
- **Verdict**: No price/quality premium for either type

---

## Files

### Analysis Scripts
- **`analyze_categories.py`** - Full category hierarchy analysis

### Reports
- **`CATEGORIES_ANALYSIS_REPORT.md`** ⭐ - Complete analysis
- **`category_distribution.csv`** - All 9 categories with statistics
- **`category_summary.json`** - Aggregated metrics

### Visualizations (6 charts)
1. Category depth distribution
2. Top root categories
3. Top leaf categories
4. Most frequent categories
5. Category price comparison
6. Category quality comparison

---

## Quick Insights

### The Standard Path (99.2% of products)
```
Electronics → Computers & Accessories → Computers & Tablets → Laptops → [Traditional or 2-in-1]
```

### Market Split
- **Traditional Laptops**: 4,862 products (89%)
- **2-in-1 Laptops**: 566 products (11%)
- **Other**: 27 products (0.5%) - edge cases

### Data Quality Issues
- 27 miscategorized products (promotional, accessories, brand-specific)
- 17 products missing specific type (generic "Laptops")
- Touchscreen should be a feature, not a category

---

## Running the Analysis

```bash
python3 analyze_categories.py
```

**Runtime**: ~20-30 seconds  
**Outputs**: 6 visualizations + CSV + JSON

---

## Use Cases

### For RAG System
- **Simple filtering**: Only 2 main types
- **Feature-based search**: Use features column for "touchscreen", "gaming", etc.
- **Brand insights**: Lenovo leads in 2-in-1, ASUS in Traditional

### For Recommendations
- **Type-based**: Traditional vs 2-in-1 preference
- **Price-neutral**: No premium for convertible form factor
- **Quality-neutral**: Both types equally rated

---

**Dataset**: 5,455 laptops | **Categories**: 14 unique | **Main Types**: 2

