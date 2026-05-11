import os
import numpy as np
from asyncio import Semaphore
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("GENERATION_OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
MAX_CONCURRENT_EMBEDDINGS = 5

print("🚀 Initializing OpenAI Embeddings...")
print("✅ OpenAI Embeddings initialized.")

_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
embedding_semaphore = Semaphore(MAX_CONCURRENT_EMBEDDINGS)


async def gemini_embed(texts: List[str]) -> np.ndarray:
    """Create embeddings for a list of texts using OpenAI."""
    async with embedding_semaphore:
        response = await _client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        vectors = [d.embedding for d in response.data]
        return np.array(vectors, dtype=np.float32)


async def gemini_embed_query(query: str) -> np.ndarray:
    """Create embedding for a single query using OpenAI."""
    async with embedding_semaphore:
        response = await _client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
        return np.array([response.data[0].embedding], dtype=np.float32)
