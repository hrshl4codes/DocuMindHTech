"""
Minimal entry point for Render deployment.
Avoids heavy imports so the container starts cleanly without Pinecone package conflicts.
Full functionality requires API keys and a configured vector database.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Create the DocuMind AI application"""
    app = FastAPI(
        title="DocuMind",
        description="RAG pipeline: upload documents, ask questions, get cited answers.",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "DocuMind",
            "frontend": "/api/",
            "docs": "/docs",
            "health": "/health",
            "status": "running",
            "mode": "minimal"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "system": "documind",
            "version": "2.0.0",
            "mode": "minimal"
        }
    
    # Favicon endpoint to prevent 404 errors
    @app.get("/favicon.ico")
    async def favicon():
        from fastapi.responses import Response
        return Response(content="", media_type="image/x-icon")
    
    # Basic API endpoints
    @app.get("/api/")
    async def api_root():
        return {
            "message": "DocuMind API",
            "status": "running",
            "mode": "minimal",
            "endpoints": {
                "health": "/api/health",
                "test": "/api/test",
                "upload": "/api/upload",
                "query": "/api/query"
            }
        }
    
    @app.get("/api/health")
    async def api_health():
        return {
            "status": "healthy",
            "mode": "minimal"
        }
    
    @app.get("/api/test")
    async def test_endpoint():
        return {
            "status": "ok",
            "mode": "minimal",
            "note": "Minimal mode. Set API keys and configure a vector database for full functionality."
        }
    
    @app.post("/api/upload")
    async def upload_endpoint():
        return {
            "status": "minimal_mode",
            "note": "Full upload functionality requires API keys and a configured vector database."
        }
    
    @app.post("/api/query")
    async def query_endpoint():
        return {
            "status": "minimal_mode",
            "note": "Full query functionality requires API keys and a configured vector database."
        }
    
    # Mount frontend
    try:
        app.mount("/api", StaticFiles(directory="frontend", html=True), name="frontend")
        print("Frontend mounted")
    except Exception as e:
        print(f"Warning: could not mount frontend: {e}")
        # Add a fallback frontend endpoint
        @app.get("/api/")
        async def fallback_frontend():
            try:
                with open("frontend/index.html", "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
            except FileNotFoundError:
                return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)
    
    return app

app = create_app()
print("DocuMind starting (minimal mode)")

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"Server: {host}:{port}")
    print(f"Docs:   http://{host}:{port}/docs")
    print(f"UI:     http://{host}:{port}/api/")
    print(f"Health: http://{host}:{port}/health")

    try:
        uvicorn.run(
            "minimal_main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start: {e}")
        exit(1)
