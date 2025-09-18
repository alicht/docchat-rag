import { useState, useRef } from 'react'
import axios from 'axios'
import { config } from '../config'
import Toast from './Toast'

interface UploadedDoc {
  id: string
  filename: string
  chunks: number
  timestamp: Date
}

interface ToastMessage {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

function DocumentUploader() {
  const [uploading, setUploading] = useState(false)
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDoc[]>([])
  const [toasts, setToasts] = useState<ToastMessage[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const addToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = Date.now().toString()
    setToasts(prev => [...prev, { id, message, type }])
  }

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    const file = files[0]

    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain']
    const allowedExtensions = ['.pdf', '.txt']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      addToast('Please select a PDF or TXT file', 'error')
      return
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      addToast('File size must be less than 10MB', 'error')
      return
    }

    await uploadFile(file)
  }

  const uploadFile = async (file: File) => {
    setUploading(true)

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

      const newDoc: UploadedDoc = {
        id: response.data.document_id,
        filename: response.data.filename,
        chunks: response.data.chunks_stored,
        timestamp: new Date()
      }

      setUploadedDocs(prev => [...prev, newDoc])
      addToast(`Successfully uploaded "${file.name}" (${response.data.chunks_stored} chunks)`, 'success')

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (error: unknown) {
      console.error('Upload error:', error)
      
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 400) {
          addToast(error.response.data.detail || 'Invalid file format', 'error')
        } else if (error.response?.status === 500) {
          addToast('Server error. Please check if OpenAI API key is configured.', 'error')
        } else if (error.code === 'ECONNREFUSED') {
          addToast('Cannot connect to backend. Make sure it\'s running on localhost:8000', 'error')
        } else {
          addToast('Upload failed. Please try again.', 'error')
        }
      } else {
        addToast('Upload failed. Please try again.', 'error')
      }
    } finally {
      setUploading(false)
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Upload Documents</h2>
          {uploadedDocs.length > 0 && (
            <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded">
              {uploadedDocs.length} doc{uploadedDocs.length !== 1 ? 's' : ''} uploaded
            </span>
          )}
        </div>
        
        <div className="space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileSelect}
            className="hidden"
            disabled={uploading}
          />

          <button
            onClick={handleButtonClick}
            disabled={uploading}
            className="w-full flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-600">Uploading...</span>
              </div>
            ) : (
              <div className="text-center">
                <div className="text-3xl mb-2">📄</div>
                <div className="text-gray-600">
                  <span className="font-medium">Click to upload</span> or drag and drop
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  PDF or TXT files (max 10MB)
                </div>
              </div>
            )}
          </button>

          {/* Recently uploaded files */}
          {uploadedDocs.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Recently uploaded:</h3>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {uploadedDocs.slice(-5).reverse().map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                  >
                    <div className="flex-1 truncate">
                      <span className="font-medium">{doc.filename}</span>
                      <span className="text-gray-500 ml-2">({doc.chunks} chunks)</span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {doc.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))}
                {uploadedDocs.length > 5 && (
                  <div className="text-xs text-gray-400 text-center">
                    ... and {uploadedDocs.length - 5} more
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Toast notifications */}
      <div className="fixed top-4 right-4 space-y-2 z-50">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </>
  )
}

export default DocumentUploader