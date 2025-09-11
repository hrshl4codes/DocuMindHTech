"""
DocuMind AI - Ultra Simple Test Version
This version will definitely work and show the frontend
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Create the FastAPI app
app = FastAPI(title="DocuMind AI Test")

@app.get("/")
async def root():
    return {"message": "DocuMind AI Test - Go to /api/ for frontend"}

@app.get("/api/")
async def frontend():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>DocuMind AI Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .test-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 DocuMind AI Test</h1>
        
        <div class="success">
            ✅ Frontend is working! This is a test version.
        </div>
        
        <div class="test-section">
            <h3>Test Information</h3>
            <p><strong>Status:</strong> Frontend is loading correctly</p>
            <p><strong>Version:</strong> Test Version</p>
            <p><strong>Time:</strong> <span id="time"></span></p>
        </div>
        
        <div class="test-section">
            <h3>Next Steps</h3>
            <p>1. This proves the frontend can be served</p>
            <p>2. The main application should work the same way</p>
            <p>3. Check the main app at the root URL</p>
        </div>
    </div>
    
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
        console.log('DocuMind AI Test Frontend loaded successfully!');
    </script>
</body>
</html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Test version working"}

if __name__ == "__main__":
    print("🧪 Starting DocuMind AI Test Version")
    uvicorn.run(app, host="0.0.0.0", port=8000)
