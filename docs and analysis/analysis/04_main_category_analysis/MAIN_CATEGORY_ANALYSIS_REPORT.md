# Main Category Analysis Report 📂

## Executive Summary

The `main_category` field shows **97.5% of products** are correctly classified as "Computers", with 2.5% miscategorized or unspecified. However, **0% alignment** with leaf categories reveals that `main_category` represents a higher-level classification (Computers) while leaf categories specify the laptop type (Traditional, 2-in-1).

---

## 1. Main Category Distribution

| Main Category | Products | Market Share |
|---------------|----------|--------------|
| **Computers** | 5,316 | 97.45% |
| **(Not Specified)** | 102 | 1.87% |
| **All Electronics** | 28 | 0.51% |
| **Tools & Home Improvement** | 2 | 0.04% |
| **Cell Phones & Accessories** | 2 | 0.04% |
| **Apple Products** | 2 | 0.04% |
| **Industrial & Scientific** | 2 | 0.04% |
| **Amazon Home** | 1 | 0.02% |

### Key Findings
- ✅ **97.45%** correctly categorized as "Computers"
- ⚠️ **102 products** (1.87%) have no main category
- ❌ **137 products** (2.5%) miscategorized in wrong departments

---

## 2. Price by Main Category

| Category | Avg Price | Products |
|----------|-----------|----------|
| **Industrial & Scientific** | $1,999 | 2 |
| **Apple Products** | $1,200 | 2 |
| **Computers** | $597 | 5,316 |
| **(Not Specified)** | $426 | 102 |
| **All Electronics** | $307 | 28 |

**Insight**: Edge cases (Industrial, Apple) are premium products; main "Computers" category aligns with expected laptop pricing.

---

## 3. Quality by Main Category

| Category | Avg Rating | Products |
|----------|------------|----------|
| **Apple Products** | 4.35⭐ | 2 |
| **Tools & Home Improvement** | 3.95⭐ | 2 |
| **Industrial & Scientific** | 3.85⭐ | 2 |
| **Computers** | 3.80⭐ | 5,316 |
| **(Not Specified)** | 3.73⭐ | 102 |

**Insight**: All categories hover around 3.7-4.0⭐, showing consistent quality across the dataset.

---

## 4. Top Brands by Main Category

### Computers (97.5% of dataset)
1. **ASUS** - 828 (15.58%)
2. **HP** - 740 (13.92%)
3. **Amazon Renewed** - 726 (13.66%)
4. **Lenovo** - 678 (12.75%)
5. **Dell** - 533 (10.03%)

**Same top 5** as overall market leaders - confirms "Computers" = main laptop category.

---

## 5. Main vs Leaf Category Alignment

### Alignment Rate: **0.00%**

This is **NOT a data quality issue**. It's by design:
- **Main Category** = High-level department ("Computers")
- **Leaf Category** = Specific product type ("Traditional Laptops", "2-in-1 Laptops")

### Top Mismatch Patterns (by design)
1. **"Computers" → "Traditional Laptops"** (4,741) - Expected
2. **"Computers" → "2 in 1 Laptops"** (548) - Expected
3. **"(Not Specified)" → "Traditional Laptops"** (90) - Needs fixing
4. **"All Electronics" → "Traditional Laptops"** (23) - Needs fixing

---

## 6. Data Quality Issues

### 🔴 Critical Issues (137 products = 2.5%)

**102 products without main_category:**
- Should be set to "Computers"
- Same brand distribution as main dataset (ASUS, HP, Lenovo)

**35 miscategorized products:**
- 28 in "All Electronics" (too generic)
- 2 in "Tools & Home Improvement" (wrong department)
- 2 in "Cell Phones & Accessories" (wrong department)
- 2 in "Industrial & Scientific" (likely high-end workstations)
- 1 in "Amazon Home" (wrong department)

### ✅ Recommendations
1. Set 102 unspecified → "Computers"
2. Move 28 "All Electronics" → "Computers"
3. Review 7 products in wrong departments (Tools, Cell Phones, Amazon Home)
4. Keep 2 "Apple Products" and 2 "Industrial & Scientific" (valid edge cases)

---

## 7. Conclusion

The `main_category` field is **97.5% accurate** with "Computers" as the dominant category. The 0% alignment with leaf categories is **expected and correct** - they serve different purposes in the hierarchy:

- **Main Category** = Department ("Computers")
- **Leaf Category** = Product Type ("Traditional Laptops", "2-in-1")

### Action Items
- ✅ Fix 102 null values → "Computers"
- ✅ Reclassify 28 "All Electronics" → "Computers"
- ✅ Review 7 wrong-department products

**Post-cleanup**: 99.8% accuracy achievable.

---

## Appendices

### Files Generated
- **main_category_distribution.csv** - All 8 categories with statistics
- **main_category_summary.json** - Aggregated metrics
- **3 Visualizations**:
  - Main category distribution bar chart
  - Price by main category
  - Rating by main category

---

**Report Generated**: November 4, 2025  
**Dataset**: 5,455 products | 8 categories | 97.5% "Computers"

