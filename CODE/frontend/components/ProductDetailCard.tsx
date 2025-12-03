'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, MessageSquare } from 'lucide-react'

interface Feature {
  feature_name: string
  positive_mentions: string[]
  negative_mentions: string[]
  positive_count: number
  negative_count: number
  net_sentiment: number
}

interface ProductDetailCardProps {
  rank: number
  title: string
  price: number
  sentimentScore: number
  isOriginal: boolean
  features?: Feature[]
  numReviews?: number
  keyStrengths?: string[]
  keyWeaknesses?: string[]
}

export default function ProductDetailCard({
  rank,
  title,
  price,
  sentimentScore,
  isOriginal,
  features = [],
  numReviews = 0,
  keyStrengths = [],
  keyWeaknesses = []
}: ProductDetailCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div
      className={`rounded-lg border-2 transition-all ${
        isOriginal
          ? 'bg-yellow-50 border-yellow-400 shadow-lg'
          : 'bg-white border-gray-200 hover:border-gray-300'
      }`}
    >
      {/* Main Card */}
      <div
        className="p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-bold text-lg">#{rank}</span>
              {isOriginal && <span className="text-yellow-600">⭐ Your Product</span>}
            </div>
            <h4 className="font-medium text-gray-900 mb-1 truncate" title={title}>
              {title}
            </h4>
            <p className="text-sm text-gray-600">
              {numReviews} reviews analyzed
            </p>
          </div>
          <div className="flex items-start gap-4 ml-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">Price</p>
              <p className="font-bold text-blue-600">${price.toFixed(2)}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Sentiment</p>
              <p className="font-bold text-purple-600">{sentimentScore.toFixed(1)}</p>
            </div>
            <button className="p-1">
              {isExpanded ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          {/* Full Title */}
          <div className="mb-4 p-3 bg-white rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">Full Product Name:</p>
            <p className="text-sm text-gray-900">{title}</p>
          </div>

          {/* Key Strengths & Weaknesses */}
          {(keyStrengths.length > 0 || keyWeaknesses.length > 0) && (
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              {/* Strengths */}
              {keyStrengths.length > 0 && (
                <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <ThumbsUp className="w-4 h-4 text-green-600" />
                    <h5 className="font-semibold text-green-900">What Users Love</h5>
                  </div>
                  <ul className="space-y-1">
                    {keyStrengths.slice(0, 5).map((strength, idx) => (
                      <li key={idx} className="text-sm text-green-800 flex items-start gap-2">
                        <span className="text-green-600 mt-0.5">✓</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {keyWeaknesses.length > 0 && (
                <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-2">
                    <ThumbsDown className="w-4 h-4 text-red-600" />
                    <h5 className="font-semibold text-red-900">User Complaints</h5>
                  </div>
                  <ul className="space-y-1">
                    {keyWeaknesses.slice(0, 5).map((weakness, idx) => (
                      <li key={idx} className="text-sm text-red-800 flex items-start gap-2">
                        <span className="text-red-600 mt-0.5">✗</span>
                        <span>{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Feature Breakdown */}
          {features.length > 0 && (
            <div className="p-3 bg-white rounded-lg border border-gray-200">
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare className="w-4 h-4 text-blue-600" />
                <h5 className="font-semibold text-gray-900">Feature Analysis from Reviews</h5>
              </div>
              <div className="space-y-2">
                {features.slice(0, 8).map((feature, idx) => (
                  <div key={idx} className="p-2 bg-gray-50 rounded">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm text-gray-900 capitalize">
                        {feature.feature_name}
                      </span>
                      <div className="flex items-center gap-3 text-xs">
                        <span className="text-green-600">
                          👍 {feature.positive_count}
                        </span>
                        <span className="text-red-600">
                          👎 {feature.negative_count}
                        </span>
                        <span
                          className={`font-semibold ${
                            feature.net_sentiment > 0
                              ? 'text-green-600'
                              : feature.net_sentiment < 0
                              ? 'text-red-600'
                              : 'text-gray-600'
                          }`}
                        >
                          {feature.net_sentiment > 0 ? '+' : ''}
                          {feature.net_sentiment}
                        </span>
                      </div>
                    </div>
                    
                    {/* Sample mentions */}
                    {feature.positive_mentions.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs text-green-700 italic">
                          "{feature.positive_mentions[0]}"
                        </p>
                      </div>
                    )}
                    {feature.negative_mentions.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs text-red-700 italic">
                          "{feature.negative_mentions[0]}"
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No features message */}
          {features.length === 0 && (
            <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200 text-center">
              <p className="text-sm text-yellow-800">
                No reviews found for detailed analysis
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

