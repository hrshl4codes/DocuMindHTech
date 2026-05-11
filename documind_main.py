"""
Production entry point. Serves the React frontend if a build exists.
API and health routes are always registered before the SPA catch-all
so they are never shadowed by the wildcard path handler.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = FastAPI(
        title="DocuMind",
        description="RAG pipeline: upload documents, ask questions, get cited answers.",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── System / health routes ────────────────────────────────
    # Registered BEFORE the SPA catch-all so they are never shadowed.

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

    # ── API routes ────────────────────────────────────────────

    from services.routes import router as api_router
    app.include_router(api_router)

    # ── Frontend static files / SPA catch-all (registered LAST) ──

    frontend_build_path = "frontend/build"
    if os.path.exists(frontend_build_path):
        app.mount(
            "/static",
            StaticFiles(directory=f"{frontend_build_path}/static"),
            name="static",
        )

        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            index = f"{frontend_build_path}/index.html"
            if os.path.exists(index):
                return FileResponse(index)
            raise HTTPException(status_code=404, detail="Frontend not found")
    else:
        @app.get("/")
        async def root():
            return FileResponse("frontend/index.html")

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

    uvicorn.run("documind_main:app", host=host, port=port, reload=reload, log_level="info")
