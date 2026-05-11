import os
import numpy as np
from asyncio import Semaphore
from typing import List, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
MAX_CONCURRENT_EMBEDDINGS = 5

embedding_semaphore = Semaphore(MAX_CONCURRENT_EMBEDDINGS)
_client = None  # type: Optional[AsyncOpenAI]


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("GENERATION_OPENAI_API_KEY"))
    return _client


async def gemini_embed(texts: List[str]) -> np.ndarray:
    """Create embeddings for a list of texts using OpenAI."""
    async with embedding_semaphore:
        response = await _get_client().embeddings.create(model=EMBEDDING_MODEL, input=texts)
        vectors = [d.embedding for d in response.data]
        return np.array(vectors, dtype=np.float32)


async def gemini_embed_query(query: str) -> np.ndarray:
    """Create embedding for a single query using OpenAI."""
    async with embedding_semaphore:
        response = await _get_client().embeddings.create(model=EMBEDDING_MODEL, input=[query])
        return np.array([response.data[0].embedding], dtype=np.float32)
