import { useState } from 'react'
import axios from 'axios'
import { config } from '../config'

function DocumentUploader() {
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string>('')
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setMessage('')
      setMessageType('')
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setMessage('')
    setMessageType('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${config.API_BASE_URL}/upload-doc`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      setMessage(`Document uploaded successfully! ${response.data.chunks_stored} chunks processed.`)
      setMessageType('success')
      setFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement
      if (fileInput) fileInput.value = ''

    } catch (error) {
      console.error('Upload error:', error)
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        setMessage(error.response.data.detail)
      } else {
        setMessage('Failed to upload document. Please try again.')
      }
      setMessageType('error')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
      
      <div className="space-y-4">
        <div>
          <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
            Select PDF or TXT file
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
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
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Uploading...</span>
            </div>
          ) : (
            'Upload Document'
          )}
        </button>

        {message && (
          <div className={`p-3 rounded-lg text-sm ${
            messageType === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-600'
              : 'bg-red-50 border border-red-200 text-red-600'
          }`}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUploader