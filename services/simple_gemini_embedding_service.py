import os
import asyncio
import random
import numpy as np
import httpx
from asyncio import Semaphore
from typing import List
from dotenv import load_dotenv
from services.logger import get_logger

load_dotenv()

log = get_logger("gemini_embeddings")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAX_CONCURRENT_EMBEDDINGS = 5
MAX_RETRIES = 3
EMBEDDING_RETRY_DELAY = 1.0

# Rate limiting semaphore
embedding_semaphore = Semaphore(MAX_CONCURRENT_EMBEDDINGS)


async def gemini_embed(texts: List[str]) -> np.ndarray:
    """
    Creates embeddings using Gemini's REST API with rate limiting
    """
    async with embedding_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                # Use Gemini's REST API for embeddings
                url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={GEMINI_API_KEY}"
                
                embeddings = []
                async with httpx.AsyncClient(timeout=30.0) as client:
                    for text in texts:
                        payload = {
                            "content": {
                                "parts": [{"text": text}]
                            },
                            "taskType": "RETRIEVAL_DOCUMENT"
                        }
                        response = await client.post(url, json=payload)
                        response.raise_for_status()
                        result = response.json()
                        embedding = result['embedding']['values']
                        embeddings.append(embedding)

                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = EMBEDDING_RETRY_DELAY * (2**attempt) + random.uniform(0, 1)
                        log.warning("embedding rate limit hit, retrying in %.2fs (attempt %d)", delay, attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                log.error("error creating Gemini embeddings: %s", e)
                raise


async def gemini_embed_query(query: str) -> np.ndarray:
    """
    Creates embedding for a single query using Gemini REST API with rate limiting
    """
    async with embedding_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={GEMINI_API_KEY}"
                
                payload = {
                    "content": {
                        "parts": [{"text": query}]
                    },
                    "taskType": "RETRIEVAL_QUERY"
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    embedding = result['embedding']['values']
                return np.array([embedding], dtype=np.float32)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = EMBEDDING_RETRY_DELAY * (2**attempt) + random.uniform(0, 1)
                        log.warning("query embedding rate limit hit, retrying in %.2fs (attempt %d)", delay, attempt + 1)
                        await asyncio.sleep(delay)
                        continue
                log.error("error creating Gemini query embedding: %s", e)
                raise

