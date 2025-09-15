import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { config } from '../config'

interface Source {
  filename: string
  chunk_index: number
  distance?: number
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
    <div className="bg-white shadow-lg rounded-lg overflow-hidden h-full">
          <div className="bg-blue-600 text-white p-4">
            <h1 className="text-2xl font-bold text-center">
              DocChat RAG Assistant
            </h1>
            <p className="text-blue-100 text-center mt-1">
              Ask questions about your uploaded documents
            </p>
          </div>
          
          {/* Messages Container */}
          <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
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
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg shadow-sm ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white rounded-br-none'
                          : 'bg-white text-gray-800 rounded-bl-none border'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      
                      {/* Sources */}
                      {message.type === 'ai' && message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-2 border-t border-gray-200">
                          <p className="text-xs font-semibold text-gray-600 mb-1">Sources:</p>
                          <div className="space-y-1">
                            {message.sources.map((source, index) => (
                              <div key={index} className="text-xs text-gray-500 flex items-center gap-2">
                                <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                                <span>{source.filename}</span>
                                <span className="text-gray-400">chunk {source.chunk_index}</span>
                                {source.distance !== undefined && (
                                  <span className="text-gray-400">
                                    ({(source.distance * 100).toFixed(1)}% match)
                                  </span>
                                )}
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
                    <div className="bg-white text-gray-800 rounded-lg rounded-bl-none border px-4 py-3 shadow-sm">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
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

          {/* Input Form */}
          <div className="bg-white border-t p-4">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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