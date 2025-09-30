"""
Real embedding generator using sentence-transformers.
"""

from typing import List, Optional
import numpy as np


class RealEmbeddingGenerator:
    """
    Generate real embeddings using sentence-transformers.
    Falls back to simpler methods if not available.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of sentence-transformers model
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM
        
        try:
            from sentence_transformers import SentenceTransformer
            print(f"📦 Loading sentence-transformers model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✅ Model loaded! Embedding dim: {self.embedding_dim}")
            self.use_transformer = True
        except ImportError:
            print("⚠️  sentence-transformers not installed")
            print("   Install with: pip install sentence-transformers")
            print("   Falling back to TF-IDF embeddings")
            self.use_transformer = False
            self._init_tfidf()
        except Exception as e:
            print(f"⚠️  Error loading model: {e}")
            print("   Falling back to TF-IDF embeddings")
            self.use_transformer = False
            self._init_tfidf()
    
    def _init_tfidf(self):
        """Initialize TF-IDF vectorizer as fallback."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf = TfidfVectorizer(max_features=384, stop_words='english')
        self.tfidf_fitted = False
        self.tfidf_corpus = []
    
    def generate(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        if self.use_transformer:
            return self._generate_transformer(text)
        else:
            return self._generate_tfidf(text)
    
    def _generate_transformer(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _generate_tfidf(self, text: str) -> List[float]:
        """Generate embedding using TF-IDF (fallback)."""
        # Add to corpus
        if text not in self.tfidf_corpus:
            self.tfidf_corpus.append(text)
            self.tfidf_fitted = False
        
        # Fit if needed
        if not self.tfidf_fitted and len(self.tfidf_corpus) > 1:
            try:
                self.tfidf.fit(self.tfidf_corpus)
                self.tfidf_fitted = True
            except:
                pass
        
        # Transform
        if self.tfidf_fitted:
            try:
                vec = self.tfidf.transform([text]).toarray()[0]
                return vec.tolist()
            except:
                pass
        
        # Ultimate fallback: simple hash-based
        return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple hash-based embedding (last resort fallback)."""
        # Hash text to generate pseudo-embedding
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % (2**32))
        return np.random.randn(self.embedding_dim).tolist()
    
    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score (0 to 1)
        """
        arr1 = np.array(emb1)
        arr2 = np.array(emb2)
        
        # Cosine similarity
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range
        return (similarity + 1) / 2
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings
        """
        if self.use_transformer:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        else:
            return [self.generate(text) for text in texts]
