"""
Cloud Vector Database Service
Implements cloud-hosted vector database integration for Track B compliance
Supports: Pinecone, Weaviate, Qdrant, Supabase pgvector
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# Cloud vector database configuration
VECTOR_DB_PROVIDER = os.getenv("VECTOR_DB_PROVIDER", "pinecone")  # pinecone, weaviate, qdrant, supabase
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Collection/Index configuration
COLLECTION_NAME = "hackrx-documents"
EMBEDDING_DIMENSION = 1536  # OpenAI text-embedding-3-small dimensions

class CloudVectorDB:
    """Unified interface for cloud vector databases"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or VECTOR_DB_PROVIDER
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate cloud vector database client"""
        if self.provider == "pinecone":
            self._init_pinecone()
        elif self.provider == "weaviate":
            self._init_weaviate()
        elif self.provider == "qdrant":
            self._init_qdrant()
        elif self.provider == "supabase":
            self._init_supabase()
        else:
            raise ValueError(f"Unsupported vector database provider: {self.provider}")
    
    def _init_pinecone(self):
        """Initialize Pinecone client"""
        try:
            from pinecone import Pinecone  # noqa: F401
            
            if not PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY not found in environment variables")
            
            pc = Pinecone(api_key=PINECONE_API_KEY)
            self.client = pc
            
            # Create or get collection
            try:
                # Check if index exists
                existing_indexes = pc.list_indexes()
                index_names = [index.name for index in existing_indexes]
                
                if COLLECTION_NAME not in index_names:
                    print(f"Creating Pinecone index: {COLLECTION_NAME}")
                    pc.create_index(
                        name=COLLECTION_NAME,
                        dimension=EMBEDDING_DIMENSION,
                        metric="cosine",
                        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
                    )
                
                self.collection = pc.Index(COLLECTION_NAME)
                print(f"✅ Pinecone initialized with index: {COLLECTION_NAME}")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Pinecone index: {e}")
                print("📝 Running without vector database - some features may be unavailable")
                self.collection = None
            
        except ImportError:
            raise ImportError("pinecone not installed. Run: pip install pinecone")
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {e}")
            raise
    
    def _init_weaviate(self):
        """Initialize Weaviate client"""
        try:
            import weaviate
            
            if not WEAVIATE_URL:
                raise ValueError("WEAVIATE_URL not found in environment variables")
            
            self.client = weaviate.Client(url=WEAVIATE_URL)
            
            # Create schema if it doesn't exist
            schema = {
                "class": COLLECTION_NAME,
                "description": "HackRX document chunks",
                "vectorizer": "none",  # We'll provide our own embeddings
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                    {"name": "title", "dataType": ["text"]},
                    {"name": "section", "dataType": ["text"]},
                    {"name": "position", "dataType": ["int"]},
                    {"name": "doc_id", "dataType": ["text"]},
                ]
            }
            
            if not self.client.schema.exists(COLLECTION_NAME):
                self.client.schema.create_class(schema)
                print(f"✅ Weaviate schema created: {COLLECTION_NAME}")
            else:
                print(f"✅ Weaviate connected to existing schema: {COLLECTION_NAME}")
            
        except ImportError:
            raise ImportError("weaviate-client not installed. Run: pip install weaviate-client")
        except Exception as e:
            print(f"❌ Weaviate initialization failed: {e}")
            raise
    
    def _init_qdrant(self):
        """Initialize Qdrant client"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct  # noqa: F401
            
            if not QDRANT_URL:
                raise ValueError("QDRANT_URL not found in environment variables")
            
            self.client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
            
            # Create collection if it doesn't exist
            try:
                self.client.get_collection(COLLECTION_NAME)
                print(f"✅ Qdrant connected to existing collection: {COLLECTION_NAME}")
            except Exception:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Qdrant collection created: {COLLECTION_NAME}")
            
        except ImportError:
            raise ImportError("qdrant-client not installed. Run: pip install qdrant-client")
        except Exception as e:
            print(f"❌ Qdrant initialization failed: {e}")
            raise
    
    def _init_supabase(self):
        """Initialize Supabase pgvector client"""
        try:
            from supabase import create_client, Client
            
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY not found in environment variables")
            
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Create table if it doesn't exist
            _create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {COLLECTION_NAME} (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                source TEXT,
                title TEXT,
                section TEXT,
                position INTEGER,
                doc_id TEXT,
                embedding VECTOR({EMBEDDING_DIMENSION}),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS {COLLECTION_NAME}_embedding_idx 
            ON {COLLECTION_NAME} USING ivfflat (embedding vector_cosine_ops);
            """
            
            # Note: This would need to be run manually or via Supabase dashboard
            print(f"✅ Supabase client initialized. Please create table: {COLLECTION_NAME}")
            
        except ImportError:
            raise ImportError("supabase not installed. Run: pip install supabase")
        except Exception as e:
            print(f"❌ Supabase initialization failed: {e}")
            raise
    
    async def upsert_vectors(
        self, 
        vectors: List[np.ndarray], 
        texts: List[str], 
        metadatas: List[Dict[str, Any]]
    ) -> bool:
        """Upsert vectors to the cloud database"""
        try:
            if self.provider == "pinecone":
                return await self._upsert_pinecone(vectors, texts, metadatas)
            elif self.provider == "weaviate":
                return await self._upsert_weaviate(vectors, texts, metadatas)
            elif self.provider == "qdrant":
                return await self._upsert_qdrant(vectors, texts, metadatas)
            elif self.provider == "supabase":
                return await self._upsert_supabase(vectors, texts, metadatas)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            print(f"❌ Upsert failed: {e}")
            return False
    
    async def _upsert_pinecone(self, vectors: List[np.ndarray], texts: List[str], metadatas: List[Dict[str, Any]]) -> bool:
        """Upsert to Pinecone"""
        import asyncio
        try:
            vectors_to_upsert = []
            for vector, text, metadata in zip(vectors, texts, metadatas):
                vectors_to_upsert.append({
                    "id": str(uuid.uuid4()),
                    "values": vector.tolist(),
                    "metadata": {"text": text, **metadata}
                })

            # Run sync Pinecone upsert in a thread so it doesn't block the event loop
            batch_size = 100
            loop = asyncio.get_event_loop()
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                await loop.run_in_executor(None, lambda b=batch: self.collection.upsert(vectors=b))

            print(f"✅ Upserted {len(vectors_to_upsert)} vectors to Pinecone")
            return True
        except Exception as e:
            print(f"❌ Pinecone upsert failed: {e}")
            return False
    
    async def _upsert_weaviate(self, vectors: List[np.ndarray], texts: List[str], metadatas: List[Dict[str, Any]]) -> bool:
        """Upsert to Weaviate"""
        try:
            # Prepare data for Weaviate
            for i, (vector, text, metadata) in enumerate(zip(vectors, texts, metadatas)):
                data_object = {
                    "text": text,
                    "source": metadata.get("source", ""),
                    "title": metadata.get("title", ""),
                    "section": metadata.get("section", ""),
                    "position": metadata.get("position", i),
                    "doc_id": metadata.get("doc_id", ""),
                }
                
                self.client.data_object.create(
                    data_object=data_object,
                    class_name=COLLECTION_NAME,
                    vector=vector.tolist()
                )
            
            print(f"✅ Upserted {len(vectors)} vectors to Weaviate")
            return True
        except Exception as e:
            print(f"❌ Weaviate upsert failed: {e}")
            return False
    
    async def _upsert_qdrant(self, vectors: List[np.ndarray], texts: List[str], metadatas: List[Dict[str, Any]]) -> bool:
        """Upsert to Qdrant"""
        try:
            from qdrant_client.models import PointStruct
            
            points = []
            for i, (vector, text, metadata) in enumerate(zip(vectors, texts, metadatas)):
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "text": text,
                        **metadata
                    }
                ))
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=batch
                )
            
            print(f"✅ Upserted {len(points)} vectors to Qdrant")
            return True
        except Exception as e:
            print(f"❌ Qdrant upsert failed: {e}")
            return False
    
    async def _upsert_supabase(self, vectors: List[np.ndarray], texts: List[str], metadatas: List[Dict[str, Any]]) -> bool:
        """Upsert to Supabase pgvector"""
        try:
            # Prepare data for Supabase
            records = []
            for vector, text, metadata in zip(vectors, texts, metadatas):
                records.append({
                    "content": text,
                    "source": metadata.get("source", ""),
                    "title": metadata.get("title", ""),
                    "section": metadata.get("section", ""),
                    "position": metadata.get("position", 0),
                    "doc_id": metadata.get("doc_id", ""),
                    "embedding": vector.tolist()
                })
            
            # Insert records
            self.client.table(COLLECTION_NAME).insert(records).execute()
            
            print(f"✅ Upserted {len(records)} vectors to Supabase")
            return True
        except Exception as e:
            print(f"❌ Supabase upsert failed: {e}")
            return False
    
    async def search_vectors(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search vectors in the cloud database"""
        try:
            if self.provider == "pinecone":
                return await self._search_pinecone(query_vector, top_k, filter_metadata)
            elif self.provider == "weaviate":
                return await self._search_weaviate(query_vector, top_k, filter_metadata)
            elif self.provider == "qdrant":
                return await self._search_qdrant(query_vector, top_k, filter_metadata)
            elif self.provider == "supabase":
                return await self._search_supabase(query_vector, top_k, filter_metadata)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    async def _search_pinecone(self, query_vector: np.ndarray, top_k: int, filter_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search in Pinecone"""
        try:
            import asyncio
            flat_vector = query_vector.flatten().tolist()
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.collection.query(
                    vector=flat_vector,
                    top_k=top_k,
                    include_metadata=True,
                    filter=filter_metadata
                )
            )
            
            search_results = []
            for match in results.matches:
                search_results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
            
            return search_results
        except Exception as e:
            print(f"❌ Pinecone search failed: {e}")
            return []
    
    async def _search_weaviate(self, query_vector: np.ndarray, top_k: int, filter_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search in Weaviate"""
        try:
            # Build GraphQL query
            query = f"""
            {{
                Get {{
                    {COLLECTION_NAME}(
                        nearVector: {{
                            vector: {query_vector.tolist()}
                        }}
                        limit: {top_k}
                    ) {{
                        text
                        source
                        title
                        section
                        position
                        doc_id
                        _additional {{
                            distance
                        }}
                    }}
                }}
            }}
            """
            
            result = self.client.query.raw(query)
            
            search_results = []
            for item in result["data"]["Get"][COLLECTION_NAME]:
                search_results.append({
                    "id": item.get("_additional", {}).get("id", ""),
                    "score": 1 - item.get("_additional", {}).get("distance", 1),
                    "text": item.get("text", ""),
                    "metadata": {
                        "source": item.get("source", ""),
                        "title": item.get("title", ""),
                        "section": item.get("section", ""),
                        "position": item.get("position", 0),
                        "doc_id": item.get("doc_id", "")
                    }
                })
            
            return search_results
        except Exception as e:
            print(f"❌ Weaviate search failed: {e}")
            return []
    
    async def _search_qdrant(self, query_vector: np.ndarray, top_k: int, filter_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search in Qdrant"""
        try:
            results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector.tolist(),
                limit=top_k,
                query_filter=filter_metadata
            )
            
            search_results = []
            for result in results:
                search_results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                })
            
            return search_results
        except Exception as e:
            print(f"❌ Qdrant search failed: {e}")
            return []
    
    async def _search_supabase(self, query_vector: np.ndarray, top_k: int, filter_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search in Supabase pgvector"""
        try:
            # Use pgvector similarity search
            _query = f"""
            SELECT *, 1 - (embedding <=> %s) as similarity
            FROM {COLLECTION_NAME}
            ORDER BY embedding <=> %s
            LIMIT %s
            """
            
            result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_vector.tolist(),
                    "match_threshold": 0.0,
                    "match_count": top_k
                }
            ).execute()
            
            search_results = []
            for row in result.data:
                search_results.append({
                    "id": row["id"],
                    "score": row["similarity"],
                    "text": row["content"],
                    "metadata": {
                        "source": row.get("source", ""),
                        "title": row.get("title", ""),
                        "section": row.get("section", ""),
                        "position": row.get("position", 0),
                        "doc_id": row.get("doc_id", "")
                    }
                })
            
            return search_results
        except Exception as e:
            print(f"❌ Supabase search failed: {e}")
            return []

# Global cloud vector database instance
cloud_vector_db = None

def get_cloud_vector_db() -> CloudVectorDB:
    """Get or create cloud vector database instance"""
    global cloud_vector_db
    if cloud_vector_db is None:
        cloud_vector_db = CloudVectorDB()
    return cloud_vector_db
