# Product Titles Analysis 📝

## Overview
Analysis of product title patterns across 5,455 laptops, revealing titles are the **strongest quality indicator** (0.361 correlation with rating).

---

## Key Findings

### 📏 Length Statistics
- **Avg**: 127 characters, 20.3 words
- **Optimal**: 150-200 chars ($685 avg, 3.99⭐)
- **Distribution**: 67% are 100-200 characters

### 🔤 Top Keywords
1. **intel** (59%) - Dominant processor
2. **core** (53%) - Architecture
3. **ram** (44%) - Memory
4. **ssd** (37%) - Storage
5. **touchscreen** (17%) - Features

### 🔧 Specs in Titles
- **Screen Size**: 90% ⭐
- **Brand**: 89%
- **Processor**: 75%
- **RAM**: 61%
- **Storage**: 58%

### 💰⭐ Strong Quality Signal
- **Rating correlation**: 0.361 ✅✅ (Strongest!)
- **Price correlation**: 0.220 ✅
- **150-200 chars = 3.99⭐** (best ratings)

### 🏪 Brand Strategies
- **HP** (141 chars) - Most detailed
- **Lenovo** (134 chars) - Comprehensive
- **Toshiba** (98 chars) - Most brief

---

## Files

### Analysis Scripts
- **`analyze_titles.py`** - Full analysis (8 steps)

### Reports
- **`TITLES_ANALYSIS_REPORT.md`** ⭐ - Complete findings
- **`titles_analysis.csv`** - Summary metrics
- **`titles_summary.json`** - Detailed data & keywords

### Visualizations (5 charts)
1. Title length distribution
2. Top 25 keywords
3. Specs mentioned in titles
4. Length vs price scatter
5. Brand comparison

---

## Running the Analysis

```bash
python3 analyze_titles.py
```

**Runtime**: ~30 seconds  
**Outputs**: 5 visualizations + CSV + JSON

---

## Key Insight 🏆

**Title length is the BEST quality indicator** we've found:
- 0.361 correlation with rating (vs 0.153 for features, -0.012 for descriptions)
- 150-200 chars = optimal (3.99⭐ avg)
- <50 chars = red flag (3.55⭐ avg)

---

**Dataset**: 5,455 laptops | **Avg**: 127 chars | **Optimal**: 150-200 chars

