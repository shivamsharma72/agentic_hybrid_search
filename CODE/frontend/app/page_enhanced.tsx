'use client'

import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, BarChart3, Sparkles, Loader2, CheckCircle, XCircle, Target, Layers } from 'lucide-react'
import { 
  searchProducts, 
  semanticSearchProducts,
  findSimilarProducts,
  analyzeSelectedProducts,
  type Product, 
  type DualRankingResponse 
} from '@/lib/api'
import ProductDetailCard from '@/components/ProductDetailCard'
import CommonFeaturesTable from '@/components/CommonFeaturesTable'

export default function Home() {
  // Search state (Stage A)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('keyword')
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [isSearching, setIsSearching] = useState(false)
  
  // Similar products state (Stage B)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [similarityMode, setSimilarityMode] = useState<'product' | 'reviews' | 'combined'>('combined')
  const [similarProducts, setSimilarProducts] = useState<Product[]>([])
  const [isFindingSimilar, setIsFindingSimilar] = useState(false)
  const [selectedForAnalysis, setSelectedForAnalysis] = useState<Set<string>>(new Set())
  
  // Analysis state (Stage C)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<DualRankingResponse | null>(null)
  
  // UI state
  const [error, setError] = useState('')
  const [stage, setStage] = useState<'search' | 'similar' | 'analysis'>('search')

  const sampleQueries = [
    'laptop with great battery for students',
    'good for coding and programming',
    'lightweight budget laptop',
    'gaming laptop under $1000'
  ]

  // Stage A: Search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    setIsSearching(true)
    setError('')
    setStage('search')
    
    try {
      const results = searchMode === 'keyword'
        ? await searchProducts(searchQuery)
        : await semanticSearchProducts(searchQuery)
      
      setSearchResults(results.products)
      if (results.products.length === 0) {
        setError(`No products found. Try: "${sampleQueries[0]}"`)
      }
    } catch (err) {
      setError('Search failed. Make sure backend is running on port 8000')
      console.error(err)
    } finally {
      setIsSearching(false)
    }
  }

  // Stage B: Find Similar
  const handleSelectProduct = async (product: Product) => {
    setSelectedProduct(product)
    setSearchResults([])
    setError('')
    setIsFindingSimilar(true)
    setStage('similar')
    
    try {
      const response = await findSimilarProducts({
        asin: product.asin,
        mode: similarityMode,
        k: 10
      })
      
      setSimilarProducts(response.products)
      
      // Auto-select the original product for analysis
      setSelectedForAnalysis(new Set([product.asin]))
    } catch (err) {
      setError('Failed to find similar products')
      console.error(err)
    } finally {
      setIsFindingSimilar(false)
    }
  }

  // Toggle product selection for analysis
  const toggleProductSelection = (asin: string) => {
    const newSelection = new Set(selectedForAnalysis)
    if (newSelection.has(asin)) {
      newSelection.delete(asin)
    } else {
      newSelection.add(asin)
    }
    setSelectedForAnalysis(newSelection)
  }

  // Stage C: Analyze Selected
  const handleAnalyzeSelected = async () => {
    if (selectedForAnalysis.size < 2) {
      setError('Please select at least 2 laptops to analyze')
      return
    }
    
    setIsAnalyzing(true)
    setError('')
    setStage('analysis')
    
    try {
      const asins = Array.from(selectedForAnalysis)
      const results = await analyzeSelectedProducts(asins)
      setAnalysisResults(results)
    } catch (err) {
      setError('Analysis failed. This may take 30-40 seconds.')
      console.error(err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const resetToSearch = () => {
    setStage('search')
    setSelectedProduct(null)
    setSimilarProducts([])
    setSelectedForAnalysis(new Set())
    setAnalysisResults(null)
    setError('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            🤖 Laptop Dual Ranking Analysis
          </h1>
          <p className="text-xl text-gray-600">
            Search by reviews • Find similar products • Compare price vs. sentiment
          </p>
        </div>

        {/* Stage Indicator */}
        <div className="flex justify-center items-center gap-4 mb-8">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${stage === 'search' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-400'}`}>
            <Search className="w-5 h-5" />
            <span className="font-semibold">Stage A: Search</span>
          </div>
          <div className={`w-8 h-0.5 ${stage !== 'search' ? 'bg-blue-500' : 'bg-gray-300'}`} />
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${stage === 'similar' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-400'}`}>
            <Target className="w-5 h-5" />
            <span className="font-semibold">Stage B: Find Similar</span>
          </div>
          <div className={`w-8 h-0.5 ${stage === 'analysis' ? 'bg-purple-500' : 'bg-gray-300'}`} />
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${stage === 'analysis' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'}`}>
            <BarChart3 className="w-5 h-5" />
            <span className="font-semibold">Stage C: Analysis</span>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Stage A: Search */}
        {stage === 'search' && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6">🔍 Search for Laptops</h2>
            
            {/* Search Mode Toggle */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Search Mode:
              </label>
              <div className="flex gap-4">
                <button
                  onClick={() => setSearchMode('keyword')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    searchMode === 'keyword'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">Keyword Search</div>
                  <div className="text-sm text-gray-600">Search by product title</div>
                </button>
                <button
                  onClick={() => setSearchMode('semantic')}
                  className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all ${
                    searchMode === 'semantic'
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">✨ Semantic Review Search</div>
                  <div className="text-sm text-gray-600">Search by what users say in reviews</div>
                </button>
              </div>
            </div>

            {/* Search Input */}
            <div className="flex gap-4 mb-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder={
                  searchMode === 'keyword'
                    ? 'Enter product name (e.g., "Dell XPS", "ThinkPad")'
                    : 'Describe what you want (e.g., "great battery for students")'
                }
                className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              />
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 flex items-center gap-2 font-semibold"
              >
                {isSearching ? (
                  <><Loader2 className="w-5 h-5 animate-spin" /> Searching...</>
                ) : (
                  <><Search className="w-5 h-5" /> Search</>
                )}
              </button>
            </div>

            {/* Sample Queries */}
            {searchMode === 'semantic' && (
              <div className="mb-6">
                <p className="text-sm text-gray-600 mb-2">💡 Try these queries:</p>
                <div className="flex flex-wrap gap-2">
                  {sampleQueries.map((query, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSearchQuery(query)}
                      className="text-sm px-3 py-1 bg-purple-50 text-purple-700 rounded-full hover:bg-purple-100 transition-colors"
                    >
                      "{query}"
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Found {searchResults.length} products:</h3>
                <div className="space-y-3">
                  {searchResults.map((product) => (
                    <div
                      key={product.asin}
                      className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 transition-all cursor-pointer flex items-center justify-between"
                      onClick={() => handleSelectProduct(product)}
                    >
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{product.title}</h4>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                          <span className="font-semibold text-blue-600">${product.price?.toFixed(2)}</span>
                          <span>⭐ {product.average_rating?.toFixed(1)}</span>
                          <span>({product.rating_number} reviews)</span>
                        </div>
                      </div>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Select
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Stage B: Find Similar Products */}
        {stage === 'similar' && selectedProduct && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <button onClick={resetToSearch} className="text-blue-600 hover:text-blue-800 mb-4">
              ← Back to Search
            </button>
            
            <h2 className="text-2xl font-bold mb-6">🎯 Find Similar Laptops</h2>
            
            {/* Selected Product */}
            <div className="p-4 bg-yellow-50 border-2 border-yellow-400 rounded-lg mb-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-yellow-600">⭐</span>
                <span className="font-semibold">Your Selection:</span>
              </div>
              <h3 className="font-semibold text-gray-900">{selectedProduct.title}</h3>
              <div className="flex gap-4 mt-2 text-sm text-gray-600">
                <span className="font-semibold text-blue-600">${selectedProduct.price?.toFixed(2)}</span>
                <span>⭐ {selectedProduct.average_rating?.toFixed(1)}</span>
              </div>
            </div>

            {/* Similarity Mode Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Find similar laptops by:
              </label>
              <div className="grid md:grid-cols-3 gap-4">
                <button
                  onClick={async () => {
                    setSimilarityMode('product')
                    setIsFindingSimilar(true)
                    try {
                      const response = await findSimilarProducts({
                        asin: selectedProduct.asin,
                        mode: 'product',
                        k: 10
                      })
                      setSimilarProducts(response.products)
                    } finally {
                      setIsFindingSimilar(false)
                    }
                  }}
                  className={`py-3 px-4 rounded-lg border-2 transition-all ${
                    similarityMode === 'product'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">📦 Specifications</div>
                  <div className="text-xs text-gray-600">Brand, specs, category</div>
                </button>
                <button
                  onClick={async () => {
                    setSimilarityMode('reviews')
                    setIsFindingSimilar(true)
                    try {
                      const response = await findSimilarProducts({
                        asin: selectedProduct.asin,
                        mode: 'reviews',
                        k: 10
                      })
                      setSimilarProducts(response.products)
                    } finally {
                      setIsFindingSimilar(false)
                    }
                  }}
                  className={`py-3 px-4 rounded-lg border-2 transition-all ${
                    similarityMode === 'reviews'
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">💬 User Reviews</div>
                  <div className="text-xs text-gray-600">Similar experiences</div>
                </button>
                <button
                  onClick={async () => {
                    setSimilarityMode('combined')
                    setIsFindingSimilar(true)
                    try {
                      const response = await findSimilarProducts({
                        asin: selectedProduct.asin,
                        mode: 'combined',
                        k: 10
                      })
                      setSimilarProducts(response.products)
                    } finally {
                      setIsFindingSimilar(false)
                    }
                  }}
                  className={`py-3 px-4 rounded-lg border-2 transition-all ${
                    similarityMode === 'combined'
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-semibold">✨ Combined (Best!)</div>
                  <div className="text-xs text-gray-600">Specs + Reviews</div>
                </button>
              </div>
            </div>

            {/* Similar Products List with Checkboxes */}
            {isFindingSimilar ? (
              <div className="text-center py-8">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                <p className="text-gray-600">Finding similar laptops...</p>
              </div>
            ) : similarProducts.length > 0 ? (
              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Select laptops to analyze ({selectedForAnalysis.size} selected):
                </h3>
                <div className="space-y-2 mb-6">
                  {/* Original product first */}
                  <label className="flex items-start gap-3 p-4 border-2 border-yellow-400 bg-yellow-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedForAnalysis.has(selectedProduct.asin)}
                      onChange={() => toggleProductSelection(selectedProduct.asin)}
                      className="mt-1 w-5 h-5"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-yellow-600">⭐</span>
                        <span className="font-semibold">Your Selection</span>
                      </div>
                      <div className="font-medium">{selectedProduct.title}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        ${selectedProduct.price?.toFixed(2)} | ⭐ {selectedProduct.average_rating?.toFixed(1)}
                      </div>
                    </div>
                  </label>
                  
                  {/* Similar products */}
                  {similarProducts.map((product, idx) => (
                    <label
                      key={product.asin}
                      className="flex items-start gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 cursor-pointer transition-all"
                    >
                      <input
                        type="checkbox"
                        checked={selectedForAnalysis.has(product.asin)}
                        onChange={() => toggleProductSelection(product.asin)}
                        className="mt-1 w-5 h-5"
                      />
                      <div className="flex-1">
                        <div className="font-medium">#{idx + 1}. {product.title}</div>
                        <div className="text-sm text-gray-600 mt-1">
                          ${product.price?.toFixed(2)} | ⭐ {product.average_rating?.toFixed(1)} | 
                          Similarity: {product.similarity?.toFixed(2)}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>

                {/* Analyze Button */}
                <div className="flex gap-4">
                  <button
                    onClick={handleAnalyzeSelected}
                    disabled={selectedForAnalysis.size < 2}
                    className="flex-1 px-6 py-4 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2 font-semibold text-lg"
                  >
                    <Sparkles className="w-6 h-6" />
                    Analyze Selected ({selectedForAnalysis.size} laptops)
                  </button>
                </div>
                {selectedForAnalysis.size < 2 && (
                  <p className="text-sm text-red-600 mt-2 text-center">
                    Please select at least 2 laptops to analyze
                  </p>
                )}
              </div>
            ) : null}
          </div>
        )}

        {/* Stage C: Analysis Results */}
        {isAnalyzing && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <Loader2 className="w-16 h-16 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-2xl font-semibold mb-2">Analyzing {selectedForAnalysis.size} Laptops...</h3>
            <p className="text-gray-600">Extracting features from reviews using AI (30-40 seconds)</p>
          </div>
        )}

        {stage === 'analysis' && analysisResults && !isAnalyzing && (
          <>
            {/* New Analysis Button */}
            <div className="mb-8">
              <button
                onClick={resetToSearch}
                className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
              >
                ← New Analysis
              </button>
            </div>

            {/* Summary */}
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
              <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>
              
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Product</p>
                  <p className="font-semibold mt-1">{analysisResults.original_product.title.substring(0, 30)}...</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Price Rank</p>
                  <p className="font-semibold text-2xl mt-1">#{analysisResults.comparison.price_rank}</p>
                  <p className="text-xs text-gray-500">of {analysisResults.comparison.total_products}</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">Sentiment Rank</p>
                  <p className="font-semibold text-2xl mt-1">#{analysisResults.comparison.sentiment_rank}</p>
                  <p className="text-xs text-gray-500">of {analysisResults.comparison.total_products}</p>
                </div>
                <div className={`p-4 rounded-lg ${analysisResults.comparison.better_value ? 'bg-green-50' : 'bg-yellow-50'}`}>
                  <p className="text-sm text-gray-600">Value Analysis</p>
                  <p className="font-semibold mt-1 flex items-center gap-2">
                    {analysisResults.comparison.better_value ? (
                      <><CheckCircle className="w-5 h-5 text-green-600" /> Good Value</>
                    ) : (
                      <><XCircle className="w-5 h-5 text-yellow-600" /> Premium</>
                    )}
                  </p>
                </div>
              </div>

              <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                <h3 className="font-semibold mb-2">What This Means:</h3>
                <p className="text-gray-700">
                  Your product ranks <strong>#{analysisResults.comparison.price_rank}</strong> by price and{' '}
                  <strong>#{analysisResults.comparison.sentiment_rank}</strong> by user reviews.
                  {analysisResults.comparison.better_value ? (
                    <span className="text-green-700 font-medium"> Users LOVE this product despite mid-range pricing - Great value! ✅</span>
                  ) : (
                    <span className="text-yellow-700 font-medium"> Premium product - High price matches high quality ⚠️</span>
                  )}
                </p>
              </div>
            </div>

            {/* Common Features Comparison */}
            <CommonFeaturesTable 
              allProducts={analysisResults.all_products}
              selectedAsin={analysisResults.original_product.asin}
            />

            {/* Rankings */}
            <div className="grid md:grid-cols-2 gap-8">
              {/* Price Ranking */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                  Price Ranking (Low → High)
                </h3>
                <div className="space-y-3">
                  {analysisResults.price_ranking.map((product) => {
                    const productData = analysisResults.all_products[product.asin]
                    const features = productData?.feature_extraction?.features || []
                    const keyStrengths = features
                      .filter((f: any) => f.net_sentiment > 0)
                      .sort((a: any, b: any) => b.net_sentiment - a.net_sentiment)
                      .slice(0, 5)
                      .map((f: any) => `${f.feature_name}: ${f.positive_mentions[0] || 'positive'}`)
                    const keyWeaknesses = features
                      .filter((f: any) => f.net_sentiment < 0)
                      .sort((a: any, b: any) => a.net_sentiment - b.net_sentiment)
                      .slice(0, 5)
                      .map((f: any) => `${f.feature_name}: ${f.negative_mentions[0] || 'negative'}`)

                    return (
                      <ProductDetailCard
                        key={product.asin}
                        rank={product.rank}
                        title={product.title}
                        price={product.price || 0}
                        sentimentScore={product.sentiment_score || 0}
                        isOriginal={product.asin === analysisResults.original_product.asin}
                        features={features}
                        numReviews={productData?.num_reviews_fetched || 0}
                        keyStrengths={keyStrengths}
                        keyWeaknesses={keyWeaknesses}
                      />
                    )
                  })}
                </div>
              </div>

              {/* Sentiment Ranking */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-6 h-6 text-purple-600" />
                  Sentiment Ranking (Best → Worst Reviews)
                </h3>
                <div className="space-y-3">
                  {analysisResults.sentiment_ranking.map((product) => {
                    const productData = analysisResults.all_products[product.asin]
                    const features = productData?.feature_extraction?.features || []
                    const keyStrengths = features
                      .filter((f: any) => f.net_sentiment > 0)
                      .sort((a: any, b: any) => b.net_sentiment - a.net_sentiment)
                      .slice(0, 5)
                      .map((f: any) => `${f.feature_name}: ${f.positive_mentions[0] || 'positive'}`)
                    const keyWeaknesses = features
                      .filter((f: any) => f.net_sentiment < 0)
                      .sort((a: any, b: any) => a.net_sentiment - b.net_sentiment)
                      .slice(0, 5)
                      .map((f: any) => `${f.feature_name}: ${f.negative_mentions[0] || 'negative'}`)

                    return (
                      <ProductDetailCard
                        key={product.asin}
                        rank={product.rank}
                        title={product.title}
                        price={product.price || 0}
                        sentimentScore={product.sentiment_score || 0}
                        isOriginal={product.asin === analysisResults.original_product.asin}
                        features={features}
                        numReviews={productData?.num_reviews_fetched || 0}
                        keyStrengths={keyStrengths}
                        keyWeaknesses={keyWeaknesses}
                      />
                    )
                  })}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

