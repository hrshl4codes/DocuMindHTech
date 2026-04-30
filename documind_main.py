import os
import time
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, Response
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from services.logger import get_logger

load_dotenv()

log = get_logger("documind")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting DocuMind AI on %s:%s", os.getenv("HOST", "0.0.0.0"), os.getenv("PORT", "8000"))
    log.info("docs at http://%s:%s/docs", os.getenv("HOST", "0.0.0.0"), os.getenv("PORT", "8000"))
    yield
    log.info("shutting down DocuMind AI")


def create_app() -> FastAPI:
    app = FastAPI(
        title="DocuMind AI",
        description="Production RAG system — document ingestion, vector search, reranking, and citations",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency = round((time.perf_counter() - start) * 1000)
        log.info("%s %s → %s  (%dms)", request.method, request.url.path, response.status_code, latency)
        return response

    frontend_build_path = "frontend/build"
    if os.path.exists(frontend_build_path):
        app.mount("/static", StaticFiles(directory=f"{frontend_build_path}/static"), name="static")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_react_app(full_path: str):
            if any(full_path.startswith(p) for p in ("api/", "docs", "redoc", "health")):
                raise HTTPException(status_code=404, detail="Not found")
            index = f"{frontend_build_path}/index.html"
            if os.path.exists(index):
                return FileResponse(index)
            raise HTTPException(status_code=404, detail="Frontend not found")

    @app.get("/health")
    async def health_check():
        checks = {}

        try:
            from services.cloud_vector_service import get_cloud_vector_db
            vdb = get_cloud_vector_db()
            checks["vector_db"] = vdb.provider if vdb.collection else "unavailable"
        except Exception:
            checks["vector_db"] = "unavailable"

        checks["gemini_key"] = bool(os.getenv("GEMINI_API_KEY"))
        checks["pinecone_key"] = bool(os.getenv("PINECONE_API_KEY"))

        try:
            from services import persistence
            checks["documents"] = len(persistence.list_documents())
        except Exception:
            checks["documents"] = "unavailable"

        healthy = checks["vector_db"] != "unavailable"
        return {"status": "ok" if healthy else "degraded", "checks": checks}

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return Response(content="", media_type="image/x-icon")

    from services.routes import router
    app.include_router(router)

    return app


app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("documind_main:app", host=host, port=port, reload=reload, log_level="info")
