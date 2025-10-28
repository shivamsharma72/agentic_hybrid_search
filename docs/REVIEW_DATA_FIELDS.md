# Review Data Field Structure Documentation

**File:** `Electronics.jsonl`  
**Description:** Complete field structure for Amazon customer review data

---

## Table of Contents

1. [Overview](#overview)
2. [Top-Level Fields](#top-level-fields)
3. [Nested Structures](#nested-structures)
4. [Field Details](#field-details)
5. [Data Types](#data-types)
6. [Usage Notes](#usage-notes)

---

## Overview

The review data contains **10 top-level fields** with a simple, flat structure compared to product metadata. Each record represents one customer review with associated metadata including rating, text, images, and verification status.

**Total Fields:**

- 10 top-level fields
- 4 sub-fields in images[] array (when present)
- Simple, user-generated content structure

---

## Top-Level Fields

### 1. rating

- **Type:** `float`
- **Description:** Star rating given by the reviewer
- **Range:** 1.0 to 5.0
- **Example:** `3.0`, `4.5`, `5.0`
- **Notes:**
  - Represents customer satisfaction level
  - Used for calculating average_rating in product metadata
  - Always present in review records

### 2. title

- **Type:** `string`
- **Description:** Review headline or title
- **Example:**
  - `"Smells like gasoline! Going back!"`
  - `"Great product!"`
  - `"Works as expected"`
- **Notes:**
  - Brief summary of review sentiment
  - Often indicates main point of review
  - Can be short or descriptive

### 3. text

- **Type:** `string`
- **Description:** Full review text content written by the customer
- **Example:**
  ```
  "First & most offensive: they reek of gasoline so if you are
  sensitive/allergic to petroleum products, stay away. Second:
  they are not soft at all..."
  ```
- **Notes:**
  - Main content of the review
  - Can be short or very detailed
  - Contains customer's detailed experience and opinions
  - May include product usage tips, complaints, or praise

### 4. images

- **Type:** `array of objects`
- **Description:** User-uploaded photos from their product experience
- **Structure:** See [Images Array Structure](#images-array-structure)
- **Notes:**
  - Can be empty array `[]` if no images uploaded
  - Provides visual evidence of product condition/usage
  - Each image has multiple size variants

### 5. asin

- **Type:** `string`
- **Description:** Amazon Standard Identification Number for the product being reviewed
- **Format:** Alphanumeric string (typically 10 characters)
- **Example:** `"B083NRGZMM"`, `"B00MCW7G9M"`
- **Notes:**
  - Primary key for linking reviews to products
  - Links to product records in meta_Electronics.jsonl
  - Unique identifier for each product

### 6. parent_asin

- **Type:** `string`
- **Description:** Parent product ASIN for product variants
- **Format:** Alphanumeric string (typically 10 characters)
- **Example:** `"B083NRGZMM"`, `"B07SM135LS"`
- **Notes:**
  - Links product variants to parent product
  - May be same as `asin` for non-variant products
  - Used for grouping reviews across product variants

### 7. user_id

- **Type:** `string`
- **Description:** Unique identifier for the reviewer
- **Format:** Long alphanumeric string
- **Example:** `"AFKZENTNBQ7A7V7UXW5JJI6UGRYQ"`
- **Notes:**
  - Anonymized user identifier
  - Can be used to track reviewer behavior
  - Useful for identifying prolific reviewers
  - Enables reviewer reputation analysis

### 8. timestamp

- **Type:** `integer`
- **Description:** Unix epoch timestamp when review was posted
- **Format:** Milliseconds since January 1, 1970
- **Example:** `1658185117948` (represents July 18, 2022)
- **Notes:**
  - Enables temporal analysis of reviews
  - Can be converted to human-readable date
  - Useful for tracking review trends over time
  - Important for time-series analysis

**Conversion Example:**

```python
import datetime
timestamp = 1658185117948
date = datetime.datetime.fromtimestamp(timestamp / 1000)
# Output: 2022-07-18 20:51:57
```

### 9. helpful_vote

- **Type:** `integer`
- **Description:** Number of "helpful" votes the review received from other users
- **Range:** 0 to potentially thousands
- **Example:** `0`, `5`, `42`, `156`
- **Notes:**
  - Indicates review quality/usefulness
  - Social validation metric
  - Higher values suggest more valuable reviews
  - Can be used to filter/rank reviews
  - 0 means no users found it helpful (or no votes yet)

### 10. verified_purchase

- **Type:** `boolean`
- **Description:** Whether Amazon verified that the reviewer purchased the product
- **Values:** `true` or `false`
- **Example:** `true`, `false`
- **Notes:**
  - `true` = Amazon confirmed the purchase
  - `false` = Review not from verified purchase
  - Important for filtering authentic reviews
  - Verified reviews generally more trustworthy
  - Used to combat fake/incentivized reviews

---

## Nested Structures

### Images Array Structure

Each image object in the `images[]` array contains user-uploaded photos from their review. These are different from product images in the metadata.

#### Field: small_image_url

- **Type:** `string`
- **Description:** URL for small version of review image
- **Example:** `"https://images-na.ssl-images-amazon.com/images/I/41ABC123.jpg"`
- **Notes:** Smallest size variant, suitable for thumbnails

#### Field: medium_image_url

- **Type:** `string`
- **Description:** URL for medium version of review image
- **Example:** `"https://images-na.ssl-images-amazon.com/images/I/51ABC123.jpg"`
- **Notes:** Medium size variant, good for preview

#### Field: large_image_url

- **Type:** `string`
- **Description:** URL for large version of review image
- **Example:** `"https://images-na.ssl-images-amazon.com/images/I/61ABC123.jpg"`
- **Notes:** Largest size variant, best quality

#### Field: attachment_type

- **Type:** `string`
- **Description:** Type of attachment
- **Values:** Typically `"IMAGE"`
- **Notes:** Indicates the media type (currently only images supported)

**Example Image Object:**

```json
{
  "small_image_url": "https://images-na.ssl-images-amazon.com/images/I/41ABC123.jpg",
  "medium_image_url": "https://images-na.ssl-images-amazon.com/images/I/51ABC123.jpg",
  "large_image_url": "https://images-na.ssl-images-amazon.com/images/I/61ABC123.jpg",
  "attachment_type": "IMAGE"
}
```

**Key Differences from Product Images:**

- Review images are uploaded by customers, not sellers
- Show real-world product usage and condition
- May include context (packaging, size comparisons, etc.)
- Quality varies significantly
- Can provide evidence for review claims

---

## Field Details

### Rating Scale Interpretation

| Rating | Interpretation | Typical Usage                          |
| ------ | -------------- | -------------------------------------- |
| 5.0    | Excellent      | Highly satisfied, exceeds expectations |
| 4.0    | Good           | Satisfied, meets expectations          |
| 3.0    | Average        | Neutral, has pros and cons             |
| 2.0    | Poor           | Dissatisfied, below expectations       |
| 1.0    | Terrible       | Very dissatisfied, major issues        |

### Timestamp Precision

- **Format:** Unix epoch time in milliseconds
- **Precision:** Millisecond level (though likely rounded)
- **Range:** Covers years of review history
- **Timezone:** UTC (Universal Coordinated Time)

### User ID Characteristics

- **Format:** Base64-like alphanumeric string
- **Length:** Variable, typically 30-40 characters
- **Anonymization:** Does not reveal personal information
- **Persistence:** Same user has same ID across reviews
- **Privacy:** Protects reviewer identity

### Helpful Vote Dynamics

- **Initial Value:** Starts at 0 when review is posted
- **Growth:** Increases as users mark review helpful
- **No Downvotes:** Only positive votes counted
- **Bias:** Older reviews tend to have more votes
- **Quality Indicator:** Higher votes suggest useful content

### Verified Purchase Importance

**Why It Matters:**

1. **Authenticity:** Confirms actual product purchase
2. **Trust:** Verified reviews more credible
3. **Fraud Prevention:** Reduces fake reviews
4. **Incentive Detection:** Helps identify biased reviews
5. **Quality Filter:** Often used to filter review lists

**Distribution:**

- Majority of reviews are verified purchases
- Non-verified may be gifts, samples, or unverified sources
- Some legitimate reviews may not be verified

---

## Data Types

### Summary of Data Types by Field

| Field             | Type          | Nullable | Can Be Empty      |
| ----------------- | ------------- | -------- | ----------------- |
| rating            | float         | No       | No                |
| title             | string        | No       | No                |
| text              | string        | No       | No                |
| images            | array[object] | No       | Yes (empty array) |
| asin              | string        | No       | No                |
| parent_asin       | string        | No       | No                |
| user_id           | string        | No       | No                |
| timestamp         | integer       | No       | No                |
| helpful_vote      | integer       | No       | No (can be 0)     |
| verified_purchase | boolean       | No       | No                |

### Type Constraints

- **rating:** Always between 1.0 and 5.0 (inclusive)
- **timestamp:** Positive integer, milliseconds since epoch
- **helpful_vote:** Non-negative integer (≥ 0)
- **verified_purchase:** Strictly boolean (true/false)
- **asin/parent_asin:** Alphanumeric, typically 10 characters

---

## Usage Notes

### Data Quality Considerations

1. **Text Quality:** Review text varies from single words to detailed essays
2. **Spam/Fake Reviews:** Some reviews may be fraudulent despite verification
3. **Language:** Primarily English, but may contain other languages
4. **Sentiment Bias:** Rating distribution may be biased (more extremes)
5. **Temporal Bias:** Older products have more reviews
6. **Image Availability:** Most reviews don't include images

### Common Use Cases

#### 1. Sentiment Analysis

```python
# Use rating and text fields
if rating >= 4.0:
    sentiment = "positive"
elif rating <= 2.0:
    sentiment = "negative"
else:
    sentiment = "neutral"
```

#### 2. Review Quality Filtering

```python
# Filter for high-quality reviews
quality_reviews = reviews.filter(
    verified_purchase == True,
    helpful_vote >= 5,
    len(text) > 100
)
```

#### 3. Temporal Analysis

```python
# Convert timestamp and analyze trends
from datetime import datetime
date = datetime.fromtimestamp(timestamp / 1000)
month_year = date.strftime("%Y-%m")
```

#### 4. Reviewer Profiling

```python
# Group by user_id to analyze reviewer behavior
reviewer_stats = reviews.groupby('user_id').agg({
    'rating': 'mean',
    'helpful_vote': 'sum',
    'verified_purchase': 'mean'
})
```

#### 5. Product-Review Linking

```python
# Join reviews with products
merged = reviews.merge(
    products,
    left_on='parent_asin',
    right_on='parent_asin'
)
```

### Linking to Product Metadata

**Relationship:**

- Review `asin` or `parent_asin` → Product `parent_asin` in meta_Electronics.jsonl
- One product can have many reviews (one-to-many relationship)
- Use `parent_asin` for more reliable linking across variants

**Join Strategy:**

```python
# Recommended join approach
reviews_with_products = pd.merge(
    reviews,
    products,
    left_on='parent_asin',
    right_on='parent_asin',
    how='left'
)
```

### Best Practices

#### Data Cleaning

1. **Remove Duplicates:** Check for duplicate reviews by user_id + asin + timestamp
2. **Handle Missing Text:** Some reviews may have minimal text
3. **Validate Ratings:** Ensure ratings are in valid range (1.0-5.0)
4. **Parse Timestamps:** Convert to datetime for analysis
5. **Filter Spam:** Use verified_purchase and helpful_vote for quality

#### Analysis Recommendations

1. **Weight by Helpful Votes:** Give more weight to helpful reviews
2. **Consider Recency:** Recent reviews may be more relevant
3. **Verify Purchase Filter:** Use verified_purchase for authentic insights
4. **Text Length Filter:** Longer reviews often more informative
5. **Rating Distribution:** Analyze distribution, not just average

#### Performance Optimization

1. **Index Fields:** Index asin, parent_asin, user_id, timestamp
2. **Batch Processing:** Process reviews in batches for large datasets
3. **Selective Loading:** Load only needed fields
4. **Cache Results:** Cache aggregated statistics
5. **Parallel Processing:** Use parallel processing for text analysis

### Common Pitfalls

1. **Timestamp Units:** Remember timestamps are in milliseconds, not seconds
2. **ASIN Matching:** Use parent_asin for better product matching
3. **Rating Bias:** Extreme ratings (1 or 5) are over-represented
4. **Text Encoding:** Handle special characters and emojis properly
5. **Null Handling:** While fields aren't null, empty arrays exist

---

## Example Complete Review Record

```json
{
  "rating": 3.0,
  "title": "Smells like gasoline! Going back!",
  "text": "First & most offensive: they reek of gasoline so if you are sensitive/allergic to petroleum products, stay away. Second: they are not soft at all. The texture is more like a thin layer of foam rubber. Not comfortable to wear for extended periods.",
  "images": [
    {
      "small_image_url": "https://images-na.ssl-images-amazon.com/images/I/41ABC123_SL75_.jpg",
      "medium_image_url": "https://images-na.ssl-images-amazon.com/images/I/41ABC123_SL160_.jpg",
      "large_image_url": "https://images-na.ssl-images-amazon.com/images/I/41ABC123.jpg",
      "attachment_type": "IMAGE"
    }
  ],
  "asin": "B083NRGZMM",
  "parent_asin": "B083NRGZMM",
  "user_id": "AFKZENTNBQ7A7V7UXW5JJI6UGRYQ",
  "timestamp": 1658185117948,
  "helpful_vote": 0,
  "verified_purchase": true
}
```

---

## Statistical Summary

### Typical Distributions

**Rating Distribution:**

- 5-star: ~40-50% (most common)
- 4-star: ~20-25%
- 3-star: ~10-15%
- 2-star: ~5-10%
- 1-star: ~15-20%

**Verified Purchase:**

- Verified: ~70-80%
- Not Verified: ~20-30%

**Images:**

- With images: ~5-10%
- Without images: ~90-95%

**Helpful Votes:**

- 0 votes: ~70-80%
- 1-5 votes: ~15-20%
- 6+ votes: ~5-10%

---

## Field Count Summary

- **Top-level fields:** 10
- **Image sub-fields:** 4 per image (when present)
- **Total unique field paths:** 14 (10 top-level + 4 nested)
- **Complexity:** Low (flat structure)

---

## Data Schema (JSON Schema Format)

```json
{
  "type": "object",
  "required": [
    "rating",
    "title",
    "text",
    "images",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase"
  ],
  "properties": {
    "rating": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 5.0
    },
    "title": {
      "type": "string"
    },
    "text": {
      "type": "string"
    },
    "images": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "small_image_url": { "type": "string" },
          "medium_image_url": { "type": "string" },
          "large_image_url": { "type": "string" },
          "attachment_type": { "type": "string" }
        }
      }
    },
    "asin": {
      "type": "string"
    },
    "parent_asin": {
      "type": "string"
    },
    "user_id": {
      "type": "string"
    },
    "timestamp": {
      "type": "integer",
      "minimum": 0
    },
    "helpful_vote": {
      "type": "integer",
      "minimum": 0
    },
    "verified_purchase": {
      "type": "boolean"
    }
  }
}
```

---

## Comparison with Product Metadata

| Aspect               | Review Data              | Product Metadata           |
| -------------------- | ------------------------ | -------------------------- |
| **Complexity**       | Simple, flat             | Complex, nested            |
| **Fields**           | 10 top-level             | 14 top-level + 150+ nested |
| **Content Type**     | User-generated           | Seller/Amazon-provided     |
| **Variability**      | Consistent structure     | Highly variable (details)  |
| **Primary Use**      | Sentiment, feedback      | Product information        |
| **Update Frequency** | Continuous (new reviews) | Periodic (product updates) |
| **Data Quality**     | Variable (user input)    | Generally consistent       |

---

**Last Updated:** 2025  
**Data Source:** Electronics.jsonl  
**Format:** JSONL (JSON Lines)  
**Record Type:** Customer Reviews
