"""
Utility modules for the Memory Layer Lab.
"""

from .logger import setup_logger
from .storage import MemoryStorage

# Embedding utils - only import if needed to avoid numpy dependency
try:
    from .embedding_utils import (
        FakeEmbeddingGenerator,
        EmbeddingCache,
        get_embedder
    )
except ImportError:
    FakeEmbeddingGenerator = None
    EmbeddingCache = None
    get_embedder = None

# Try to import improved embedding generator
try:
    from .real_embedding import RealEmbeddingGenerator as ImprovedEmbeddingGenerator
except ImportError:
    # Fallback to fake if dependencies not available
    ImprovedEmbeddingGenerator = FakeEmbeddingGenerator

# Keep old name for backwards compatibility
RealEmbeddingGenerator = ImprovedEmbeddingGenerator

# LLM clients
try:
    from .llm_client import (
        LLMClient,
        OpenAIClient,
        AnthropicClient,
        MockLLMClient,
        get_llm_client
    )
except ImportError:
    LLMClient = None
    OpenAIClient = None
    AnthropicClient = None
    MockLLMClient = None
    get_llm_client = None

__all__ = [
    'setup_logger',
    'MemoryStorage',
    'FakeEmbeddingGenerator',
    'RealEmbeddingGenerator',
    'EmbeddingCache',
    'get_embedder',
    'LLMClient',
    'OpenAIClient',
    'AnthropicClient',
    'MockLLMClient',
    'get_llm_client',
]
