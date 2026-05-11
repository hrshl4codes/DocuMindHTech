"""
DocuMind AI Chunking Service
Implements intelligent chunking strategy with metadata for citations
Chunking parameters: 800-1200 tokens with 10-15% overlap
"""

import re
import hashlib
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocuMindChunkingService:
    """Intelligent chunking service for DocuMind AI"""
    
    def __init__(
        self,
        chunk_size: int = 1000,  # 800-1200 tokens
        chunk_overlap: int = 150,  # 10-15% overlap
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators for better chunking
        if separators is None:
            self.separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamation
                "? ",    # Question
                "; ",    # Semicolon
                ", ",    # Comma
                " ",     # Space
                ""       # Character level
            ]
        else:
            self.separators = separators
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def chunk_document(
        self, 
        content: str, 
        source: str, 
        title: str = "",
        doc_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk document with comprehensive metadata for citations
        
        Args:
            content: Document text content
            source: Source URL or file path
            title: Document title
            doc_id: Unique document identifier
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not content or not content.strip():
            return []
        
        # Generate document ID if not provided
        if not doc_id:
            doc_id = hashlib.sha256(f"{source}_{title}".encode()).hexdigest()[:16]
        
        # Clean and normalize content
        cleaned_content = self._clean_content(content)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(cleaned_content)
        
        # Create chunk metadata
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            metadata = self._create_chunk_metadata(
                chunk=chunk,
                chunk_index=i,
                total_chunks=len(chunks),
                source=source,
                title=title,
                doc_id=doc_id,
                position=i
            )
            chunk_metadata.append(metadata)
        
        print(f"✅ Created {len(chunks)} chunks for document: {title or source}")
        return chunk_metadata
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize document content"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters that might interfere with chunking
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
        
        # Normalize line breaks
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        return content.strip()
    
    def _create_chunk_metadata(
        self, 
        chunk: str, 
        chunk_index: int, 
        total_chunks: int,
        source: str, 
        title: str, 
        doc_id: str,
        position: int
    ) -> Dict[str, Any]:
        """Create comprehensive metadata for a chunk"""
        
        # Generate unique chunk ID
        chunk_id = f"{doc_id}_chunk_{chunk_index}"
        
        # Extract section information if available
        section = self._extract_section(chunk, chunk_index)
        
        # Calculate chunk statistics
        word_count = len(chunk.split())
        char_count = len(chunk)
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = char_count // 4
        
        metadata = {
            # Core identification
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "position": position,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            
            # Source information
            "source": source,
            "title": title or "Untitled Document",
            "section": section,
            
            # Content information
            "text": chunk,
            "word_count": word_count,
            "char_count": char_count,
            "estimated_tokens": estimated_tokens,
            
            # Chunking parameters
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "overlap_percentage": (self.chunk_overlap / self.chunk_size) * 100,
            
            # Citation metadata
            "citation_source": source,
            "citation_title": title or "Untitled Document",
            "citation_section": section,
            "citation_position": f"Chunk {chunk_index + 1} of {total_chunks}",
            
            # Additional metadata for retrieval
            "has_numbers": bool(re.search(r'\d+', chunk)),
            "has_questions": chunk.strip().endswith('?'),
            "has_lists": bool(re.search(r'^\s*[-*•]\s', chunk, re.MULTILINE)),
            "language": self._detect_language(chunk),
        }
        
        return metadata
    
    def _extract_section(self, chunk: str, chunk_index: int) -> str:
        """Extract section information from chunk content"""
        # Look for common section markers
        section_patterns = [
            r'^#+\s*(.+)$',  # Markdown headers
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headers
            r'^\d+\.\s*(.+)$',  # Numbered sections
            r'^[A-Z][a-z]+.*:$',  # Title case with colon
        ]
        
        lines = chunk.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if not line:
                continue
                
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    return match.group(1).strip()
        
        # Fallback to generic section
        return f"Section {chunk_index + 1}"
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Basic heuristics for common languages
        if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', text, re.IGNORECASE):
            return "non-english"
        elif re.search(r'[一-龯]', text):  # Chinese characters
            return "chinese"
        elif re.search(r'[あ-ん]', text):  # Hiragana
            return "japanese"
        elif re.search(r'[가-힣]', text):  # Korean
            return "korean"
        else:
            return "english"
    
    def get_chunking_parameters(self) -> Dict[str, Any]:
        """Get current chunking parameters for documentation"""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "overlap_percentage": (self.chunk_overlap / self.chunk_size) * 100,
            "separators": self.separators,
            "strategy": "RecursiveCharacterTextSplitter",
            "token_estimation": "char_count / 4",
            "compliance": "Track B - 800-1200 tokens with 10-15% overlap"
        }
    
    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate chunk quality and provide statistics"""
        if not chunks:
            return {"error": "No chunks to validate"}
        
        total_chunks = len(chunks)
        total_tokens = sum(chunk.get("estimated_tokens", 0) for chunk in chunks)
        avg_tokens = total_tokens / total_chunks if total_chunks > 0 else 0
        
        # Check chunk size distribution
        oversized_chunks = [c for c in chunks if c.get("estimated_tokens", 0) > self.chunk_size * 1.2]
        undersized_chunks = [c for c in chunks if c.get("estimated_tokens", 0) < self.chunk_size * 0.5]
        
        # Check for broken sentences
        broken_sentences = 0
        for chunk in chunks:
            text = chunk.get("text", "")
            if text and not text.strip().endswith((".", "!", "?", "\n")):
                broken_sentences += 1
        
        validation_stats = {
            "total_chunks": total_chunks,
            "total_estimated_tokens": total_tokens,
            "average_tokens_per_chunk": round(avg_tokens, 2),
            "oversized_chunks": len(oversized_chunks),
            "undersized_chunks": len(undersized_chunks),
            "broken_sentences": broken_sentences,
            "chunk_size_compliance": len(oversized_chunks) == 0,
            "sentence_boundary_compliance": broken_sentences == 0,
            "overall_quality": "good" if len(oversized_chunks) == 0 and broken_sentences == 0 else "needs_improvement"
        }
        
        return validation_stats

# Global chunking service instance
documind_chunker = DocuMindChunkingService()

def get_chunker() -> DocuMindChunkingService:
    """Get the global DocuMind chunking service instance"""
    return documind_chunker
