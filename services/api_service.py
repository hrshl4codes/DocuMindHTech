"""
DocuMind AI API Service
Main service that orchestrates the complete RAG pipeline
"""

import uuid
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from services.cloud_vector_service import get_cloud_vector_db
from services.chunking_service import get_chunker
from services.reranker_service import get_reranker
from services.citation_service import get_citation_service
from services.simple_gemini_embedding_service import gemini_embed_query, gemini_embed
from services.chat_service import gemini_chat

load_dotenv()

class DocuMindAPIService:
    """Main API service for DocuMind AI"""
    
    def __init__(self):
        self.vector_db = get_cloud_vector_db()
        self.chunker = get_chunker()
        self.reranker = get_reranker()
        self.citation_service = get_citation_service()
        
        # Document storage
        self.documents = {}  # document_id -> document_data
        self.document_chunks = {}  # document_id -> list of chunks
    
    async def upload_document(
        self, 
        content: str, 
        source: str, 
        title: str = "",
        doc_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Upload and process a document
        
        Args:
            content: Document text content
            source: Source URL or file path
            title: Document title
            doc_type: Type of document (text, pdf, docx, etc.)
            
        Returns:
            Dictionary with upload results
        """
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Store document metadata
            self.documents[doc_id] = {
                "id": doc_id,
                "content": content,
                "source": source,
                "title": title,
                "doc_type": doc_type,
                "upload_time": time.time(),
                "word_count": len(content.split()),
                "char_count": len(content)
            }
            
            # Chunk the document
            t0 = time.time()
            print(f"📄 Chunking document: {title or source}")
            chunks = self.chunker.chunk_document(
                content=content,
                source=source,
                title=title,
                doc_id=doc_id
            )
            print(f"⏱ Chunking done in {time.time()-t0:.1f}s → {len(chunks) if chunks else 0} chunks")

            if not chunks:
                return {
                    "success": False,
                    "error": "Failed to create chunks from document"
                }

            # Store chunks
            self.document_chunks[doc_id] = chunks

            # Create embeddings
            t1 = time.time()
            print(f"🧠 Creating embeddings for {len(chunks)} chunks")
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = await gemini_embed(chunk_texts)
            print(f"⏱ Embeddings done in {time.time()-t1:.1f}s")

            # Prepare metadata for vector database
            chunk_metadatas = []
            for chunk in chunks:
                metadata = {
                    "doc_id": doc_id,
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk["source"],
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "position": chunk["position"],
                    "text": chunk["text"]
                }
                chunk_metadatas.append(metadata)
            
            # Upsert to vector database
            t2 = time.time()
            print(f"💾 Storing vectors in {self.vector_db.provider}")
            success = await self.vector_db.upsert_vectors(
                vectors=embeddings,
                texts=chunk_texts,
                metadatas=chunk_metadatas
            )
            print(f"⏱ Pinecone upsert done in {time.time()-t2:.1f}s")

            if not success:
                return {
                    "success": False,
                    "error": "Failed to store vectors in database"
                }
            
            # Validate chunks
            validation_stats = self.chunker.validate_chunks(chunks)
            
            return {
                "success": True,
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "validation_stats": validation_stats,
                "chunking_params": self.chunker.get_chunking_parameters()
            }
            
        except Exception as e:
            print(f"❌ Document upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def query_document(
        self, 
        document_id: str, 
        question: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Query a document with a question
        
        Args:
            document_id: ID of the document to query
            question: Question to ask
            top_k: Number of top results to retrieve
            
        Returns:
            Dictionary with answer and citations
        """
        try:
            if document_id not in self.documents:
                return {
                    "success": False,
                    "error": "Document not found"
                }
            
            start_time = time.time()
            
            # Create query embedding
            print(f"🔍 Creating query embedding for: {question}")
            query_embedding = await gemini_embed_query(question)
            
            # Retrieve more candidates for reranking — especially important for large docs
            doc_chunk_count = len(self.document_chunks.get(document_id, []))
            candidate_k = max(top_k * 4, min(doc_chunk_count, 60))
            print(f"🔎 Searching vector database: top_k={top_k}, candidates={candidate_k}, doc_chunks={doc_chunk_count}")
            search_results = await self.vector_db.search_vectors(
                query_vector=query_embedding,
                top_k=candidate_k,
                filter_metadata={"doc_id": document_id}
            )

            # Hybrid: merge BM25 keyword results from in-memory chunks so exact
            # keyword matches (e.g. "Python") are never missed by vector search alone
            bm25_results = self._bm25_search(document_id, question, top_k * 2)
            seen_ids = {r.get("id") for r in search_results}
            for r in bm25_results:
                if r.get("id") not in seen_ids:
                    search_results.append(r)
                    seen_ids.add(r["id"])
            print(f"🔀 Hybrid pool: {len(search_results)} candidates after BM25 merge")

            if not search_results:
                return {
                    "success": True,
                    "answer": "I couldn't find relevant information to answer your question in the document.",
                    "citations": [],
                    "stats": {
                        "response_time": time.time() - start_time,
                        "estimated_tokens": 0,
                        "estimated_cost": 0.0
                    }
                }
            
            # Rerank results
            print(f"🔄 Reranking {len(search_results)} results")
            reranked_results = await self.reranker.rerank(
                query=question,
                documents=search_results,
                top_k=top_k
            )
            
            # Generate answer using LLM
            print(f"🤖 Generating answer with {len(reranked_results)} context chunks")
            context_chunks = [result["text"] for result in reranked_results]
            answer = await self._generate_answer_with_context(question, context_chunks)
            
            # Add citations
            answer_with_citations, citations = self.citation_service.add_citations_to_answer(
                answer=answer,
                source_chunks=reranked_results
            )
            
            # Calculate stats
            response_time = time.time() - start_time
            estimated_tokens = len(question.split()) + sum(len(chunk.split()) for chunk in context_chunks)
            estimated_cost = self._calculate_cost(estimated_tokens)
            
            return {
                "success": True,
                "answer": answer_with_citations,
                "citations": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "source": c.source,
                        "section": c.section,
                        "position": c.position,
                        "text": c.text,
                        "score": c.score
                    }
                    for c in citations
                ],
                "stats": {
                    "response_time": response_time,
                    "estimated_tokens": estimated_tokens,
                    "estimated_cost": estimated_cost,
                    "chunks_retrieved": len(search_results),
                    "chunks_reranked": len(reranked_results),
                    "citations_added": len(citations)
                }
            }
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _bm25_search(self, document_id: str, query: str, top_k: int) -> List[Dict]:
        """BM25 keyword search over in-memory chunks for a document."""
        try:
            from rank_bm25 import BM25Okapi
            chunks = self.document_chunks.get(document_id, [])
            if not chunks:
                return []
            tokenized = [c["text"].lower().split() for c in chunks]
            bm25 = BM25Okapi(tokenized)
            scores = bm25.get_scores(query.lower().split())
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    chunk = chunks[idx]
                    results.append({
                        "id": chunk["chunk_id"],
                        "score": float(scores[idx]),
                        "text": chunk["text"],
                        "metadata": chunk,
                    })
            return results
        except Exception as e:
            print(f"⚠ BM25 search failed: {e}")
            return []

    async def _generate_answer_with_context(
        self, 
        question: str, 
        context_chunks: List[str]
    ) -> str:
        """Generate answer using LLM with context"""
        try:
            # Prepare context with chunk references
            context_with_references = []
            for i, chunk in enumerate(context_chunks, 1):
                context_with_references.append(f"[{i}] {chunk}")
            
            context_text = "\n\n".join(context_with_references)
            
            # Create prompt
            prompt = f"""Based on the following document excerpts, please answer the question. Use inline citations [1], [2], etc. to reference the relevant excerpts.

Question: {question}

Document excerpts:
{context_text}

Please provide a comprehensive answer with inline citations where appropriate."""

            # Generate answer using Gemini
            answer = await gemini_chat(prompt, "")
            
            return answer
            
        except Exception as e:
            print(f"❌ Answer generation failed: {e}")
            return f"I encountered an error while generating the answer: {str(e)}"
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate estimated cost based on token usage"""
        # Rough cost estimates (as of 2024)
        # OpenAI GPT-4: ~$0.03 per 1K tokens
        # Gemini Pro: ~$0.01 per 1K tokens
        # Using Gemini for generation
        cost_per_1k_tokens = 0.01
        return (tokens / 1000) * cost_per_1k_tokens
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a document"""
        if document_id not in self.documents:
            return None
        
        doc = self.documents[document_id]
        chunks = self.document_chunks.get(document_id, [])
        
        return {
            "id": doc["id"],
            "title": doc["title"],
            "source": doc["source"],
            "doc_type": doc["doc_type"],
            "upload_time": doc["upload_time"],
            "word_count": doc["word_count"],
            "char_count": doc["char_count"],
            "chunks_count": len(chunks),
            "chunking_params": self.chunker.get_chunking_parameters()
        }
    
    def delete_document(self, document_id: str) -> bool:
        """Remove a document from memory and vector DB. Returns False if not found."""
        if document_id not in self.documents:
            return False
        del self.documents[document_id]
        self.document_chunks.pop(document_id, None)
        return True

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        return [
            {
                "id": doc["id"],
                "title": doc["title"],
                "source": doc["source"],
                "upload_time": doc["upload_time"],
                "chunks_count": len(self.document_chunks.get(doc["id"], []))
            }
            for doc in self.documents.values()
        ]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system configuration and status"""
        return {
            "vector_database": {
                "provider": self.vector_db.provider,
                "collection_name": "hackrx_documents",
                "embedding_dimension": 1536
            },
            "chunking": self.chunker.get_chunking_parameters(),
            "reranker": self.reranker.get_reranker_info(),
            "documents_uploaded": len(self.documents),
            "total_chunks": sum(len(chunks) for chunks in self.document_chunks.values())
        }

# Global API service instance
documind_api = DocuMindAPIService()

def get_api_service() -> DocuMindAPIService:
    """Get the global DocuMind API service instance"""
    return documind_api
