from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import numpy as np

class ShortTermMemory:
    """
    Manages short-term memory for the chatbot.
    
    This stores recent messages in a fixed-size buffer with optional TTL.
    """
    
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        """
        Initialize short-term memory.
        
        Args:
            max_size: Maximum number of messages to store
            ttl_seconds: Time-to-live for messages in seconds
        """
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.messages: List[Dict[str, Any]] = []
    
    def add(self, role: str, content: str, **metadata) -> None:
        """
        Add a new message to short-term memory.
        
        Args:
            role: 'user' or 'assistant'
            content: The message content
            **metadata: Additional metadata to store with the message
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        self.messages.append(message)
        self._enforce_limits()
    
    def get_recent(self, n: Optional[int] = None, query_embedding: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent messages, optionally filtered by similarity.
        
        Args:
            n: Number of messages to retrieve (None = all)
            query_embedding: Optional query embedding for semantic filtering
            
        Returns:
            List of recent messages
        """
        if query_embedding is not None:
            # Semantic search: rank by similarity
            messages_with_scores = []
            for msg in self.messages:
                msg_embedding = msg.get('embedding', [])
                if msg_embedding:
                    similarity = self._cosine_similarity(query_embedding, msg_embedding)
                    msg_copy = msg.copy()
                    msg_copy['similarity'] = similarity
                    messages_with_scores.append(msg_copy)
            
            # Sort by similarity
            messages_with_scores.sort(key=lambda x: x['similarity'], reverse=True)
            
            if n is None:
                return messages_with_scores
            return messages_with_scores[:n] if n > 0 else []
        else:
            # Time-based: most recent
            if n is None:
                return self.messages.copy()
            return self.messages[-n:] if n > 0 else []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def search_by_embedding(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search messages by embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of messages sorted by similarity
        """
        self._clean_expired()
        
        if not self.messages:
            return []
        
        # Calculate similarities
        results = []
        for msg in self.messages:
            if 'embedding' in msg.get('metadata', {}):
                msg_embedding = msg['metadata']['embedding']
                similarity = self._cosine_similarity(query_embedding, msg_embedding)
                results.append({
                    'message': msg,
                    'similarity': similarity
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top-k messages
        return [r['message'] for r in results[:top_k]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def clear(self) -> None:
        """Clear all messages from short-term memory."""
        self.messages = []
    
    def _enforce_limits(self) -> None:
        """Ensure memory doesn't exceed max_size."""
        while len(self.messages) > self.max_size:
            self.messages.pop(0)
    
    def _clean_expired(self) -> None:
        """Remove messages that have exceeded their TTL."""
        if not self.ttl:
            return
            
        now = datetime.utcnow()
        self.messages = [
            msg for msg in self.messages
            if now - datetime.fromisoformat(msg['timestamp']) < self.ttl
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to a dictionary."""
        return {
            'messages': self.messages,
            'max_size': self.max_size,
            'ttl_seconds': self.ttl.total_seconds() if self.ttl else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShortTermMemory':
        """Deserialize memory from a dictionary."""
        instance = cls(
            max_size=data.get('max_size', 10),
            ttl_seconds=data.get('ttl_seconds', 3600)
        )
        instance.messages = data.get('messages', [])
        return instance
