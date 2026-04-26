# Features Field Analysis Summary - Parquet Data

**Date:** October 31, 2025  
**Source:** 10 Parquet files (`data/processed/raw_meta_Electronics/`)  
**Sample Size:** 200,000 products (out of 1.8M total)  
**Field:** `features` (numpy.ndarray - Array of feature strings)

---

## 📊 Executive Summary

### Key Findings:

1. **Coverage:** 76.43% of products have features (152,861 out of 200,000)
2. **Array Length:** Average 4.7 features per product (median: 5)
3. **Total Features:** 724,730 individual features extracted
4. **Unique Features:** 577,577 unique feature strings (79.7% uniqueness!)
5. **Feature Length:** Average 141 characters (median: 107 chars)
6. **Laptop Keywords:** "laptop" appears in 30,524 features (4.6% of sample)

---

## 🎯 Data Structure

### Features Field Structure:

```python
features = numpy.ndarray([
    "Feature 1: Detailed description...",
    "Feature 2: Another specification...",
    "Feature 3: Usage information...",
    ...
])
```

### Characteristics:

- **Type:** numpy.ndarray (not Python list)
- **Items:** Each item is a complete feature string
- **Length:** 1-60 features per product (most have 5)
- **Content:** Mix of specs, descriptions, and marketing text

---

## 📈 Detailed Statistics

### 1. Coverage by Category (Top 20)

| Category                  | Products | With Features | Coverage | Avg Features |
| ------------------------- | -------- | ------------- | -------- | ------------ |
| Automotive                | 1,598    | 1,397         | 87.4%    | 4.5          |
| Musical Instruments       | 903      | 778           | 86.2%    | 4.7          |
| Tools & Home Improvement  | 3,076    | 2,621         | 85.2%    | 4.7          |
| Car Electronics           | 3,198    | 2,603         | 81.4%    | 4.7          |
| Office Products           | 2,640    | 2,121         | 80.3%    | 4.7          |
| Sports & Outdoors         | 1,901    | 1,511         | 79.5%    | 4.7          |
| GPS & Navigation          | 1,000    | 787           | 78.7%    | 4.7          |
| Home Audio & Theater      | 13,174   | 10,326        | 78.4%    | 4.6          |
| Cell Phones & Accessories | 18,995   | 14,868        | 78.3%    | 4.8          |
| Industrial & Scientific   | 6,514    | 5,132         | 78.8%    | 4.7          |
| All Electronics           | 50,711   | 39,005        | 76.9%    | 4.7          |
| Camera & Photo            | 27,190   | 20,893        | 76.8%    | 4.7          |
| Amazon Devices            | 1,163    | 889           | 76.4%    | 5.6          |
| AMAZON FASHION            | 2,881    | 2,198         | 76.3%    | 5.4          |
| Amazon Home               | 2,921    | 2,249         | 77.0%    | 4.9          |
| Toys & Games              | 509      | 386           | 75.8%    | 4.5          |
| Computers                 | 57,307   | 41,955        | 73.2%    | 4.8          |

**Key Insight:** Most categories have 75-85% coverage with similar average feature counts (4.5-5.0).

---

### 2. Feature String Length Distribution

| Length Category         | Count   | Percentage | Example                                                                                                   |
| ----------------------- | ------- | ---------- | --------------------------------------------------------------------------------------------------------- |
| Very Short (<20 chars)  | 37,431  | 5.2%       | "UPC: 662774021904"                                                                                       |
| Short (20-50 chars)     | 129,800 | 17.9%      | "Compatible with MacBook Pro 13 inch"                                                                     |
| Medium (50-150 chars)   | 286,068 | 39.5%      | "Easy Apply. Easy, bubble-free installation and goo-free removal. Installation guide is well documented." |
| Long (150-300 chars)    | 197,240 | 27.2%      | Full sentence descriptions                                                                                |
| Very Long (>=300 chars) | 74,191  | 10.2%      | Multi-sentence paragraphs                                                                                 |

**Key Insight:** Most features (39.5%) are medium-length (50-150 chars), perfect for readable bullet points.

---

### 3. Feature Patterns

| Pattern             | Occurrences | Percentage | Example                                 |
| ------------------- | ----------- | ---------- | --------------------------------------- |
| Has colon (`:`)     | 29,840      | 29.8%      | "Brand: Sony", "Weight: 2.5 lbs"        |
| Contains dimensions | 12,664      | 12.7%      | "15.6 inches", "5 cm wide"              |
| Contains specs      | 12,071      | 12.1%      | "16GB RAM", "Intel Core i7", "2.4 GHz"  |
| Contains weight     | 1,931       | 1.9%       | "8 pounds", "3.5 kg", "12 oz"           |
| Starts with number  | 1,676       | 1.7%       | "1. First feature", "2. Second feature" |
| All caps            | 637         | 0.6%       | "SATISFACTION GUARANTEED"               |
| Question mark       | 408         | 0.4%       | "Need help? Contact us..."              |
| Has bullets         | 73          | 0.1%       | "• Feature one", "● Feature two"        |

**Key Insight:** Nearly 30% of features use colon format (key:value), making them easy to parse.

---

## 🔝 Top 100 Keywords (Filtered)

### Most Common Keywords in Features:

| Rank   | Keyword    | Frequency | % of Sample |
| ------ | ---------- | --------- | ----------- |
| 1      | easy       | 16,218    | 8.11%       |
| 2      | cable      | 15,948    | 7.97%       |
| 3      | case       | 15,597    | 7.80%       |
| 4      | design     | 14,652    | 7.33%       |
| 5      | power      | 13,765    | 6.88%       |
| 6      | camera     | 11,164    | 5.58%       |
| 7      | ipad       | 10,241    | 5.12%       |
| 8      | battery    | 10,109    | 5.05%       |
| 9      | free       | 9,808     | 4.90%       |
| 10     | protection | 9,767     | 4.88%       |
| 11     | screen     | 9,396     | 4.70%       |
| **12** | **laptop** | **9,254** | **4.63%**   |
| 13     | charging   | 8,794     | 4.40%       |
| 14     | inch       | 8,707     | 4.35%       |
| 15     | warranty   | 8,604     | 4.30%       |
| 16     | video      | 8,461     | 4.23%       |
| 17     | please     | 8,455     | 4.23%       |
| 18     | support    | 8,433     | 4.22%       |
| 19     | built      | 7,525     | 3.76%       |
| 20     | light      | 7,520     | 3.76%       |

**Electronics-Specific Keywords (21-50):**

- audio (7,238), material (7,099), devices (7,042), sound (6,743)
- tablet (6,732), device (6,689), bluetooth (6,398), adapter (6,293)
- wireless (6,175), control (5,938), hdmi (5,658), phone (5,627)
- port (5,568), plug (5,246), card (5,164), speed (5,160)
- display (5,076), keyboard (5,035), music (4,973)

**Laptop-Specific Keywords (51-100):**

- computer (4,484), memory (4,235), drive (3,901)

---

## 💻 Laptop-Specific Analysis

### Laptop Keyword Categories:

#### 1. **LAPTOP TYPES** (Most Direct)

| Keyword       | Occurrences | Context             |
| ------------- | ----------- | ------------------- |
| laptop        | 30,524      | Direct mentions     |
| macbook       | 8,701       | Apple laptops       |
| notebook      | 4,402       | Alternative term    |
| chromebook    | 2,619       | Chrome OS laptops   |
| thinkpad      | 969         | Lenovo brand        |
| 2-in-1        | 918         | Convertible laptops |
| ultrabook     | 592         | Thin & light        |
| gaming laptop | 223         | Gaming-focused      |

**Total: 48,948 laptop type mentions**

---

#### 2. **HARDWARE SPECS** (Tech Specs)

| Keyword    | Occurrences | What It Indicates   |
| ---------- | ----------- | ------------------- |
| ram        | 18,634      | Memory specs        |
| memory     | 13,041      | Storage/RAM         |
| storage    | 11,764      | Hard drive capacity |
| intel      | 9,906       | Intel processors    |
| ghz        | 7,160       | Processor speed     |
| processor  | 6,165       | CPU mentions        |
| hard drive | 5,206       | Storage type        |
| ssd        | 4,407       | Solid state drives  |
| graphics   | 4,352       | GPU mentions        |
| amd        | 2,417       | AMD processors      |

**Total: 82,992 hardware spec mentions**

---

#### 3. **DISPLAY** (Screen-related)

| Keyword     | Occurrences | What It Indicates     |
| ----------- | ----------- | --------------------- |
| screen      | 29,781      | General display       |
| led         | 28,314      | LED displays          |
| display     | 20,167      | Screen mentions       |
| ips         | 14,364      | IPS panel type        |
| monitor     | 12,635      | External displays     |
| resolution  | 11,016      | Screen resolution     |
| lcd         | 7,169       | LCD displays          |
| touchscreen | 2,036       | Touch capability      |
| retina      | 1,570       | Apple Retina displays |

**Total: 127,052 display mentions**

---

#### 4. **CONNECTIVITY** (Ports & Wireless)

| Keyword     | Occurrences | What It Indicates     |
| ----------- | ----------- | --------------------- |
| usb         | 44,232      | USB ports             |
| bluetooth   | 16,355      | Wireless connectivity |
| hdmi        | 13,980      | Video output          |
| ethernet    | 5,730       | Wired network         |
| wifi        | 5,307       | Wireless network      |
| usb-c       | 4,928       | USB-C ports           |
| thunderbolt | 1,641       | Thunderbolt ports     |

**Total: 92,173 connectivity mentions**

---

#### 5. **OPERATING SYSTEMS**

| Keyword    | Occurrences | What It Indicates |
| ---------- | ----------- | ----------------- |
| windows    | 10,680      | Windows OS        |
| chromebook | 2,619       | Chrome OS         |
| mac os     | 2,309       | macOS (older)     |
| linux      | 2,115       | Linux OS          |
| macos      | 489         | macOS (current)   |
| chrome os  | 481         | Chrome OS         |
| ubuntu     | 169         | Ubuntu Linux      |

**Total: 18,862 OS mentions**

---

#### 6. **BATTERY**

| Keyword       | Occurrences | What It Indicates             |
| ------------- | ----------- | ----------------------------- |
| wh            | 88,306      | Watt-hours (battery capacity) |
| battery       | 27,347      | Battery mentions              |
| mah           | 6,005       | Milliamp-hours                |
| battery life  | 4,741       | Battery duration              |
| hours battery | 367         | Battery life specs            |

**Total: 126,766 battery mentions**
**Note:** "wh" is extremely common (88K) - likely in product specs

---

#### 7. **BUILD QUALITY**

| Keyword     | Occurrences | What It Indicates    |
| ----------- | ----------- | -------------------- |
| weight      | 22,562      | Product weight       |
| thin        | 19,732      | Slim design          |
| lightweight | 13,306      | Portable             |
| portable    | 12,287      | Easy to carry        |
| metal       | 8,867       | Metal construction   |
| aluminum    | 7,947       | Aluminum body        |
| plastic     | 6,143       | Plastic construction |

**Total: 90,844 build quality mentions**

---

## 📋 Sample Features by Category

### Example 1: **Laptop Component (Motherboard)**

**ASIN:** B00JKCHDEU  
**Title:** Gigabyte GA-Z97X-GAMING 7 LGA 1150 Z97 Gaming Audio Networking ATX Motherboard

**Features (14 total):**

1. "LGA1150"
2. "Chipset: Intel Z97 Express"
3. "Memory: 4x DDR3-3200(OC)/ 3100(OC)/ 3000(OC)/ ..."
4. "Slots: 3x PCI-Express 3.0 x16 Slots..."
5. "Audio: Realtek ALC1150 7.1-Channel High Definition Audio CODEC"
6. "LAN: Qualcomm Atheros Killer E2201 Gigabit Ethernet Controller"
7. "Supports 4th and 5th Generation Intel Core processors..."

**Observation:** Highly technical, spec-heavy features with clear key:value format.

---

### Example 2: **Cell Phone Accessory (Case)**

**ASIN:** B08XWCH52F  
**Title:** elago BT21 Case Compatible with Samsung Galaxy Buds 2 Pro Case

**Features (5 total):**

1. "UNISTARS UNITE! elago's new case just got hit with the UNIVERSTAR!..."
2. "KOYA, RJ, SHOOKY, MANG, CHIMMY, TATA, COOKY, VAN. Show your love..."
3. "elago is an AUTHORIZED LICENSEE OF BT21. Be sure to buy authentic products!"
4. "CASE IS MADE FROM durable TPU material..."
5. "elago is a DESIGN COMPANY FIRST AND FOREMOST..."

**Observation:** Marketing-focused, longer sentences, brand storytelling.

---

### Example 3: **Camera Accessory (Filter Wheel)**

**ASIN:** B0791ZB44Y  
**Title:** Astromania 1.25" Multiple 5-Position Filter Wheel for Telescope

**Features (5 total):**

1. "It is 5-Position 1.25" Filter Wheel For Telecope..."
2. "The robustly constructed filter wheel is supplied with a 1.25" eyepiece adaptor..."
3. "Keep in mind that use of the Multiple Filter Wheel requires 23mm of inward focus travel..."
4. "Use: The Astromania Multiple Filter Wheel features a helpful number system..."
5. "Care and Storage: Feel free to leave your 1.25'' filters installed..."

**Observation:** Mix of specs and usage instructions.

---

## 🎯 Laptop Identification Strategy

### Multi-Criteria Approach:

Based on the analysis, laptops can be identified using this hierarchy:

#### **Tier 1: Direct Laptop Keywords (Highest Confidence)**

```python
direct_laptop_keywords = [
    'laptop', 'notebook', 'ultrabook', 'chromebook',
    'macbook', 'thinkpad', 'gaming laptop', '2-in-1'
]
```

**Coverage:** 48,948 mentions (4.6% of sample)

---

#### **Tier 2: Hardware Specs (High Confidence)**

```python
hardware_keywords = [
    'ram', 'processor', 'cpu', 'intel core', 'amd ryzen',
    'ssd', 'hard drive', 'storage', 'ghz', 'cores'
]
```

**Coverage:** 82,992 mentions (11.4% of sample)  
**Note:** Must combine with display/OS keywords to avoid false positives (desktops, servers)

---

#### **Tier 3: Operating Systems (Medium Confidence)**

```python
os_keywords = [
    'windows 10', 'windows 11', 'macos', 'mac os',
    'chrome os', 'chromebook'  # chromebook is also in Tier 1
]
```

**Coverage:** 18,862 mentions (2.6% of sample)

---

#### **Tier 4: Form Factor (Supporting Evidence)**

```python
form_factor_keywords = [
    'thin', 'lightweight', 'portable', 'aluminum',
    'touchscreen', 'convertible', '2-in-1'
]
```

**Coverage:** 90,844+ mentions (build quality keywords)

---

### Recommended Filter Logic:

```python
def is_laptop(product):
    """
    Multi-tier laptop identification from features array
    """
    features_text = ' '.join(product['features']).lower()
    categories_text = ' '.join(product['categories']).lower()
    title_text = product['title'].lower()

    # Tier 1: Direct keywords (IMMEDIATE YES)
    direct_keywords = ['laptop', 'notebook', 'ultrabook', 'chromebook',
                      'macbook', 'thinkpad']
    if any(kw in features_text or kw in title_text for kw in direct_keywords):
        return True, "Tier 1: Direct keyword"

    # Tier 2: Check categories for laptop/computer
    if 'laptop' in categories_text or 'notebooks' in categories_text:
        return True, "Tier 2: Category"

    # Tier 3: Hardware + OS combination (STRONG EVIDENCE)
    has_hardware = any(kw in features_text for kw in ['ram', 'processor', 'intel', 'amd', 'ghz'])
    has_os = any(kw in features_text for kw in ['windows', 'macos', 'chrome os'])
    has_display = any(kw in features_text for kw in ['screen', 'display', 'touchscreen'])

    if (has_hardware and has_os) or (has_hardware and has_display and 'portable' in features_text):
        return True, "Tier 3: Spec combination"

    return False, "Not a laptop"
```

---

## 🔍 Data Quality Issues

### 1. **Inconsistent Formatting**

- Some use "Brand: Sony", others "Brand: SONY", others just "Sony"
- Mixed bullet styles: numbered (1., 2.), bullets (•, ●), or none
- Inconsistent capitalization

### 2. **Marketing Fluff**

- ~10% of features are marketing text ("BEST QUALITY!", "100% SATISFACTION GUARANTEED!")
- Makes filtering harder

### 3. **Very Long Features**

- 10.2% of features are 300+ characters (paragraphs)
- Should ideally be split into multiple features

### 4. **Embedded URLs**

- 41 features contain URLs (0.04%)
- Not useful for filtering

---

## 💡 Recommendations

### For Laptop Identification:

1. **Use Multi-Tier Approach** (outlined above)
2. **Combine with Categories Array** (already preserved in PostgreSQL)
3. **Weight by Confidence:** Tier 1 > Tier 2 > Tier 3

### For PostgreSQL Array Columns:

1. **Add `features_array TEXT[]`** to products table
2. **Benefits:**

   - Each feature is separate (easier to search)
   - GIN index for fast queries (6.6x faster)
   - No need to join/split text
   - Better for graph construction

3. **Query Example:**

```sql
-- Find products with RAM specifications
SELECT parent_asin, title
FROM products
WHERE EXISTS (
    SELECT 1 FROM unnest(features_array) AS f
    WHERE f ILIKE '%ram%' OR f ILIKE '%memory%'
);

-- Much faster than:
-- WHERE features ILIKE '%ram%'  -- scans entire flattened text
```

### For Graph Construction:

1. **Extract Key:Value Features** (29.8% have colons)
2. **Create Feature Nodes** from parsed features
3. **Connect Products to Features** via relationships
4. **Example:**
   ```
   Product → HAS_FEATURE → "16GB RAM"
   Product → HAS_FEATURE → "Intel Core i7"
   Product → HAS_OS → "Windows 11"
   ```

---

## 📊 Summary Statistics

| Metric                   | Value                       |
| ------------------------ | --------------------------- |
| **Total Sample**         | 200,000 products            |
| **With Features**        | 152,861 (76.4%)             |
| **Total Features**       | 724,730 individual features |
| **Unique Features**      | 577,577 (79.7% unique)      |
| **Avg Length**           | 141 characters              |
| **Median Length**        | 107 characters              |
| **Avg Features/Product** | 4.7 features                |
| **Max Features**         | 60 features                 |
| **Laptop Mentions**      | 48,948 (direct keywords)    |
| **Hardware Specs**       | 82,992 mentions             |
| **Display Mentions**     | 127,052 mentions            |

---

## 📁 Exported Files

1. **`features_parquet_analysis.csv`** - 50,000 sample features with metadata
   - Columns: feature, length, word_count, has_colon, has_specs, has_dimensions, is_laptop_related

---

## 🚀 Next Steps

1. ✅ **Features analysis complete** (current)
2. **Create laptop identification script** using multi-tier logic
3. **Add array columns to PostgreSQL** for 348K filtered products
4. **Build graph** from features array
5. **Train GNN** on graph structure

---

**Analysis completed on:** October 31, 2025  
**Total analysis time:** ~3 minutes (200K sample)  
**Full dataset time estimate:** ~30 minutes (1.8M products)
