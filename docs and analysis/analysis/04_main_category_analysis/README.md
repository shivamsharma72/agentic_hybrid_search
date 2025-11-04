# Main Category Analysis 📂

## Overview
Analysis of the `main_category` field across 5,455 laptops, revealing 97.5% correct classification with 2.5% needing cleanup.

---

## Key Findings

### 📊 Distribution
- **Computers**: 5,316 (97.45%) ✅
- **(Not Specified)**: 102 (1.87%) ⚠️ Needs fixing
- **All Electronics**: 28 (0.51%) ⚠️ Too generic
- **Others**: 9 (0.17%) ❌ Miscategorized

### 💰 Pricing
- **Computers**: $597 avg (main category)
- **Apple Products**: $1,200 avg (premium)
- **Not Specified**: $426 avg (similar to main)

### ⭐ Quality
- All categories: 3.7-4.0⭐ (consistent quality)
- **Apple Products** highest at 4.35⭐

---

## Files

### Analysis Script
- **`analyze_main_category.py`** - Full analysis

### Reports
- **`MAIN_CATEGORY_ANALYSIS_REPORT.md`** ⭐ - Brief findings
- **`main_category_distribution.csv`** - All 8 categories
- **`main_category_summary.json`** - Metrics

### Visualizations (3 charts)
1. Main category distribution
2. Price by category
3. Rating by category

---

## Quick Insights

### Main vs Leaf Categories
- **0% alignment** - This is **expected**!
- Main = Department level ("Computers")
- Leaf = Product type ("Traditional Laptops")
- Different hierarchy levels, not a bug

### Data Quality
- **137 products** need fixing (2.5%)
  - 102 missing main_category
  - 28 in "All Electronics" (too generic)
  - 7 in wrong departments

---

## Running the Analysis

```bash
python3 analyze_main_category.py
```

**Runtime**: ~15 seconds  
**Outputs**: 3 visualizations + CSV + JSON

---

**Dataset**: 5,455 laptops | **Accuracy**: 97.5% | **Cleanup Needed**: 2.5%

