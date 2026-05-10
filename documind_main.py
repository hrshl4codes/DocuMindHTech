"""
Production entry point. Serves the React frontend if a build exists, otherwise falls back to frontend/index.html.
"""

import os
import uuid
import uvicorn
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = FastAPI(
        title="DocuMind",
        description="RAG pipeline: upload documents, ask questions, get cited answers.",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    frontend_build_path = "frontend/build"
    if os.path.exists(frontend_build_path):
        print("Mounting React frontend from build directory")
        app.mount("/static", StaticFiles(directory=f"{frontend_build_path}/static"), name="static")

        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            if full_path.startswith(("api/", "docs", "redoc", "health")):
                raise HTTPException(status_code=404, detail="Not found")
            if os.path.exists(f"{frontend_build_path}/index.html"):
                return FileResponse(f"{frontend_build_path}/index.html")
            raise HTTPException(status_code=404, detail="Frontend not found")
    else:
        print("React build not found, falling back to frontend/index.html")

        @app.get("/")
        async def root():
            return FileResponse("frontend/index.html")

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "system": "documind",
            "version": "2.0.0",
        }

    @app.get("/favicon.ico")
    async def favicon():
        from fastapi.responses import Response
        return Response(content="", media_type="image/x-icon")

    @app.get("/api")
    async def api_info():
        return {
            "status": "running",
            "endpoints": {
                "health": "/health",
                "upload": "/api/upload",
                "query": "/api/query",
                "docs": "/docs",
            }
        }

    @app.get("/api/health")
    async def api_health():
        return {"status": "healthy"}

    @app.get("/api/test")
    async def test_endpoint():
        return {
            "status": "ok",
            "mode": "minimal",
            "note": "Set API keys and configure a vector database for full functionality.",
        }

    @app.get("/api/debug")
    async def debug_endpoint():
        try:
            return {
                "frontend_directory_exists": os.path.exists("frontend"),
                "index_html_exists": os.path.exists("frontend/index.html"),
                "build_directory_exists": os.path.exists("frontend/build"),
                "current_directory": os.getcwd(),
                "directory_contents": os.listdir("."),
            }
        except Exception as e:
            return {"error": str(e)}

    MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

    @app.post("/api/upload")
    async def upload_endpoint(
        file: Optional[UploadFile] = File(None),
        text: Optional[str] = Form(None)
    ):
        if not file and not text:
            raise HTTPException(status_code=400, detail="Either file or text must be provided")

        if file:
            contents = await file.read()
            if len(contents) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit")

        document_id = str(uuid.uuid4())
        return JSONResponse({
            "success": True,
            "document_id": document_id,
            "status": "minimal_mode",
            "note": "Full functionality requires API keys and a configured vector database.",
        })

    @app.post("/api/query")
    async def query_endpoint(request: Request):
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        if not body or "question" not in body or "document_id" not in body:
            raise HTTPException(status_code=400, detail="question and document_id are required")

        question = body.get("question", "").strip()
        if not question:
            raise HTTPException(status_code=400, detail="question cannot be empty")

        document_id = body.get("document_id", "")
        return JSONResponse({
            "success": True,
            "answer": f"Demo response to: '{question}' (document: {document_id}). Full mode requires API keys and a vector database.",
            "status": "minimal_mode",
        })

    return app


app = create_app()
print("DocuMind starting")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    print(f"Server: {host}:{port}")
    print(f"Docs:   http://{host}:{port}/docs")
    print(f"UI:     http://{host}:{port}/")
    print(f"Health: http://{host}:{port}/health")

    try:
        uvicorn.run("documind_main:app", host=host, port=port, reload=reload, log_level="info")
    except Exception as e:
        print(f"Failed to start: {e}")
        exit(1)
