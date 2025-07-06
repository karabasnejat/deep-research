"""
Long-term Memory Module - Vector store integration for persistent memory
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

class LongTermMemory:
    def __init__(self, 
                 vector_store_type: str = "chroma",
                 collection_name: str = "research_memory",
                 persist_directory: str = "./memory_db"):
        """
        Initialize long-term memory with vector store
        
        Args:
            vector_store_type: Type of vector store ("chroma", "faiss", "pinecone")
            collection_name: Name of the collection/index
            persist_directory: Directory to persist data
        """
        self.vector_store_type = vector_store_type.lower()
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.index = None
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> None:
        """Initialize the selected vector store"""
        if self.vector_store_type == "chroma":
            self._initialize_chroma()
        elif self.vector_store_type == "faiss":
            self._initialize_faiss()
        elif self.vector_store_type == "pinecone":
            self._initialize_pinecone()
        else:
            raise ValueError(f"Unsupported vector store type: {self.vector_store_type}")
    
    def _initialize_chroma(self) -> None:
        """Initialize ChromaDB"""
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB not available. Install with: pip install chromadb")
        
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Deep Research Agent long-term memory"}
                )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            # Fallback to in-memory storage
            self._initialize_fallback()
    
    def _initialize_faiss(self) -> None:
        """Initialize FAISS"""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        try:
            index_path = os.path.join(self.persist_directory, f"{self.collection_name}.index")
            metadata_path = os.path.join(self.persist_directory, f"{self.collection_name}_metadata.json")
            
            # Load existing index or create new one
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            else:
                # Create new index (384 dimensions for sentence transformers)
                self.index = faiss.IndexFlatL2(384)
                self.metadata = {"documents": [], "ids": []}
        except Exception as e:
            print(f"FAISS initialization error: {e}")
            self._initialize_fallback()
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone"""
        try:
            import pinecone
            
            api_key = os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment variables")
            
            pinecone.init(api_key=api_key, environment=environment)
            
            # Create index if it doesn't exist
            if self.collection_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.collection_name,
                    dimension=384,  # sentence transformer dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.collection_name)
            
        except Exception as e:
            print(f"Pinecone initialization error: {e}")
            self._initialize_fallback()
    
    def _initialize_fallback(self) -> None:
        """Initialize fallback in-memory storage"""
        self.vector_store_type = "memory"
        self.memory_store = {
            "documents": [],
            "embeddings": [],
            "metadata": [],
            "ids": []
        }
    
    def store_memory(self, 
                    content: str, 
                    metadata: Optional[Dict[str, Any]] = None,
                    memory_type: str = "research",
                    importance: float = 1.0) -> str:
        """
        Store a memory in long-term storage
        
        Args:
            content: Text content to store
            metadata: Additional metadata
            memory_type: Type of memory (research, conversation, insight, etc.)
            importance: Importance score (0.0 to 1.0)
            
        Returns:
            Memory ID
        """
        # Create memory ID
        memory_id = f"{memory_type}_{datetime.now().timestamp()}"
        
        # Prepare metadata
        full_metadata = {
            "type": memory_type,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "content_length": len(content),
            **(metadata or {})
        }
        
        # Store based on vector store type
        if self.vector_store_type == "chroma":
            self._store_chroma(memory_id, content, full_metadata)
        elif self.vector_store_type == "faiss":
            self._store_faiss(memory_id, content, full_metadata)
        elif self.vector_store_type == "pinecone":
            self._store_pinecone(memory_id, content, full_metadata)
        else:
            self._store_memory_fallback(memory_id, content, full_metadata)
        
        return memory_id
    
    def retrieve_memories(self, 
                         query: str, 
                         limit: int = 5,
                         memory_type: Optional[str] = None,
                         min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on query
        
        Args:
            query: Search query
            limit: Maximum number of memories to return
            memory_type: Filter by memory type
            min_importance: Minimum importance score
            
        Returns:
            List of relevant memories with scores
        """
        if self.vector_store_type == "chroma":
            return self._retrieve_chroma(query, limit, memory_type, min_importance)
        elif self.vector_store_type == "faiss":
            return self._retrieve_faiss(query, limit, memory_type, min_importance)
        elif self.vector_store_type == "pinecone":
            return self._retrieve_pinecone(query, limit, memory_type, min_importance)
        else:
            return self._retrieve_memory_fallback(query, limit, memory_type, min_importance)
    
    def _store_chroma(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Store memory in ChromaDB"""
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[memory_id]
            )
        except Exception as e:
            print(f"ChromaDB storage error: {e}")
    
    def _store_faiss(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Store memory in FAISS"""
        try:
            # Generate embedding (placeholder - would use actual embedding model)
            embedding = self._generate_embedding(content)
            
            # Add to index
            self.index.add(np.array([embedding]))
            
            # Store metadata
            self.metadata["documents"].append(content)
            self.metadata["ids"].append(memory_id)
            
            # Save index and metadata
            index_path = os.path.join(self.persist_directory, f"{self.collection_name}.index")
            metadata_path = os.path.join(self.persist_directory, f"{self.collection_name}_metadata.json")
            
            faiss.write_index(self.index, index_path)
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f)
                
        except Exception as e:
            print(f"FAISS storage error: {e}")
    
    def _store_pinecone(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Store memory in Pinecone"""
        try:
            embedding = self._generate_embedding(content)
            
            self.index.upsert(
                vectors=[(memory_id, embedding, metadata)]
            )
        except Exception as e:
            print(f"Pinecone storage error: {e}")
    
    def _store_memory_fallback(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """Store memory in fallback storage"""
        embedding = self._generate_embedding(content)
        
        self.memory_store["documents"].append(content)
        self.memory_store["embeddings"].append(embedding)
        self.memory_store["metadata"].append(metadata)
        self.memory_store["ids"].append(memory_id)
    
    def _retrieve_chroma(self, query: str, limit: int, memory_type: Optional[str], min_importance: float) -> List[Dict[str, Any]]:
        """Retrieve memories from ChromaDB"""
        try:
            # Build where clause for filtering
            where_clause = {}
            if memory_type:
                where_clause["type"] = memory_type
            if min_importance > 0:
                where_clause["importance"] = {"$gte": min_importance}
            
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            memories = []
            for i, doc in enumerate(results["documents"][0]):
                memories.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else 0.0
                })
            
            return memories
            
        except Exception as e:
            print(f"ChromaDB retrieval error: {e}")
            return []
    
    def _retrieve_faiss(self, query: str, limit: int, memory_type: Optional[str], min_importance: float) -> List[Dict[str, Any]]:
        """Retrieve memories from FAISS"""
        try:
            query_embedding = self._generate_embedding(query)
            
            # Search
            distances, indices = self.index.search(np.array([query_embedding]), limit)
            
            # Format results
            memories = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata["documents"]):
                    memories.append({
                        "id": self.metadata["ids"][idx],
                        "content": self.metadata["documents"][idx],
                        "metadata": {},
                        "distance": distances[0][i]
                    })
            
            return memories
            
        except Exception as e:
            print(f"FAISS retrieval error: {e}")
            return []
    
    def _retrieve_pinecone(self, query: str, limit: int, memory_type: Optional[str], min_importance: float) -> List[Dict[str, Any]]:
        """Retrieve memories from Pinecone"""
        try:
            query_embedding = self._generate_embedding(query)
            
            # Build filter
            filter_dict = {}
            if memory_type:
                filter_dict["type"] = memory_type
            if min_importance > 0:
                filter_dict["importance"] = {"$gte": min_importance}
            
            results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                filter=filter_dict if filter_dict else None,
                include_metadata=True
            )
            
            # Format results
            memories = []
            for match in results["matches"]:
                memories.append({
                    "id": match["id"],
                    "content": match["metadata"].get("content", ""),
                    "metadata": match["metadata"],
                    "score": match["score"]
                })
            
            return memories
            
        except Exception as e:
            print(f"Pinecone retrieval error: {e}")
            return []
    
    def _retrieve_memory_fallback(self, query: str, limit: int, memory_type: Optional[str], min_importance: float) -> List[Dict[str, Any]]:
        """Retrieve memories from fallback storage"""
        # Simple text matching for fallback
        query_lower = query.lower()
        matches = []
        
        for i, doc in enumerate(self.memory_store["documents"]):
            if query_lower in doc.lower():
                matches.append({
                    "id": self.memory_store["ids"][i],
                    "content": doc,
                    "metadata": self.memory_store["metadata"][i],
                    "score": 1.0
                })
        
        return matches[:limit]
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder implementation)"""
        # TODO: Implement actual embedding generation using sentence transformers
        # For now, return a simple hash-based embedding
        import hashlib
        
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to pseudo-embedding (384 dimensions)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        if self.vector_store_type == "chroma":
            try:
                count = self.collection.count()
                return {
                    "total_memories": count,
                    "vector_store": "chroma",
                    "collection_name": self.collection_name
                }
            except:
                return {"total_memories": 0, "vector_store": "chroma", "error": "Unable to get stats"}
        
        elif self.vector_store_type == "faiss":
            return {
                "total_memories": self.index.ntotal if self.index else 0,
                "vector_store": "faiss",
                "collection_name": self.collection_name
            }
        
        elif self.vector_store_type == "pinecone":
            try:
                stats = self.index.describe_index_stats()
                return {
                    "total_memories": stats.get("total_vector_count", 0),
                    "vector_store": "pinecone",
                    "collection_name": self.collection_name
                }
            except:
                return {"total_memories": 0, "vector_store": "pinecone", "error": "Unable to get stats"}
        
        else:
            return {
                "total_memories": len(self.memory_store["documents"]),
                "vector_store": "memory",
                "collection_name": self.collection_name
            }
    
    def clear_memories(self, memory_type: Optional[str] = None) -> int:
        """Clear memories, optionally filtered by type"""
        # TODO: Implement memory clearing for each vector store type
        cleared_count = 0
        
        if self.vector_store_type == "memory":
            if memory_type:
                # Filter by type
                indices_to_remove = []
                for i, metadata in enumerate(self.memory_store["metadata"]):
                    if metadata.get("type") == memory_type:
                        indices_to_remove.append(i)
                
                # Remove in reverse order to maintain indices
                for i in reversed(indices_to_remove):
                    del self.memory_store["documents"][i]
                    del self.memory_store["embeddings"][i]
                    del self.memory_store["metadata"][i]
                    del self.memory_store["ids"][i]
                    cleared_count += 1
            else:
                # Clear all
                cleared_count = len(self.memory_store["documents"])
                self.memory_store = {
                    "documents": [],
                    "embeddings": [],
                    "metadata": [],
                    "ids": []
                }
        
        return cleared_count 