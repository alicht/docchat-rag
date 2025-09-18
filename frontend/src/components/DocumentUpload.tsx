import { useState } from 'react'
import axios from 'axios'

interface DocumentUploadProps {
  onUploadSuccess: () => void
}

function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleUpload = async () => {
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setMessage('')

    try {
      await axios.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setMessage('Document uploaded successfully!')
      setFile(null)
      onUploadSuccess()
      
      setTimeout(() => setMessage(''), 3000)
    } catch (error: unknown) {
      console.error('Upload error:', error)
      setMessage('Error uploading document. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold mb-4">Upload Document</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select a text file
          </label>
          <input
            type="file"
            accept=".txt,.md"
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
            disabled={uploading}
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>

        {message && (
          <p className={`text-sm ${
            message.includes('Error') ? 'text-red-500' : 'text-green-500'
          }`}>
            {message}
          </p>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload