# DocChat RAG

A document-based chat application using Retrieval-Augmented Generation (RAG) with React frontend and FastAPI backend. Upload your documents and chat with them using AI-powered natural language understanding.

![DocChat RAG](https://img.shields.io/badge/Python-3.11+-blue) ![React](https://img.shields.io/badge/React-18+-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991)

## Features

- 📄 **Document Upload**: Support for PDF and TXT files with automatic text extraction
- 🧠 **Smart Chunking**: Uses LangChain's text splitters for optimal document segmentation
- 🔍 **Semantic Search**: ChromaDB vector store with OpenAI embeddings for accurate retrieval
- 💬 **Natural Chat**: Clean chat interface with real-time responses
- 📊 **Source Attribution**: Shows which document chunks were used for each answer
- 🚀 **Modern Stack**: React + TypeScript + Tailwind CSS frontend, FastAPI backend
- 🐳 **Docker Ready**: Full containerization support with Docker Compose

## Tech Stack

- **Frontend**: React 18 (Vite + TypeScript), TailwindCSS, Axios
- **Backend**: FastAPI (Python 3.11+), Uvicorn, Pydantic
- **AI/ML**: OpenAI GPT-4o-mini, OpenAI text-embedding-3-small, LangChain
- **Database**: ChromaDB (local vector store with persistence)
- **Infrastructure**: Docker, Docker Compose

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone and setup
git clone <repository-url>
cd docchat-rag

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# 3. Start with Docker Compose
docker-compose up --build

# 4. Open your browser
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
```

### Option 2: Manual Setup

#### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key

#### 1. Clone the repository

```bash
git clone <repository-url>
cd docchat-rag
```

#### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your-api-key-here
```

**Get your API key**: [OpenAI Platform](https://platform.openai.com/api-keys)

#### 3. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

#### 4. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Docker Setup

### Backend Only

```bash
cd backend
docker build -t docchat-backend .
docker run -p 8000:8000 \
  -v $(pwd)/../data:/app/data \
  -e OPENAI_API_KEY=your-api-key-here \
  docchat-backend
```

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

## Usage Guide

### 1. Upload Documents
- Click the upload area or drag & drop files
- Supports PDF and TXT files (max 10MB)
- Documents are automatically processed and chunked
- Track uploads with the document counter

### 2. Chat with Documents
- Ask questions in natural language
- Get AI-powered answers based on your documents
- View source references for each response
- Maintain conversation history

### 3. Example Queries
- "What are the main topics covered in this document?"
- "Summarize the key findings from the research paper"
- "What does the document say about machine learning?"

## Project Structure

```
docchat-rag/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── routes/         # API endpoints
│   │   │   ├── documents.py # Document management
│   │   │   └── chat.py     # Chat functionality
│   │   ├── services/       # Business logic
│   │   │   ├── vector_store.py # ChromaDB integration
│   │   │   ├── embeddings.py  # OpenAI embeddings
│   │   │   └── llm.py      # Language model service
│   │   └── utils/          # Utility functions
│   ├── tests/              # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── ChatBox.tsx    # Main chat interface
│   │   │   ├── DocumentUploader.tsx # File upload
│   │   │   └── Toast.tsx      # Notifications
│   │   ├── config.ts       # API configuration
│   │   └── main.tsx        # App entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
├── data/                   # ChromaDB persistence
├── docker-compose.yml      # Multi-container setup
├── .env.example           # Environment template
└── README.md              # This file
```

## API Endpoints

### Core Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `POST /ask` - Chat with documents (RAG pipeline)
- `POST /upload-doc` - Upload and process documents

### Legacy Endpoints
- `POST /api/documents/upload` - Legacy document upload
- `GET /api/documents/` - List documents
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/chat/` - Legacy chat endpoint

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `BACKEND_PORT` | Backend server port | 8000 |
| `BACKEND_URL` | Backend URL for frontend | http://localhost:8000 |

### Customization

- **Chunk size**: Modify `chunk_size` in `vector_store.py`
- **Model selection**: Change models in `llm.py` and `embeddings.py`
- **UI styling**: Edit Tailwind classes in React components
- **API base URL**: Update `config.ts` in frontend

## Testing

### Test Documents

The project includes comprehensive test PDFs designed to validate the RAG system's fine-grained parsing and topic extraction capabilities:

#### Available Test Documents

1. **`rag_test_pdfs/Mixed_Policies.pdf`** (~20 pages)
   - **HR Policies**: Employee onboarding, performance reviews, vacation policies, remote work guidelines
   - **Contract Policies**: Vendor contracts, NDAs, employment modifications, IP assignment
   - **Real Estate Policies**: Lease management, space allocation, facility maintenance, security
   - **IT Policies**: Password security, software licensing, data backup, network access

2. **`rag_test_pdfs/Medical_and_Legal.pdf`** (~20 pages)
   - **Patient Care Guidelines**: Intake procedures, HIPAA compliance, prescription protocols, emergency response
   - **Legal Contract Standards**: Contract formation, dispute resolution, IP protection, compliance requirements

Each document contains structured **Topic X-Y** entries (e.g., "Topic 1-1: Employee Onboarding Process") optimized for fine-grained parsing and semantic search testing.

### Testing the RAG System

#### 1. Upload Test Documents

```bash
# Start the application
npm run dev  # Frontend (localhost:5174)
uvicorn app.main:app --reload --port 8000  # Backend

# Visit http://localhost:5174
# Upload one or both test PDFs using the document uploader
```

#### 2. Test Topic-Specific Queries

The system performs **regex-based topic filtering** for precise retrieval:

```bash
# Direct topic queries (exact matches)
"Topic 1-1"  # Returns specific Employee Onboarding content
"Topic 5-2"  # Returns Service Level Agreement standards
"Topic 13-1" # Returns Password Security Requirements

# Semantic queries (content-based search)
"What are the password requirements?"
"Tell me about vacation policies"
"How should contracts handle force majeure?"
"What are the patient privacy rules?"
```

#### 3. Browse All Topics

Use the **TopicBrowser sidebar** to explore indexed content:
- Click the hamburger menu (☰) to open the topic browser
- Scroll through all indexed topics with metadata
- Click any topic to preview content snippet
- Use for discovery before asking specific questions

#### 4. API Testing

```bash
# Direct API calls for testing
curl -X POST "http://localhost:8000/upload-doc" \
  -F "file=@rag_test_pdfs/Mixed_Policies.pdf"

curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Topic 1-1"}'

# Browse all topics with pagination
curl "http://localhost:8000/list-topics?page=1&limit=20"
```

#### 5. Expected Results

- **Fine-grained parsing**: Each "Topic X-Y" becomes a separate searchable chunk
- **Metadata enrichment**: Page numbers, line numbers, topic labels in search results
- **Precise retrieval**: Topic queries return exact matches with high relevance scores
- **Source attribution**: Responses include filename, topic, page/line references

### Performance Validation

Test with different configurations by setting environment variables:

```bash
# Test with different retrieval amounts
export MAX_RESULTS=1  # Default: focused answers
export MAX_RESULTS=3  # More comprehensive context
export MAX_RESULTS=5  # Maximum context for complex queries

# Restart backend to apply changes
uvicorn app.main:app --reload --port 8000
```

### Development

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Code Quality

```bash
# Backend linting (if configured)
cd backend
ruff check .

# Frontend linting
cd frontend
npm run lint
```

### Hot Reload
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev` (enabled by default)

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check API key has sufficient credits

2. **"Cannot connect to backend"**
   - Verify backend is running on port 8000
   - Check CORS settings in `main.py`

3. **"No documents found"**
   - Upload documents first using the upload interface
   - Check ChromaDB data persistence in `./data/`

4. **Docker build fails**
   - Ensure Docker daemon is running
   - Check available disk space
   - Verify `.env` file exists

### Performance Tips

- **Large documents**: Consider increasing chunk overlap for better context
- **Many documents**: ChromaDB automatically handles indexing and search optimization
- **Response time**: Adjust `top_k` parameter in search queries

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for GPT-4o-mini and embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [LangChain](https://langchain.com/) for text processing
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://react.dev/) and [Vite](https://vitejs.dev/) for the frontend