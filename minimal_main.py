"""
DocuMind AI - Minimal Version for Render Deployment
This version completely avoids Pinecone imports to prevent package conflicts
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
        title="DocuMind AI - Advanced Document Intelligence",
        description="Advanced Document Intelligence System with cloud vector database, reranking, and citations",
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
            "message": "DocuMind AI - Advanced Document Intelligence System",
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
            "system": "documind_ai",
            "message": "Service is running",
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
            "message": "DocuMind AI API",
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
            "message": "API is running",
            "mode": "minimal"
        }
    
    @app.get("/api/test")
    async def test_endpoint():
        return {
            "message": "DocuMind AI is working!",
            "status": "success",
            "mode": "minimal",
            "note": "Running in minimal mode - full services require API keys and proper package installation"
        }
    
    @app.post("/api/upload")
    async def upload_endpoint():
        return {
            "message": "Upload endpoint ready",
            "status": "minimal_mode",
            "note": "Full upload functionality requires API keys and vector database configuration"
        }
    
    @app.post("/api/query")
    async def query_endpoint():
        return {
            "message": "Query endpoint ready",
            "status": "minimal_mode",
            "note": "Full query functionality requires API keys and vector database configuration"
        }
    
    # Mount frontend
    try:
        app.mount("/api", StaticFiles(directory="frontend", html=True), name="frontend")
        print("✅ Frontend mounted successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not mount frontend: {e}")
        # Add a fallback frontend endpoint
        @app.get("/api/")
        async def fallback_frontend():
            try:
                with open("frontend/index.html", "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
            except FileNotFoundError:
                return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)
    
    return app

# Create the DocuMind AI application
app = create_app()
print("🏆 Starting DocuMind AI - Minimal Version")

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"🌐 Server starting on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔗 DocuMind Frontend: http://{host}:{port}/api/")
    print(f"❤️ Health Check: http://{host}:{port}/health")
    
    try:
        uvicorn.run(
            "minimal_main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        exit(1)
