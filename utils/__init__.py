"""
Utility modules for the Memory Layer Lab.
"""

from .logger import setup_logger
from .storage import MemoryStorage
from .embedding_utils import (
    FakeEmbeddingGenerator,
    EmbeddingCache,
    get_embedder
)

# Try to import improved embedding generator
try:
    from .real_embedding import RealEmbeddingGenerator as ImprovedEmbeddingGenerator
except ImportError:
    # Fallback to fake if dependencies not available
    ImprovedEmbeddingGenerator = FakeEmbeddingGenerator

# Keep old name for backwards compatibility
RealEmbeddingGenerator = ImprovedEmbeddingGenerator
from .llm_client import (
    LLMClient,
    OpenAIClient,
    AnthropicClient,
    MockLLMClient,
    get_llm_client
)

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
