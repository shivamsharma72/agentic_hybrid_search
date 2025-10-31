#!/bin/bash

# Quick Verification Script for Amazon Electronics RAG Project
# Run this to verify everything is working correctly

echo "======================================================"
echo "   AMAZON ELECTRONICS RAG - QUICK VERIFICATION"
echo "======================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/Users/shivamsharma/Desktop/ASU Subjects/semester 4 /swm project"

echo "📍 Project Directory: $PROJECT_DIR"
echo ""

# 1. Check PostgreSQL
echo "1️⃣  Checking PostgreSQL status..."
if brew services list | grep -q "postgresql@17.*started"; then
    echo -e "${GREEN}✅ PostgreSQL 17 is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL 17 is NOT running${NC}"
    echo "   To start: brew services start postgresql@17"
fi
echo ""

# 2. Check database connection
echo "2️⃣  Checking database connection..."
if psql -U postgres -d amazon_electronics_rag -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Can connect to database${NC}"
else
    echo -e "${RED}❌ Cannot connect to database${NC}"
    echo "   Check if PostgreSQL is running and database exists"
fi
echo ""

# 3. Check pgvector extension
echo "3️⃣  Checking pgvector extension..."
if psql -U postgres -d amazon_electronics_rag -c "SELECT * FROM pg_extension WHERE extname='vector';" | grep -q "vector"; then
    echo -e "${GREEN}✅ pgvector extension installed${NC}"
else
    echo -e "${RED}❌ pgvector extension NOT installed${NC}"
fi
echo ""

# 4. Check products table
echo "4️⃣  Checking products table..."
PRODUCT_COUNT=$(psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM products;" 2>/dev/null | tr -d ' ')
if [ "$PRODUCT_COUNT" == "348228" ]; then
    echo -e "${GREEN}✅ Products table: $PRODUCT_COUNT rows (CORRECT)${NC}"
elif [ -n "$PRODUCT_COUNT" ] && [ "$PRODUCT_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Products table: $PRODUCT_COUNT rows (Expected: 348,228)${NC}"
else
    echo -e "${RED}❌ Products table is empty or doesn't exist${NC}"
fi
echo ""

# 5. Check reviews table
echo "5️⃣  Checking reviews table..."
REVIEW_COUNT=$(psql -U postgres -d amazon_electronics_rag -t -c "SELECT COUNT(*) FROM reviews;" 2>/dev/null | tr -d ' ')
if [ "$REVIEW_COUNT" == "37512193" ]; then
    echo -e "${GREEN}✅ Reviews table: $REVIEW_COUNT rows (LOADED!)${NC}"
elif [ "$REVIEW_COUNT" == "0" ]; then
    echo -e "${YELLOW}⏸️  Reviews table: 0 rows (Pending load)${NC}"
else
    echo -e "${YELLOW}⚠️  Reviews table: $REVIEW_COUNT rows${NC}"
fi
echo ""

# 6. Check product parquet files
echo "6️⃣  Checking product parquet files..."
PRODUCT_PARQUET_DIR="$PROJECT_DIR/data/processed/raw_meta_Electronics"
if [ -d "$PRODUCT_PARQUET_DIR" ]; then
    PRODUCT_FILE_COUNT=$(ls "$PRODUCT_PARQUET_DIR"/*.parquet 2>/dev/null | wc -l | tr -d ' ')
    PRODUCT_SIZE=$(du -sh "$PRODUCT_PARQUET_DIR" 2>/dev/null | cut -f1)
    if [ "$PRODUCT_FILE_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Product parquet files: $PRODUCT_FILE_COUNT files, $PRODUCT_SIZE${NC}"
    else
        echo -e "${RED}❌ No product parquet files found${NC}"
    fi
else
    echo -e "${RED}❌ Product parquet directory not found${NC}"
fi
echo ""

# 7. Check review parquet files
echo "7️⃣  Checking review parquet files..."
REVIEW_PARQUET_DIR="$PROJECT_DIR/data/processed/reviews_Electronics"
if [ -d "$REVIEW_PARQUET_DIR" ]; then
    REVIEW_FILE_COUNT=$(ls "$REVIEW_PARQUET_DIR"/*.parquet 2>/dev/null | wc -l | tr -d ' ')
    REVIEW_SIZE=$(du -sh "$REVIEW_PARQUET_DIR" 2>/dev/null | cut -f1)
    if [ "$REVIEW_FILE_COUNT" == "10" ]; then
        echo -e "${GREEN}✅ Review parquet files: $REVIEW_FILE_COUNT files, $REVIEW_SIZE${NC}"
    elif [ "$REVIEW_FILE_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Review parquet files: $REVIEW_FILE_COUNT files (Expected: 10)${NC}"
    else
        echo -e "${RED}❌ No review parquet files found${NC}"
    fi
else
    echo -e "${RED}❌ Review parquet directory not found${NC}"
fi
echo ""

# 8. Check whitelist files
echo "8️⃣  Checking whitelist files..."
ELECTRONICS_WHITELIST="$PROJECT_DIR/logs/electronics_products_whitelist.pkl"
if [ -f "$ELECTRONICS_WHITELIST" ]; then
    WHITELIST_SIZE=$(ls -lh "$ELECTRONICS_WHITELIST" | awk '{print $5}')
    echo -e "${GREEN}✅ Electronics whitelist exists: $WHITELIST_SIZE${NC}"
else
    echo -e "${RED}❌ Electronics whitelist not found${NC}"
fi
echo ""

# 9. Check documentation
echo "9️⃣  Checking documentation..."
DOC_FILES=("$PROJECT_DIR/docs/DATASET_SECTION_IEEE_FORMAT.md" "$PROJECT_DIR/docs/PROJECT_STATUS_SUMMARY.md" "$PROJECT_DIR/docs/ESCI_ANALYSIS_REPORT.md")
DOC_COUNT=0
for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        ((DOC_COUNT++))
    fi
done
if [ "$DOC_COUNT" == "3" ]; then
    echo -e "${GREEN}✅ All documentation files present ($DOC_COUNT/3)${NC}"
else
    echo -e "${YELLOW}⚠️  Documentation files: $DOC_COUNT/3${NC}"
fi
echo ""

# 10. Check schema files
echo "🔟 Checking schema files..."
SCHEMA_FILES=("$PROJECT_DIR/schema/products_table.sql" "$PROJECT_DIR/schema/reviews_table.sql")
SCHEMA_COUNT=0
for schema in "${SCHEMA_FILES[@]}"; do
    if [ -f "$schema" ]; then
        ((SCHEMA_COUNT++))
    fi
done
if [ "$SCHEMA_COUNT" == "2" ]; then
    echo -e "${GREEN}✅ All schema files present ($SCHEMA_COUNT/2)${NC}"
else
    echo -e "${YELLOW}⚠️  Schema files: $SCHEMA_COUNT/2${NC}"
fi
echo ""

# Summary
echo "======================================================"
echo "   SUMMARY"
echo "======================================================"
echo ""
echo "Database Status:"
echo "  - Products: $PRODUCT_COUNT / 348,228"
echo "  - Reviews:  $REVIEW_COUNT / 37,512,193"
echo ""
echo "Files Status:"
echo "  - Product Parquet: $PRODUCT_FILE_COUNT files"
echo "  - Review Parquet:  $REVIEW_FILE_COUNT / 10 files"
echo "  - Documentation:   $DOC_COUNT / 3 files"
echo "  - Schema:          $SCHEMA_COUNT / 2 files"
echo ""

if [ "$PRODUCT_COUNT" == "348228" ] && [ "$REVIEW_FILE_COUNT" == "10" ]; then
    echo -e "${GREEN}🎉 READY TO PROCEED!${NC}"
    if [ "$REVIEW_COUNT" == "0" ]; then
        echo ""
        echo "Next step: Load reviews to database"
        echo "  1. Start PostgreSQL: brew services start postgresql@17"
        echo "  2. cd scripts/"
        echo "  3. python3 load_reviews_to_postgres.py"
    elif [ "$REVIEW_COUNT" == "37512193" ]; then
        echo ""
        echo -e "${GREEN}✨ ALL DATA LOADED! Ready for Phase 3 (Embeddings)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Some components need attention. Check messages above.${NC}"
fi

echo ""
echo "======================================================"

