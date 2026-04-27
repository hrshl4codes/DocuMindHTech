"""
DocuMind AI - Production Version for Render Deployment
This version serves the React frontend and provides API endpoints
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
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
    
    # Check if frontend build exists and mount static files
    frontend_build_path = "frontend/build"
    if os.path.exists(frontend_build_path):
        print("📁 Mounting React frontend from build directory")
        app.mount("/static", StaticFiles(directory=f"{frontend_build_path}/static"), name="static")
        
        # Serve React app for all non-API routes
        @app.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            # Don't serve React app for API routes
            if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("health"):
                raise HTTPException(status_code=404, detail="Not found")
            
            # Serve index.html for all other routes (React Router)
            if os.path.exists(f"{frontend_build_path}/index.html"):
                return FileResponse(f"{frontend_build_path}/index.html")
            else:
                raise HTTPException(status_code=404, detail="Frontend not found")
    else:
        print("⚠️ Frontend build not found, serving fallback HTML")
        
        # Fallback: serve simple HTML if React build doesn't exist
        @app.get("/")
        async def root():
            try:
                return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>DocuMind AI - Document Intelligence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; color: white; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .section { 
            background: white; border-radius: 15px; padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        }
        .section-title { 
            font-size: 1.3rem; margin-bottom: 20px; color: #2c3e50; 
            border-bottom: 2px solid #3498db; padding-bottom: 10px; 
        }
        .upload-area { 
            border: 3px dashed #bdc3c7; border-radius: 10px; padding: 40px 20px; 
            text-align: center; transition: all 0.3s ease; cursor: pointer; margin-bottom: 20px; 
        }
        .upload-area:hover { border-color: #3498db; background-color: #f8f9fa; }
        .upload-icon { font-size: 3rem; color: #bdc3c7; margin-bottom: 15px; }
        .upload-text { color: #7f8c8d; font-size: 1.1rem; }
        .text-input { 
            width: 100%; min-height: 150px; padding: 15px; border: 2px solid #ecf0f1; 
            border-radius: 10px; font-size: 1rem; resize: vertical; font-family: inherit; margin-bottom: 15px; 
        }
        .text-input:focus { outline: none; border-color: #3498db; }
        .query-input { 
            width: 100%; padding: 15px; border: 2px solid #ecf0f1; 
            border-radius: 10px; font-size: 1rem; margin-bottom: 15px; 
        }
        .query-input:focus { outline: none; border-color: #3498db; }
        .btn { 
            background: linear-gradient(135deg, #3498db, #2980b9); color: white; border: none; 
            padding: 12px 25px; border-radius: 8px; font-size: 1rem; cursor: pointer; 
            transition: all 0.3s ease; margin-right: 10px; margin-bottom: 10px; 
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4); }
        .btn:disabled { background: #bdc3c7; cursor: not-allowed; transform: none; }
        .btn-secondary { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }
        .results-section { 
            background: white; border-radius: 15px; padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 20px; 
        }
        .answer { 
            background: #f8f9fa; border-left: 4px solid #3498db; padding: 20px; 
            margin-bottom: 20px; border-radius: 0 10px 10px 0; 
        }
        .answer-text { font-size: 1.1rem; line-height: 1.8; margin-bottom: 15px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .stat-card { 
            background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
            padding: 20px; border-radius: 10px; text-align: center; 
        }
        .stat-value { font-size: 2rem; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .loading { text-align: center; padding: 20px; }
        .spinner { 
            border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; 
            width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 15px; 
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .error { background: #e74c3c; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .success { background: #27ae60; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .file-info { 
            background: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 15px; 
            border-left: 4px solid #3498db; 
        }
        .file-name { font-weight: bold; color: #2c3e50; }
        .file-size { color: #7f8c8d; font-size: 0.9rem; }
        @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 DocuMind AI</h1>
            <p>Professional Document Intelligence System</p>
        </div>

        <div class="main-content">
            <div class="section">
                <h2 class="section-title">📁 Document Upload</h2>
                
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">
                        <strong>Click to upload</strong> or drag and drop<br />
                        <small>Supports PDF, DOCX, TXT, and more</small>
                    </div>
                </div>
                
                <input type="file" id="fileInput" style="display: none" onchange="handleFileUpload(event)" accept=".pdf,.docx,.txt,.md" />
                
                <div id="fileInfo" class="file-info" style="display: none;">
                    <div class="file-name" id="fileName"></div>
                    <div class="file-size" id="fileSize"></div>
                </div>

                <h3 class="section-title">📝 Or Paste Text</h3>
                <textarea class="text-input" id="textInput" placeholder="Paste your document text here..."></textarea>
                
                <button class="btn" onclick="handleUpload()" id="uploadBtn">Upload Document</button>
                <button class="btn btn-secondary" onclick="handleClear()">Clear</button>
            </div>

            <div class="section">
                <h2 class="section-title">💬 Ask Questions</h2>
                
                <input type="text" class="query-input" id="questionInput" placeholder="What would you like to know about the document?" />
                
                <button class="btn" onclick="handleQuery()" id="queryBtn" disabled>Ask Question</button>
                <button class="btn btn-secondary" onclick="clearQuery()">Clear Query</button>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <div>Processing your request...</div>
                </div>
            </div>
        </div>

        <div id="messages"></div>

        <div id="results" class="results-section" style="display: none;">
            <h2 class="section-title">🧠 Answer</h2>
            <div class="answer">
                <div class="answer-text" id="answerText"></div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">✅</div>
                <div class="stat-label">System Running</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">HTML</div>
                <div class="stat-label">Frontend</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Ready</div>
                <div class="stat-label">Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">API</div>
                <div class="stat-label">Connected</div>
            </div>
        </div>
    </div>

    <script>
        let currentDocument = null;
        let currentDocumentId = null;

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                currentDocument = file;
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = formatFileSize(file.size);
                document.getElementById('fileInfo').style.display = 'block';
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        async function handleUpload() {
            const textInput = document.getElementById('textInput').value.trim();
            if (!currentDocument && !textInput) {
                showMessage('Please select a file or enter text', 'error');
                return;
            }

            setLoading(true, 'uploadBtn', 'Uploading...');
            clearMessages();

            try {
                const formData = new FormData();
                if (currentDocument) {
                    formData.append('file', currentDocument);
                } else {
                    formData.append('text', textInput);
                }

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (data.success) {
                    currentDocumentId = data.document_id;
                    showMessage('Document uploaded successfully!', 'success');
                } else {
                    showMessage(data.error || 'Upload failed', 'error');
                }
            } catch (error) {
                showMessage('Upload failed: ' + error.message, 'error');
            } finally {
                setLoading(false, 'uploadBtn', 'Upload Document');
            }
        }

        async function handleQuery() {
            const question = document.getElementById('questionInput').value.trim();
            if (!question) {
                showMessage('Please enter a question', 'error');
                return;
            }

            if (!currentDocumentId) {
                showMessage('Please upload a document first', 'error');
                return;
            }

            setLoading(true, 'queryBtn', 'Processing...');
            clearMessages();

            try {
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        document_id: currentDocumentId,
                        question: question
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('answerText').textContent = data.answer;
                    document.getElementById('results').style.display = 'block';
                } else {
                    showMessage(data.error || 'Query failed', 'error');
                }
            } catch (error) {
                showMessage('Query failed: ' + error.message, 'error');
            } finally {
                setLoading(false, 'queryBtn', 'Ask Question');
            }
        }

        function handleClear() {
            currentDocument = null;
            currentDocumentId = null;
            document.getElementById('textInput').value = '';
            document.getElementById('questionInput').value = '';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            document.getElementById('fileInput').value = '';
            clearMessages();
        }

        function clearQuery() {
            document.getElementById('questionInput').value = '';
        }

        function setLoading(loading, buttonId, text) {
            const button = document.getElementById(buttonId);
            const loadingDiv = document.getElementById('loading');
            
            if (loading) {
                button.disabled = true;
                button.textContent = text;
                loadingDiv.style.display = 'block';
            } else {
                button.disabled = buttonId === 'queryBtn' && !currentDocumentId;
                button.textContent = text;
                loadingDiv.style.display = 'none';
            }
        }

        function showMessage(message, type) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = type;
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
        }

        function clearMessages() {
            document.getElementById('messages').innerHTML = '';
        }

        // Enable query button when document is uploaded
        document.getElementById('textInput').addEventListener('input', function() {
            if (this.value.trim() || currentDocument) {
                document.getElementById('queryBtn').disabled = false;
            }
        });
    </script>
</body>
</html>
        """)
            except Exception as e:
                print(f"❌ Error serving HTML frontend: {e}")
                return HTMLResponse(content=f"<h1>Error loading frontend</h1><p>{str(e)}</p>", status_code=500)
    
    # Test endpoint to verify HTML serving
    @app.get("/test-html")
    async def test_html():
        return HTMLResponse(content="<h1>HTML Test</h1><p>If you see this, HTML responses are working!</p>")
    
    @app.get("/health")
    async def health_check():
        checks = {}

        # vector DB
        try:
            from services.cloud_vector_service import get_cloud_vector_db
            vdb = get_cloud_vector_db()
            checks["vector_db"] = vdb.provider if vdb.collection else "unavailable"
        except Exception:
            checks["vector_db"] = "unavailable"

        # API keys present (existence only, not validity)
        checks["gemini_key"] = bool(os.getenv("GEMINI_API_KEY"))
        checks["pinecone_key"] = bool(os.getenv("PINECONE_API_KEY"))

        # document count
        try:
            from services import persistence
            checks["documents"] = len(persistence.list_documents())
        except Exception:
            checks["documents"] = "unavailable"

        healthy = checks["vector_db"] != "unavailable"
        return {
            "status": "ok" if healthy else "degraded",
            "checks": checks,
        }
    
    # Favicon endpoint to prevent 404 errors
    @app.get("/favicon.ico")
    async def favicon():
        from fastapi.responses import Response
        return Response(content="", media_type="image/x-icon")
    

    # API endpoint for testing
    @app.get("/api")
    async def api_info():
        return {
            "message": "DocuMind AI API",
            "status": "running",
            "frontend": "React app at root URL",
            "endpoints": {
                "health": "/health",
                "test": "/api/test",
                "upload": "/api/upload",
                "query": "/api/query"
            }
        }
    
    # Basic API endpoints (after frontend mounting)
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
    
    @app.get("/api/debug")
    async def debug_endpoint():
        import os
        try:
            # Check if frontend directory exists
            frontend_exists = os.path.exists("frontend")
            index_exists = os.path.exists("frontend/index.html")
            build_exists = os.path.exists("frontend/build")
            
            # Get file size if it exists
            file_size = 0
            if index_exists:
                file_size = os.path.getsize("frontend/index.html")
            
            # Get environment variables
            env_vars = {
                "HOST": os.getenv("HOST", "0.0.0.0"),
                "PORT": os.getenv("PORT", "8000"),
                "VECTOR_DB_PROVIDER": os.getenv("VECTOR_DB_PROVIDER", "pinecone"),
                "RERANKER_PROVIDER": os.getenv("RERANKER_PROVIDER", "cohere"),
                "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "3.11.0"),
                "NODE_VERSION": os.getenv("NODE_VERSION", "18.17.0"),
                "REACT_APP_API_URL": os.getenv("REACT_APP_API_URL", "https://documindrex.onrender.com"),
                "RELOAD": os.getenv("RELOAD", "false")
            }
            
            return {
                "frontend_directory_exists": frontend_exists,
                "index_html_exists": index_exists,
                "build_directory_exists": build_exists,
                "file_size_bytes": file_size,
                "current_directory": os.getcwd(),
                "directory_contents": os.listdir(".") if os.path.exists(".") else "Directory not found",
                "environment_variables": env_vars
            }
        except Exception as e:
            return {"error": str(e)}
    
    from services.routes import router
    app.include_router(router)

    return app

# Create the DocuMind AI application
app = create_app()
print("🏆 Starting DocuMind AI - Minimal Version")

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # Get additional environment variables
    vector_db_provider = os.getenv("VECTOR_DB_PROVIDER", "pinecone")
    reranker_provider = os.getenv("RERANKER_PROVIDER", "cohere")
    python_version = os.getenv("PYTHON_VERSION", "3.11.0")
    node_version = os.getenv("NODE_VERSION", "18.17.0")
    react_app_api_url = os.getenv("REACT_APP_API_URL", "https://documindrex.onrender.com")
    
    print(f"🔧 Environment Configuration:")
    print(f"   HOST: {host}")
    print(f"   PORT: {port}")
    print(f"   VECTOR_DB_PROVIDER: {vector_db_provider}")
    print(f"   RERANKER_PROVIDER: {reranker_provider}")
    print(f"   PYTHON_VERSION: {python_version}")
    print(f"   NODE_VERSION: {node_version}")
    print(f"   REACT_APP_API_URL: {react_app_api_url}")
    print(f"   RELOAD: {reload}")
    
    print(f"🌐 Server starting on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔗 DocuMind Frontend: http://{host}:{port}/api/")
    print(f"❤️ Health Check: http://{host}:{port}/health")
    
    try:
        uvicorn.run(
            "documind_main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        exit(1)

