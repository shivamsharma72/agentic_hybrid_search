# Features Field - Quick Reference Guide

**TL;DR:** Features are arrays of 4-5 bullet points per product (76% coverage). Perfect for laptop identification!

---

## 📊 At a Glance

| Metric                   | Value                  |
| ------------------------ | ---------------------- |
| **Coverage**             | 76.4% of products      |
| **Avg Features/Product** | 4.7 items              |
| **Avg Feature Length**   | 141 characters         |
| **Unique Features**      | 577K out of 725K       |
| **Laptop Mentions**      | 48,948 direct keywords |

---

## 🎯 Laptop Keywords (Sorted by Frequency)

### Top 20 Laptop Indicators:

| Rank | Keyword         | Occurrences | Use Case            |
| ---- | --------------- | ----------- | ------------------- |
| 1    | **usb**         | 44,232      | Connectivity        |
| 2    | **wh**          | 88,306      | Battery capacity    |
| 3    | **laptop**      | 30,524      | **Direct match** ⭐ |
| 4    | **screen**      | 29,781      | Display             |
| 5    | **led**         | 28,314      | Display type        |
| 6    | **battery**     | 27,347      | Power               |
| 7    | **weight**      | 22,562      | Build quality       |
| 8    | **display**     | 20,167      | Screen              |
| 9    | **thin**        | 19,732      | Form factor         |
| 10   | **ram**         | 18,634      | **Spec** ⭐         |
| 11   | **bluetooth**   | 16,355      | Connectivity        |
| 12   | **ips**         | 14,364      | Display type        |
| 13   | **hdmi**        | 13,980      | Ports               |
| 14   | **memory**      | 13,041      | RAM/Storage         |
| 15   | **lightweight** | 13,306      | Portability         |
| 16   | **monitor**     | 12,635      | Display             |
| 17   | **portable**    | 12,287      | Form factor         |
| 18   | **storage**     | 11,764      | Hard drive          |
| 19   | **resolution**  | 11,016      | Display             |
| 20   | **windows**     | 10,680      | **OS** ⭐           |

---

## 🔍 Quick Laptop Detection

### One-Liner Check:

```python
is_laptop = any(kw in ' '.join(features).lower()
                for kw in ['laptop', 'notebook', 'chromebook', 'macbook'])
```

### Comprehensive Check (3-Tier):

```python
# Tier 1: Direct keywords (BEST)
direct = ['laptop', 'notebook', 'ultrabook', 'chromebook', 'macbook']

# Tier 2: Hardware specs (GOOD)
hardware = ['ram', 'processor', 'cpu', 'intel', 'amd', 'ghz', 'ssd']

# Tier 3: OS (SUPPORTING)
os_keywords = ['windows', 'macos', 'chrome os']

# Logic:
# IF Tier 1 → Laptop
# ELSE IF (Tier 2 AND Tier 3) → Laptop
# ELSE → Not laptop
```

---

## 📋 Feature Pattern Types

| Pattern        | %   | Example                          |
| -------------- | --- | -------------------------------- |
| **Key:Value**  | 30% | "Brand: Sony", "Weight: 2.5 lbs" |
| **Dimensions** | 13% | "15.6 inches", "30 cm wide"      |
| **Specs**      | 12% | "16GB RAM", "2.4 GHz"            |
| **Sentences**  | 40% | "Easy to install and use..."     |
| **Paragraphs** | 10% | Long marketing text              |

---

## 📊 Coverage by Category

| Category        | Coverage | Avg Features |
| --------------- | -------- | ------------ |
| Automotive      | 87%      | 4.5          |
| Tools           | 85%      | 4.7          |
| Car Electronics | 81%      | 4.7          |
| Audio           | 78%      | 4.6          |
| All Electronics | 77%      | 4.7          |
| Cameras         | 77%      | 4.7          |
| **Computers**   | **73%**  | **4.8**      |

---

## 💻 Laptop Keywords by Category

### Hardware (82,992 mentions):

- ram (18K), memory (13K), storage (12K), intel (10K)
- ghz (7K), processor (6K), hard drive (5K), ssd (4K)

### Display (127,052 mentions):

- screen (30K), led (28K), display (20K), ips (14K)
- monitor (13K), resolution (11K), lcd (7K)

### Connectivity (92,173 mentions):

- usb (44K), bluetooth (16K), hdmi (14K)
- ethernet (6K), wifi (5K), usb-c (5K)

### OS (18,862 mentions):

- windows (11K), chromebook (3K), mac os (2K), linux (2K)

### Types (48,948 mentions):

- laptop (31K), macbook (9K), notebook (4K), chromebook (3K)

---

## 🎯 Recommended Queries

### PostgreSQL (After adding array column):

```sql
-- Find all laptops
SELECT parent_asin, title
FROM products
WHERE
    'laptop' = ANY(
        SELECT LOWER(unnest(features_array))
    )
    OR 'Laptops' = ANY(categories);

-- Find laptops with RAM specs
SELECT parent_asin, title
FROM products
WHERE EXISTS (
    SELECT 1 FROM unnest(features_array) AS f
    WHERE f ILIKE '%ram%' OR f ILIKE '%memory%'
);

-- Find Windows laptops
SELECT parent_asin, title
FROM products
WHERE
    'Laptops' = ANY(categories)
    AND EXISTS (
        SELECT 1 FROM unnest(features_array) AS f
        WHERE f ILIKE '%windows%'
    );
```

### Python (Parquet):

```python
import pandas as pd
import numpy as np

df = pd.read_parquet('product.parquet')

# Filter laptops
def is_laptop(row):
    features = ' '.join(row['features']).lower() if isinstance(row['features'], np.ndarray) else ''
    categories = ' '.join(row['categories']).lower() if isinstance(row['categories'], np.ndarray) else ''

    # Check direct keywords
    if any(kw in features or kw in categories
           for kw in ['laptop', 'notebook', 'chromebook']):
        return True

    # Check specs combination
    has_ram = 'ram' in features or 'memory' in features
    has_os = any(os in features for os in ['windows', 'macos', 'chrome os'])

    return has_ram and has_os

laptops = df[df.apply(is_laptop, axis=1)]
```

---

## 📁 Key Files

1. **`FEATURES_FIELD_ANALYSIS_SUMMARY.md`** - Full analysis (40+ pages)
2. **`features_parquet_analysis.csv`** - 50K sample features
3. **`analyze_features_from_parquet.py`** - Analysis script

---

## 🚀 Next Steps

1. ✅ Features analysis complete
2. **Identify laptops** using multi-tier logic
3. **Add `features_array TEXT[]`** to PostgreSQL
4. **Create GIN index** for fast queries
5. **Build graph** from features

---

**Quick Laptop Count Estimate:**

- 30,524 "laptop" keyword mentions
- ~48,948 total laptop-type mentions
- Estimated: **25,000-35,000 laptops** in 348K products (7-10%)

---

**Last Updated:** October 31, 2025
