# Parquet Metadata Field Summary

**Source:** Hugging Face Amazon-Reviews-2023 Electronics Metadata (10 parquet files)  
**Total Products:** 1,610,012 electronics items  
**Sample Analysis:** Based on `full-00000-of-00010.parquet` (161,002 records)

---

## Field Summary Table

| #   | Field Name        | Completeness | Data Type     | Description                                   |
| --- | ----------------- | ------------ | ------------- | --------------------------------------------- |
| 1   | `title`           | 100.00%      | string        | Product title/name (1-1605 chars, avg: 126)   |
| 2   | `average_rating`  | 100.00%      | float         | Customer rating (1.0-5.0, mean: 4.06)         |
| 3   | `rating_number`   | 100.00%      | integer       | Number of reviews (1-507,202, median: 19)     |
| 4   | `features`        | 100.00%      | array[string] | Product features/highlights (can be empty)    |
| 5   | `description`     | 100.00%      | array[string] | Product description (can be empty)            |
| 6   | `price`           | 100.00%      | string/null   | Price in USD (9,089 unique values)            |
| 7   | `images`          | 100.00%      | object        | Image URLs (hi_res, large, thumb, variant)    |
| 8   | `videos`          | 100.00%      | object        | Video metadata (title, url, user_id)          |
| 9   | `categories`      | 100.00%      | array[string] | Category hierarchy path                       |
| 10  | `details`         | 100.00%      | object        | Product specifications (highly variable)      |
| 11  | `parent_asin`     | 100.00%      | string        | **Primary product ID (10 chars, all unique)** |
| 12  | `store`           | 99.45%       | string        | Store/brand name (40,997 unique stores)       |
| 13  | `main_category`   | 98.98%       | string        | Top-level category (38 unique, 4-28 chars)    |
| 14  | `subtitle`        | 0.04%        | string        | Subtitle/edition info (book products only)    |
| 15  | `author`          | 0.02%        | object        | Author information (book products only)       |
| 16  | `bought_together` | 0.00%        | null          | **EMPTY - Not available in this dataset**     |

---

## Detailed Field Analysis

### 1. **title** ✅ CORE FIELD

- **Completeness:** 100% (161,002 records)
- **Type:** String
- **Length:** 1-1,605 characters (avg: 126.1)
- **Unique:** 159,816 unique titles
- **Usage:** Primary text for semantic embeddings, display name
- **Examples:**
  - "FS-1051 FATSHARK TELEPORTER V3 HEADSET"
  - "Digi-Tatoo Decal Skin Compatible With MacBook Pro 13 inch..."

---

### 2. **average_rating** ✅ CORE FIELD

- **Completeness:** 100%
- **Type:** Float
- **Range:** 1.0 to 5.0
- **Statistics:**
  - Mean: 4.06
  - Median: 4.20
- **Usage:** Quality filtering, ranking, recommendation scoring

---

### 3. **rating_number** ✅ CORE FIELD

- **Completeness:** 100%
- **Type:** Integer
- **Range:** 1 to 507,202 reviews
- **Statistics:**
  - Mean: 405.56
  - Median: 19
- **Usage:** Popularity indicator, confidence weighting

---

### 4. **features** ✅ CORE FIELD

- **Completeness:** 100%
- **Type:** Array of strings
- **Content:** Product highlights, key specifications, warnings
- **Usage:**
  - Semantic embeddings (combined with title + description)
  - Feature extraction for filtering
  - Display in product cards
- **Notes:** Can be empty array `[]`
- **Examples:**
  ```
  ["WARNING: Please IDENTIFY MODEL NUMBER on the bottom...",
   "Extra Care Yet Not Bulky. Our skin is capable of...",
   "Elegant Style. Our stylish design..."]
  ```

---

### 5. **description** ✅ CORE FIELD

- **Completeness:** 100%
- **Type:** Array of strings
- **Content:** Detailed product description paragraphs
- **Usage:**
  - Primary text for semantic embeddings
  - Context for RAG generation
  - Product detail display
- **Notes:** Can be empty array `[]`

---

### 6. **price**

- **Completeness:** 100% (but many are `null`)
- **Type:** String or null
- **Values:** 9,089 unique price points
- **Length:** 1-10 characters (avg: 4.3)
- **Usage:**
  - Price filtering in queries
  - Budget-based recommendations
  - Display information
- **Notes:** Stored as string, needs conversion to float

---

### 7. **images** ✅ IMPORTANT

- **Completeness:** 100%
- **Type:** Object with arrays
- **Structure:**
  ```json
  {
    "hi_res": array of URLs or null,
    "large": array of URLs,
    "thumb": array of thumbnail URLs,
    "variant": array of variant labels
  }
  ```
- **Usage:**
  - Product display
  - Visual recommendations
  - Multimodal embeddings (future)

---

### 8. **videos**

- **Completeness:** 100%
- **Type:** Object with arrays
- **Structure:**
  ```json
  {
    "title": array of video titles,
    "url": array of video URLs,
    "user_id": array of uploader IDs
  }
  ```
- **Usage:** Product demonstration videos, mostly empty
- **Notes:** Most products have empty arrays

---

### 9. **categories** ✅ CORE FIELD

- **Completeness:** 100%
- **Type:** Array of strings (hierarchical path)
- **Structure:** `["Electronics", "Computers & Accessories", "Laptop Accessories", "Skins & Decals"]`
- **Usage:**
  - Category-based filtering
  - Hierarchical graph relationships in Neo4j
  - Multi-level recommendation (category → subcategory → product)
  - Semantic clustering
- **Examples:**
  - `["Electronics", "Television & Video", "Video Glasses"]`
  - `["Electronics", "Computers & Accessories", "Laptop Accessories"]`

---

### 10. **details** ✅ IMPORTANT

- **Completeness:** 100%
- **Type:** Object/Dictionary (highly variable keys)
- **Length:** 2-6,338 characters (avg: 438.9)
- **Unique:** 159,952 unique detail objects
- **Content:** Product specifications, technical details
- **Common Keys:**
  - `"Date First Available"`
  - `"Manufacturer"`
  - `"Product Dimensions"`
  - `"Item Weight"`
  - `"Item model number"`
  - `"Brand"`
  - `"Color"`
  - `"Material"`
  - Category-specific fields (varies widely)
- **Usage:**
  - Technical specification search
  - Attribute-based filtering
  - Structured data extraction

---

### 11. **parent_asin** ✅ PRIMARY KEY

- **Completeness:** 100%
- **Type:** String (exactly 10 characters)
- **Format:** Alphanumeric Amazon Standard Identification Number
- **Unique:** 161,002 / 161,002 (100% unique)
- **Usage:**
  - **Primary key for products table**
  - Join key with reviews table
  - Node ID in Neo4j graph
  - Product lookup and deduplication
- **Examples:** `B00MCW7G9M`, `B00YT6XQSE`, `B07SM135LS`

---

### 12. **store** ✅ USEFUL

- **Completeness:** 99.45% (160,112 records)
- **Type:** String
- **Length:** 0-425 characters (avg: 7.9)
- **Unique:** 40,997 unique stores/brands
- **Usage:**
  - Brand-based filtering
  - Store-level analytics
  - Brand relationships in graph
- **Examples:** "Fat Shark", "SIIG", "Digi-Tatoo"

---

### 13. **main_category** ✅ USEFUL

- **Completeness:** 98.98% (159,360 records)
- **Type:** String
- **Length:** 4-28 characters (avg: 14.8)
- **Unique:** 38 unique top-level categories
- **Usage:**
  - High-level filtering
  - Category distribution analysis
- **Examples:** "All Electronics", "Computers", "AMAZON FASHION"
- **Note:** Less granular than `categories` field

---

### 14. **subtitle** ⚠️ SPARSE

- **Completeness:** 0.04% (62 records only)
- **Type:** String
- **Length:** 5-42 characters (avg: 24.6)
- **Unique:** 56 unique subtitles
- **Content:** Edition info, binding type, publication date
- **Usage:** Minimal - mostly for book products
- **Examples:**
  - "3rd Edition"
  - "Paperback – October 1, 2017"
  - "Spiral-bound – December 15, 2008"

---

### 15. **author** ⚠️ SPARSE

- **Completeness:** 0.02% (37 records only)
- **Type:** Object
- **Structure:**
  ```json
  {
    "avatar": "URL to author image",
    "name": "Author name",
    "about": ["Bio paragraph 1", "Bio paragraph 2", ...]
  }
  ```
- **Length:** 190-3,583 characters (avg: 952.3)
- **Unique:** 36 unique authors
- **Usage:** Minimal - only for books in electronics category
- **Examples:** "John Wooden", "Romina Garber", "Brad Marlowe"

---

### 16. **bought_together** ❌ NOT AVAILABLE

- **Completeness:** 0% (completely empty)
- **Type:** null
- **Status:** Not available in this dataset version
- **Impact:** Cannot use pre-computed "frequently bought together" relationships
- **Alternative:** Can compute co-purchase patterns from review data and user behavior

---

## Key Insights for Hybrid RAG System

### Core Fields for PostgreSQL (Semantic Search)

1. **`parent_asin`** - Primary key
2. **`title`** - Main semantic content
3. **`description`** - Detailed semantic content
4. **`features`** - Key highlights
5. **`average_rating`** - Quality filter
6. **`rating_number`** - Popularity/confidence
7. **`price`** - Budget filtering
8. **`categories`** - Hierarchical filtering

### Core Fields for Neo4j (Graph Structure)

1. **`parent_asin`** - Node ID
2. **`categories`** - Category hierarchy edges
3. **`store`** - Brand relationships
4. **Review co-occurrence** - (from review data, not metadata)

### Fields for Display/UX

1. **`title`**, **`description`**, **`features`**
2. **`images`** (hi_res, large, thumb)
3. **`price`**, **`store`**
4. **`average_rating`**, **`rating_number`**
5. **`details`** (for specifications)

### Unusable/Sparse Fields

- **`bought_together`** - 0% complete (not available)
- **`author`** - 0.02% complete (ignore)
- **`subtitle`** - 0.04% complete (ignore)

---

## Data Quality Notes

✅ **Excellent Completeness:** 11 of 16 fields are 100% complete  
✅ **Unique Primary Key:** `parent_asin` is 100% unique  
⚠️ **Price Data:** Present but many nulls, needs cleaning  
⚠️ **Bought Together:** Not available, need alternative approach  
⚠️ **Nested Structures:** Images, videos, details require JSON parsing

---

## Recommended Schema for PostgreSQL

```sql
CREATE TABLE products (
    parent_asin         VARCHAR(10) PRIMARY KEY,
    title               TEXT NOT NULL,
    description         TEXT,  -- joined array
    features            TEXT,  -- joined array
    average_rating      REAL,
    rating_number       INTEGER,
    price               REAL,  -- converted from string
    main_category       VARCHAR(50),
    categories          TEXT[],  -- PostgreSQL array
    store               VARCHAR(255),
    details             JSONB,  -- flexible structured data
    images              JSONB,  -- store full image object
    -- Embeddings
    blair_embedding     VECTOR(768),
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_products_rating ON products(average_rating);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_store ON products(store);
CREATE INDEX idx_products_categories ON products USING GIN(categories);
CREATE INDEX idx_products_embedding ON products USING ivfflat(blair_embedding vector_cosine_ops);
```

---

**Generated:** Based on analysis of 161,002 products from `full-00000-of-00010.parquet`  
**Total Dataset:** 1,610,012 products across 10 parquet files
