'use client'

import { useState } from 'react'
import { Search, TrendingUp, TrendingDown, BarChart3, Sparkles, Loader2, CheckCircle, XCircle, Target, Layers } from 'lucide-react'
import { 
  searchProducts, 
  semanticSearchProducts,
  findSimilarProducts,
  analyzeSelectedProducts,
  analyzeQuery,
  queryAwareSearch,
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
  
  // Query orchestrator state
  const [queryAnalysis, setQueryAnalysis] = useState<any>(null)
  const [isAnalyzingQuery, setIsAnalyzingQuery] = useState(false)
  const [originalQueryForContext, setOriginalQueryForContext] = useState('')
  const [chatHistory, setChatHistory] = useState<Array<{role: 'user' | 'ai', content: string}>>([])
  const [followUpQuery, setFollowUpQuery] = useState('')
  const [availableSpecs, setAvailableSpecs] = useState<any>(null)

  const sampleQueries = [
    'laptop with great battery for students',
    'good for coding and programming',
    'lightweight budget laptop',
    'gaming laptop under $1000'
  ]

  // Stage A: Search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return
    
    // COMMENTED OUT: Query Analysis (for semantic mode)
    // if (searchMode === 'semantic') {
    //   setIsAnalyzingQuery(true)
    //   setChatHistory([{role: 'user', content: searchQuery}])
    //   
    //   try {
    //     const analysis = await analyzeQuery(searchQuery)
    //     setQueryAnalysis(analysis)
    //     setAvailableSpecs(analysis.available_specs || null)
    //     
    //     if (!analysis.is_specific && analysis.confidence < 0.5) {
    //       setIsAnalyzingQuery(false)
    //       return // Show chat interface, don't search yet
    //     }
    //   } catch (err) {
    //     console.error('Query analysis failed:', err)
    //   }
    //   setIsAnalyzingQuery(false)
    // }
    
    setIsSearching(true)
    setError('')
    setStage('search')
    
    try {
      const results = searchMode === 'keyword'
        ? await searchProducts(searchQuery)
        : await semanticSearchProducts(searchQuery)
      
      setSearchResults(results.products)
      setOriginalQueryForContext(searchQuery) // Save for query-aware search
      
      if (results.products.length === 0) {
        setError(`No products found. Try: "${sampleQueries[0]}"`)
      }
      
      // Clear chat on successful search
      setChatHistory([])
      setQueryAnalysis(null)
    } catch (err) {
      setError('Search failed. Make sure backend is running on port 8000')
      console.error(err)
    } finally {
      setIsSearching(false)
    }
  }
  
  // COMMENTED OUT: Handle follow-up query from chat
  const handleFollowUpQuery = async () => {
    // if (!followUpQuery.trim()) return
    // 
    // // Add user message to chat
    // setChatHistory(prev => [...prev, {role: 'user', content: followUpQuery}])
    // 
    // setIsAnalyzingQuery(true)
    // 
    // try {
    //   const analysis = await analyzeQuery(followUpQuery)
    //   setQueryAnalysis(analysis)
    //   setAvailableSpecs(analysis.available_specs || null)
    //   
    //   if (analysis.is_specific || analysis.confidence >= 0.7) {
    //     // Good enough! Search now
    //     setSearchQuery(followUpQuery)
    //     setFollowUpQuery('')
    //     handleSearch()
    //   } else {
    //     // Still not specific, continue conversation
    //     setFollowUpQuery('')
    //   }
    // } catch (err) {
    //   console.error('Follow-up analysis failed:', err)
    // }
    // 
    // setIsAnalyzingQuery(false)
  }

  // Stage B: Find Similar
  const handleSelectProduct = async (product: Product) => {
    setSelectedProduct(product)
    setSearchResults([])
    setError('') // Clear any previous errors
    setIsFindingSimilar(true)
    setStage('similar')
    
    try {
      // Use query-aware search if we have original query context from semantic search
      if (originalQueryForContext && searchMode === 'semantic') {
        const response = await queryAwareSearch({
          original_query: originalQueryForContext,
          selected_asin: product.asin,
          mode: 'query_aware',
          k: 10
        })
        setSimilarProducts(response.products)
        setError('') // Clear error on success
      } else {
        // Fallback to regular similarity
        const response = await findSimilarProducts({
          asin: product.asin,
          mode: similarityMode,
          k: 10
        })
        setSimilarProducts(response.products)
        setError('') // Clear error on success
      }
      
      // Auto-select the original product for analysis
      setSelectedForAnalysis(new Set([product.asin]))
    } catch (err: any) {
      const errorMsg = err?.message || 'Failed to find similar products'
      setError(errorMsg)
      console.error('Similar products error:', err)
      setSimilarProducts([]) // Clear products on error
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
      console.log(`🎯 Starting analysis for ${asins.length} laptops...`)
      console.log(`📝 Original query: "${searchQuery}"`)
      const results = await analyzeSelectedProducts(asins, searchQuery)
      console.log('✅ Analysis complete!', results)
      setAnalysisResults(results)
    } catch (err: any) {
      console.error('❌ Analysis error:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Unknown error'
      setError(`Analysis failed: ${errorMsg}. Please check that the backend is running and try again.`)
      setStage('similar') // Go back to similar products stage
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

            {/* AI Analyzing Animation */}
            {isAnalyzingQuery && (
              <div className="mb-6 bg-white border-2 border-blue-300 rounded-2xl shadow-2xl overflow-hidden">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl animate-bounce">
                      🤖
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-lg">AI Search Assistant</h3>
                      <p className="text-blue-100 text-sm">Analyzing your query...</p>
                    </div>
                  </div>
                </div>
                <div className="p-6 bg-gray-50">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      AI
                    </div>
                    <div className="bg-white rounded-2xl rounded-tl-none px-5 py-4 shadow-md flex-1 border border-gray-200">
                      <div className="flex items-center gap-2">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></span>
                          <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                          <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
                        </div>
                        <span className="text-gray-600 text-sm italic">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Conversational AI Orchestrator */}
            {searchMode === 'semantic' && queryAnalysis && !queryAnalysis.is_specific && (
              <div className="mb-6 bg-white border-2 border-blue-300 rounded-2xl shadow-2xl overflow-hidden max-h-[600px] flex flex-col">
                {/* Chat Header */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl">
                        🤖
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-lg">AI Search Assistant</h3>
                        <p className="text-blue-100 text-sm">Let's find your perfect laptop together!</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setQueryAnalysis(null)
                        setChatHistory([])
                        setFollowUpQuery('')
                      }}
                      className="text-white hover:bg-white/20 rounded-lg px-3 py-1 text-sm transition-colors"
                    >
                      ✕ Close
                    </button>
                  </div>
                </div>

                {/* Chat Messages - Scrollable */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
                  {/* Render chat history */}
                  {chatHistory.map((msg, idx) => (
                    <div key={idx} className={msg.role === 'user' ? 'flex justify-end' : 'flex items-start gap-3'}>
                      {msg.role === 'ai' && (
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                          AI
                        </div>
                      )}
                      <div className={
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-md shadow-md'
                          : 'bg-white rounded-2xl rounded-tl-none px-5 py-4 shadow-md flex-1 border border-gray-200'
                      }>
                        <p className={msg.role === 'user' ? 'font-semibold' : 'text-gray-800'}>
                          {msg.content}
                        </p>
                      </div>
                    </div>
                  ))}

                  {/* AI Response - Understanding */}
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      AI
                    </div>
                    <div className="bg-white rounded-2xl rounded-tl-none px-5 py-4 shadow-md flex-1 border border-gray-200">
                      <p className="text-gray-800 mb-2">
                        I understand you're looking for a laptop, but let's get more specific to find the best matches! 🎯
                      </p>
                      <div className="bg-amber-50 border-l-4 border-amber-400 p-3 rounded-r-lg mt-3">
                        <p className="text-sm text-amber-900 font-semibold mb-1">
                          🤔 Current query confidence: {(queryAnalysis.confidence * 100).toFixed(0)}%
                        </p>
                        <p className="text-sm text-amber-800">
                          {queryAnalysis.specs_count === 0 ? 'No specific features mentioned yet.' : `${queryAnalysis.specs_count} specs detected.`}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* AI Response - Interactive Questions */}
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0">
                      💬
                    </div>
                    <div className="bg-white rounded-2xl rounded-tl-none px-5 py-4 shadow-md flex-1 border border-gray-200">
                      <p className="text-gray-800 font-semibold mb-3">
                        Can you tell me more? For example:
                      </p>
                      <div className="space-y-2 mb-4">
                        {queryAnalysis.suggestions && queryAnalysis.suggestions.map((sug: string, idx: number) => (
                          <div key={idx} className="flex items-start gap-2 bg-purple-50 p-3 rounded-lg border border-purple-200">
                            <span className="text-purple-600 font-bold flex-shrink-0">💡</span>
                            <p className="text-sm text-gray-700">{sug}</p>
                          </div>
                        ))}
                      </div>
                      
                      {/* Available specs from database */}
                      {availableSpecs && (
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-3">
                          <p className="text-sm font-semibold text-blue-900 mb-2">
                            📊 Here's what we have in our database:
                          </p>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            {availableSpecs.brands && (
                              <div>
                                <span className="font-semibold">Brands:</span> {availableSpecs.brands.slice(0, 5).join(', ')}
                              </div>
                            )}
                            {availableSpecs.price_ranges && (
                              <div>
                                <span className="font-semibold">Price:</span> ${availableSpecs.price_ranges.min} - ${availableSpecs.price_ranges.max}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <p className="text-sm text-gray-600 italic">
                        Type your refined query below with these details! ⬇️
                      </p>
                    </div>
                  </div>
                </div>

                {/* Chat Input */}
                <div className="border-t-2 border-gray-200 p-4 bg-white">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={followUpQuery}
                      onChange={(e) => setFollowUpQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleFollowUpQuery()}
                      placeholder="Type your refined search... (e.g., 'Dell laptop under $800 with 16GB RAM for students')"
                      className="flex-1 px-4 py-3 border-2 border-blue-300 rounded-xl focus:border-blue-500 focus:outline-none text-sm"
                    />
                    <button
                      onClick={handleFollowUpQuery}
                      disabled={!followUpQuery.trim()}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center gap-2 transition-all"
                    >
                      <Search className="w-5 h-5" />
                      Refine
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                    <span className="text-green-500">●</span>
                    Press Enter or click Refine to continue the conversation
                  </p>
                </div>
              </div>
            )}

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Found {searchResults.length} products
                  {searchMode === 'semantic' && <span className="text-purple-600 ml-2">(Semantic Hybrid Search)</span>}
                </h3>
                <div className="space-y-3">
                  {searchResults.map((product: any) => (
                    <div
                      key={product.asin}
                      className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 transition-all cursor-pointer"
                      onClick={() => handleSelectProduct(product)}
                    >
                      <div className="flex gap-4">
                        {/* Product Image */}
                        {product.image_url && (
                          <img 
                            src={product.image_url}
                            alt={product.title}
                            className="w-32 h-32 object-contain rounded-lg border border-gray-200 bg-white flex-shrink-0"
                            onError={(e) => {
                              e.currentTarget.src = 'https://via.placeholder.com/150?text=No+Image'
                            }}
                          />
                        )}
                        
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-gray-900 line-clamp-2">{product.title}</h4>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                            {product.price && (
                              <span className="font-semibold text-blue-600">${product.price?.toFixed(2)}</span>
                            )}
                            {product.average_rating && (
                              <span>⭐ {product.average_rating?.toFixed(1)}</span>
                            )}
                            {product.rating_number > 0 && (
                              <span>({product.rating_number} reviews)</span>
                            )}
                          </div>
                          
                          {/* Show match reason for semantic search */}
                          {searchMode === 'semantic' && (
                            <div className="mt-3 space-y-2">
                              {product.match_reason && (
                                <p className="text-xs text-purple-600 bg-purple-50 inline-block px-2 py-1 rounded">
                                  {product.match_reason}
                                </p>
                              )}
                              
                              {/* BLAIR Similarity Scores */}
                              <div className="flex gap-3 items-center">
                                {product.product_similarity > 0 && (
                                  <div className="flex items-center gap-1">
                                    <span className="text-xs font-semibold text-blue-700">📦 Product:</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                      <div 
                                        className="h-full bg-blue-500 rounded-full"
                                        style={{width: `${(product.product_similarity * 100)}%`}}
                                      ></div>
                                    </div>
                                    <span className="text-xs text-gray-700 font-mono">{product.product_similarity.toFixed(3)}</span>
                                  </div>
                                )}
                                
                                {product.review_similarity > 0 && (
                                  <div className="flex items-center gap-1">
                                    <span className="text-xs font-semibold text-purple-700">💬 Reviews:</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                      <div 
                                        className="h-full bg-purple-500 rounded-full"
                                        style={{width: `${(product.review_similarity * 100)}%`}}
                                      ></div>
                                    </div>
                                    <span className="text-xs text-gray-700 font-mono">{product.review_similarity.toFixed(3)}</span>
                                  </div>
                                )}
                                
                                {product.hybrid_score && (
                                  <div className="flex items-center gap-1">
                                    <span className="text-xs font-semibold text-green-700">✨ Total:</span>
                                    <span className="text-xs text-green-700 font-mono font-bold">{product.hybrid_score.toFixed(3)}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                        <button 
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 ml-4"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleSelectProduct(product)
                          }}
                        >
                          Select
                        </button>
                      </div>
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
            
            {/* Original Query Context */}
            {originalQueryForContext && (
              <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="text-sm text-blue-700 font-medium">
                      💡 Original search context: <strong>"{originalQueryForContext}"</strong>
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      🎯 Using query-aware search to find laptops matching your intent!
                    </p>
                  </div>
                </div>
              </div>
            )}
            
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
                    setError('')
                    try {
                      // Specs mode: Use title-based search (no query context)
                      const response = await findSimilarProducts({
                        asin: selectedProduct.asin,
                        mode: 'product',
                        k: 10
                      })
                      setSimilarProducts(response.products)
                    } catch (err: any) {
                      setError(err?.message || 'Failed to find similar products')
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
                    setError('')
                    try {
                      // Reviews mode: Use query-aware if available
                      if (originalQueryForContext && searchMode === 'semantic') {
                        const response = await queryAwareSearch({
                          original_query: originalQueryForContext,
                          selected_asin: selectedProduct.asin,
                          mode: 'query_aware',
                          k: 10
                        })
                        setSimilarProducts(response.products)
                      } else {
                        const response = await findSimilarProducts({
                          asin: selectedProduct.asin,
                          mode: 'reviews',
                          k: 10
                        })
                        setSimilarProducts(response.products)
                      }
                    } catch (err: any) {
                      setError(err?.message || 'Failed to find similar products')
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
                  <div className="text-xs text-gray-600">
                    {originalQueryForContext && searchMode === 'semantic' ? 'Query + Reviews' : 'Similar experiences'}
                  </div>
                </button>
                <button
                  onClick={async () => {
                    setSimilarityMode('combined')
                    setIsFindingSimilar(true)
                    setError('')
                    try {
                      // Combined mode: Use query-aware if available
                      if (originalQueryForContext && searchMode === 'semantic') {
                        const response = await queryAwareSearch({
                          original_query: originalQueryForContext,
                          selected_asin: selectedProduct.asin,
                          mode: 'query_aware',
                          k: 10
                        })
                        setSimilarProducts(response.products)
                      } else {
                        const response = await findSimilarProducts({
                          asin: selectedProduct.asin,
                          mode: 'combined',
                          k: 10
                        })
                        setSimilarProducts(response.products)
                      }
                    } catch (err: any) {
                      setError(err?.message || 'Failed to find similar products')
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
                  <div className="text-xs text-gray-600">
                    {originalQueryForContext && searchMode === 'semantic' ? 'Query + Product + Reviews' : 'Specs + Reviews'}
                  </div>
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
                    
                    {/* Product Image */}
                    {selectedProduct.image_url && (
                      <img 
                        src={selectedProduct.image_url}
                        alt={selectedProduct.title}
                        className="w-24 h-24 object-contain rounded-lg border border-yellow-400 bg-white"
                        onError={(e) => {
                          e.currentTarget.src = 'https://via.placeholder.com/120?text=No+Image'
                        }}
                      />
                    )}
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-yellow-600">⭐</span>
                        <span className="font-semibold">Your Selection</span>
                      </div>
                      <div className="font-medium line-clamp-2">{selectedProduct.title}</div>
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
                      
                      {/* Product Image */}
                      {product.image_url && (
                        <img 
                          src={product.image_url}
                          alt={product.title}
                          className="w-20 h-20 object-contain rounded-lg border border-gray-200 bg-white"
                          onError={(e) => {
                            e.currentTarget.src = 'https://via.placeholder.com/100?text=No+Image'
                          }}
                        />
                      )}
                      
                      <div className="flex-1">
                        <div className="font-medium line-clamp-2">#{idx + 1}. {product.title}</div>
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

            {/* AI Recommendation Summary */}
            {analysisResults.recommendation && (
              <div className="bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 rounded-2xl shadow-xl p-8 mt-8 border-2 border-green-200">
                <div className="flex items-start gap-4">
                  <div className="text-5xl">💡</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                      <Sparkles className="w-6 h-6 text-green-600" />
                      AI-Powered Recommendation
                    </h3>
                    
                    <div className="bg-white p-6 rounded-xl shadow-md mb-4">
                      <p className="text-gray-800 leading-relaxed text-lg">
                        {analysisResults.recommendation.text}
                      </p>
                    </div>

                    {analysisResults.recommendation.price_tiers && (
                      <div className="grid md:grid-cols-3 gap-4 mt-4">
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">💰</span>
                            <h4 className="font-semibold text-blue-900">Budget Tier</h4>
                          </div>
                          <p className="text-sm text-blue-700">{analysisResults.recommendation.price_tiers.budget.range}</p>
                          <p className="text-xs text-blue-600 mt-1">{analysisResults.recommendation.price_tiers.budget.count} laptop(s)</p>
                        </div>

                        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">⭐</span>
                            <h4 className="font-semibold text-purple-900">Mid Tier</h4>
                          </div>
                          <p className="text-sm text-purple-700">{analysisResults.recommendation.price_tiers.mid.range}</p>
                          <p className="text-xs text-purple-600 mt-1">{analysisResults.recommendation.price_tiers.mid.count} laptop(s)</p>
                        </div>

                        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">👑</span>
                            <h4 className="font-semibold text-green-900">Premium Tier</h4>
                          </div>
                          <p className="text-sm text-green-700">{analysisResults.recommendation.price_tiers.premium.range}</p>
                          <p className="text-xs text-green-600 mt-1">{analysisResults.recommendation.price_tiers.premium.count} laptop(s)</p>
                        </div>
                      </div>
                    )}

                    <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <p className="text-xs text-gray-600 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-yellow-600" />
                        Generated by GPT-4 based on your search query and sentiment analysis
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

