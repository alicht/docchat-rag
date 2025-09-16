import React, { useState, useEffect } from 'react'
import { ChevronRightIcon, ChevronDownIcon, DocumentTextIcon } from '@heroicons/react/24/outline'

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
    if (isOpen) {
      fetchTopics(1)
    }
  }, [isOpen])

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
    <div className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out ${
      isOpen ? 'translate-x-0' : '-translate-x-full'
    } lg:relative lg:translate-x-0 lg:flex`}>
      
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className="relative flex flex-col w-80 bg-white border-r border-gray-200 h-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Browse Topics</h2>
          <button
            onClick={onToggle}
            className="lg:hidden p-1 rounded-md hover:bg-gray-100"
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>
        
        {/* Topics List */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="p-4 text-sm text-red-600 bg-red-50">
              {error}
            </div>
          )}
          
          {topics.length === 0 && !loading && !error && (
            <div className="p-4 text-sm text-gray-500 text-center">
              No topics found. Upload some documents first.
            </div>
          )}
          
          <div className="space-y-1 p-2">
            {topics.map((topic, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedTopic === topic
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedTopic(topic)}
              >
                <div className="flex items-start space-x-2">
                  <DocumentTextIcon className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {topic.topic || 'Untitled'}
                    </div>
                    <div className="text-xs text-gray-500 truncate">
                      {topic.filename}
                    </div>
                    {formatLocation(topic) && (
                      <div className="text-xs text-gray-400">
                        {formatLocation(topic)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Load More Button */}
          {hasMore && (
            <div className="p-4">
              <button
                onClick={loadMore}
                disabled={loading}
                className="w-full py-2 px-4 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Preview Panel */}
      {selectedTopic && (
        <div className="hidden lg:flex flex-col w-96 bg-gray-50 border-r border-gray-200">
          <div className="p-4 border-b border-gray-200 bg-white">
            <h3 className="text-lg font-semibold text-gray-900">Preview</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Topic</h4>
                <p className="text-sm text-gray-900">
                  {selectedTopic.topic || 'Untitled'}
                </p>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Source</h4>
                <p className="text-sm text-gray-600">{selectedTopic.filename}</p>
                {formatLocation(selectedTopic) && (
                  <p className="text-xs text-gray-500 mt-1">
                    {formatLocation(selectedTopic)}
                  </p>
                )}
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Preview</h4>
                <div className="text-sm text-gray-800 leading-relaxed bg-white p-3 rounded-lg border">
                  {selectedTopic.preview}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TopicBrowser