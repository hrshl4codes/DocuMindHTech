# DocuMind

A RAG-based document intelligence system. Upload a document, ask questions, get answers with inline citations.

---

## How it works

```
Upload:
  document → text extraction → chunking (1000 tok / 150 overlap)
           → Gemini embeddings → Pinecone vector DB

Query:
  question → embed → vector search (top-10) → rerank (top-5)
           → Gemini LLM → answer with [1][2] citations
```

---

## Architecture

```
┌─────────────┐        ┌──────────────────────────────────────┐
│   Browser   │        │              Backend (FastAPI)        │
│  React SPA  │◄──────►│  /api/upload   /api/query   /health  │
└─────────────┘        │                                      │
      │                │  services/                           │
   nginx               │  ├── chunking_service.py             │
   proxy               │  ├── simple_gemini_embedding_service │
                       │  ├── cloud_vector_service.py         │
                       │  ├── reranker_service.py             │
                       │  ├── chat_service.py                 │
                       │  └── citation_service.py             │
                       └──────────────────────────────────────┘
```

---

## Run locally

**Prerequisites:** Docker, Docker Compose, API keys

```bash
cp .env.example .env
# fill in at minimum: GEMINI_API_KEY, PINECONE_API_KEY, COHERE_API_KEY

docker-compose up
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| Backend   | http://localhost:8000        |
| API docs  | http://localhost:8000/docs   |

---

## Run without Docker

```bash
# Backend
pip install -r requirements.txt
python documind_main.py

# Frontend (separate terminal)
cd frontend && npm install && npm start
```

---

## Tech stack

| Layer       | Tech                                         |
|-------------|----------------------------------------------|
| Backend     | FastAPI, Python 3.11, uvicorn                |
| Frontend    | React 18, served via nginx                   |
| Embeddings  | Google Gemini `embedding-001` (768d)         |
| Vector DB   | Pinecone (primary) — Weaviate / Qdrant / Supabase supported |
| Reranker    | Cohere Rerank-3 — Jina / Voyage / BGE supported |
| LLM         | Gemini 2.0 Flash (primary), OpenAI GPT-4 (fallback) |
| Chunking    | LangChain `RecursiveCharacterTextSplitter`   |

---

## Environment variables

See `.env.example`. Minimum required to run the full pipeline:

```
GEMINI_API_KEY
PINECONE_API_KEY
COHERE_API_KEY
VECTOR_DB_PROVIDER=pinecone
RERANKER_PROVIDER=cohere
```

---

## API endpoints

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| POST   | `/api/upload`           | Upload document or text  |
| POST   | `/api/query`            | Query with a question    |
| GET    | `/api/documents`        | List uploaded documents  |
| GET    | `/health`               | Health check             |
| GET    | `/docs`                 | Swagger UI               |
