import { useState } from 'react'
import Chat from './components/Chat'
import DocumentUpload from './components/DocumentUpload'
import DocumentList from './components/DocumentList'

function App() {
  const [refreshDocs, setRefreshDocs] = useState(0)

  const handleDocumentUploaded = () => {
    setRefreshDocs(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8 text-center">
          DocChat RAG
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Chat />
          </div>
          
          <div className="space-y-6">
            <DocumentUpload onUploadSuccess={handleDocumentUploaded} />
            <DocumentList key={refreshDocs} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App