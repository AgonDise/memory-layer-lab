"""
Embedding utilities for generating and managing embeddings.
"""

import numpy as np
import hashlib
from typing import List, Dict, Any, Optional
import json
import os


class FakeEmbeddingGenerator:
    """
    Generate deterministic fake embeddings for testing.
    
    Same text always produces same embedding (reproducible).
    Good for testing without requiring real embedding models.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize generator.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self._cache = {}  # Cache for performance
    
    def generate(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector (normalized)
        """
        if use_cache and text in self._cache:
            return self._cache[text]
        
        # Use hash of text as seed for reproducibility
        seed = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        
        # Generate random vector
        embedding = np.random.randn(self.embedding_dim)
        
        # Normalize to unit length (good for cosine similarity)
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        result = embedding.tolist()
        
        if use_cache:
            self._cache[text] = result
        
        return result
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of embedding vectors
        """
        return [self.generate(text) for text in texts]
    
    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        vec1 = np.array(emb1)
        vec2 = np.array(emb2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def clear_cache(self):
        """Clear embedding cache."""
        self._cache = {}
    
    def get_cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self._cache)


class RealEmbeddingGenerator:
    """
    Generate real embeddings using sentence-transformers.
    
    Requires: pip install sentence-transformers
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize with a sentence-transformers model.
        
        Args:
            model_name: Name of the model to use
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.enabled = True
        except ImportError:
            print("Warning: sentence-transformers not installed. Install with:")
            print("  pip install sentence-transformers")
            self.enabled = False
            self.embedding_dim = 384
    
    def generate(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not self.enabled:
            raise RuntimeError("sentence-transformers not installed")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batched, faster).
        
        Args:
            texts: List of texts
            
        Returns:
            List of embedding vectors
        """
        if not self.enabled:
            raise RuntimeError("sentence-transformers not installed")
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity."""
        from sentence_transformers import util
        return float(util.cos_sim(emb1, emb2)[0][0])


class EmbeddingCache:
    """
    Persistent cache for embeddings.
    
    Saves embeddings to disk to avoid regeneration.
    """
    
    def __init__(self, cache_file: str = 'embedding_cache.json'):
        """
        Initialize cache.
        
        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file
        self.cache: Dict[str, List[float]] = {}
        self._load()
    
    def _load(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self.cache = {}
    
    def save(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        return self.cache.get(text)
    
    def put(self, text: str, embedding: List[float]):
        """Put embedding in cache."""
        self.cache[text] = embedding
    
    def has(self, text: str) -> bool:
        """Check if text is in cache."""
        return text in self.cache
    
    def clear(self):
        """Clear cache."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)


def get_embedder(mode: str = 'fake', **kwargs):
    """
    Factory function to get an embedding generator.
    
    Args:
        mode: 'fake' or 'real'
        **kwargs: Additional arguments for the generator
        
    Returns:
        Embedding generator instance
    """
    if mode == 'fake':
        return FakeEmbeddingGenerator(**kwargs)
    elif mode == 'real':
        return RealEmbeddingGenerator(**kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'fake' or 'real'")


# Example usage
if __name__ == '__main__':
    print("=" * 60)
    print("Embedding Utils Demo")
    print("=" * 60)
    
    # Fake embeddings
    print("\n1. Fake Embeddings (Deterministic)")
    fake_gen = FakeEmbeddingGenerator(embedding_dim=128)
    
    texts = [
        "Hello world",
        "Hello world",  # Same text
        "Goodbye world"  # Different text
    ]
    
    for i, text in enumerate(texts, 1):
        emb = fake_gen.generate(text)
        print(f"  {i}. '{text}' → [{emb[0]:.3f}, {emb[1]:.3f}, ...]")
    
    # Check reproducibility
    emb1 = fake_gen.generate("test")
    emb2 = fake_gen.generate("test")
    assert emb1 == emb2
    print("\n  ✓ Same text produces same embedding")
    
    # Similarity
    emb_a = fake_gen.generate("machine learning")
    emb_b = fake_gen.generate("machine learning")
    emb_c = fake_gen.generate("deep learning")
    
    sim_same = fake_gen.cosine_similarity(emb_a, emb_b)
    sim_diff = fake_gen.cosine_similarity(emb_a, emb_c)
    
    print(f"\n  Similarity (same text): {sim_same:.3f}")
    print(f"  Similarity (diff text): {sim_diff:.3f}")
    
    # Cache
    print(f"\n  Cache size: {fake_gen.get_cache_size()} items")
    
    # Real embeddings (if available)
    print("\n2. Real Embeddings (sentence-transformers)")
    try:
        real_gen = RealEmbeddingGenerator()
        if real_gen.enabled:
            emb_real = real_gen.generate("Hello world")
            print(f"  ✓ Generated real embedding (dim={len(emb_real)})")
            print(f"    [{emb_real[0]:.3f}, {emb_real[1]:.3f}, ...]")
        else:
            print("  ✗ sentence-transformers not installed")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Persistent cache
    print("\n3. Persistent Cache")
    cache = EmbeddingCache('test_cache.json')
    
    text = "cached text"
    if not cache.has(text):
        emb = fake_gen.generate(text)
        cache.put(text, emb)
        cache.save()
        print(f"  ✓ Cached: '{text}'")
    else:
        emb = cache.get(text)
        print(f"  ✓ Loaded from cache: '{text}'")
    
    print(f"  Cache size: {cache.size()} items")
    
    # Clean up
    cache.clear()
    
    print("\n✅ Demo complete!")
