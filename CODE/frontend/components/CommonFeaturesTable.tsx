'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface CommonFeaturesTableProps {
  allProducts: Record<string, any>
  selectedAsin: string
}

export default function CommonFeaturesTable({ allProducts, selectedAsin }: CommonFeaturesTableProps) {
  // Extract all features across all products
  const featureMap = new Map<string, { asins: string[], avgSentiment: number, totalMentions: number }>()
  
  Object.entries(allProducts).forEach(([asin, data]) => {
    const features = data?.feature_extraction?.features || []
    features.forEach((feature: any) => {
      const name = feature.feature_name.toLowerCase()
      if (!featureMap.has(name)) {
        featureMap.set(name, { asins: [], avgSentiment: 0, totalMentions: 0 })
      }
      const entry = featureMap.get(name)!
      entry.asins.push(asin)
      entry.avgSentiment += feature.net_sentiment
      entry.totalMentions += feature.positive_count + feature.negative_count
    })
  })
  
  // Calculate averages and filter for common features (mentioned in 3+ products)
  const commonFeatures = Array.from(featureMap.entries())
    .map(([name, data]) => ({
      name,
      count: data.asins.length,
      avgSentiment: data.avgSentiment / data.asins.length,
      totalMentions: data.totalMentions,
      asins: data.asins
    }))
    .filter(f => f.count >= 3)
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
  
  if (commonFeatures.length === 0) {
    return null
  }
  
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
      <h3 className="text-xl font-bold mb-4">Common Features Across Products</h3>
      <p className="text-sm text-gray-600 mb-4">
        Features mentioned in at least 3 products (showing grounding in actual reviews)
      </p>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Feature</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Products</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Total Mentions</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Avg Sentiment</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Your Product</th>
            </tr>
          </thead>
          <tbody>
            {commonFeatures.map((feature, idx) => {
              const inYourProduct = feature.asins.includes(selectedAsin)
              const yourProductData = inYourProduct 
                ? allProducts[selectedAsin]?.feature_extraction?.features?.find(
                    (f: any) => f.feature_name.toLowerCase() === feature.name
                  )
                : null
              
              return (
                <tr key={idx} className={`border-b border-gray-100 ${inYourProduct ? 'bg-yellow-50' : ''}`}>
                  <td className="py-3 px-4">
                    <span className="font-medium capitalize">{feature.name}</span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                      {feature.count} / {Object.keys(allProducts).length}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center text-gray-600">
                    {feature.totalMentions}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-center gap-2">
                      {feature.avgSentiment > 0.5 ? (
                        <>
                          <TrendingUp className="w-4 h-4 text-green-600" />
                          <span className="text-green-600 font-medium">+{feature.avgSentiment.toFixed(1)}</span>
                        </>
                      ) : feature.avgSentiment < -0.5 ? (
                        <>
                          <TrendingDown className="w-4 h-4 text-red-600" />
                          <span className="text-red-600 font-medium">{feature.avgSentiment.toFixed(1)}</span>
                        </>
                      ) : (
                        <>
                          <Minus className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600 font-medium">{feature.avgSentiment.toFixed(1)}</span>
                        </>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {inYourProduct && yourProductData ? (
                      <div className="flex items-center justify-center gap-2">
                        {yourProductData.net_sentiment > 0 ? (
                          <span className="text-green-600 font-medium">
                            ✓ +{yourProductData.net_sentiment}
                          </span>
                        ) : yourProductData.net_sentiment < 0 ? (
                          <span className="text-red-600 font-medium">
                            ✗ {yourProductData.net_sentiment}
                          </span>
                        ) : (
                          <span className="text-gray-600">~</span>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>Grounding Note:</strong> All feature analysis is extracted directly from user reviews using LLM interpretation.
          Each feature shows actual review mentions (positive 👍 and negative 👎 counts) to ensure transparency and grounding in real data.
        </p>
      </div>
    </div>
  )
}

