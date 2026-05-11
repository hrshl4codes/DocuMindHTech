"""
DocuMind AI Reranker Service
Implements cloud-based reranking with Cohere, Jina, Voyage, or BGE
"""

import os
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Reranker configuration
RERANKER_PROVIDER = os.getenv("RERANKER_PROVIDER", "cohere")  # cohere, jina, voyage, bge
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
BGE_API_KEY = os.getenv("BGE_API_KEY")

class DocuMindRerankerService:
    """Reranker service for DocuMind AI"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or RERANKER_PROVIDER
        self.api_key = self._get_api_key()
        self.base_url = self._get_base_url()
    
    def _get_api_key(self) -> str:
        """Get API key for the selected provider"""
        if self.provider == "cohere":
            return COHERE_API_KEY
        elif self.provider == "jina":
            return JINA_API_KEY
        elif self.provider == "voyage":
            return VOYAGE_API_KEY
        elif self.provider == "bge":
            return BGE_API_KEY
        else:
            raise ValueError(f"Unsupported reranker provider: {self.provider}")
    
    def _get_base_url(self) -> str:
        """Get base URL for the selected provider"""
        urls = {
            "cohere": "https://api.cohere.ai/v1",
            "jina": "https://api.jina.ai/v1",
            "voyage": "https://api.voyageai.com/v1",
            "bge": "https://api.bge-reranker.com/v1"
        }
        return urls.get(self.provider, "")
    
    async def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cloud-based reranker
        
        Args:
            query: Search query
            documents: List of document dictionaries with 'text' field
            top_k: Number of top documents to return
            
        Returns:
            List of reranked documents with scores
        """
        if not documents or not query:
            return []
        
        try:
            if self.provider == "cohere":
                return await self._rerank_cohere(query, documents, top_k)
            elif self.provider == "jina":
                return await self._rerank_jina(query, documents, top_k)
            elif self.provider == "voyage":
                return await self._rerank_voyage(query, documents, top_k)
            elif self.provider == "bge":
                return await self._rerank_bge(query, documents, top_k)
            else:
                raise ValueError(f"Unsupported reranker provider: {self.provider}")
        except Exception as e:
            print(f"❌ Reranking failed: {e}")
            # Fallback to simple text similarity
            return self._fallback_rerank(query, documents, top_k)
    
    async def _rerank_cohere(self, query: str, documents: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Rerank using Cohere Rerank API"""
        if not self.api_key:
            raise ValueError("COHERE_API_KEY not found")
        
        # Prepare documents for Cohere
        doc_texts = [doc.get("text", "") for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "rerank-english-v2.0",
                    "query": query,
                    "documents": doc_texts,
                    "top_k": min(top_k, len(documents))
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Process results
        reranked_docs = []
        for item in result.get("results", []):
            doc_index = item["index"]
            if doc_index < len(documents):
                doc = documents[doc_index].copy()
                doc["rerank_score"] = item["relevance_score"]
                doc["rerank_provider"] = "cohere"
                reranked_docs.append(doc)
        
        return reranked_docs[:top_k]
    
    async def _rerank_jina(self, query: str, documents: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Rerank using Jina Reranker API"""
        if not self.api_key:
            raise ValueError("JINA_API_KEY not found")
        
        # Prepare documents for Jina
        doc_texts = [doc.get("text", "") for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "jina-reranker-v1-base-en",
                    "query": query,
                    "documents": doc_texts,
                    "top_k": min(top_k, len(documents))
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Process results
        reranked_docs = []
        for item in result.get("results", []):
            doc_index = item["index"]
            if doc_index < len(documents):
                doc = documents[doc_index].copy()
                doc["rerank_score"] = item["relevance_score"]
                doc["rerank_provider"] = "jina"
                reranked_docs.append(doc)
        
        return reranked_docs[:top_k]
    
    async def _rerank_voyage(self, query: str, documents: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Rerank using Voyage Rerank API"""
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not found")
        
        # Prepare documents for Voyage
        doc_texts = [doc.get("text", "") for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "voyage-rerank-lite-1",
                    "query": query,
                    "documents": doc_texts,
                    "top_k": min(top_k, len(documents))
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Process results
        reranked_docs = []
        for item in result.get("results", []):
            doc_index = item["index"]
            if doc_index < len(documents):
                doc = documents[doc_index].copy()
                doc["rerank_score"] = item["relevance_score"]
                doc["rerank_provider"] = "voyage"
                reranked_docs.append(doc)
        
        return reranked_docs[:top_k]
    
    async def _rerank_bge(self, query: str, documents: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Rerank using BGE Reranker API"""
        if not self.api_key:
            raise ValueError("BGE_API_KEY not found")
        
        # Prepare documents for BGE
        doc_texts = [doc.get("text", "") for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "bge-reranker-base",
                    "query": query,
                    "documents": doc_texts,
                    "top_k": min(top_k, len(documents))
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Process results
        reranked_docs = []
        for item in result.get("results", []):
            doc_index = item["index"]
            if doc_index < len(documents):
                doc = documents[doc_index].copy()
                doc["rerank_score"] = item["relevance_score"]
                doc["rerank_provider"] = "bge"
                reranked_docs.append(doc)
        
        return reranked_docs[:top_k]
    
    def _fallback_rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
        """Fallback reranking using simple text similarity"""
        import difflib
        
        query_lower = query.lower()
        scored_docs = []
        
        for doc in documents:
            text = doc.get("text", "").lower()
            # Simple similarity score
            similarity = difflib.SequenceMatcher(None, query_lower, text).ratio()
            
            doc_copy = doc.copy()
            doc_copy["rerank_score"] = similarity
            doc_copy["rerank_provider"] = "fallback"
            scored_docs.append(doc_copy)
        
        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_docs[:top_k]
    
    def get_reranker_info(self) -> Dict[str, Any]:
        """Get reranker configuration information"""
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "supported_providers": ["cohere", "jina", "voyage", "bge"],
            "compliance": "Track B - Cloud-based reranker"
        }

# Global reranker service instance
documind_reranker = DocuMindRerankerService()

def get_reranker() -> DocuMindRerankerService:
    """Get the global DocuMind reranker service instance"""
    return documind_reranker
