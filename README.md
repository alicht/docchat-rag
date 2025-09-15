# DocChat RAG

A document-based chat application using Retrieval-Augmented Generation (RAG) with React frontend and FastAPI backend.

## Tech Stack

- **Frontend**: React (Vite + TypeScript), TailwindCSS
- **Backend**: FastAPI (Python), Uvicorn
- **Database**: ChromaDB (local vector store)
- **LLM & Embeddings**: OpenAI (GPT-4o-mini + text-embedding-3-small)

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd docchat-rag
```

### 2. Set up environment variables

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Docker Setup (Backend only)

To run the backend with Docker:

```bash
cd backend
docker build -t docchat-backend .
docker run -p 8000:8000 -v $(pwd)/data:/app/data --env-file ../.env docchat-backend
```

## Usage

1. Open the application at `http://localhost:5173`
2. Upload text documents (.txt or .md files) using the Upload Document section
3. Ask questions about your documents in the chat interface
4. The system will retrieve relevant context and generate responses using GPT-4o-mini

## Project Structure

```
docchat-rag/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic (LLM, embeddings, vector store)
│   │   └── utils/            # Utility functions
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── pages/           # Page components
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── data/                    # ChromaDB persistent storage
├── .env.example            # Environment variables template
└── README.md               # This file
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - API health status
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents/` - List all documents
- `DELETE /api/documents/{id}` - Delete a document
- `POST /api/chat/` - Send a chat message

## Development

- Backend hot reload is enabled with `--reload` flag
- Frontend hot reload is enabled by default with Vite
- ChromaDB data persists in the `./data` directory