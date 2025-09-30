from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import logging
import json
import os

logger = logging.getLogger(__name__)

class VectorDatabase:
    """
    Vector Database for Long-term Memory semantic search.
    
    Supports multiple backends: FAISS, ChromaDB, Qdrant, Weaviate.
    Default implementation uses FAISS (in-memory or file-based).
    """
    
    def __init__(self, 
                 embedding_dim: int = 384,
                 backend: str = 'faiss',
                 index_path: Optional[str] = None):
        """
        Initialize vector database.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            backend: Backend type ('faiss', 'chromadb', 'qdrant', 'weaviate')
            index_path: Path to save/load index
        """
        self.embedding_dim = embedding_dim
        self.backend = backend
        self.index_path = index_path
        
        # Initialize based on backend
        if backend == 'faiss':
            self._init_faiss()
        elif backend == 'chromadb':
            self._init_chromadb()
        else:
            # Fallback to simple in-memory storage
            self._init_simple()
    
    def _init_faiss(self):
        """Initialize FAISS backend."""
        try:
            import faiss
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.documents = []  # Store document metadata
            self.enabled = True
            
            # Load existing index if available
            if self.index_path and os.path.exists(self.index_path):
                self._load_index()
            
            logger.info("FAISS vector database initialized")
        except ImportError:
            logger.warning("FAISS not installed, using simple storage")
            self._init_simple()
    
    def _init_chromadb(self):
        """Initialize ChromaDB backend."""
        try:
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.create_collection(
                name="ltm_collection",
                metadata={"description": "Long-term memory semantic search"}
            )
            self.enabled = True
            logger.info("ChromaDB vector database initialized")
        except ImportError:
            logger.warning("ChromaDB not installed, using simple storage")
            self._init_simple()
    
    def _init_simple(self):
        """Initialize simple in-memory storage."""
        self.vectors = []  # List of numpy arrays
        self.documents = []  # List of document metadata
        self.enabled = True
        logger.info("Simple vector storage initialized")
    
    def add_document(self,
                     doc_id: str,
                     content: str,
                     embedding: List[float],
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document with its embedding.
        
        Args:
            doc_id: Document ID
            content: Document content
            embedding: Embedding vector
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.enabled:
            return False
        
        doc_data = {
            'id': doc_id,
            'content': content,
            'metadata': metadata or {}
        }
        
        if self.backend == 'faiss':
            return self._add_faiss(embedding, doc_data)
        elif self.backend == 'chromadb':
            return self._add_chromadb(doc_id, content, embedding, metadata)
        else:
            return self._add_simple(embedding, doc_data)
    
    def _add_faiss(self, embedding: List[float], doc_data: Dict[str, Any]) -> bool:
        """Add to FAISS index."""
        try:
            import faiss
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)
            self.documents.append(doc_data)
            logger.debug(f"Added document to FAISS: {doc_data['id']}")
            return True
        except Exception as e:
            logger.error(f"Error adding to FAISS: {e}")
            return False
    
    def _add_chromadb(self, 
                      doc_id: str, 
                      content: str, 
                      embedding: List[float],
                      metadata: Dict[str, Any]) -> bool:
        """Add to ChromaDB."""
        try:
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata] if metadata else None
            )
            logger.debug(f"Added document to ChromaDB: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {e}")
            return False
    
    def _add_simple(self, embedding: List[float], doc_data: Dict[str, Any]) -> bool:
        """Add to simple storage."""
        self.vectors.append(np.array(embedding))
        self.documents.append(doc_data)
        logger.debug(f"Added document to simple storage: {doc_data['id']}")
        return True
    
    def search(self,
               query_embedding: List[float],
               top_k: int = 5,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results
            filter_metadata: Filter by metadata (optional)
            
        Returns:
            List of similar documents with scores
        """
        if not self.enabled:
            return []
        
        if self.backend == 'faiss':
            return self._search_faiss(query_embedding, top_k)
        elif self.backend == 'chromadb':
            return self._search_chromadb(query_embedding, top_k)
        else:
            return self._search_simple(query_embedding, top_k)
    
    def _search_faiss(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in FAISS index."""
        try:
            import faiss
            
            if self.index.ntotal == 0:
                return []
            
            query_vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['score'] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                    doc['rank'] = i + 1
                    results.append(doc)
            
            return results
        except Exception as e:
            logger.error(f"Error searching FAISS: {e}")
            return []
    
    def _search_chromadb(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in ChromaDB."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            documents = []
            if results['ids']:
                for i, (doc_id, content, metadata, distance) in enumerate(zip(
                    results['ids'][0],
                    results['documents'][0],
                    results['metadatas'][0] if results['metadatas'] else [{}] * len(results['ids'][0]),
                    results['distances'][0]
                )):
                    documents.append({
                        'id': doc_id,
                        'content': content,
                        'metadata': metadata,
                        'score': float(1.0 / (1.0 + distance)),
                        'rank': i + 1
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
    
    def _search_simple(self, query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search in simple storage."""
        if not self.vectors:
            return []
        
        query_vec = np.array(query_embedding)
        similarities = []
        
        for i, vec in enumerate(self.vectors):
            # Cosine similarity
            similarity = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
            similarities.append((i, float(similarity)))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top-k
        results = []
        for rank, (idx, score) in enumerate(similarities[:top_k], 1):
            doc = self.documents[idx].copy()
            doc['score'] = score
            doc['rank'] = rank
            results.append(doc)
        
        return results
    
    def save_index(self) -> bool:
        """Save index to disk."""
        if not self.index_path:
            logger.warning("No index path specified")
            return False
        
        try:
            if self.backend == 'faiss':
                import faiss
                faiss.write_index(self.index, self.index_path)
                
                # Save documents metadata
                metadata_path = self.index_path + '.meta.json'
                with open(metadata_path, 'w') as f:
                    json.dump(self.documents, f, indent=2)
                
                logger.info(f"Saved FAISS index to {self.index_path}")
                return True
            elif self.backend == 'simple':
                # Save simple storage
                data = {
                    'vectors': [v.tolist() for v in self.vectors],
                    'documents': self.documents
                }
                with open(self.index_path, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved simple index to {self.index_path}")
                return True
            else:
                logger.warning(f"Save not implemented for backend: {self.backend}")
                return False
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            return False
    
    def _load_index(self) -> bool:
        """Load index from disk."""
        try:
            if self.backend == 'faiss':
                import faiss
                self.index = faiss.read_index(self.index_path)
                
                # Load documents metadata
                metadata_path = self.index_path + '.meta.json'
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.documents = json.load(f)
                
                logger.info(f"Loaded FAISS index from {self.index_path}")
                return True
            elif self.backend == 'simple' and os.path.exists(self.index_path):
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                self.vectors = [np.array(v) for v in data['vectors']]
                self.documents = data['documents']
                logger.info(f"Loaded simple index from {self.index_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all vectors and documents."""
        if self.backend == 'faiss':
            try:
                import faiss
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.documents = []
                logger.info("Cleared FAISS index")
            except Exception as e:
                logger.error(f"Error clearing FAISS: {e}")
        elif self.backend == 'chromadb':
            try:
                self.client.delete_collection(name="ltm_collection")
                self.collection = self.client.create_collection(name="ltm_collection")
                logger.info("Cleared ChromaDB collection")
            except Exception as e:
                logger.error(f"Error clearing ChromaDB: {e}")
        else:
            self.vectors = []
            self.documents = []
            logger.info("Cleared simple storage")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self.backend == 'faiss':
            return {
                'backend': 'faiss',
                'total_documents': self.index.ntotal if hasattr(self, 'index') else 0,
                'embedding_dim': self.embedding_dim,
            }
        elif self.backend == 'chromadb':
            return {
                'backend': 'chromadb',
                'total_documents': self.collection.count() if hasattr(self, 'collection') else 0,
                'embedding_dim': self.embedding_dim,
            }
        else:
            return {
                'backend': 'simple',
                'total_documents': len(self.documents),
                'embedding_dim': self.embedding_dim,
            }
