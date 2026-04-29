"""
Track B evaluation framework — 5 Q&A pairs covering core RAG capabilities.
Questions are document-agnostic so they work against any uploaded document.
"""

import time
from dataclasses import dataclass


@dataclass
class EvaluationQuestion:
    id: str
    question: str
    category: str
    difficulty: str


EVALUATION_QUESTIONS = [
    EvaluationQuestion(
        id="q1",
        question="What is the main topic or purpose of this document?",
        category="summary",
        difficulty="easy",
    ),
    EvaluationQuestion(
        id="q2",
        question="What are the key findings, conclusions, or outcomes described?",
        category="analysis",
        difficulty="medium",
    ),
    EvaluationQuestion(
        id="q3",
        question="What specific facts, figures, or data points are mentioned?",
        category="factual",
        difficulty="medium",
    ),
    EvaluationQuestion(
        id="q4",
        question="What recommendations, next steps, or action items are suggested?",
        category="analysis",
        difficulty="hard",
    ),
    EvaluationQuestion(
        id="q5",
        question="Summarize the entire document in three concise sentences.",
        category="summary",
        difficulty="hard",
    ),
]


class TrackBEvaluation:
    def __init__(self):
        self.evaluation_questions = EVALUATION_QUESTIONS

    async def evaluate_document(self, api_service, document_id: str) -> dict:
        results = []

        for q in self.evaluation_questions:
            start = time.time()
            try:
                response = await api_service.query_document(
                    document_id=document_id,
                    question=q.question,
                    top_k=5,
                )
                answer = response.get("answer", "")
                sources_used = len(response.get("sources", []))
                status = "ok"
            except Exception as e:
                answer = ""
                sources_used = 0
                status = f"error: {e}"

            latency = round(time.time() - start, 2)

            results.append({
                "question_id": q.id,
                "question": q.question,
                "category": q.category,
                "difficulty": q.difficulty,
                "answer": answer,
                "latency_seconds": latency,
                "sources_used": sources_used,
                "status": status,
            })

        answered = sum(1 for r in results if r["status"] == "ok" and r["answer"])
        avg_latency = round(
            sum(r["latency_seconds"] for r in results) / len(results), 2
        )

        return {
            "document_id": document_id,
            "total_questions": len(results),
            "answered": answered,
            "average_latency_seconds": avg_latency,
            "results": results,
        }


_instance = None


def get_track_b_evaluation() -> TrackBEvaluation:
    global _instance
    if _instance is None:
        _instance = TrackBEvaluation()
    return _instance
