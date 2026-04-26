# Price vs Rating Analysis 💰⭐

## Overview
Combined analysis of price and rating relationship across 5,455 laptops, revealing **weak correlation** (0.115) - price is a poor quality predictor.

---

## Key Findings

### 💰 Price Statistics
- **Coverage**: 38% (2,075/5,455) ⚠️ 62% missing
- **Mean**: $594 | **Median**: $444
- **Distribution**: 47% Budget (<$400), 6% Luxury ($1.5K+)

### ⭐ Rating Statistics
- **Coverage**: 100% ✅
- **Mean**: 3.80⭐ | **Median**: 3.80⭐
- **Distribution**: 68% rated "Good" or better (3.5-4.5⭐)

### 🔗 Correlations
- **Price vs Rating**: 0.115 (Pearson) | 0.176 (Spearman) - **Weak**
- **Rating vs Reviews**: 0.233 ✅ - Moderate positive
- **Price vs Reviews**: -0.088 - Negative (cheaper = more reviews)

### 💎 Value Segments
- **Best Value**: 735 products, $284 avg, 4.24⭐
- **Budget Gems**: 82 products, $328 avg, 4.52⭐ 🏆
- **Overpriced**: 14 products, $1,356 avg, 3.08⭐ ⚠️

### 📊 Rating by Price Tier
- Budget (<$400): 4.00⭐
- Premium ($1K-$1.5K): 4.15⭐
- **Difference**: Only 0.15⭐ for 3x price!

---

## Files

### Analysis Scripts
- **`analyze_price_rating.py`** - Full analysis (10 steps)

### Reports
- **`PRICE_RATING_ANALYSIS_REPORT.md`** ⭐ - Complete findings
- **`price_rating_analysis.csv`** - Summary metrics
- **`price_rating_summary.json`** - Detailed correlations

### Visualizations (6 charts)
1. Price distribution (3 views)
2. Rating distribution (2 views)
3. Price vs Rating scatter + boxplot
4. Price vs Reviews scatter
5. Rating vs Reviews scatter
6. Price-Quality matrix heatmap

---

## Running the Analysis

```bash
python3 analyze_price_rating.py
```

**Runtime**: ~40 seconds  
**Outputs**: 6 visualizations + CSV + JSON

---

## Key Insight 🔍

**Price is a WEAK quality predictor** (0.115 correlation):
- Budget ($400): 4.00⭐
- Premium ($1,250): 4.15⭐
- **Only 0.15⭐ difference** for 3x price!

**Better predictors**:
- Title length (0.361) - 3x stronger
- Review count (0.233) - 2x stronger
- Feature count (0.153) - stronger

---

## Value Recommendation 💎

**"Budget Gems"** segment:
- 82 products at $328 avg
- 4.52⭐ rating
- Best value in dataset!

---

**Dataset**: 5,455 laptops | **Myth**: Price = Quality ❌ | **Reality**: Weak correlation (0.115)

