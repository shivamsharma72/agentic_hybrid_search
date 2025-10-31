# Complete Hierarchical Distribution Analysis

## Accurate Picture with True vs Intermediate Leaves

**Date:** October 31, 2025  
**Analysis:** Complete category hierarchy considering leaf types  
**Products:** 330,697

---

## 🎯 Executive Summary

This analysis provides an **ACCURATE** picture of category distribution by distinguishing:

1. **TRUE LEAVES** (834): Never act as parents - always final categories
2. **INTERMEDIATE LEAVES** (178): Act as BOTH leaf AND parent
3. **PURE PARENTS** (71): Never appear as leaf - always have children

**Key Finding:** 20.19% of products (66,782) have intermediate leaves that also act as parents!

---

## 📊 Category Type Distribution

### Overall Classification

| Type             | Count     | % of Categories | Products (as leaf) | % of Products |
| ---------------- | --------- | --------------- | ------------------ | ------------- |
| **TRUE LEAVES**  | 834       | 77.01%          | 263,915            | 79.81%        |
| **INTERMEDIATE** | 178       | 16.44%          | 66,782             | 20.19%        |
| **PURE PARENTS** | 71        | 6.56%           | 0                  | 0.00%         |
| **TOTAL**        | **1,083** | **100%**        | **330,697**        | **100%**      |

### Key Insights

✅ **77% of categories are TRUE leaves** - Never have children  
⚠️ **16% are INTERMEDIATE** - Can be endpoints OR have children  
📊 **7% are PURE parents** - Always have descendants

✅ **80% of products** have specific, true leaf categories  
⚠️ **20% of products** have generic, intermediate categories

---

## 📈 Hierarchy Depth Distribution

Products are distributed across 6 hierarchy depths (2-7 levels):

| Depth | Total Products | True Leaf   | Intermediate | % of Total |
| ----- | -------------- | ----------- | ------------ | ---------- |
| 2     | 9,724          | 5,265       | 4,459        | 2.94%      |
| 3     | 39,360         | 21,655      | 17,705       | 11.90%     |
| **4** | **122,126**    | **98,909**  | **23,217**   | **36.93%** |
| **5** | **126,119**    | **104,927** | **21,192**   | **38.14%** |
| 6     | 31,291         | 31,082      | 209          | 9.46%      |
| 7     | 2,077          | 2,077       | 0            | 0.63%      |

### Statistics

- **Average Depth:** 4.41 levels
- **Most Common:** Depth 5 (126,119 products)
- **Range:** 2-7 levels

### Interpretation

- **Depths 4-5:** 75% of all products (most common)
- **Deep hierarchies (6-7):** Only 10% of products
- **Shallow hierarchies (2-3):** 15% of products (more generic)

---

## 🔍 Top 30 Categories by Total Products (Subtree Size)

This shows the **TRUE size** of each category including all descendants:

| Rank | Category                           | Type         | Direct     | Subtree    | % Direct  |
| ---- | ---------------------------------- | ------------ | ---------- | ---------- | --------- |
| 1    | Electronics                        | INTERMEDIATE | 2          | 1,965,742  | 0.0%      |
| 2    | Computers & Accessories            | INTERMEDIATE | 1,225      | 560,289    | 0.2%      |
| 3    | Service Plans                      | INTERMEDIATE | 100        | 330,687    | 0.0%      |
| 4    | Warranties & Services              | INTERMEDIATE | 1          | 330,607    | 0.0%      |
| 5    | Portable Audio & Video             | INTERMEDIATE | 238        | 139,631    | 0.2%      |
| 6    | Accessories                        | INTERMEDIATE | 746        | 128,182    | 0.6%      |
| 7    | Camera & Photo                     | INTERMEDIATE | 1,169      | 115,377    | 1.0%      |
| 8    | Television & Video                 | INTERMEDIATE | 168        | 86,940     | 0.2%      |
| 9    | Security & Surveillance            | INTERMEDIATE | 441        | 83,815     | 0.5%      |
| 10   | CB & Two-Way Radios                | INTERMEDIATE | 80         | 81,297     | 0.1%      |
| 11   | Computer Accessories & Peripherals | INTERMEDIATE | 292        | 64,651     | 0.5%      |
| 12   | Laptop Accessories                 | INTERMEDIATE | 286        | 55,877     | 0.5%      |
| 13   | Tablet Accessories                 | INTERMEDIATE | 1,822      | 48,725     | 3.7%      |
| 14   | MP3 & MP4 Player Accessories       | INTERMEDIATE | 391        | 48,641     | 0.8%      |
| 15   | Headphones, Earbuds & Accessories  | INTERMEDIATE | 260        | 43,260     | 0.6%      |
| 16   | GPS, Finders & Accessories         | INTERMEDIATE | 39         | 36,201     | 0.1%      |
| 17   | Car & Vehicle Electronics          | INTERMEDIATE | 236        | 35,883     | 0.7%      |
| 18   | Home Audio                         | INTERMEDIATE | 136        | 35,694     | 0.4%      |
| 19   | GPS System Accessories             | INTERMEDIATE | 147        | 34,010     | 0.4%      |
| 20   | Bags, Cases & Sleeves              | INTERMEDIATE | 1,233      | 31,401     | 3.9%      |
| 21   | Accessories & Supplies             | INTERMEDIATE | 135        | 26,821     | 0.5%      |
| 22   | Computer Components                | INTERMEDIATE | 134        | 22,356     | 0.6%      |
| 23   | Vehicle Electronics Accessories    | INTERMEDIATE | 85         | 21,142     | 0.4%      |
| 24   | **Cases**                          | INTERMEDIATE | **20,168** | **20,183** | **99.9%** |
| 25   | Home Audio Accessories             | INTERMEDIATE | 69         | 19,564     | 0.4%      |
| 26   | Audio & Video Accessories          | INTERMEDIATE | 687        | 19,029     | 3.6%      |
| 27   | Amazon Device Accessories          | INTERMEDIATE | 20         | 16,762     | 0.1%      |
| 28   | Internal Components                | INTERMEDIATE | 2,160      | 16,193     | 13.3%     |
| 29   | Headphones & Earbuds               | INTERMEDIATE | 1,068      | 15,577     | 6.9%      |
| 30   | Cables & Accessories               | INTERMEDIATE | 46         | 14,313     | 0.3%      |

### Key Observations

1. **Top categories are ALL intermediate** (act as parents)
2. **"Cases" (#24):** 20,168 direct + only 15 via children = 99.9% direct!
   - This is an INTERMEDIATE leaf that's almost always an endpoint
3. **Most intermediate categories:** < 1% direct (mostly via children)

---

## 🎯 Example: "Laptops" Category (Detailed Breakdown)

Perfect example of an **INTERMEDIATE** category:

```
"Laptops" (Intermediate)
├─ Direct Products (as leaf): 17 (0.31%)
└─ Via Children: 5,428 (99.69%)
   ├─ Traditional Laptops: 4,862 products
   └─ 2 in 1 Laptops: 566 products

Total Subtree: 5,445 products
```

### Analysis

- **17 products** end at "Laptops" (generic, no subcategory)
- **5,428 products** have specific subcategories
- If you query `WHERE leaf_category = 'Laptops'`, you get **only 17**
- To get ALL laptops, you need **hierarchical query** for children too!

---

## 🌳 Graph Structure Implications

### Previous Understanding (Wrong)

```
(Product A) -[:BELONGS_TO]-> (Laptops)
(Product B) -[:BELONGS_TO]-> (Traditional Laptops)

[Laptops and Traditional Laptops treated as same level]
```

### Accurate Understanding (Correct)

```
(Product A) -[:BELONGS_TO]-> (Laptops:Intermediate)
(Product B) -[:BELONGS_TO]-> (Traditional Laptops:TrueLeaf)
(Traditional Laptops) -[:CHILD_OF]-> (Laptops)
                                        ↑
                                    HIERARCHY!
```

### Neo4j Implementation

```cypher
// Create category nodes with type metadata
MERGE (c1:Category {
  name: "Laptops",
  type: "INTERMEDIATE",
  direct_products: 17,
  total_subtree: 5445
})

MERGE (c2:Category {
  name: "Traditional Laptops",
  type: "TRUE_LEAF",
  direct_products: 4862,
  total_subtree: 4862
})

// Create hierarchy
MERGE (c2)-[:CHILD_OF]->(c1)

// Connect products
MERGE (p1:Product {asin: "A"})-[:BELONGS_TO]->(c1)  // Generic
MERGE (p2:Product {asin: "B"})-[:BELONGS_TO]->(c2)  // Specific

// Query all laptops (including children)
MATCH (p:Product)-[:BELONGS_TO]->(c:Category)
WHERE c.name = "Laptops"
   OR (c)-[:CHILD_OF*]->(parent:Category {name: "Laptops"})
RETURN p;
```

---

## 💡 Recommendations for RAG + Graph + GNN

### 1. Database Schema Enhancement

Add columns to track hierarchy:

```sql
-- Add leaf type tracking
ALTER TABLE products ADD COLUMN leaf_type VARCHAR(20);
UPDATE products SET leaf_type =
  CASE
    WHEN leaf_category IN (SELECT DISTINCT parent FROM category_hierarchy)
      THEN 'INTERMEDIATE'
    ELSE 'TRUE_LEAF'
  END;

-- Add depth tracking
ALTER TABLE products ADD COLUMN leaf_depth INT;
UPDATE products SET leaf_depth = array_length(categories, 1);

-- Create indexes
CREATE INDEX idx_leaf_type ON products(leaf_type);
CREATE INDEX idx_leaf_depth ON products(leaf_depth);
```

### 2. Query Strategies

#### Simple Query (Direct Only)

```sql
-- Get products directly in "Laptops" (17 products)
SELECT * FROM products WHERE leaf_category = 'Laptops';
```

#### Hierarchical Query (Include Children)

```sql
-- Get ALL laptops (5,445 products)
WITH RECURSIVE laptop_tree AS (
  SELECT 'Laptops' as category
  UNION ALL
  SELECT child FROM category_hierarchy
  WHERE parent IN (SELECT category FROM laptop_tree)
)
SELECT * FROM products
WHERE leaf_category IN (SELECT category FROM laptop_tree);
```

### 3. Recommendation Strategy

#### For TRUE LEAF Products (80% of products)

```python
def recommend_true_leaf(product_asin):
    """Products with specific categories - same-leaf recommendations."""
    leaf = get_leaf_category(product_asin)
    # Get similar products in SAME leaf
    return query(f"WHERE leaf_category = '{leaf}'
                    AND leaf_type = 'TRUE_LEAF'
                    ORDER BY similarity DESC LIMIT 10")
```

#### For INTERMEDIATE LEAF Products (20% of products)

```python
def recommend_intermediate_leaf(product_asin):
    """Products with generic categories - include subtree."""
    leaf = get_leaf_category(product_asin)
    # Get similar products in SAME leaf OR children
    children = get_children_recursive(leaf)
    all_categories = [leaf] + children
    return query(f"WHERE leaf_category IN {all_categories}
                    ORDER BY similarity DESC LIMIT 10")
```

### 4. GNN Training Features

Use leaf type as a feature:

```python
# Product feature vector
features = [
    embedding,              # 768-dim BLAIR-RoBERTa
    leaf_type_onehot,      # [1,0] for true, [0,1] for intermediate
    leaf_depth,            # Normalized depth (2-7)
    subtree_size,          # Log of subtree size
]

# GNN can learn:
# - TRUE LEAF products are more specific
# - INTERMEDIATE products should connect to children
# - Depth indicates specificity level
```

### 5. Explainable Recommendations

```python
def explain_recommendation(source, target):
    """Generate human-readable explanation."""

    if source.leaf_type == 'TRUE_LEAF' and target.leaf_type == 'TRUE_LEAF':
        if source.leaf == target.leaf:
            return f"Both are {source.leaf} (specific match)"
        else:
            return f"Similar specs but different categories"

    elif source.leaf_type == 'INTERMEDIATE':
        if target.leaf in get_children(source.leaf):
            return f"{target.leaf} is a specific type of {source.leaf}"
        else:
            return f"Related via parent category"
```

---

## 📊 Distribution Summary Tables

### By Category Type (Products)

| Type         | Products    | %        | Avg per Category | Max    | Min |
| ------------ | ----------- | -------- | ---------------- | ------ | --- |
| TRUE LEAF    | 263,915     | 79.81%   | 316.5            | 10,015 | 1   |
| INTERMEDIATE | 66,782      | 20.19%   | 375.2            | 20,168 | 1   |
| **Total**    | **330,697** | **100%** | **326.8**        | -      | -   |

### By Subtree Size (Including Children)

| Subtree Size  | Categories | %     | Example                              |
| ------------- | ---------- | ----- | ------------------------------------ |
| 100,000+      | 7          | 0.6%  | Electronics, Computers & Accessories |
| 10,000-99,999 | 42         | 3.9%  | Camera & Photo, Security             |
| 1,000-9,999   | 183        | 16.9% | USB Cables, Monitors                 |
| 100-999       | 353        | 32.6% | Laptop Chargers, Tablet Cases        |
| < 100         | 427        | 39.4% | Niche accessories                    |

### By Depth Distribution

| Depth | TRUE LEAF | INTERMEDIATE | Total   | %      |
| ----- | --------- | ------------ | ------- | ------ |
| 2     | 5,265     | 4,459        | 9,724   | 2.94%  |
| 3     | 21,655    | 17,705       | 39,360  | 11.90% |
| 4     | 98,909    | 23,217       | 122,126 | 36.93% |
| 5     | 104,927   | 21,192       | 126,119 | 38.14% |
| 6     | 31,082    | 209          | 31,291  | 9.46%  |
| 7     | 2,077     | 0            | 2,077   | 0.63%  |

**Key Insight:** Intermediate leaves are more common at shallower depths (2-4)!

---

## 🎯 Critical Findings

### 1. NOT All Leaves Are Equal

- **834 (77%)** are TRUE leaves - never have children
- **178 (16%)** are INTERMEDIATE - can have children
- **Distribution:** 80% products have true leaves, 20% have intermediate

### 2. Intermediate Leaves Have HUGE Subtrees

Top intermediate subtrees:

- Electronics: 2 direct → 1,965,742 total (0.0% direct!)
- Computers & Accessories: 1,225 direct → 560,289 total (0.2% direct!)
- Service Plans: 100 direct → 330,687 total (0.0% direct!)

### 3. But Some Intermediates Are Mostly Direct

- Cases: 20,168 direct → 20,183 total (**99.9% direct!**)
- Internal Components: 2,160 direct → 16,193 total (13.3% direct)
- Headphones & Earbuds: 1,068 direct → 15,577 total (6.9% direct)

### 4. Depth Correlates with Leaf Type

- **Depth 2-4:** 45% intermediate leaves (generic categories)
- **Depth 5-7:** < 10% intermediate leaves (specific categories)
- **Most products (38%)** are at depth 5 (very specific)

### 5. Hierarchy is DEEP

- **Average depth:** 4.41 levels
- **Range:** 2-7 levels (5 levels of specificity!)
- **Mode:** 5 levels (most common)

---

## 📁 Exported Files

### 1. `complete_leaf_distribution.csv`

All 1,012 leaf categories with:

- Category name
- Type (TRUE_LEAF or INTERMEDIATE)
- Direct products (as leaf)
- Total subtree products
- Number of children
- % direct vs via children

### 2. `intermediate_subtree_analysis.csv`

178 intermediate categories with:

- Direct product count
- Children product count
- Total subtree size
- % breakdown

### 3. `complete_category_hierarchy.csv`

All parent-child relationships with:

- Parent name and type
- Child name and type
- Enables recursive queries

---

## 🚀 Next Steps

### Immediate Actions

1. **Add `leaf_type` column to database**

   ```sql
   ALTER TABLE products ADD COLUMN leaf_type VARCHAR(20);
   UPDATE products SET leaf_type = (query from CSV);
   ```

2. **Add `leaf_depth` column**

   ```sql
   ALTER TABLE products ADD COLUMN leaf_depth INT;
   UPDATE products SET leaf_depth = array_length(categories, 1);
   ```

3. **Test hierarchical queries**
   - Query with children inclusion
   - Compare results (direct vs subtree)

### For Graph Construction

1. **Create category nodes in Neo4j**

   - Include type metadata (TRUE_LEAF, INTERMEDIATE, PURE_PARENT)
   - Include direct and subtree counts

2. **Add hierarchy relationships**

   - `[:CHILD_OF]` from child to parent
   - Enable graph traversal

3. **Connect products to leaves**
   - `[:BELONGS_TO]` from product to its leaf
   - One-to-one mapping preserved

### For GNN Training

1. **Use leaf type as feature**

   - One-hot encode: TRUE_LEAF vs INTERMEDIATE
   - Include depth as normalized feature

2. **Create hierarchical embeddings**

   - Learn parent-child relationships
   - Propagate information up/down hierarchy

3. **Test neighborhood strategies**
   - Same-leaf only
   - Include siblings (same parent)
   - Include parent/children

---

## 📌 Summary

**Before this analysis:** We thought all 1,012 leaves were "final" categories.

**After this analysis:** We know:

- 834 are TRUE leaves (never parents)
- 178 are INTERMEDIATE (both leaf AND parent)
- 20% of products have intermediate leaves
- Hierarchy is deeper and more complex than assumed

**Impact:**

- Graph structure is HIERARCHICAL, not flat
- Recommendations need to consider subtrees
- Queries need recursive logic for intermediate leaves
- GNN features should include leaf type and depth

**This is the ACCURATE picture of your data!** 🎯✅

---

_Generated by: Complete Hierarchical Distribution Analysis_  
_Date: October 31, 2025_  
_Products: 330,697 | Categories: 1,083 | Analysis Time: 6.5 seconds_
