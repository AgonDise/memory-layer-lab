from typing import List, Dict, Any, Optional
import re

class ContextCompressor:
    """
    Compresses context to fit within token budgets.
    
    Strategies:
    - Truncation
    - Extractive summarization
    - MMR (Maximal Marginal Relevance)
    - Score-based filtering
    """
    
    def __init__(self, 
                 max_tokens: int = 2000,
                 strategy: str = 'score_based'):
        """
        Initialize context compressor.
        
        Args:
            max_tokens: Maximum token budget
            strategy: Compression strategy ('truncate', 'score_based', 'mmr')
        """
        self.max_tokens = max_tokens
        self.strategy = strategy
    
    def compress(self, 
                 aggregated_context: Dict[str, Any],
                 preserve_recent: bool = True) -> Dict[str, Any]:
        """
        Compress aggregated context to fit token budget.
        
        Args:
            aggregated_context: Aggregated context from MemoryAggregator
            preserve_recent: Always keep most recent items
            
        Returns:
            Compressed context dictionary
        """
        items = aggregated_context.get('items', [])
        
        if not items:
            return {
                'compressed_items': [],
                'total_tokens': 0,
                'compression_ratio': 0.0,
                'strategy': self.strategy
            }
        
        # Apply compression strategy
        if self.strategy == 'truncate':
            compressed = self._truncate_compress(items)
        elif self.strategy == 'score_based':
            compressed = self._score_based_compress(items, preserve_recent)
        elif self.strategy == 'mmr':
            compressed = self._mmr_compress(items, preserve_recent)
        else:
            compressed = self._score_based_compress(items, preserve_recent)
        
        # Calculate metrics
        original_tokens = sum(self._estimate_tokens(item['content']) for item in items)
        compressed_tokens = sum(self._estimate_tokens(item['content']) for item in compressed)
        
        return {
            'compressed_items': compressed,
            'total_tokens': compressed_tokens,
            'original_tokens': original_tokens,
            'compression_ratio': compressed_tokens / original_tokens if original_tokens > 0 else 0.0,
            'strategy': self.strategy,
            'items_kept': len(compressed),
            'items_removed': len(items) - len(compressed)
        }
    
    def _truncate_compress(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simple truncation: keep items until token budget is reached.
        
        Args:
            items: List of items (should be pre-sorted by score)
            
        Returns:
            Compressed list
        """
        compressed = []
        token_count = 0
        
        for item in items:
            item_tokens = self._estimate_tokens(item['content'])
            
            if token_count + item_tokens <= self.max_tokens:
                compressed.append(item)
                token_count += item_tokens
            else:
                break
        
        return compressed
    
    def _score_based_compress(self, 
                              items: List[Dict[str, Any]],
                              preserve_recent: bool = True) -> List[Dict[str, Any]]:
        """
        Score-based compression: prioritize high-scoring items.
        
        Args:
            items: List of items with scores
            preserve_recent: Keep recent items regardless of score
            
        Returns:
            Compressed list
        """
        if preserve_recent:
            # Always keep recent items (STM)
            recent_items = [i for i in items if i['source'] == 'short_term']
            other_items = [i for i in items if i['source'] != 'short_term']
            
            # Sort others by score
            other_items.sort(key=lambda x: x['final_score'], reverse=True)
            
            compressed = []
            token_count = 0
            
            # Add recent items first
            for item in recent_items[-3:]:  # Keep last 3 recent
                item_tokens = self._estimate_tokens(item['content'])
                if token_count + item_tokens <= self.max_tokens:
                    compressed.append(item)
                    token_count += item_tokens
            
            # Add high-scoring others
            for item in other_items:
                item_tokens = self._estimate_tokens(item['content'])
                if token_count + item_tokens <= self.max_tokens:
                    compressed.append(item)
                    token_count += item_tokens
                else:
                    break
            
            return compressed
        else:
            return self._truncate_compress(items)
    
    def _mmr_compress(self, 
                      items: List[Dict[str, Any]],
                      preserve_recent: bool = True,
                      lambda_param: float = 0.7) -> List[Dict[str, Any]]:
        """
        MMR (Maximal Marginal Relevance) compression for diversity.
        
        Args:
            items: List of items
            preserve_recent: Keep recent items
            lambda_param: Balance between relevance and diversity (0-1)
            
        Returns:
            Compressed list with diversity
        """
        # For now, use score-based with diversity consideration
        # TODO: Implement proper MMR algorithm
        return self._score_based_compress(items, preserve_recent)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def format_compressed(self, compressed_context: Dict[str, Any]) -> str:
        """
        Format compressed context for LLM.
        
        Args:
            compressed_context: Compressed context dictionary
            
        Returns:
            Formatted string
        """
        items = compressed_context.get('compressed_items', [])
        
        if not items:
            return ""
        
        parts = []
        parts.append("=== Compressed Context ===")
        parts.append(f"Tokens: {compressed_context['total_tokens']}/{self.max_tokens}")
        parts.append(f"Compression: {compressed_context['compression_ratio']:.1%}\n")
        
        for i, item in enumerate(items, 1):
            source_tag = {
                'short_term': '🔴',
                'mid_term': '🟡',
                'long_term': '🟢'
            }.get(item['source'], '⚪')
            
            parts.append(f"{i}. {source_tag} [{item['source']}] (score: {item['final_score']:.2f})")
            parts.append(f"   {item['content'][:200]}...")
            parts.append("")
        
        return "\n".join(parts)
    
    def get_context_string(self, compressed_context: Dict[str, Any]) -> str:
        """
        Get clean context string without metadata.
        
        Args:
            compressed_context: Compressed context dictionary
            
        Returns:
            Clean context string for LLM input
        """
        items = compressed_context.get('compressed_items', [])
        
        parts = []
        for item in items:
            parts.append(item['content'])
        
        return "\n\n".join(parts)
