from typing import List, Dict, Any, Optional
import time
import logging
from .short_term import ShortTermMemory
from .mid_term import MidTermMemory
from .long_term import LongTermMemory
from .summarizer import Summarizer
from .preprocessor import InputPreprocessor
from .aggregator import MemoryAggregator
from .compressor import ContextCompressor

# Langfuse integration (optional)
try:
    from utils.langfuse_client import create_langfuse_client, LangfuseTracer
    from utils.config_manager import get_config
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

logger = logging.getLogger(__name__)

class MemoryOrchestrator:
    """
    Orchestrates the different memory layers to provide context for the chatbot.
    
    This class manages:
    - Moving data between memory layers
    - Summarizing old conversations
    - Building context for responses
    """
    
    def __init__(self, 
                 short_term: ShortTermMemory,
                 mid_term: MidTermMemory,
                 long_term: LongTermMemory,
                 summarizer: Summarizer,
                 preprocessor: Optional[InputPreprocessor] = None,
                 aggregator: Optional[MemoryAggregator] = None,
                 compressor: Optional[ContextCompressor] = None,
                 summarize_every: int = 5,
                 enable_tracing: bool = False):
        """
        Initialize the memory orchestrator.
        
        Args:
            short_term: Short-term memory instance
            mid_term: Mid-term memory instance
            long_term: Long-term memory instance
            summarizer: Summarizer instance
            preprocessor: Input preprocessor (optional)
            aggregator: Memory aggregator (optional)
            compressor: Context compressor (optional)
            summarize_every: Number of messages before triggering summarization
            enable_tracing: Enable Langfuse tracing
        """
        self.short_term = short_term
        self.mid_term = mid_term
        self.long_term = long_term
        self.summarizer = summarizer
        self.preprocessor = preprocessor or InputPreprocessor()
        self.aggregator = aggregator or MemoryAggregator()
        self.compressor = compressor or ContextCompressor()
        self.summarize_every = summarize_every
        self.message_count = 0
        
        # Langfuse tracing setup
        self.tracing_enabled = enable_tracing and LANGFUSE_AVAILABLE
        self.langfuse_client = None
        self.tracer = None
        
        if self.tracing_enabled:
            try:
                config = get_config()
                if config.get('langfuse.enabled', False):
                    self.langfuse_client = create_langfuse_client()
                    self.tracer = LangfuseTracer(self.langfuse_client)
                    logger.info("✅ Langfuse tracing enabled in orchestrator")
                else:
                    self.tracing_enabled = False
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {e}")
                self.tracing_enabled = False
    
    def add_message(self, role: str, content: str, **metadata) -> None:
        """
        Add a new message and manage memory layers.
        
        Args:
            role: 'user' or 'assistant'
            content: The message content
            **metadata: Additional metadata
        """
        start_time = time.time()
        
        # Trace if enabled
        if self.tracing_enabled and self.langfuse_client:
            self.langfuse_client.log_event(
                trace_id="current",
                name="add_message",
                metadata={
                    "role": role,
                    "content_length": len(content),
                    "metadata": metadata
                }
            )
        
        # Add to short-term memory
        self.short_term.add(role, content, **metadata)
        self.message_count += 1
        
        # Check if we need to summarize
        if self.message_count >= self.summarize_every:
            self._summarize_and_move()
            self.message_count = 0
        
        # Log timing
        if self.tracing_enabled:
            duration = time.time() - start_time
            logger.debug(f"add_message took {duration*1000:.2f}ms")
    
    def get_context(self, 
                    query: Optional[str] = None,
                    n_recent: Optional[int] = None, 
                    n_chunks: Optional[int] = 3,
                    use_embedding_search: bool = False) -> Dict[str, Any]:
        """
        Build context from all memory layers with advanced workflow.
        
        Args:
            query: Query string for embedding search
            n_recent: Number of recent messages to include
            n_chunks: Number of mid-term chunks to include
            use_embedding_search: Use embedding-based retrieval
            
        Returns:
            Dictionary with context from all memory layers
        """
        start_time = time.time()
        
        # Trace context retrieval
        if self.tracing_enabled and self.tracer:
            with self.tracer.trace_context("get_context", metadata={
                "query": query[:100] if query else None,
                "use_embedding_search": use_embedding_search
            }):
                return self._get_context_internal(query, n_recent, n_chunks, use_embedding_search, start_time)
        else:
            return self._get_context_internal(query, n_recent, n_chunks, use_embedding_search, start_time)
    
    def _get_context_internal(self, query, n_recent, n_chunks, use_embedding_search, start_time):
        """Internal context retrieval logic."""
        query_embedding = None
        
        # Preprocess query if provided
        if query and use_embedding_search:
            query_obj = self.preprocessor.preprocess(query)
            query_embedding = query_obj['embedding']
        
        # Retrieve from memory layers
        retrieval_start = time.time()
        if use_embedding_search and query_embedding:
            stm_context = self.short_term.search_by_embedding(query_embedding, top_k=n_recent or 5)
            mtm_context = self.mid_term.search_by_embedding(query_embedding, top_k=n_chunks or 3)
        else:
            stm_context = self.short_term.get_recent(n_recent)
            mtm_context = self.mid_term.get_recent_chunks(n_chunks)
        retrieval_time = time.time() - retrieval_start
        
        # Aggregate contexts
        agg_start = time.time()
        aggregated = self.aggregator.aggregate(
            stm_context=stm_context,
            mtm_context=mtm_context,
            ltm_context=None,
            query_embedding=query_embedding
        )
        agg_time = time.time() - agg_start
        
        # Compress context
        comp_start = time.time()
        compressed = self.compressor.compress(aggregated)
        comp_time = time.time() - comp_start
        
        total_time = time.time() - start_time
        
        # Log timing
        if self.tracing_enabled and self.langfuse_client:
            self.langfuse_client.log_span(
                trace_id="current",
                name="context_retrieval",
                metadata={
                    "retrieval_time_ms": retrieval_time * 1000,
                    "aggregation_time_ms": agg_time * 1000,
                    "compression_time_ms": comp_time * 1000,
                    "total_time_ms": total_time * 1000,
                    "stm_count": aggregated['stm_count'],
                    "mtm_count": aggregated['mtm_count']
                }
            )
        
        return {
            'aggregated': aggregated,
            'compressed': compressed,
            'query_embedding': query_embedding,
            'stm_count': aggregated['stm_count'],
            'mtm_count': aggregated['mtm_count'],
            'timing': {
                'retrieval_ms': retrieval_time * 1000,
                'aggregation_ms': agg_time * 1000,
                'compression_ms': comp_time * 1000,
                'total_ms': total_time * 1000
            }
        }
    
    def get_context_string(self, 
                          query: Optional[str] = None,
                          n_recent: Optional[int] = None, 
                          n_chunks: Optional[int] = 3,
                          use_compression: bool = True) -> str:
        """
        Get context as a formatted string for the chatbot.
        
        Args:
            query: Query for embedding search
            n_recent: Number of recent messages to include
            n_chunks: Number of mid-term chunks to include
            use_compression: Use context compression
            
        Returns:
            Formatted context string
        """
        context = self.get_context(
            query=query,
            n_recent=n_recent,
            n_chunks=n_chunks,
            use_embedding_search=(query is not None)
        )
        
        if use_compression:
            # Return compressed context
            return self.compressor.get_context_string(context['compressed'])
        else:
            # Return aggregated context
            return self.aggregator.format_for_llm(context['aggregated'])
    
    def _summarize_and_move(self) -> None:
        """Summarize short-term memory and move to mid-term."""
        messages = self.short_term.get_recent()
        
        if not messages:
            return
        
        # Generate summary
        summary = self.summarizer.summarize(messages)
        
        # Generate embedding for summary
        summary_embedding = self.preprocessor._generate_embedding(summary)
        
        # Extract metadata
        metadata = {
            'message_count': len(messages),
            'topics': self.summarizer.extract_key_topics(messages),
            'embedding': summary_embedding,
        }
        
        # Add to mid-term memory
        self.mid_term.add_chunk(summary, metadata)
        
        # Optionally clear older messages from short-term
        # (keeping the most recent few)
        # For now, we rely on the short-term memory's own size limit
    
    def clear_all(self) -> None:
        """Clear all memory layers."""
        self.short_term.clear()
        self.mid_term.clear()
        self.long_term.clear()
        self.message_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize orchestrator state to a dictionary."""
        return {
            'short_term': self.short_term.to_dict(),
            'mid_term': self.mid_term.to_dict(),
            'long_term': self.long_term.to_dict(),
            'message_count': self.message_count,
            'summarize_every': self.summarize_every,
        }
