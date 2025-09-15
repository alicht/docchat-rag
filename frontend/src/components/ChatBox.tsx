import { useState } from 'react'
import axios from 'axios'
import { config } from '../config'

interface Message {
  question: string
  answer: string
}

function ChatBox() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim()) return

    const question = input.trim()
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(
        `${config.API_BASE_URL}${config.endpoints.ask}`,
        { question }
      )
      
      setMessages(prev => [...prev, {
        question,
        answer: response.data.answer
      }])
    } catch (err) {
      console.error('Error calling API:', err)
      setError('Server error')
      setMessages(prev => [...prev, {
        question,
        answer: 'Server error - Could not get response'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Chat Interface
          </h1>
          
          <form onSubmit={handleSubmit} className="mb-6">
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Sending...' : 'Submit'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No messages yet. Ask a question to get started!
              </p>
            ) : (
              messages.map((message, index) => (
                <div key={index} className="border-b border-gray-200 pb-4 last:border-0">
                  <div className="mb-2">
                    <span className="text-sm font-semibold text-gray-600">Question:</span>
                    <p className="text-gray-900 mt-1">{message.question}</p>
                  </div>
                  <div>
                    <span className="text-sm font-semibold text-gray-600">Answer:</span>
                    <p className="text-gray-900 mt-1">{message.answer}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatBox