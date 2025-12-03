#!/bin/bash

echo "🚀 Setting up Modern Dual Ranking System"
echo "============================================"
echo ""

# Get the directory where this script is located
DIR="$(cd "$(dirname "$0")" && pwd)"

# Step 1: Backend Setup
echo "📦 Step 1: Setting up FastAPI Backend..."
cd "$DIR/backend"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

echo "✅ Backend ready"
echo ""

# Step 2: Frontend Setup
echo "🎨 Step 2: Setting up Next.js Frontend..."
cd "$DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "This will initialize Next.js. Please answer the prompts:"
    echo ""
    echo "Recommended answers:"
    echo "- TypeScript? Yes"
    echo "- ESLint? Yes"
    echo "- Tailwind CSS? Yes"
    echo "- src/ directory? No"
    echo "- App Router? Yes"
    echo "- Turbopack? No"
    echo "- Customize import alias? No"
    echo ""
    
    npx create-next-app@latest . --typescript --tailwind --app --eslint
    
    echo ""
    echo "Installing additional dependencies..."
    npm install axios recharts lucide-react clsx tailwind-merge
else
    echo "✅ Frontend already initialized"
fi

echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Start Backend - Terminal 1:"
echo "   cd dual_ranking_nextjs/CODE/backend"
echo "   ./run_backend.sh"
echo ""
echo "2. Start Frontend - Terminal 2:"
echo "   cd dual_ranking_nextjs/CODE/frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3001"
echo ""
echo "📖 See README.md for more information"
echo ""
