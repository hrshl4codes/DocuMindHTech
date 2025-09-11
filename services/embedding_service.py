import os
import asyncio
import random
import numpy as np
from asyncio import Semaphore
from typing import List
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Configuration
GENERATION_OPENAI_API_KEY = os.getenv("GENERATION_OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
MAX_CONCURRENT_EMBEDDINGS = 5
MAX_RETRIES = 3
EMBEDDING_RETRY_DELAY = 1.0

# Initialize OpenAI Embeddings service
print("🚀 Initializing OpenAI Embeddings...")
embedding_service = OpenAIEmbeddings(
    model=OPENAI_EMBEDDING_MODEL, api_key=GENERATION_OPENAI_API_KEY
)
print("✅ OpenAI Embeddings initialized.")

# Rate limiting semaphore
embedding_semaphore = Semaphore(MAX_CONCURRENT_EMBEDDINGS)


async def openai_embed(texts: List[str]) -> np.ndarray:
    """
    Creates embeddings using OpenAI's text-embedding-3-large model with rate limiting
    """
    async with embedding_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                # Use the embedding_service initialized globally
                embeddings = await asyncio.to_thread(
                    embedding_service.embed_documents, texts
                )
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = EMBEDDING_RETRY_DELAY * (2**attempt) + random.uniform(
                            0, 1
                        )
                        print(
                            f"⚠ Embedding rate limit hit, retrying in {delay:.2f}s (attempt {attempt + 1})"
                        )
                        await asyncio.sleep(delay)
                        continue
                print(f"Error creating OpenAI embeddings: {e}")
                raise


async def openai_embed_query(query: str) -> np.ndarray:
    """
    Creates embedding for a single query using OpenAI with rate limiting
    """
    async with embedding_semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                embedding = await asyncio.to_thread(
                    embedding_service.embed_query, query
                )
                return np.array([embedding], dtype=np.float32)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        delay = EMBEDDING_RETRY_DELAY * (2**attempt) + random.uniform(
                            0, 1
                        )
                        print(
                            f"⚠ Query embedding rate limit hit, retrying in {delay:.2f}s (attempt {attempt + 1})"
                        )
                        await asyncio.sleep(delay)
                        continue
                print(f"Error creating OpenAI query embedding: {e}")
                raise
