from typing import Dict, Any, List, Optional
import re
import numpy as np
from datetime import datetime

class InputPreprocessor:
    """
    Preprocesses user input and creates structured query objects.
    
    Handles:
    - Text normalization
    - Intent detection
    - Embedding generation (mock or real)
    """
    
    def __init__(self, embedding_dim: int = 384, use_mock_embeddings: bool = True):
        """
        Initialize input preprocessor.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            use_mock_embeddings: Use mock embeddings or real model
        """
        self.embedding_dim = embedding_dim
        self.use_mock_embeddings = use_mock_embeddings
        
        # Intent keywords mapping
        self.intent_keywords = {
            'code_search': ['find', 'search', 'locate', 'where is', 'show me'],
            'debug': ['bug', 'error', 'fix', 'debug', 'issue', 'problem'],
            'documentation': ['explain', 'what is', 'how to', 'document', 'describe'],
            'commit_log': ['commit', 'history', 'changelog', 'git log', 'version'],
            'general': []  # fallback
        }
    
    def preprocess(self, raw_text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Preprocess user input into structured query object.
        
        Args:
            raw_text: Raw user input
            metadata: Optional metadata (file context, etc.)
            
        Returns:
            Structured query object with embedding and intent
        """
        # Normalize text
        normalized_text = self._normalize_text(raw_text)
        
        # Detect intent
        intent = self._detect_intent(normalized_text)
        
        # Generate embedding
        embedding = self._generate_embedding(normalized_text)
        
        # Extract keywords
        keywords = self._extract_keywords(normalized_text)
        
        return {
            'raw_text': raw_text,
            'normalized_text': normalized_text,
            'embedding': embedding,
            'intent': intent,
            'keywords': keywords,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text: lowercase, remove extra whitespace, clean special chars.
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove some special characters (keep important ones like ?, !)
        text = re.sub(r'[^\w\s\?\!\.\_\-]', '', text)
        
        return text.strip()
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect user intent from text.
        
        Args:
            text: Normalized text
            
        Returns:
            Intent category
        """
        text_lower = text.lower()
        
        # Check each intent category
        for intent, keywords in self.intent_keywords.items():
            if intent == 'general':
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return intent
        
        return 'general'
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Normalized text
            
        Returns:
            Embedding vector
        """
        if self.use_mock_embeddings:
            return self._mock_embedding(text)
        else:
            # TODO: Use real embedding model (sentence-transformers, OpenAI, etc.)
            return self._mock_embedding(text)
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding using simple hash + random.
        
        Args:
            text: Text to embed
            
        Returns:
            Mock embedding vector
        """
        # Use hash for reproducibility
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        
        # Generate random vector and normalize
        embedding = np.random.randn(self.embedding_dim)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Normalized text
            
        Returns:
            List of keywords
        """
        # Simple extraction: words longer than 3 characters
        words = text.split()
        keywords = [w for w in words if len(w) > 3 and w.isalnum()]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Top 10 keywords
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0 to 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # Normalize to 0-1 range
        return float((similarity + 1) / 2)
