"""
DocuMind AI API Routes
FastAPI routes for the DocuMind AI system
"""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from services.api_service import get_api_service
from services.cloud_vector_service import COLLECTION_NAME, EMBEDDING_DIMENSION

router = APIRouter(prefix="/api", tags=["DocuMind AI"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

BLOCKED_EXTENSIONS = {
    "exe", "sh", "bat", "cmd", "ps1", "py", "js", "php", "rb", "pl",
}

class QueryRequest(BaseModel):
    document_id: str
    question: str
    top_k: Optional[int] = 10

@router.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the frontend interface"""
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

@router.post("/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    title: Optional[str] = Form(""),
    source: Optional[str] = Form("")
):
    api_service = get_api_service()
    try:
        if file and file.filename:
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

            if ext in BLOCKED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"File type .{ext} is not allowed")

            content = await file.read()

            if len(content) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

            from services.text_extract import process_file_content
            content_str = await process_file_content(content, ext, file.filename)

            result = await api_service.upload_document(
                content=content_str,
                source=source or file.filename,
                title=title or file.filename,
                doc_type=ext or "unknown",
            )

        elif text:
            result = await api_service.upload_document(
                content=text,
                source=source or "text_input",
                title=title or "Text Document",
                doc_type="text",
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
    try:
        result = await get_api_service().query_document(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents
    """
    try:
        documents = get_api_service().list_documents()
        return {"documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document_info(document_id: str):
    """
    Get information about a specific document
    """
    try:
        doc_info = get_api_service().get_document_info(document_id)
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
        return get_api_service().get_system_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its chunks
    """
    try:
        from services import persistence
        if not persistence.get_document(document_id):
            raise HTTPException(status_code=404, detail="Document not found")

        persistence.delete_document(document_id)
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
        return {"status": "healthy", "system_info": get_api_service().get_system_info()}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

# Additional utility endpoints for Track B compliance

@router.get("/chunking-params")
async def get_chunking_parameters():
    """
    Get current chunking parameters
    """
    try:
        return get_api_service().chunker.get_chunking_parameters()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reranker-info")
async def get_reranker_info():
    """
    Get reranker configuration information
    """
    try:
        return get_api_service().reranker.get_reranker_info()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector-db-info")
async def get_vector_db_info():
    """
    Get vector database configuration information
    """
    try:
        vdb = get_api_service().vector_db
        return {
            "provider":           vdb.provider,
            "collection_name":    COLLECTION_NAME,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "api_configured":     bool(vdb.api_key),
        }
        
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
        results = await evaluation.evaluate_document(get_api_service(), document_id)

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
        results = await evaluation.evaluate_document(get_api_service(), document_id)

        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
