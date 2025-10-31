# Product Details Field - Quick Reference

**Database:** `amazon_electronics_rag` | **Table:** `products` | **Field:** `details` (JSONB)

---

## 📊 At a Glance

| Metric                   | Value                             |
| ------------------------ | --------------------------------- |
| 🎯 **Coverage**          | 100% (348,228 / 348,228 products) |
| 🔑 **Total Unique Keys** | 1,541                             |
| 📏 **Avg Keys/Product**  | 13.15 (median: 12)                |
| 📝 **Value Types**       | 94% short text (<50 chars)        |
| 🌟 **Top Keys**          | 9 keys in >50% of products        |

---

## 🔝 Top 20 Most Common Keys

| #   | Key                               | Coverage | Use For                        |
| --- | --------------------------------- | -------- | ------------------------------ |
| 1   | `Date First Available`            | 94%      | Product age, temporal analysis |
| 2   | `Item Weight`                     | 90%      | Shipping, physical constraints |
| 3   | `Manufacturer`                    | 87%      | **Brand nodes in graph**       |
| 4   | `Brand`                           | 81%      | **Brand nodes in graph**       |
| 5   | `Item model number`               | 75%      | Product identification         |
| 6   | `Product Dimensions`              | 63%      | Size filtering, normalization  |
| 7   | `Is Discontinued By Manufacturer` | 56%      | Product lifecycle              |
| 8   | `Best Sellers Rank`               | 56%      | Popularity metric              |
| 9   | `Color`                           | 50%      | Visual attribute filtering     |
| 10  | `Compatible Devices`              | 36%      | **Compatibility graph edges**  |
| 11  | `Package Dimensions`              | 29%      | Shipping                       |
| 12  | `Special Feature`                 | 29%      | **Feature nodes in graph**     |
| 13  | `Connectivity Technology`         | 23%      | **Technical specs, graph**     |
| 14  | `Form Factor`                     | 14%      | Product type classification    |
| 15  | `Country of Origin`               | 14%      | Manufacturing origin           |
| 16  | `Material`                        | 13%      | **Material nodes in graph**    |
| 17  | `Batteries`                       | 13%      | Power specifications           |
| 18  | `Connector Type`                  | 12%      | Cable/accessory specs          |
| 19  | `Model Name`                      | 12%      | Product line identification    |
| 20  | `Screen Size`                     | 9%       | Display products               |

---

## 🎯 Priority Keys for Graph (Top 30)

### **Tier 1: Universal (>50% coverage)**

✅ Use these for all product types

- `Brand`, `Manufacturer` → **Brand nodes**
- `Color` → Property/node
- `Date First Available` → Temporal property

### **Tier 2: High Coverage (10-50%)**

✅ Use for most electronics

- `Material` → **Material nodes**
- `Compatible Devices` → **Compatibility edges**
- `Special Feature` → **Feature nodes** (parse comma-separated)
- `Connectivity Technology` → **Feature nodes**
- `Form Factor` → Spec nodes
- `Batteries`, `Voltage`, `Power Source` → Spec nodes

### **Tier 3: Category-Specific (5-10%)**

✅ Use for specific categories only

- **Computers:** `RAM`, `Hard Drive`, `CPU Speed`, `Operating System`
- **Displays:** `Screen Size`, `Standing screen display size`, `Other display features`
- **Cables:** `Cable Type`, `Connector Type`, `Connector Gender`
- **Audio:** `Wattage`, `Wireless Type`, `Speaker Type`

---

## 💡 Common Query Patterns

### Find products by brand:

```sql
SELECT * FROM products
WHERE details ->> 'Brand' = 'Sony';
```

### Find products with specific RAM:

```sql
SELECT * FROM products
WHERE details ? 'RAM'
  AND details ->> 'RAM' LIKE '%16 GB%';
```

### Find Bluetooth products:

```sql
SELECT * FROM products
WHERE details ? 'Connectivity Technology'
  AND details ->> 'Connectivity Technology' ILIKE '%bluetooth%';
```

### Count products by color:

```sql
SELECT details ->> 'Color' as color, COUNT(*)
FROM products
WHERE details ? 'Color'
GROUP BY details ->> 'Color'
ORDER BY COUNT(*) DESC;
```

### Find compatible products:

```sql
SELECT * FROM products
WHERE details ? 'Compatible Devices'
  AND details ->> 'Compatible Devices' ILIKE '%laptop%';
```

---

## ⚠️ Data Quality Notes

### Inconsistencies to Handle:

1. **Key names:** `Item Dimensions LxWxH` vs `Item Dimensions  LxWxH` (extra space)
2. **Capitalization:** `Special Feature` vs `Special features`
3. **Units:** "1.5 pounds" vs "0.68 Kilograms" (need normalization)
4. **Multi-values:** `Special Feature` often has comma-separated values
5. **Nested JSON:** `Best Sellers Rank` is a nested object

### Recommendations:

- ✅ Normalize key names (lowercase, trim spaces)
- ✅ Parse and convert units (weight, dimensions)
- ✅ Split comma-separated values (features, compatible devices)
- ✅ Extract nested JSON values

---

## 📁 Files

1. **Analysis Script:** `analyze_details_field.py` (414 lines)
2. **CSV Export:** `details_analysis.csv` (1,542 rows)
3. **Full Summary:** `DETAILS_FIELD_ANALYSIS_SUMMARY.md` (comprehensive)
4. **Quick Reference:** `DETAILS_QUICK_REFERENCE.md` (this file)

---

## 🚀 Next Steps

1. ✅ **Complete:** Details field analysis
2. 🎯 **Next:** Extract and normalize top 30 keys
3. 📋 **Future:** Create Neo4j graph nodes from specs
4. 📋 **Future:** Build spec-based similarity edges

---

_Quick reference for the `details` JSONB field in the products table_

