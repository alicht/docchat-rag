import React, { useState, useEffect } from 'react'
import { XMarkIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

interface TopicItem {
  filename: string
  topic?: string | null
  page?: number | null
  line?: number | null
  preview: string
}

interface ListTopicsResponse {
  topics: TopicItem[]
  total: number
  page: number
  limit: number
  has_more: boolean
}

interface TopicBrowserProps {
  isOpen: boolean
  onToggle: () => void
}

const TopicBrowser: React.FC<TopicBrowserProps> = ({ isOpen, onToggle }) => {
  const [topics, setTopics] = useState<TopicItem[]>([])
  const [selectedTopic, setSelectedTopic] = useState<TopicItem | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)

  const fetchTopics = async (pageNum: number = 1) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`http://localhost:8000/list-topics?page=${pageNum}&limit=50`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch topics')
      }
      
      const data: ListTopicsResponse = await response.json()
      
      if (pageNum === 1) {
        setTopics(data.topics)
      } else {
        setTopics(prev => [...prev, ...data.topics])
      }
      
      setHasMore(data.has_more)
      setPage(pageNum)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load topics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTopics(1)
  }, [])

  const loadMore = () => {
    if (hasMore && !loading) {
      fetchTopics(page + 1)
    }
  }

  const formatLocation = (topic: TopicItem) => {
    const parts = []
    if (topic.page) parts.push(`Page ${topic.page}`)
    if (topic.line) parts.push(`Line ${topic.line}`)
    return parts.join(', ')
  }

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-gray-50 border-r border-gray-200 shadow-lg z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 md:relative md:shadow-none`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
          <h2 className="text-lg font-semibold text-gray-900">📑 Topics</h2>
          <button
            onClick={onToggle}
            className="md:hidden p-1 rounded-md hover:bg-gray-100"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Loading State */}
        {loading && topics.length === 0 && (
          <div className="p-4 text-center">
            <div className="text-sm text-gray-500">Loading topics...</div>
          </div>
        )}
        
        {/* Error State */}
        {error && (
          <div className="p-4 text-sm text-red-600 bg-red-50">
            {error}
          </div>
        )}
        
        {/* Empty State */}
        {topics.length === 0 && !loading && !error && (
          <div className="p-4 text-sm text-gray-500 text-center">
            No topics found. Upload some documents first.
          </div>
        )}
        
        {/* Topics List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-2 space-y-1">
            {topics.map((topic, index) => (
              <div key={index}>
                <div
                  className={`p-3 rounded-lg cursor-pointer transition-colors hover:bg-gray-100 ${
                    selectedTopic === topic ? 'bg-blue-50 border border-blue-200' : ''
                  }`}
                  onClick={() => setSelectedTopic(selectedTopic === topic ? null : topic)}
                >
                  <div className="flex items-start space-x-2">
                    <DocumentTextIcon className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-bold text-sm text-gray-900 truncate">
                        {topic.filename}
                      </div>
                      <div className="text-sm text-gray-700 truncate">
                        {topic.topic || 'Untitled'}
                      </div>
                      {formatLocation(topic) && (
                        <div className="text-xs text-gray-400">
                          {formatLocation(topic)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Inline Preview Snippet */}
                {selectedTopic === topic && (
                  <div className="mt-2 ml-6 p-3 bg-white rounded-lg border border-gray-200 text-xs text-gray-600 leading-relaxed">
                    {topic.preview}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {/* Load More Button */}
          {hasMore && (
            <div className="p-4">
              <button
                onClick={loadMore}
                disabled={loading}
                className="w-full py-2 px-4 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 bg-white"
              >
                {loading ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

export default TopicBrowser