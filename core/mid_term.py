from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import numpy as np
import logging

logger = logging.getLogger(__name__)

class MidTermMemory:
    """
    Manages mid-term memory for the chatbot.
    
    This stores summarized chunks of conversations for longer-term context.
    """
    
    def __init__(self, 
                 max_size: int = 100,
                 temporal_graph=None,
                 knowledge_graph=None,
                 mtm_query=None):
        """
        Initialize mid-term memory.
        
        Args:
            max_size: Maximum number of chunks to store
            temporal_graph: TemporalGraph instance (optional)
            knowledge_graph: KnowledgeGraph instance (optional)
            mtm_query: MTMQuery instance (optional)
        """
        self.max_size = max_size
        self.chunks: List[Dict[str, Any]] = []
        
        # Neo4j integration (optional)
        self.temporal_graph = temporal_graph
        self.knowledge_graph = knowledge_graph
        self.mtm_query = mtm_query
        self.neo4j_enabled = mtm_query is not None
    
    def add_chunk(self, summary: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new summarized chunk to mid-term memory.
        
        Args:
            summary: The summarized content
            metadata: Additional metadata (e.g., original message count, timestamps)
        """
        chunk = {
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.chunks.append(chunk)
        self._enforce_limits()
    
    def get_recent_chunks(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent chunks.
        
        Args:
            n: Number of chunks to return. If None, return all.
            
        Returns:
            List of chunk dictionaries, most recent last.
        """
        return self.chunks[-(n or len(self.chunks)):]
    
    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search chunks by embedding similarity.
        Enhanced with Neo4j MTM query if available.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of chunks sorted by similarity with scores
        """
        results = []
        
        # Search in local chunks
        if self.chunks:
            for chunk in self.chunks:
                if 'embedding' in chunk.get('metadata', {}):
                    chunk_embedding = chunk['metadata']['embedding']
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    results.append({
                        'chunk': chunk,
                        'similarity': similarity,
                        'source': 'local'
                    })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top-k with scores
        return [{
            'summary': r['chunk']['summary'],
            'metadata': r['chunk']['metadata'],
            'timestamp': r['chunk']['timestamp'],
            'relevance_score': r['similarity'],
            'source': r.get('source', 'local')
        } for r in results[:top_k]]
    
    def get_graph_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Get context from Neo4j graphs if enabled.
        
        Args:
            query: Query string
            top_k: Number of results
            
        Returns:
            Graph context dictionary
        """
        if not self.neo4j_enabled or not self.mtm_query:
            return {'temporal': [], 'knowledge': []}
        
        try:
            return self.mtm_query.get_mtm_context(query, top_k)
        except Exception as e:
            logger.error(f"Error querying MTM graphs: {e}")
            return {'temporal': [], 'knowledge': []}
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search chunks by keyword matching.
        
        Args:
            keywords: List of keywords to search
            top_k: Number of top results to return
            
        Returns:
            List of chunks sorted by keyword match score
        """
        if not self.chunks:
            return []
        
        results = []
        for chunk in self.chunks:
            # Check keywords in summary
            summary_lower = chunk['summary'].lower()
            
            # Count keyword matches
            match_count = sum(1 for kw in keywords if kw.lower() in summary_lower)
            
            if match_count > 0:
                results.append({
                    'chunk': chunk,
                    'match_score': match_count / len(keywords)
                })
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top-k
        return [{
            'summary': r['chunk']['summary'],
            'metadata': r['chunk']['metadata'],
            'timestamp': r['chunk']['timestamp'],
            'match_score': r['match_score']
        } for r in results[:top_k]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def clear(self) -> None:
        """Clear all chunks from mid-term memory."""
        self.chunks = []
    
    def _enforce_limits(self) -> None:
        """Ensure memory doesn't exceed max_size."""
        while len(self.chunks) > self.max_size:
            self.chunks.pop(0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to a dictionary."""
        return {
            'chunks': self.chunks,
            'max_size': self.max_size,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MidTermMemory':
        """Deserialize memory from a dictionary."""
        instance = cls(max_size=data.get('max_size', 100))
        instance.chunks = data.get('chunks', [])
        return instance
