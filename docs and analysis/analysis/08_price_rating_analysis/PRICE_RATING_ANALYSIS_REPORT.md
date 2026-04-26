# Price vs Rating Analysis Report 💰⭐

## Executive Summary

Only **38% of products** have price data (2,075/5,455), with a mean of $594 and median of $444. Ratings are universal (100% coverage) with a mean of 3.80⭐. **Weak positive correlation** exists between price and rating (0.115 Pearson, 0.176 Spearman) - higher price slightly improves quality. The "Best Value" segment (35% of priced products) offers $284 avg and 4.24⭐, while 82 "Budget Gems" provide 4.52⭐ for just $328.

---

## 1. Price Distribution

### Statistics

| Metric | Value |
|--------|-------|
| **Coverage** | 2,075 / 5,455 (38.04%) ⚠️ |
| **Mean** | $593.97 |
| **Median** | $444.00 |
| **Std Dev** | $494.42 (High variance) |
| **Range** | $24.95 - $5,598.00 |
| **Q1 (25th percentile)** | $239.50 |
| **Q3 (75th percentile)** | $797.75 |

**Issue**: Only 38% of products have price data - 62% missing (3,380 products).

### Price Tier Distribution

| Tier | Range | Products | % of Priced |
|------|-------|----------|-------------|
| **Budget** | <$400 | 976 | 47.04% ⭐ |
| **Mid-Range** | $400-$700 | 486 | 23.42% |
| **Upper-Mid** | $700-$1K | 293 | 14.12% |
| **Premium** | $1K-$1.5K | 204 | 9.83% |
| **Luxury** | $1.5K+ | 116 | 5.59% |

**Key Finding**: Nearly half (47%) are budget laptops (<$400). Only 5.6% are luxury ($1.5K+).

---

## 2. Rating Distribution

### Statistics

| Metric | Value |
|--------|-------|
| **Coverage** | 5,455 / 5,455 (100%) ✅ |
| **Mean** | 3.80⭐ |
| **Median** | 3.80⭐ |
| **Std Dev** | 0.44 (Low variance) |
| **Range** | 2.00 - 5.00 |

**Perfect = Mean**: Mean equals median (3.80⭐) indicates symmetric, normal distribution.

### Rating Distribution

| Category | Range | Products | Percentage |
|----------|-------|----------|------------|
| **Poor** | <3.0 | 322 | 5.90% |
| **Fair** | 3.0-3.5 | 1,307 | 23.96% |
| **Good** | 3.5-4.0 | 2,025 | 37.12% ⭐ |
| **Very Good** | 4.0-4.5 | 1,699 | 31.15% |
| **Excellent** | 4.5+ | 102 | 1.87% |

**Key Finding**: 68% rated "Good" or better (3.5-4.5⭐). Only 2% achieve "Excellent" (4.5+).

---

## 3. Price vs Rating Correlation

### Correlations

| Method | Correlation | Interpretation |
|--------|-------------|----------------|
| **Pearson** | 0.115 | Weak positive (linear) |
| **Spearman** | 0.176 | Weak positive (monotonic) |

**Finding**: Weak but positive correlation - higher price **slightly** improves ratings.

### Average Rating by Price Tier

| Price Tier | Avg Rating | Products | Rating Trend |
|------------|------------|----------|--------------|
| **Budget** (<$400) | 4.00⭐ | 976 | Baseline |
| **Mid-Range** ($400-$700) | 4.08⭐ | 486 | +0.08 |
| **Upper-Mid** ($700-$1K) | 4.12⭐ | 293 | +0.12 |
| **Premium** ($1K-$1.5K) | 4.15⭐ | 204 | +0.15 |
| **Luxury** ($1.5K+) | 4.10⭐ | 116 | +0.10 (drops!) |

**Insight**: 
- Ratings improve with price up to Premium ($1K-$1.5K = 4.15⭐)
- Luxury ($1.5K+) ratings **drop to 4.10⭐** - expectations not met?
- Total range: 4.00 to 4.15⭐ (only 0.15⭐ difference!) - **minimal impact**

---

## 4. Review Count Analysis

### Statistics

| Metric | Value |
|--------|-------|
| **Total Reviews** | 1,131,200 across all products |
| **Mean per Product** | 207 reviews |
| **Median per Product** | 72 reviews |
| **Max Reviews** | 35,925 (one product!) |

**Key**: Huge variance - median (72) much lower than mean (207) indicates a few products with massive review counts skewing the average.

---

## 5. Price vs Review Count

### Correlation: **-0.088** (Weak negative)

**Finding**: Slightly negative correlation - **cheaper products get more reviews**. This makes sense:
- Budget products have higher sales volume
- More sales = more reviews
- Premium products are niche, fewer buyers

---

## 6. Rating vs Review Count

### Correlation: **0.233** ✅ (Moderate positive)

**Finding**: Products with more reviews tend to have **higher ratings**. This could be:
1. **Selection bias**: Good products get more sales → more reviews
2. **Social proof**: High ratings → more purchases → more reviews (virtuous cycle)
3. **Quality signal**: More reviews = established, reliable products

---

## 7. Price-Quality Matrix

### Product Distribution

| Price ↓ / Quality → | Standard (<3.5⭐) | Good (3.5-4.0⭐) | Excellent (4.0+⭐) |
|---------------------|------------------|------------------|-------------------|
| **Budget** (<$500) | 134 | 432 | **605** ⭐ |
| **Mid-Range** ($500-$1K) | 55 | 168 | **361** |
| **Premium** ($1K+) | 25 | 80 | **215** |

**Key Finding**: Even in the Budget tier, **605 products** (52%) achieve Excellent ratings (4.0+)!

---

## 8. Value Segments 💎

### Best Value (Budget + Excellent Quality)
- **735 products** (35.42% of priced products)
- **$284 avg price**
- **4.24⭐ avg rating**
- **Best for**: Budget-conscious buyers seeking quality

### Premium Value (Mid-Range + Excellent)
- **404 products** (19.47%)
- **$723 avg price**
- **4.31⭐ avg rating**
- **Best for**: Buyers seeking balance of performance and price

### Budget Gems (Budget + 4.5+⭐) 🏆
- **82 products** (3.95%)
- **$328 avg price**
- **4.52⭐ avg rating**
- **Best for**: Finding hidden gems at low prices

### Overpriced (Premium + Low Quality)
- **14 products** (0.67%)
- **$1,356 avg price**
- **3.08⭐ avg rating** ⚠️
- **Avoid**: High price, low satisfaction

---

## 9. Key Findings

### ✅ Insights
1. **Price barely affects rating**: Only 0.15⭐ difference between Budget and Premium
2. **Budget dominates**: 47% of products are <$400, and they're rated 4.00⭐ avg
3. **Best Value exists**: 735 products offer <$500 with 4.24⭐ avg
4. **Budget Gems**: 82 products at $328 with 4.52⭐ - incredible value
5. **Luxury paradox**: $1.5K+ products rated 4.10⭐ (lower than Premium at 4.15⭐)

### ⚠️ Issues
1. **62% missing prices**: Only 2,075/5,455 have price data
2. **Weak correlation**: 0.115-0.176 means price is a poor quality predictor
3. **Overpriced segment**: 14 products at $1,356 with only 3.08⭐
4. **Review bias**: Cheaper products get more reviews (-0.088 correlation)

### 💡 Market Dynamics
1. **Value democratization**: Quality no longer tied to price
2. **Budget competitiveness**: Budget laptops (4.00⭐) rival Premium (4.15⭐)
3. **Premium expectations**: Luxury buyers are harder to please (4.10⭐ despite $1.5K+)
4. **Review virtuous cycle**: Good ratings → more sales → more reviews (0.233 correlation)

---

## 10. Comparison with Other Analyses

| Factor | Correlation with Rating |
|--------|------------------------|
| **Title Length** | 0.361 ⭐⭐ (Strongest!) |
| **Rating vs Review Count** | 0.233 |
| **Feature Count** | 0.153 |
| **Price (Spearman)** | 0.176 |
| **Price (Pearson)** | 0.115 |
| **Price vs Reviews** | -0.088 (negative) |

**Ranking**: Title length (0.361) > Reviews (0.233) > Features (0.153) > Price (0.115-0.176)

---

## 11. Recommendations

### For Consumers
- **Target "Best Value"** segment: <$500 with 4.0+⭐ (735 products available)
- **Hunt for "Budget Gems"**: 82 products at $328 with 4.52⭐ - best bang for buck
- **Don't overpay**: Premium ($1K-$1.5K) only gets you +0.15⭐ vs Budget
- **Avoid luxury misconception**: $1.5K+ laptops rated 4.10⭐ (worse than Premium!)
- **Check reviews**: 0.233 correlation - more reviews = likely better product

### For Sellers
- **Budget is viable**: 47% of market, 4.00⭐ avg - competitive pricing works
- **Premium positioning**: Must deliver 4.15+⭐ to justify $1K-$1.5K price
- **Avoid overpricing**: 14 products at $1,356 with 3.08⭐ - damaging to brand
- **Encourage reviews**: 0.233 correlation - more reviews boost perceived quality

### For Platform (Amazon)
- **Fix missing prices**: 62% lack pricing (3,380 products) - critical data gap
- **Highlight value segments**: Promote "Best Value" (735) and "Budget Gems" (82)
- **Flag overpriced**: Warn about 14 products with high price, low rating
- **Review incentives**: Strong 0.233 correlation - reviews drive sales

### For RAG System
- **Don't overweight price**: Only 0.115 correlation with rating
- **Use title length**: 0.361 correlation - better quality signal than price
- **Surface Budget Gems**: Query for <$500 with 4.5+⭐ (82 products)
- **Review count boost**: 0.233 correlation - products with more reviews likely better
- **Value recommendation**: Prioritize $284 avg, 4.24⭐ segment (best value)

---

## 12. Price-Rating Relationship Summary

**Myth Busted**: "Higher price = better quality" is **mostly false** for laptops.

**Reality**:
- Budget ($400 avg): 4.00⭐
- Premium ($1,250 avg): 4.15⭐
- **Difference**: Only 0.15⭐ for 3x the price!

**Better Predictors**:
1. Title length (0.361) - 3x stronger than price
2. Review count (0.233) - 2x stronger than price
3. Feature count (0.153) - stronger than price

**Conclusion**: **Price is a weak quality signal** for laptops. Focus on title details, reviews, and features instead.

---

## Appendices

### A. Files Generated
- **price_rating_analysis.csv** - Summary metrics
- **price_rating_summary.json** - Detailed statistics & correlations
- **6 Visualizations**:
  - Price distribution (3 views)
  - Rating distribution (2 views)
  - Price vs Rating scatter + boxplot
  - Price vs Reviews scatter
  - Rating vs Reviews scatter
  - Price-Quality heatmap + scatter

### B. Statistical Notes
- **Pearson**: Measures linear relationship
- **Spearman**: Measures monotonic relationship (better for non-linear)
- **Coverage issue**: 62% missing prices affects correlation reliability
- **Normal distribution**: Ratings are normally distributed (mean = median = 3.80⭐)

---

**Report Generated**: November 4, 2025  
**Dataset**: 5,455 laptops | **Priced**: 38% | **Avg Price**: $594 | **Avg Rating**: 3.80⭐

