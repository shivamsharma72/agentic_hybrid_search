# 🚀 Quick Start Guide - Laptop Data Analysis

Get your analysis up and running in minutes!

---

## ⚡ Super Quick Start

```bash
# 1. Install dependencies
pip install psycopg2-binary pandas numpy matplotlib seaborn wordcloud scikit-learn

# 2. Navigate to analysis folder
cd final/analysis

# 3. Run all analyses
python3 run_all_analyses.py
```

---

## 📊 What Gets Created

After running, you'll have:

```
analysis/
├── 01_details_analysis/
│   ├── visualizations/
│   │   ├── top_specification_keys.png
│   │   ├── ram_distribution.png
│   │   └── storage_distribution.png
│   ├── details_summary.json
│   └── details_report.md
│
├── 02_store_analysis/
│   ├── visualizations/
│   │   ├── top_stores.png
│   │   └── store_market_share.png
│   └── store_report.md
│
... (7 more folders with similar structure)
```

---

## 🎯 Run Individual Analyses

### **Details Analysis:**
```bash
cd 01_details_analysis
python3 analyze_details.py
```

### **Store Analysis:**
```bash
cd 02_store_analysis
python3 analyze_stores.py
```

### **Price & Rating:**
```bash
cd 08_price_rating_analysis
python3 analyze_price.py
python3 analyze_ratings.py
python3 analyze_price_rating_correlation.py
```

### **Reviews (Most Interesting!):**
```bash
cd 09_reviews_analysis
python3 analyze_review_content.py
python3 analyze_review_sentiment.py
python3 cross_analysis_with_products.py
```

---

## 📋 Prerequisites Checklist

- [ ] PostgreSQL running
- [ ] Database `amazon_electronics_rag` exists
- [ ] Tables `products_backup` and `reviews_backup` exist
- [ ] Python 3.8+ installed
- [ ] Required packages installed (see above)

---

## ⏱️ Time Estimates

| Analysis | Time | Complexity |
|----------|------|------------|
| Details | ~10 min | Medium |
| Store | ~5 min | Easy |
| Categories | ~5 min | Medium |
| Main Category | ~2 min | Easy |
| Description | ~15 min | Hard (NLP) |
| Features | ~10 min | Medium |
| Titles | ~5 min | Easy |
| Price & Rating | ~10 min | Medium |
| Reviews | ~30 min | Hard (350K reviews) |
| **TOTAL** | **~1.5 hours** | |

---

## 💡 What You'll Discover

### **From Products:**
- Most common laptop specs (RAM, Storage, Processor)
- Brand market share
- Price ranges by category
- Feature emphasis patterns
- Specification completeness

### **From Reviews:**
- What users actually care about
- Common complaints vs. marketing claims
- Best value laptops (price vs. satisfaction)
- Brand reputation (promises vs. delivery)
- Hidden quality issues
- Feature importance ranking

### **From Cross-Analysis:**
- Products with misleading descriptions
- Overrated vs. underrated laptops
- Specification sweet spots
- Value for money leaders
- Trustworthy brands

---

## 🐛 Troubleshooting

### **"Connection refused" error:**
```bash
# Check PostgreSQL is running
psql -l

# If not running:
brew services start postgresql  # macOS
sudo service postgresql start   # Linux
```

### **"relation does not exist" error:**
Make sure tables exist:
```sql
psql -d amazon_electronics_rag -c "\dt"
```

Should show `products_backup` and `reviews_backup`

### **"ModuleNotFoundError":**
```bash
pip install <missing_module>
```

---

## 📊 View Results

After analysis completes:

1. **Visualizations:** Check `*/visualizations/*.png` files
2. **Reports:** Read `*_report.md` files in each folder
3. **Data:** Explore `.json` and `.csv` summary files

---

## 🎓 For Students/Reviewers

### **Quick Demo (5 minutes):**
```bash
# Just run details analysis (fastest, most visual)
cd 01_details_analysis
python3 analyze_details.py
```

Opens 3 charts showing laptop specs distribution!

### **Full Analysis (1.5 hours):**
```bash
# Run everything
python3 run_all_analyses.py
```

Perfect for comprehensive project demonstration.

---

## 📚 Learn More

- **Full Documentation:** See `README.md`
- **Database Setup:** See `../00_database_setup/`
- **RAG System:** See `../rag_chatbot/`

---

**Happy Analyzing! 📊🚀**

