"""
DocuMind AI Citation Service
Implements inline citations [1], [2] with source snippets display
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class Citation:
    """Citation data structure"""
    id: int
    text: str
    source: str
    title: str
    section: str
    position: str
    chunk_id: str
    score: float = 0.0

class DocuMindCitationService:
    """Citation service for DocuMind AI"""
    
    def __init__(self):
        self.citation_pattern = r'\[(\d+)\]'
        self.max_citations = 10  # Maximum number of citations to show
    
    def add_citations_to_answer(
        self, 
        answer: str, 
        source_chunks: List[Dict[str, Any]]
    ) -> Tuple[str, List[Citation]]:
        """
        Add inline citations to answer and create citation list
        
        Args:
            answer: Generated answer text
            source_chunks: List of source chunks used for generation
            
        Returns:
            Tuple of (answer_with_citations, citation_list)
        """
        if not source_chunks:
            return answer, []
        
        # Create citations from source chunks
        citations = self._create_citations(source_chunks)
        
        # Add inline citations to answer
        answer_with_citations = self._insert_citations(answer, citations)
        
        return answer_with_citations, citations
    
    def _create_citations(self, source_chunks: List[Dict[str, Any]]) -> List[Citation]:
        """Create citation objects from source chunks"""
        citations = []
        
        for i, chunk in enumerate(source_chunks[:self.max_citations]):
            citation = Citation(
                id=i + 1,
                text=chunk.get("text", ""),
                source=chunk.get("source", "Unknown Source"),
                title=chunk.get("title", "Untitled Document"),
                section=chunk.get("section", f"Section {i + 1}"),
                position=chunk.get("citation_position", f"Chunk {i + 1}"),
                chunk_id=chunk.get("chunk_id", f"chunk_{i}"),
                score=chunk.get("rerank_score", chunk.get("score", 0.0))
            )
            citations.append(citation)
        
        return citations
    
    def _insert_citations(self, answer: str, citations: List[Citation]) -> str:
        """
        Insert inline citations into answer text
        Uses simple sentence-based citation placement
        """
        if not citations:
            return answer
        
        # Split answer into sentences
        sentences = self._split_into_sentences(answer)
        
        # Add citations to relevant sentences
        cited_sentences = []
        citation_count = 0
        
        for i, sentence in enumerate(sentences):
            # Determine if this sentence should have a citation
            should_cite = self._should_cite_sentence(sentence, i, len(sentences))
            
            if should_cite and citation_count < len(citations):
                citation_id = citation_count + 1
                sentence_with_citation = f"{sentence} [{citation_id}]"
                citation_count += 1
            else:
                sentence_with_citation = sentence
            
            cited_sentences.append(sentence_with_citation)
        
        # Join sentences back together
        answer_with_citations = " ".join(cited_sentences)
        
        return answer_with_citations
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _should_cite_sentence(self, sentence: str, sentence_index: int, total_sentences: int) -> bool:
        """
        Determine if a sentence should have a citation
        Uses heuristics to identify important sentences
        """
        # Always cite the first sentence
        if sentence_index == 0:
            return True
        
        # Cite sentences with specific keywords
        citation_keywords = [
            "according to", "states", "indicates", "shows", "reveals",
            "demonstrates", "confirms", "suggests", "implies", "based on",
            "as mentioned", "as stated", "the document", "the source",
            "research", "study", "data", "evidence", "findings"
        ]
        
        sentence_lower = sentence.lower()
        for keyword in citation_keywords:
            if keyword in sentence_lower:
                return True
        
        # Cite sentences with numbers or statistics
        if re.search(r'\d+', sentence):
            return True
        
        # Cite every 2-3 sentences to maintain good coverage
        if sentence_index % 3 == 0:
            return True
        
        return False
    
    def format_citations_display(self, citations: List[Citation]) -> str:
        """
        Format citations for display in the UI
        Returns HTML-formatted citation list
        """
        if not citations:
            return ""
        
        citation_html = "<div class='citations'>\n<h4>Sources:</h4>\n<ol>\n"
        
        for citation in citations:
            citation_html += f"""
            <li id="citation-{citation.id}">
                <strong>[{citation.id}]</strong> {citation.title}
                <br>
                <small>
                    <strong>Source:</strong> {citation.source}<br>
                    <strong>Section:</strong> {citation.section}<br>
                    <strong>Position:</strong> {citation.position}
                </small>
                <details>
                    <summary>View excerpt</summary>
                    <blockquote>
                        {self._truncate_text(citation.text, 200)}...
                    </blockquote>
                </details>
            </li>
            """
        
        citation_html += "</ol>\n</div>"
        return citation_html
    
    def format_citations_markdown(self, citations: List[Citation]) -> str:
        """
        Format citations in Markdown format
        """
        if not citations:
            return ""
        
        citation_md = "## Sources\n\n"
        
        for citation in citations:
            citation_md += f"**[{citation.id}]** {citation.title}\n"
            citation_md += f"- **Source:** {citation.source}\n"
            citation_md += f"- **Section:** {citation.section}\n"
            citation_md += f"- **Position:** {citation.position}\n"
            citation_md += f"- **Excerpt:** {self._truncate_text(citation.text, 150)}...\n\n"
        
        return citation_md
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis"""
        if len(text) <= max_length:
            return text
        
        # Find the last complete word within the limit
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we can find a good break point
            return truncated[:last_space]
        else:
            return truncated
    
    def extract_citations_from_text(self, text: str) -> List[int]:
        """Extract citation IDs from text with citations"""
        matches = re.findall(self.citation_pattern, text)
        return [int(match) for match in matches]
    
    def validate_citations(self, answer: str, citations: List[Citation]) -> Dict[str, Any]:
        """Validate that citations in answer match available citations"""
        citation_ids_in_text = self.extract_citations_from_text(answer)
        available_citation_ids = [c.id for c in citations]
        
        missing_citations = [cid for cid in citation_ids_in_text if cid not in available_citation_ids]
        unused_citations = [cid for cid in available_citation_ids if cid not in citation_ids_in_text]
        
        return {
            "total_citations": len(citations),
            "citations_in_text": len(citation_ids_in_text),
            "missing_citations": missing_citations,
            "unused_citations": unused_citations,
            "citation_coverage": len(citation_ids_in_text) / len(citations) if citations else 0,
            "is_valid": len(missing_citations) == 0
        }
    
    def get_citation_stats(self, citations: List[Citation]) -> Dict[str, Any]:
        """Get statistics about citations"""
        if not citations:
            return {"total": 0, "sources": 0, "sections": 0}
        
        unique_sources = set(c.source for c in citations)
        unique_sections = set(c.section for c in citations)
        avg_score = sum(c.score for c in citations) / len(citations) if citations else 0
        
        return {
            "total_citations": len(citations),
            "unique_sources": len(unique_sources),
            "unique_sections": len(unique_sections),
            "average_relevance_score": round(avg_score, 3),
            "sources": list(unique_sources),
            "sections": list(unique_sections)
        }

# Global citation service instance
documind_citation_service = DocuMindCitationService()

def get_citation_service() -> DocuMindCitationService:
    """Get the global DocuMind citation service instance"""
    return documind_citation_service
