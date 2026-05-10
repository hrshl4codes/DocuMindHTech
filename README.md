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

```bash
pip install -r requirements.txt
python minimal_main.py
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
├── minimal_main.py          # Entry point (Render-ready, no heavy deps)
├── documind_main.py         # Full version with React frontend support
├── requirements.txt
├── render.yaml
├── frontend/
│   └── index.html
└── services/
    ├── routes.py
    ├── api_service.py       # Orchestrates the pipeline
    ├── chunking_service.py
    ├── reranker_service.py
    ├── citation_service.py
    ├── cloud_vector_service.py
    ├── embedding_service.py
    ├── chat_service.py
    ├── text_extract.py
    └── image_analyze.py
```

## Notes

- Gemini has a 1,000 req/min rate limit for both generation and embeddings
- Pinecone is faster but more expensive than Weaviate or Qdrant
- Reranking adds 200–500ms per query but meaningfully improves accuracy on longer documents
- Memory usage is roughly 2GB for 1,000 documents with embeddings cached
