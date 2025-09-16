import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { config } from '../config'

interface Source {
  filename: string
  chunk_id: number
  score: number
  preview: string
  doc_url?: string | null
}

interface ChatMessage {
  id: string
  type: 'user' | 'ai'
  content: string
  sources?: Source[]
  timestamp: Date
}

function ChatBox() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const addMessage = (type: 'user' | 'ai', content: string, sources?: Source[]) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type,
      content,
      sources,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    
    // Add user message immediately
    addMessage('user', question)
    setLoading(true)

    try {
      const response = await axios.post(
        `${config.API_BASE_URL}${config.endpoints.ask}`,
        { question }
      )
      
      // Add AI response
      addMessage('ai', response.data.answer, response.data.sources)
      
    } catch (err) {
      console.error('Error calling API:', err)
      
      // Handle different error scenarios
      if (axios.isAxiosError(err) && err.response?.status === 500) {
        addMessage('ai', 'Sorry, I encountered an error while processing your question. Please make sure the backend is running and configured properly.')
      } else if (axios.isAxiosError(err) && err.code === 'ECONNREFUSED') {
        addMessage('ai', 'Cannot connect to the backend server. Please make sure it is running on localhost:8000.')
      } else {
        addMessage('ai', 'Something went wrong. Please try again later.')
      }
    } finally {
      setLoading(false)
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden h-full flex flex-col">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 shadow-sm">
            <h1 className="text-2xl font-bold text-center">
              DocChat RAG Assistant
            </h1>
            <p className="text-blue-100 text-center mt-1">
              Ask questions about your uploaded documents
            </p>
          </div>
          
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 scroll-smooth" style={{ minHeight: '400px', maxHeight: '500px' }}>
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">💬</div>
                <p className="text-gray-500 text-lg">
                  Start a conversation by asking a question about your documents
                </p>
                <p className="text-gray-400 text-sm mt-2">
                  Upload documents first using the /upload-doc endpoint
                </p>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-br-md'
                          : 'bg-white text-gray-800 rounded-bl-md border border-gray-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      
                      {/* Sources */}
                      {message.type === 'ai' && message.sources && message.sources.length > 0 && (
                        <div className="mt-4">
                          <p className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                            <span className="w-4 h-4 mr-2">📄</span>
                            Sources ({message.sources.length})
                          </p>
                          <div className="space-y-3">
                            {message.sources.map((source, index) => (
                              <div 
                                key={index} 
                                className="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:bg-gray-100 transition-colors duration-200 hover:border-gray-300"
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex-1">
                                    {source.doc_url ? (
                                      <a 
                                        href={source.doc_url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="font-semibold text-blue-600 hover:text-blue-800 hover:underline text-sm"
                                      >
                                        {source.filename}
                                      </a>
                                    ) : (
                                      <span className="font-semibold text-gray-800 text-sm">
                                        {source.filename}
                                      </span>
                                    )}
                                  </div>
                                  <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                                    {source.score.toFixed(1)}% match
                                  </span>
                                </div>
                                
                                <p className="text-xs text-gray-600 leading-relaxed mb-2">
                                  {source.preview.length > 150 
                                    ? source.preview.substring(0, 150) + "..." 
                                    : source.preview
                                  }
                                </p>
                                
                                <div className="flex items-center text-xs text-gray-400">
                                  <span className="bg-gray-200 px-2 py-1 rounded text-xs">
                                    Chunk {source.chunk_id}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Timestamp */}
                      <div className={`text-xs mt-2 ${
                        message.type === 'user' ? 'text-blue-200' : 'text-gray-400'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white text-gray-800 rounded-2xl rounded-bl-md border border-gray-200 px-4 py-3 shadow-sm">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-500">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Form - Sticky at bottom */}
          <div className="bg-white border-t border-gray-200 p-4 shadow-lg">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-medium rounded-full hover:from-blue-700 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Send</span>
                  </div>
                ) : (
                  'Send'
                )}
              </button>
            </form>
          </div>
        </div>
  )
}

export default ChatBox