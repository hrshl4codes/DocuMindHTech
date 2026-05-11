# DocuMind

Upload a document, ask questions, get answers with cited sources.

Built as a production-grade RAG system — not a demo. Proper chunking, hybrid retrieval, reranking, and citations.

**Live:** https://docu-mind-h-tech.vercel.app

## How it works

```
Upload
  └─ extract text (PDF/DOCX/images/Excel/PPTX)
  └─ chunk with overlap
  └─ embed via OpenAI
  └─ store in Pinecone

Query
  └─ embed question
  └─ vector search (Pinecone) + BM25 keyword search (in-memory)
  └─ merge candidate pools, rerank top results
  └─ generate answer via OpenAI GPT-4o-mini
  └─ return answer with inline citations
```

Hybrid search matters: pure vector search misses exact keyword matches ("Python", "clause 4.2"). BM25 catches those. Both pools get merged and reranked before the LLM sees them.

## Stack

| Layer | Choice |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small (1536d) |
| Vector DB | Pinecone (serverless) |
| Reranker | Cohere (BM25 fallback if no key) |
| Document parsing | PyMuPDF, python-docx, pandas, python-pptx |
| API | FastAPI + uvicorn |
| Frontend | React (Create React App) |
| CI | GitHub Actions (ruff + pytest + docker build) |
| Backend deployment | Render |
| Frontend deployment | Vercel |

## Running locally

**With Docker:**

```bash
cp .env.example .env   # fill in your keys
docker-compose up
```

Frontend at `localhost:3000`, API at `localhost:8000`.

**Without Docker:**

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python documind_main.py
```

API at `localhost:8000`, Swagger docs at `/docs`.

**Required environment variables:**

```env
GENERATION_OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
VECTOR_DB_PROVIDER=pinecone
```

Optional (for Cohere reranking):
```env
COHERE_API_KEY=...
RERANKER_PROVIDER=cohere
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload a document (file or text) |
| POST | `/api/query` | Ask a question about a document |
| GET | `/api/documents` | List uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/docs` | Swagger UI |

**Upload a file:**
```bash
curl -X POST https://documindhtech-1.onrender.com/api/upload \
  -F "file=@report.pdf"
```

**Query:**
```bash
curl -X POST https://documindhtech-1.onrender.com/api/query \
  -H "Content-Type: application/json" \
  -d '{"document_id": "...", "question": "What are the key findings?"}'
```

## Deployment

**Backend (Render):**
`render.yaml` is pre-configured. Connect the repo, set the env vars below as secrets, and deploy.

```
GENERATION_OPENAI_API_KEY=...
PINECONE_API_KEY=...
VECTOR_DB_PROVIDER=pinecone
```

**Frontend (Vercel):**
`frontend/vercel.json` is pre-configured. Import the repo, set Root Directory to `frontend/`, and deploy. No env vars needed.

## Chunking

`RecursiveCharacterTextSplitter` with 1000-char chunks and 150-char overlap (~15%). Overlap keeps sentence context intact across boundaries, which matters for citation accuracy.

## Project structure

```
├── documind_main.py          # Entry point — FastAPI app, mounts router + SPA
├── services/
│   ├── routes.py             # API router (/api/*)
│   ├── api_service.py        # Pipeline orchestrator (upload + query)
│   ├── chunking_service.py   # RecursiveCharacterTextSplitter wrapper
│   ├── cloud_vector_service.py  # Pinecone / Weaviate / Qdrant / Supabase
│   ├── reranker_service.py   # Cohere / BM25 reranker
│   ├── citation_service.py   # Inline citation mapping
│   ├── chat_service.py       # OpenAI chat wrapper
│   ├── simple_gemini_embedding_service.py  # OpenAI embeddings
│   └── text_extract.py       # Multi-format extraction
├── frontend/                 # React app
├── tests/
│   └── test_main.py          # pytest suite (mocked, no credentials needed)
├── Dockerfile.backend        # Multi-stage Python image (non-root)
├── Dockerfile.frontend       # Multi-stage nginx image
├── docker-compose.yml
└── render.yaml
```

## CI

GitHub Actions runs on every push to `main`:

1. **Backend**: ruff lint → pytest → docker build
2. **Frontend**: eslint → jest → docker build

Tests are mocked — CI passes without API keys.
