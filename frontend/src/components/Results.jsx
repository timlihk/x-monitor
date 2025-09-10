import React, { useState, useEffect } from 'react'
import { ExternalLink, Calendar, MessageSquare } from 'lucide-react'
import { resultsApi } from '../services/api'
import LoadingSpinner from './LoadingSpinner'

const Results = () => {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedResult, setSelectedResult] = useState(null)

  useEffect(() => {
    loadResults()
  }, [])

  const loadResults = async () => {
    try {
      const response = await resultsApi.getAll()
      setResults(response.data)
    } catch (error) {
      console.error('Error loading results:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatSummary = (summary) => {
    if (!summary) return 'No summary available'
    
    return summary.split('\n').map((line, index) => {
      if (line.trim() === '') return null
      return (
        <p key={index} className="mb-2">
          {line}
        </p>
      )
    }).filter(Boolean)
  }

  const getTopTweets = (tweets) => {
    if (!tweets || !Array.isArray(tweets)) return []
    
    return tweets
      .sort((a, b) => {
        const aMetrics = a.public_metrics || {}
        const bMetrics = b.public_metrics || {}
        return (bMetrics.like_count + bMetrics.retweet_count) - (aMetrics.like_count + aMetrics.retweet_count)
      })
      .slice(0, 5)
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <div className="px-4 py-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Analysis Results</h1>
          <p className="mt-2 text-sm text-gray-700">
            View summaries and top tweets from your monitored terms.
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {results.map((result) => (
          <div
            key={result.id}
            className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedResult(selectedResult === result.id ? null : result.id)}
          >
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">
                  {result.monitored_term?.keyword || 'Unknown Term'}
                </h3>
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-1" />
                  {new Date(result.created_at).toLocaleDateString()}
                </div>
              </div>
              
              <div className="mt-4">
                <div className="text-sm text-gray-600">
                  {formatSummary(result.summary).slice(0, 2)}
                </div>
                
                {selectedResult === result.id && (
                  <>
                    <div className="mt-4">
                      <div className="text-sm text-gray-600">
                        {formatSummary(result.summary).slice(2)}
                      </div>
                    </div>
                    
                    {result.tweets_raw && result.tweets_raw.length > 0 && (
                      <div className="mt-6">
                        <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                          <MessageSquare className="h-4 w-4 mr-2" />
                          Top Tweets ({getTopTweets(result.tweets_raw).length})
                        </h4>
                        <div className="space-y-3">
                          {getTopTweets(result.tweets_raw).map((tweet) => (
                            <div key={tweet.id} className="bg-gray-50 rounded-lg p-3">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2 mb-2">
                                    {tweet.author && (
                                      <span className="text-sm font-medium text-gray-900">
                                        @{tweet.author.username}
                                        {tweet.author.verified && <span className="text-blue-500 ml-1">✓</span>}
                                      </span>
                                    )}
                                    <span className="text-xs text-gray-500">
                                      {new Date(tweet.created_at).toLocaleDateString()}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-700 mb-2">{tweet.text}</p>
                                  {tweet.public_metrics && (
                                    <div className="flex space-x-4 text-xs text-gray-500">
                                      <span>❤️ {tweet.public_metrics.like_count || 0}</span>
                                      <span>🔄 {tweet.public_metrics.retweet_count || 0}</span>
                                      <span>💬 {tweet.public_metrics.reply_count || 0}</span>
                                    </div>
                                  )}
                                </div>
                                <a
                                  href={tweet.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="ml-3 text-blue-600 hover:text-blue-800"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <ExternalLink className="h-4 w-4" />
                                </a>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
              
              <div className="mt-4 text-xs text-gray-400 text-center">
                {selectedResult === result.id ? 'Click to collapse' : 'Click to expand'}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {results.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No results yet. Run some analyses to see summaries here!</p>
        </div>
      )}
    </div>
  )
}

export default Results