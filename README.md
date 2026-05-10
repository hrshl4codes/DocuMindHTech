# DocuMind

A RAG system that extracts text from documents, builds a vector index, and answers questions with inline citations.

## How it works

```
Upload document → extract text → chunk → embed → store in vector DB
Query → embed question → vector search → rerank → LLM → answer with citations
```

## Stack

- **LLM / embeddings**: Gemini 2.5 Pro (primary), OpenAI GPT-4 (fallback)
- **Vector database**: Pinecone (primary), Weaviate, Qdrant, Supabase pgvector
- **Reranking**: Cohere, Jina, Voyage, BGE
- **Document parsing**: PyMuPDF (PDF), python-docx (DOCX), pandas (Excel), Tesseract OCR (images)
- **API**: FastAPI + uvicorn
- **Deployment**: Render

## Running locally

**With Docker (recommended):**

```bash
docker-compose up
```

Frontend at `http://localhost:3000`, API at `http://localhost:8000`.

**Without Docker:**

```bash
pip install -r requirements.txt
python documind_main.py
```

App starts at `http://localhost:8000`. API docs at `/docs`.

For full functionality, set these environment variables:

```env
GEMINI_API_KEY=...
PINECONE_API_KEY=...
COHERE_API_KEY=...
```

## Deploying to Render

`render.yaml` is pre-configured. Connect the repo and Render picks it up automatically.

Health check: `GET /health`

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /api/upload | Upload a document |
| POST | /api/query | Ask a question about an uploaded document |
| GET | /docs | Swagger UI |

## Chunking

Chunks are 800–1200 tokens with ~15% overlap using `RecursiveCharacterTextSplitter`. The overlap keeps context intact across chunk boundaries.

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
```

## Retrieval

Queries run hybrid search (vector + BM25), then rerank the top 10 results down to 5. The reranker corrects cases where cosine similarity surfaces technically similar but contextually wrong chunks.

```python
TOP_K = 10
RERANK_TOP_K = 5
VECTOR_WEIGHT = 0.7
BM25_WEIGHT = 0.3
```

## Project structure

```
DocuMindHTech-main/
├── documind_main.py         # Entry point — serves API + React SPA
├── requirements.txt         # Runtime deps
├── requirements-dev.txt     # Dev/test deps (pytest, ruff, httpx)
├── Dockerfile.backend       # Multi-stage Python image
├── Dockerfile.frontend      # Multi-stage nginx image
├── docker-compose.yml       # Run backend + frontend together
├── render.yaml              # Render deployment config
├── tests/
│   └── test_main.py         # pytest suite for all API endpoints
├── frontend/                # React CRA application
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   │       ├── LandingView.jsx
│   │       ├── UploadView.jsx
│   │       ├── QueryView.jsx
│   │       ├── UploadView.test.jsx
│   │       └── QueryView.test.jsx
│   └── package.json
└── services/
    ├── routes.py            # Full RAG API router (uses api_service)
    ├── api_service.py       # Pipeline orchestrator
    ├── chunking_service.py
    ├── reranker_service.py
    ├── citation_service.py
    ├── cloud_vector_service.py
    ├── chat_service.py
    ├── text_extract.py      # Multi-format extraction with OCR
    └── image_analyze.py
```

## Notes

- Gemini has a 1,000 req/min rate limit for both generation and embeddings
- Pinecone is faster but more expensive than Weaviate or Qdrant
- Reranking adds 200–500ms per query but meaningfully improves accuracy on longer documents
- Memory usage is roughly 2GB for 1,000 documents with embeddings cached
