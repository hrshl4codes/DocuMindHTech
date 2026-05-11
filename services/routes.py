"""
DocuMind AI API Routes
FastAPI routes for the DocuMind AI system
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from services.api_service import get_api_service
from services.text_extract import process_file_content

# Initialize router
router = APIRouter(prefix="/api", tags=["DocuMind AI"])

# Pydantic models
class QueryRequest(BaseModel):
    document_id: str
    question: str
    top_k: Optional[int] = 10

class TextUploadRequest(BaseModel):
    text: str
    title: Optional[str] = ""
    source: Optional[str] = "text_input"

class SystemInfoResponse(BaseModel):
    vector_database: dict
    chunking: dict
    reranker: dict
    documents_uploaded: int
    total_chunks: int

# Initialize API service
api_service = get_api_service()

@router.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the frontend interface"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

@router.post("/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    title: Optional[str] = Form(""),
    source: Optional[str] = Form("")
):
    """
    Upload a document (file or text)
    """
    try:
        if file and file.filename:
            content = await file.read()
            if len(content) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds the 50 MB limit")
            ext = ('.' + file.filename.rsplit('.', 1)[-1].lower()) if '.' in file.filename else ''
            content_str = await process_file_content(content, ext, file.filename)
            result = await api_service.upload_document(
                content=content_str,
                source=source or file.filename,
                title=title or file.filename,
                doc_type=file.filename.split('.')[-1] if '.' in file.filename else 'unknown'
            )
        elif text:
            result = await api_service.upload_document(
                content=text,
                source=source or "text_input",
                title=title or "Text Document",
                doc_type="text"
            )
        else:
            raise HTTPException(status_code=400, detail="Either file or text must be provided")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_document(request: QueryRequest):
    """
    Query a document with a question
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    try:
        result = await api_service.query_document(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents
    """
    try:
        documents = api_service.list_documents()
        return {"documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_info(document_id: str):
    """
    Get information about a specific document
    """
    try:
        doc_info = api_service.get_document_info(document_id)
        if not doc_info:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system")
async def get_system_info():
    """
    Get system configuration and status
    """
    try:
        info = api_service.get_system_info()
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its chunks
    """
    try:
        if not api_service.delete_document(document_id):
            raise HTTPException(status_code=404, detail="Document not found")

        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        system_info = api_service.get_system_info()
        return {
            "status": "healthy",
            "message": "Track B Mini RAG API is operational",
            "system_info": system_info
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"System error: {str(e)}"
        }

# Additional utility endpoints for Track B compliance

@router.get("/chunking-params")
async def get_chunking_parameters():
    """
    Get current chunking parameters
    """
    try:
        params = api_service.chunker.get_chunking_parameters()
        return params
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reranker-info")
async def get_reranker_info():
    """
    Get reranker configuration information
    """
    try:
        info = api_service.reranker.get_reranker_info()
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-db-info")
async def get_vector_db_info():
    """
    Get vector database configuration information
    """
    try:
        info = {
            "provider": api_service.vector_db.provider,
            "collection_name": "hackrx_documents",
            "embedding_dimension": 1536,
            "base_url": api_service.vector_db.base_url,
            "api_configured": bool(api_service.vector_db.api_key)
        }
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Evaluation endpoint for Track B compliance
@router.post("/evaluate")
async def evaluate_system(document_id: Optional[str] = None):
    """
    Run evaluation with 5 Q&A pairs (Track B requirement)
    """
    try:
        from evaluation.track_b_evaluation import get_track_b_evaluation
        
        if not document_id:
            # Return evaluation framework info
            evaluation = get_track_b_evaluation()
            return {
                "evaluation_questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "category": q.category,
                        "difficulty": q.difficulty
                    }
                    for q in evaluation.evaluation_questions
                ],
                "message": "Evaluation framework ready. Provide document_id to run evaluation.",
                "note": "This endpoint provides the evaluation structure required for Track B compliance"
            }
        
        # Run actual evaluation
        evaluation = get_track_b_evaluation()
        results = await evaluation.evaluate_document(api_service, document_id)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate/{document_id}")
async def evaluate_document(document_id: str):
    """
    Evaluate a specific document with 5 Q&A pairs
    """
    try:
        from evaluation.track_b_evaluation import get_track_b_evaluation
        
        evaluation = get_track_b_evaluation()
        results = await evaluation.evaluate_document(api_service, document_id)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
