#!/usr/bin/env python3
"""
Enhanced Memory Orchestrator V2

FULL integration of STM ↔ MTM ↔ LTM for complete LLM context.
"""

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

logger = logging.getLogger(__name__)


class EnhancedMemoryOrchestrator:
    """
    Enhanced orchestrator with FULL STM-MTM-LTM integration.
    
    Key improvements:
    - LTM included in context building
    - Hybrid search strategies
    - Smart context prioritization
    - Complete memory workflow
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
                 ltm_top_k: int = 5,
                 ltm_strategy: str = 'hybrid'):
        """
        Initialize enhanced orchestrator.
        
        Args:
            short_term: STM instance
            mid_term: MTM instance
            long_term: LTM instance (with HybridLTM support)
            summarizer: Summarizer for STM→MTM
            preprocessor: Input preprocessor
            aggregator: Memory aggregator
            compressor: Context compressor
            summarize_every: Messages before summarization
            ltm_top_k: Number of LTM facts to retrieve
            ltm_strategy: LTM retrieval strategy ('vector', 'graph', 'hybrid')
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
        
        # LTM configuration
        self.ltm_top_k = ltm_top_k
        self.ltm_strategy = ltm_strategy
        
        logger.info(f"✅ Enhanced orchestrator initialized with LTM integration")
        logger.info(f"   LTM strategy: {ltm_strategy}, top_k: {ltm_top_k}")
    
    def add_message(self, role: str, content: str, **metadata) -> None:
        """
        Add message and manage memory layers.
        
        Workflow:
        1. Add to STM
        2. Check if summarization needed
        3. Summarize STM → MTM
        4. Extract entities → LTM (if applicable)
        """
        # Add to STM
        self.short_term.add(role, content, **metadata)
        self.message_count += 1
        
        # Periodically summarize
        if self.message_count >= self.summarize_every:
            self._summarize_and_move()
            self.message_count = 0
        
        # Extract knowledge for LTM (if important)
        if self._is_knowledge_worthy(role, content, metadata):
            self._extract_to_ltm(role, content, metadata)
    
    def get_context(self,
                    query: Optional[str] = None,
                    n_recent: Optional[int] = None,
                    n_chunks: Optional[int] = 3,
                    use_ltm: bool = True,
                    use_embedding_search: bool = False) -> Dict[str, Any]:
        """
        Build COMPLETE context from all memory layers.
        
        Args:
            query: Query string for semantic search
            n_recent: Number of recent STM messages
            n_chunks: Number of MTM chunks
            use_ltm: Include LTM in context
            use_embedding_search: Use embedding-based retrieval
            
        Returns:
            Complete context from STM + MTM + LTM
        """
        start_time = time.time()
        
        # Generate query embedding if needed
        query_embedding = None
        if query and use_embedding_search:
            query_obj = self.preprocessor.preprocess(query)
            query_embedding = query_obj['embedding']
        
        # STEP 1: Retrieve from all layers
        logger.debug("Retrieving from memory layers...")
        retrieval_start = time.time()
        
        stm_context, mtm_context, ltm_context = self._retrieve_from_all_layers(
            query=query,
            query_embedding=query_embedding,
            n_recent=n_recent,
            n_chunks=n_chunks,
            use_ltm=use_ltm,
            use_embedding_search=use_embedding_search
        )
        
        retrieval_time = time.time() - retrieval_start
        
        # STEP 2: Aggregate contexts
        agg_start = time.time()
        aggregated = self.aggregator.aggregate(
            stm_context=stm_context,
            mtm_context=mtm_context,
            ltm_context=ltm_context,  # ✅ LTM included!
            query_embedding=query_embedding
        )
        agg_time = time.time() - agg_start
        
        # STEP 3: Compress if needed
        comp_start = time.time()
        compressed = self.compressor.compress(aggregated)
        comp_time = time.time() - comp_start
        
        total_time = time.time() - start_time
        
        # Log stats
        logger.debug(f"Context built: STM={aggregated.get('stm_count', 0)}, "
                    f"MTM={aggregated.get('mtm_count', 0)}, "
                    f"LTM={aggregated.get('ltm_count', 0)} "
                    f"in {total_time*1000:.1f}ms")
        
        return {
            'aggregated': aggregated,
            'compressed': compressed,
            'query_embedding': query_embedding,
            'stm_count': aggregated.get('stm_count', 0),
            'mtm_count': aggregated.get('mtm_count', 0),
            'ltm_count': aggregated.get('ltm_count', 0),  # ✅ Track LTM
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
                          use_ltm: bool = True,
                          use_compression: bool = True) -> str:
        """
        Get context as formatted string for LLM.
        
        Returns complete context with STM + MTM + LTM.
        """
        context = self.get_context(
            query=query,
            n_recent=n_recent,
            n_chunks=n_chunks,
            use_ltm=use_ltm,
            use_embedding_search=(query is not None)
        )
        
        if use_compression:
            return self.compressor.get_context_string(context['compressed'])
        else:
            return self.aggregator.format_for_llm(context['aggregated'])
    
    def _retrieve_from_all_layers(self,
                                  query: Optional[str],
                                  query_embedding: Optional[List[float]],
                                  n_recent: Optional[int],
                                  n_chunks: Optional[int],
                                  use_ltm: bool,
                                  use_embedding_search: bool) -> tuple:
        """
        Retrieve context from all three memory layers.
        
        Returns:
            (stm_context, mtm_context, ltm_context)
        """
        # Retrieve from STM
        if use_embedding_search and query_embedding:
            stm_context = self.short_term.search_by_embedding(
                query_embedding,
                top_k=n_recent or 5
            )
        else:
            stm_context = self.short_term.get_recent(n_recent)
        
        # Retrieve from MTM
        if use_embedding_search and query_embedding:
            mtm_context = self.mid_term.search_by_embedding(
                query_embedding,
                top_k=n_chunks or 3
            )
        else:
            mtm_context = self.mid_term.get_recent_chunks(n_chunks)
        
        # ✅ Retrieve from LTM
        ltm_context = []
        if use_ltm and self.long_term:
            ltm_context = self._retrieve_from_ltm(
                query=query,
                query_embedding=query_embedding,
                use_embedding_search=use_embedding_search
            )
        
        return stm_context, mtm_context, ltm_context
    
    def _retrieve_from_ltm(self,
                          query: Optional[str],
                          query_embedding: Optional[List[float]],
                          use_embedding_search: bool) -> List[Dict]:
        """
        Retrieve relevant facts from LTM.
        
        Supports multiple strategies:
        - Embedding search (semantic)
        - Category-based
        - Hybrid (vector + graph)
        """
        try:
            # Check if LTM has hybrid capabilities
            if hasattr(self.long_term, 'hybrid_ltm') and self.long_term.hybrid_ltm:
                # Use hybrid LTM
                return self._retrieve_from_hybrid_ltm(query, query_embedding)
            
            # Fallback to simple retrieval
            if use_embedding_search and query_embedding:
                # Simple embedding search
                if hasattr(self.long_term, 'search_by_embedding'):
                    return self.long_term.search_by_embedding(
                        query_embedding,
                        top_k=self.ltm_top_k
                    )
            
            # Basic retrieval
            if hasattr(self.long_term, 'get_relevant_facts'):
                return self.long_term.get_relevant_facts(
                    categories=['architecture', 'function', 'guideline', 'commit_log'],
                    limit=self.ltm_top_k
                )
            elif hasattr(self.long_term, 'facts'):
                return self.long_term.facts[:self.ltm_top_k]
            
            return []
            
        except Exception as e:
            logger.warning(f"LTM retrieval failed: {e}")
            return []
    
    def _retrieve_from_hybrid_ltm(self,
                                  query: Optional[str],
                                  query_embedding: Optional[List[float]]) -> List[Dict]:
        """Retrieve from HybridLTM (VectorDB + Graph)."""
        from ltm.hybrid_ltm import QueryStrategy
        
        # Map strategy string to enum
        strategy_map = {
            'vector': QueryStrategy.VECTOR_FIRST,
            'graph': QueryStrategy.GRAPH_FIRST,
            'hybrid': QueryStrategy.PARALLEL,
            'vector_only': QueryStrategy.VECTOR_ONLY,
            'graph_only': QueryStrategy.GRAPH_ONLY
        }
        
        strategy = strategy_map.get(self.ltm_strategy, QueryStrategy.PARALLEL)
        
        # Query hybrid LTM
        result = self.long_term.hybrid_ltm.query(
            query=query or '',
            strategy=strategy,
            top_k=self.ltm_top_k
        )
        
        # Combine semantic and graph results
        combined = []
        combined.extend(result.semantic_matches[:self.ltm_top_k])
        
        # Add graph relations if strategy includes graph
        if strategy in [QueryStrategy.GRAPH_FIRST, QueryStrategy.PARALLEL]:
            combined.extend(result.graph_relations[:3])
        
        return combined[:self.ltm_top_k]
    
    def _summarize_and_move(self) -> None:
        """Summarize STM → MTM."""
        messages = self.short_term.get_recent()
        
        if not messages or len(messages) < 2:
            return
        
        # Generate summary
        summary = self.summarizer.summarize(messages)
        summary_embedding = self.preprocessor._generate_embedding(summary)
        
        # Extract metadata
        metadata = {
            'message_count': len(messages),
            'topics': self.summarizer.extract_key_topics(messages),
            'embedding': summary_embedding,
        }
        
        # Add to MTM
        self.mid_term.add_chunk(summary, metadata)
        
        logger.debug(f"Summarized {len(messages)} messages to MTM")
    
    def _is_knowledge_worthy(self, role: str, content: str, metadata: dict) -> bool:
        """
        Determine if message contains knowledge worth storing in LTM.
        
        Criteria:
        - Contains code snippets
        - Mentions architecture/design
        - Bug fixes or solutions
        - Best practices
        - Important decisions
        """
        # Only assistant messages for now
        if role != 'assistant':
            return False
        
        # Check for knowledge indicators
        knowledge_keywords = [
            'architecture', 'design', 'pattern',
            'fix', 'solution', 'implement',
            'guideline', 'best practice', 'recommendation',
            'function', 'class', 'module',
            'bug', 'error', 'issue'
        ]
        
        content_lower = content.lower()
        has_keywords = any(kw in content_lower for kw in knowledge_keywords)
        
        # Check metadata
        has_code = metadata.get('has_code', False)
        is_important = metadata.get('importance', 'low') in ['high', 'critical']
        
        return has_keywords or has_code or is_important
    
    def _extract_to_ltm(self, role: str, content: str, metadata: dict) -> None:
        """Extract knowledge and add to LTM."""
        try:
            # Simple extraction for now
            # TODO: Use LLM to extract structured knowledge
            
            # Determine category
            content_lower = content.lower()
            if 'function' in content_lower or 'method' in content_lower:
                category = 'function'
            elif 'architecture' in content_lower or 'design' in content_lower:
                category = 'architecture'
            elif 'bug' in content_lower or 'fix' in content_lower:
                category = 'commit_log'
            else:
                category = 'guideline'
            
            # Add to LTM
            if hasattr(self.long_term, 'add'):
                self.long_term.add(
                    content=content,
                    metadata={
                        'category': category,
                        'source': 'conversation',
                        'role': role,
                        **metadata
                    }
                )
                logger.debug(f"Extracted knowledge to LTM: {category}")
                
        except Exception as e:
            logger.warning(f"Failed to extract to LTM: {e}")
    
    def clear_all(self) -> None:
        """Clear all memory layers."""
        self.short_term.clear()
        self.mid_term.clear()
        self.long_term.clear()
        self.message_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all memory layers."""
        return {
            'stm_count': len(self.short_term.get_recent(100)),
            'mtm_count': len(self.mid_term.get_all()),
            'ltm_count': len(self.long_term.facts) if hasattr(self.long_term, 'facts') else 0,
            'message_count': self.message_count,
            'summarize_every': self.summarize_every,
            'ltm_strategy': self.ltm_strategy
        }
    
    def __repr__(self):
        stats = self.get_stats()
        return (f"EnhancedMemoryOrchestrator("
                f"STM={stats['stm_count']}, "
                f"MTM={stats['mtm_count']}, "
                f"LTM={stats['ltm_count']})")
