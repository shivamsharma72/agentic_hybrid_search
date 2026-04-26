# 📊 Laptop Data Analysis

Comprehensive analysis of 5,455 laptop products and 350,105 reviews from Amazon Electronics dataset.

---

## 📁 Analysis Structure

```
analysis/
├── 01_details_analysis/          # Product specifications (JSONB)
├── 02_store_analysis/             # Brand/seller analysis
├── 03_categories_analysis/        # Category hierarchy
├── 04_main_category_analysis/     # Top-level categories
├── 05_description_analysis/       # Marketing text analysis
├── 06_features_analysis/          # Product features analysis
├── 07_titles_analysis/            # Product naming patterns
├── 08_price_rating_analysis/      # Price & rating correlation
└── 09_reviews_analysis/           # User review insights
```

---

## 🎯 Analysis Goals

### **01. Details Analysis**
**What:** Analyze product specifications stored in JSONB `details` column

**Key Questions:**
- What specs are most commonly provided?
- What's the typical RAM/Storage/Processor configuration?
- How complete is the specification data?
- **Bestseller Rank:** Which products rank highest and why?

**Outputs:**
- Specification key frequency
- RAM distribution (4GB, 8GB, 16GB, 32GB+)
- Storage distribution (256GB SSD, 512GB SSD, 1TB)
- Processor brands (Intel, AMD, Apple)
- Screen sizes (13", 14", 15", 17")
- Best Seller Rank analysis

---

### **02. Store Analysis**
**What:** Analyze brands and sellers

**Key Questions:**
- Which brands dominate the market?
- Brand market share?
- Average price by brand?
- Brand reputation (ratings)?

**Outputs:**
- Top 20 stores/brands
- Market share by brand
- Price ranges by brand
- Average ratings by brand
- Product count by brand

---

### **03. Categories Analysis**
**What:** Analyze category hierarchy (array field)

**Key Questions:**
- How are laptops categorized?
- What's the category tree structure?
- Most common leaf categories?

**Outputs:**
- Category hierarchy tree
- Product distribution across categories
- Category depth analysis
- Most specific categories

---

### **04. Main Category Analysis**
**What:** Analyze top-level category

**Key Questions:**
- What main categories exist?
- Distribution of products?
- Consistency with detailed categories?

**Outputs:**
- Main category distribution
- Cross-reference with subcategories

---

### **05. Description Analysis**
**What:** NLP analysis of product descriptions

**Key Questions:**
- What keywords are most common?
- What features do descriptions emphasize?
- How long are descriptions?
- What's the marketing language?

**Outputs:**
- Description length distribution
- Most common keywords
- Word clouds (top terms)
- Feature mentions frequency
- Marketing language patterns

---

### **06. Features Analysis**
**What:** Analyze bullet-point features

**Key Questions:**
- How many features per product?
- Most common feature types?
- What do sellers emphasize?

**Outputs:**
- Features per product distribution
- Most common feature categories:
  - Performance ("Fast", "Powerful")
  - Display ("HD", "Touchscreen")
  - Battery ("Long lasting")
  - Build ("Lightweight", "Durable")
- Feature frequency analysis

---

### **07. Titles Analysis**
**What:** Analyze product naming conventions

**Key Questions:**
- What brands appear in titles?
- What specs are mentioned in titles?
- Naming patterns?
- Common keywords?

**Outputs:**
- Title length distribution
- Brand mentions frequency
- Spec mentions in titles
- Common keywords ("Gaming", "Business", "Ultrabook")
- Title structure patterns

---

### **08. Price & Rating Analysis**
**What:** Combined analysis of price and ratings

**Key Questions:**
- Price distribution?
- Rating distribution?
- Correlation between price and rating?
- Best value laptops?
- Overpriced products?

**Outputs:**
- Price ranges:
  - Budget: < $500
  - Mid-range: $500-$1000
  - Premium: $1000-$1500
  - High-end: > $1500
- Rating distribution (1-5 stars)
- Price vs. Rating scatter plot
- **Value for money** analysis
- Best value quadrant (low price, high rating)
- Overpriced quadrant (high price, low rating)

---

### **09. Reviews Analysis**
**What:** Comprehensive analysis of 350K+ user reviews

**Key Questions:**
- What do users actually say?
- Common complaints vs. praises?
- Sentiment vs. star rating?
- Do reviews validate product claims?
- What features do users care about?

**Outputs:**

#### **A. Sentiment Analysis**
- Positive/Neutral/Negative distribution
- Sentiment by brand
- Sentiment by price range
- Rating vs. actual sentiment validation

#### **B. Content Analysis**
- Most mentioned topics:
  - Performance
  - Build quality
  - Battery life
  - Screen quality
  - Keyboard/Trackpad
  - Heat/Noise
- Word clouds (positive vs. negative)
- N-gram analysis

#### **C. Quality Analysis**
- Review length distribution
- Verified vs. Unverified purchases
- Helpful votes analysis
- Review completeness

#### **D. Cross-Analysis with Products**
- **Validate claims:** Description vs. Review mentions
- **Identify issues:** Hidden problems not in specs
- **Feature validation:** Do mentioned features matter?
- **Brand reputation:** Promises vs. delivery
- **Price perception:** Value for money mentions
- **Spec sweet spots:** Optimal configurations from reviews

---

## 🚀 How to Run

### **Prerequisites:**
```bash
pip install psycopg2-binary pandas numpy matplotlib seaborn wordcloud scikit-learn
```

### **Run Individual Analysis:**
```bash
cd analysis/01_details_analysis
python3 analyze_details.py
```

### **Run All Analyses:**
```bash
cd analysis
python3 run_all_analyses.py
```

---

## 📊 Expected Outputs

Each analysis folder will contain:

1. **Python Scripts** (`.py`)
   - Data extraction from PostgreSQL
   - Statistical analysis
   - Visualization generation

2. **Markdown Reports** (`*_report.md`)
   - Executive summary
   - Key findings
   - Statistics tables
   - Embedded visualizations
   - Insights and recommendations

3. **Visualizations** (`visualizations/` folder)
   - Bar charts, histograms, pie charts
   - Scatter plots, box plots
   - Word clouds (for text data)
   - Tree diagrams (for hierarchies)
   - Heatmaps (for correlations)

4. **Data Exports** (`.csv`, `.json`)
   - Summary statistics
   - Top N lists
   - Detailed breakdowns

---

## 💡 Key Insights Expected

### **From Product Analysis:**
1. **Specification Trends:** Most common laptop configurations
2. **Brand Landscape:** Market leaders and their positioning
3. **Category Structure:** How Amazon organizes laptops
4. **Marketing Language:** What sellers emphasize
5. **Price-Quality Relationship:** Value segments

### **From Reviews Analysis:**
1. **User Priorities:** What actually matters to buyers
2. **Reality Check:** Marketing claims vs. user experience
3. **Hidden Issues:** Problems not mentioned in specs
4. **Brand Reputation:** Who delivers on promises
5. **Feature Importance:** What specs impact satisfaction
6. **Sweet Spots:** Optimal configurations for value

### **From Cross-Analysis:**
1. **Best Value Products:** High quality, reasonable price
2. **Hidden Gems:** Good products with low visibility
3. **Overrated Products:** High ratings but poor reviews
4. **Common Failures:** Recurring quality issues
5. **Trusted Brands:** Consistent quality delivery
6. **Misleading Marketing:** Claims not backed by reviews

---

## 📈 Analysis Timeline

- **Details Analysis:** ~10 minutes
- **Store Analysis:** ~5 minutes
- **Categories Analysis:** ~5 minutes
- **Main Category Analysis:** ~2 minutes
- **Description Analysis:** ~15 minutes (NLP processing)
- **Features Analysis:** ~10 minutes
- **Titles Analysis:** ~5 minutes
- **Price/Rating Analysis:** ~10 minutes
- **Reviews Analysis:** ~30 minutes (350K reviews)

**Total:** ~1.5 hours for complete analysis

---

## 🎓 Use Cases

1. **Market Research:** Understand laptop market landscape
2. **Product Selection:** Data-driven laptop buying decisions
3. **Competitive Analysis:** Brand positioning and strategies
4. **Quality Assurance:** Identify problematic products
5. **Pricing Strategy:** Optimal price points
6. **Feature Prioritization:** What specs matter most
7. **Academic Research:** E-commerce data analysis

---

## 📚 Data Source

- **Database:** `amazon_electronics_rag`
- **Products Table:** `products_backup` (5,455 laptops)
- **Reviews Table:** `reviews_backup` (350,105 reviews)
- **Source Dataset:** Amazon Reviews 2023 (McAuley Lab, UCSD)
- **Embeddings:** BLAIR-RoBERTa (768-dim vectors)

---

## 🔧 Technical Details

- **Database:** PostgreSQL 14+ with pgvector
- **Python:** 3.8+
- **Key Libraries:**
  - `psycopg2`: Database connectivity
  - `pandas`: Data manipulation
  - `matplotlib`, `seaborn`: Visualization
  - `wordcloud`: Text visualization
  - `scikit-learn`: ML/NLP analysis
  - `numpy`: Numerical computing

---

## 📝 Notes

- All analyses use the **laptop-only subset** of Amazon Electronics
- Data has been **5-core filtered** (every product ≥5 reviews, every user ≥5 reviews)
- **Laptop network adapters** removed during cleaning
- Embeddings provide **semantic search** capabilities
- Cross-modal alignment allows **product ↔ review** matching

---

**Created:** November 2025  
**Version:** 1.0  
**Status:** Ready for Analysis

