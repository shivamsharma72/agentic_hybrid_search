#!/bin/bash

echo "=========================================="
echo "PUSHING DUAL RANKING SYSTEM TO GITHUB"
echo "=========================================="
echo ""
echo "Repository: https://github.com/shivamsharma72/agentic_hybrid_search"
echo "New Branch: dual_ranking_system"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo "📁 Working directory: $PROJECT_DIR"
echo ""

# Step 1: Initialize git if not already
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi
echo ""

# Step 2: Add remote (if not already added)
echo "🔗 Setting up remote..."
if git remote | grep -q "origin"; then
    echo "   Remote 'origin' already exists, updating URL..."
    git remote set-url origin git@github.com:shivamsharma72/agentic_hybrid_search.git
else
    echo "   Adding remote 'origin'..."
    git remote add origin git@github.com:shivamsharma72/agentic_hybrid_search.git
fi
echo "✅ Remote configured: git@github.com:shivamsharma72/agentic_hybrid_search.git"
echo ""

# Step 3: Create new branch
echo "🌿 Creating new branch: dual_ranking_system"
git checkout -b dual_ranking_system
echo "✅ Branch created and checked out"
echo ""

# Step 4: Add all files (respecting .gitignore)
echo "📦 Adding files to git..."
git add .
echo "✅ Files staged"
echo ""

# Step 5: Show what will be committed
echo "📋 Files to be committed:"
echo "----------------------------------------"
git status --short | head -20
echo "..."
echo "----------------------------------------"
echo ""

# Count files
TOTAL_FILES=$(git status --short | wc -l | tr -d ' ')
echo "Total files: $TOTAL_FILES"
echo ""

# Check for large files
echo "🔍 Checking for large files..."
LARGE_FILES=$(git ls-files | xargs ls -lh 2>/dev/null | awk '$5 ~ /M$/ {print $9, $5}' | head -10)
if [ -n "$LARGE_FILES" ]; then
    echo "⚠️  Large files found:"
    echo "$LARGE_FILES"
    echo ""
    echo "Note: .parquet files should be excluded by .gitignore"
else
    echo "✅ No large files detected"
fi
echo ""

# Verify .parquet files are excluded
echo "🔍 Verifying .parquet files are excluded..."
PARQUET_COUNT=$(git ls-files | grep -c "\.parquet$" || true)
if [ "$PARQUET_COUNT" -eq 0 ]; then
    echo "✅ No .parquet files in git (correct!)"
else
    echo "❌ WARNING: Found $PARQUET_COUNT .parquet files in git!"
    echo "   These should be excluded by .gitignore"
    git ls-files | grep "\.parquet$"
    echo ""
    echo "Do you want to continue? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi
echo ""

# Step 6: Commit
echo "💾 Committing changes..."
git commit -m "Add dual ranking system with BLAIR-RoBERTa semantic search

- Complete Next.js + FastAPI application
- BLAIR-RoBERTa hybrid search (products + reviews)
- Query-aware similarity search
- LLM-powered dual ranking (price vs sentiment)
- GPT-4 purchase recommendations
- Evaluation system with 76.96% Recall@50
- Complete documentation and setup scripts
- Data downloadable from Dropbox (1.17 GB)"

echo "✅ Commit created"
echo ""

# Step 7: Show commit info
echo "📝 Commit details:"
echo "----------------------------------------"
git log --oneline -1
echo "----------------------------------------"
echo ""

# Step 8: Push to GitHub
echo "🚀 Pushing to GitHub..."
echo "   Branch: dual_ranking_system"
echo "   Remote: origin (git@github.com:shivamsharma72/agentic_hybrid_search.git)"
echo ""

git push -u origin dual_ranking_system

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! PUSHED TO GITHUB!"
    echo "=========================================="
    echo ""
    echo "🌐 View your branch:"
    echo "   https://github.com/shivamsharma72/agentic_hybrid_search/tree/dual_ranking_system"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Go to GitHub and verify files are there"
    echo "   2. Check that .parquet files are NOT in the repo"
    echo "   3. Verify README.md shows Dropbox links"
    echo "   4. Create a Pull Request if you want to merge to main"
    echo ""
    echo "🎉 Your dual ranking system is now on GitHub!"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ PUSH FAILED"
    echo "=========================================="
    echo ""
    echo "Common issues:"
    echo "   1. SSH key not configured - run: ssh -T git@github.com"
    echo "   2. No internet connection"
    echo "   3. Repository permissions issue"
    echo ""
    echo "Try running manually:"
    echo "   git push -u origin dual_ranking_system"
    echo ""
fi

