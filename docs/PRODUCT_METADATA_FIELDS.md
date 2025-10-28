# Product Metadata Field Structure Documentation

**File:** `meta_Electronics.jsonl`  
**Description:** Complete field structure for Amazon product metadata

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

The product metadata contains **14 top-level fields** with nested structures for images, videos, and detailed product specifications. The total number of unique field paths across all products is approximately **170+**, with the `details` object being the most variable based on product category.

**Total Fields:**

- 14 top-level fields
- 4 sub-fields in images[] array
- 3 sub-fields in videos[] array
- 150+ possible keys in details{} dictionary

---

## Top-Level Fields

### 1. main_category

- **Type:** `string` or `null`
- **Description:** The main category classification for the product
- **Example:** `"All Electronics"`, `"Computers"`, `"AMAZON FASHION"`
- **Notes:** Can be null for some products

### 2. title

- **Type:** `string`
- **Description:** Full product title/name
- **Example:** `"FS-1051 FATSHARK TELEPORTER V3 HEADSET"`
- **Notes:** Required field, always present

### 3. average_rating

- **Type:** `float`
- **Description:** Average customer rating for the product
- **Range:** 0.0 to 5.0
- **Example:** `3.5`, `4.5`
- **Notes:** Calculated from all customer reviews

### 4. rating_number

- **Type:** `integer`
- **Description:** Total number of ratings/reviews
- **Example:** `6`, `246`, `233`
- **Notes:** Indicates review volume

### 5. features

- **Type:** `array of strings`
- **Description:** List of product features and highlights
- **Example:**
  ```json
  [
    "WARNING: Please IDENTIFY MODEL NUMBER on the bottom of your Macbook.",
    "Extra Care Yet Not Bulky.",
    "Elegant Style."
  ]
  ```
- **Notes:** Can be empty array `[]`

### 6. description

- **Type:** `array of strings`
- **Description:** Detailed product description
- **Example:**
  ```json
  [
    "Teleporter V3 The "Teleporter V3" kit sets a new level of value...",
    "Additional details about the product..."
  ]
  ```
- **Notes:** Can be empty array `[]`

### 7. price

- **Type:** `float` or `null`
- **Description:** Product price in USD
- **Example:** `19.99`, `14.99`, `9.99`
- **Notes:** Can be null if price is not available

### 8. images

- **Type:** `array of objects`
- **Description:** Collection of product images in various sizes
- **Structure:** See [Images Array Structure](#images-array-structure)
- **Notes:** Each product typically has multiple image variants

### 9. videos

- **Type:** `array of objects`
- **Description:** Collection of product videos
- **Structure:** See [Videos Array Structure](#videos-array-structure)
- **Notes:** Can be empty array `[]`

### 10. store

- **Type:** `string`
- **Description:** Store or brand name
- **Example:** `"Fat Shark"`, `"SIIG"`, `"Digi-Tatoo"`, `"NotoCity"`
- **Notes:** Represents the seller or manufacturer

### 11. categories

- **Type:** `array of strings`
- **Description:** Product category hierarchy from general to specific
- **Example:**
  ```json
  ["Electronics", "Television & Video", "Video Glasses"]
  ```
- **Notes:** Shows the full category path

### 12. details

- **Type:** `object/dictionary`
- **Description:** Product specifications and technical details
- **Structure:** See [Details Object Structure](#details-object-structure)
- **Notes:** Highly variable based on product category

### 13. parent_asin

- **Type:** `string`
- **Description:** Parent product ASIN (Amazon Standard Identification Number)
- **Example:** `"B00MCW7G9M"`, `"B07SM135LS"`
- **Notes:** Links product variants to parent product

### 14. bought_together

- **Type:** `null` (in current dataset)
- **Description:** Products frequently bought together
- **Notes:** Appears to be null in all records

---

## Nested Structures

### Images Array Structure

Each image object in the `images[]` array contains:

#### Field: thumb

- **Type:** `string`
- **Description:** URL for thumbnail image (40px width)
- **Example:** `"https://m.media-amazon.com/images/I/41qrX56lsYL._AC_US40_.jpg"`

#### Field: large

- **Type:** `string`
- **Description:** URL for large image
- **Example:** `"https://m.media-amazon.com/images/I/41qrX56lsYL._AC_.jpg"`

#### Field: variant

- **Type:** `string`
- **Description:** Image variant type
- **Values:** `"MAIN"`, `"PT01"`, `"PT02"`, `"PT03"`, `"PT04"`, `"PT05"`, etc.
- **Notes:** MAIN is the primary product image

#### Field: hi_res

- **Type:** `string` or `null`
- **Description:** URL for high-resolution image
- **Example:** `"https://m.media-amazon.com/images/I/51qxU4Zd5TL._AC_SL1050_.jpg"`
- **Notes:** Can be null if high-res version not available

**Example Image Object:**

```json
{
  "thumb": "https://m.media-amazon.com/images/I/31t4bj9t88L._AC_US40_.jpg",
  "large": "https://m.media-amazon.com/images/I/31t4bj9t88L._AC_.jpg",
  "variant": "MAIN",
  "hi_res": "https://m.media-amazon.com/images/I/61RPxmi+mPL._AC_SL1500_.jpg"
}
```

---

### Videos Array Structure

Each video object in the `videos[]` array contains:

#### Field: title

- **Type:** `string`
- **Description:** Video title or description
- **Example:** `"AL 2Sides Video"`, `"MacBook Protective Skin"`

#### Field: url

- **Type:** `string`
- **Description:** URL to the video
- **Example:** `"https://www.amazon.com/vdp/58d77b2d7a6b44d38df104438e138167?ref=dp_vse_rvc_0"`

#### Field: user_id

- **Type:** `string`
- **Description:** ID of user who uploaded the video
- **Example:** `"/shop/influencer-b1d7cc37"`, `""`
- **Notes:** Can be empty string for official videos

**Example Video Object:**

```json
{
  "title": "MacBook Protective Skin",
  "url": "https://www.amazon.com/vdp/b47a21292a3a4df4a11fd9b4237a43fb?ref=dp_vse_rvc_1",
  "user_id": ""
}
```

---

### Details Object Structure

The `details` object is a dictionary with **highly variable keys** depending on product category. Below are the most common fields organized by category:

#### Basic Information

- **Brand** - Product brand name
- **Manufacturer** - Manufacturer name
- **Model Name** - Product model name
- **Item model number** - Model number/SKU
- **Model number** - Alternative model number field
- **Date First Available** - When product was first listed
- **Color** - Product color
- **Size** - Product size
- **Style** - Product style
- **Theme** - Product theme
- **Pattern** - Product pattern
- **Material** - Primary material

#### Dimensions & Weight

- **Product Dimensions** - Product dimensions (e.g., "11.6 x 6.9 x 3.1 inches")
- **Item Weight** - Weight of the item
- **Package Dimensions** - Shipping package dimensions
- **Package Weight** - Shipping package weight
- **Item Dimensions LxWxH** - Alternative dimension format
- **Item Package Dimensions L x W x H** - Another dimension format

#### Electronics Specifications

- **Processor** - Processor type
- **Processor Brand** - Processor manufacturer
- **RAM** - RAM amount
- **Ram Memory Installed Size** - RAM size (alternative)
- **Hard Disk Size** - Storage capacity
- **Hard Drive** - Hard drive specifications
- **Graphics Coprocessor** - GPU model
- **Graphics Card Ram Size** - GPU memory
- **Operating System** - OS (e.g., "Windows 10", "macOS")
- **Hardware Platform** - Platform type
- **Display Size** - Screen size
- **Screen Size** - Alternative screen size field
- **Screen Resolution** - Display resolution
- **Resolution** - Alternative resolution field
- **Connectivity Technology** - Connection types
- **Wireless Type** - Wireless standards
- **Batteries Included?** - Whether batteries are included
- **Batteries Required?** - Whether batteries are needed
- **Are Batteries Included** - Alternative battery field

#### Computer/Laptop Specifications

- **CPU Model** - CPU model name
- **CPU Speed** - Processor speed
- **Cache Size** - CPU cache size
- **Computer Memory Type** - RAM type (DDR3, DDR4, etc.)
- **Flash Memory Size** - Flash storage size
- **Memory Speed** - RAM speed
- **Hard Disk Interface** - Storage interface (SATA, NVMe, etc.)
- **Hard Drive Interface** - Alternative interface field
- **Graphics Processor Manufacturer** - GPU manufacturer
- **Chipset Brand** - Chipset manufacturer
- **Number of Processors** - CPU count
- **Form Factor** - Device form factor

#### Camera/Photography

- **Camera Lens Description** - Lens specifications
- **Lens Type** - Type of lens
- **Maximum Focal Length** - Max focal length
- **Minimum Focal Length** - Min focal length
- **Video Capture Resolution** - Video recording resolution
- **Rear Webcam Resolution** - Rear camera resolution

#### Connectivity

- **Connector Type** - Type of connector
- **Hardware Interface** - Interface type
- **Number of USB 2.0 Ports** - USB 2.0 port count
- **Number of USB 3.0 Ports** - USB 3.0 port count
- **Total USB Ports** - Total USB ports
- **Total HDMI Ports** - HDMI port count
- **Wireless Communication Technology** - Wireless tech specs

#### Audio/Video

- **Speaker Type** - Speaker specifications
- **Number of Channels** - Audio channels
- **Surround Sound Channel Configuration** - Surround sound setup
- **Video Output Interface** - Video output type

#### Ranking & Availability

- **Best Sellers Rank** - Sales ranking (can be nested object)
- **Is Discontinued By Manufacturer** - Discontinuation status
- **Country of Origin** - Manufacturing country
- **Department** - Department classification

#### Miscellaneous

- **Special Feature** - Special features
- **Recommended Uses For Product** - Recommended use cases
- **Compatible Devices** - Compatible device list
- **Warranty** - Warranty information
- **Finish Type** - Surface finish
- **Power Source** - Power source type
- **Unit Count** - Number of units
- **Number of Items** - Item count
- **Reusability** - Reusability information
- **Is Waterproof** - Waterproof status
- **Room Type** - Recommended room type
- **Age Range (Description)** - Age range
- **Voltage** - Operating voltage
- **Wattage** - Power consumption

**Example Details Object:**

```json
{
  "Brand": "Digi-Tatoo",
  "Color": "Fresh Marble",
  "Material": "Vinyl",
  "Item Weight": "3.84 ounces",
  "Package Dimensions": "14.13 x 9.8 x 0.16 inches",
  "Manufacturer": "Digi-Tatoo",
  "Date First Available": "June 3, 2019",
  "Best Sellers Rank": {
    "Computers & Accessories": 87106,
    "Laptop Decals": 16463
  }
}
```

---

## Data Types

### Summary of Data Types by Field

| Field           | Type          | Nullable          |
| --------------- | ------------- | ----------------- |
| main_category   | string        | Yes               |
| title           | string        | No                |
| average_rating  | float         | No                |
| rating_number   | integer       | No                |
| features        | array[string] | No (can be empty) |
| description     | array[string] | No (can be empty) |
| price           | float         | Yes               |
| images          | array[object] | No (can be empty) |
| videos          | array[object] | No (can be empty) |
| store           | string        | No                |
| categories      | array[string] | No (can be empty) |
| details         | object        | No (can be empty) |
| parent_asin     | string        | No                |
| bought_together | null          | Yes (always null) |

---

## Usage Notes

### Data Quality Considerations

1. **Missing Fields:** Not all products have all fields populated
2. **Null Values:** Fields like `price`, `main_category`, and `hi_res` can be null
3. **Empty Arrays:** `features`, `description`, `videos`, and `categories` can be empty
4. **Variable Details:** The `details` object varies significantly by product category
5. **Image Availability:** Not all image variants have high-resolution versions

### Common Use Cases

1. **Product Search:** Use `title`, `description`, `features`, and `categories`
2. **Price Analysis:** Use `price` field (handle nulls appropriately)
3. **Rating Analysis:** Use `average_rating` and `rating_number`
4. **Image Display:** Use `images` array, prioritize `MAIN` variant
5. **Category Analysis:** Use `categories` and `main_category`
6. **Specifications:** Parse `details` object for technical specs

### Linking to Reviews

- Use `parent_asin` to link products to reviews in `Electronics.jsonl`
- Reviews reference products via their `asin` or `parent_asin` fields

### Best Practices

1. Always check for null/empty values before processing
2. Handle missing `details` keys gracefully
3. Parse `Best Sellers Rank` carefully (can be nested object)
4. Validate URLs in `images` and `videos` before use
5. Consider product category when accessing `details` fields

---

## Example Complete Product Record

```json
{
  "main_category": "Computers",
  "title": "Digi-Tatoo Decal Skin Compatible With MacBook Pro 13 inch",
  "average_rating": 4.5,
  "rating_number": 246,
  "features": [
    "WARNING: Please IDENTIFY MODEL NUMBER on the bottom of your Macbook.",
    "Extra Care Yet Not Bulky.",
    "Elegant Style."
  ],
  "description": [],
  "price": 19.99,
  "images": [
    {
      "thumb": "https://m.media-amazon.com/images/I/31t4bj9t88L._AC_US40_.jpg",
      "large": "https://m.media-amazon.com/images/I/31t4bj9t88L._AC_.jpg",
      "variant": "MAIN",
      "hi_res": "https://m.media-amazon.com/images/I/61RPxmi+mPL._AC_SL1500_.jpg"
    }
  ],
  "videos": [],
  "store": "Digi-Tatoo",
  "categories": [
    "Electronics",
    "Computers & Accessories",
    "Laptop Accessories",
    "Skins & Decals",
    "Decals"
  ],
  "details": {
    "Brand": "Digi-Tatoo",
    "Color": "Fresh Marble",
    "Material": "Vinyl",
    "Item Weight": "3.84 ounces",
    "Package Dimensions": "14.13 x 9.8 x 0.16 inches",
    "Manufacturer": "Digi-Tatoo",
    "Date First Available": "June 3, 2019"
  },
  "parent_asin": "B07SM135LS",
  "bought_together": null
}
```

---

## Field Count Summary

- **Top-level fields:** 14
- **Image sub-fields:** 4 per image
- **Video sub-fields:** 3 per video
- **Details possible keys:** 150+
- **Total unique field paths:** ~170+

---

**Last Updated:** 2025  
**Data Source:** meta_Electronics.jsonl  
**Format:** JSONL (JSON Lines)
