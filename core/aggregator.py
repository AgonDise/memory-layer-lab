from typing import List, Dict, Any, Optional
import numpy as np

class MemoryAggregator:
    """
    Aggregates and ranks context from multiple memory layers.
    
    Handles:
    - Merging contexts from STM, MTM, LTM
    - Deduplication
    - Relevance ranking
    """
    
    def __init__(self, 
                 stm_weight: float = 0.5,
                 mtm_weight: float = 0.3,
                 ltm_weight: float = 0.2):
        """
        Initialize memory aggregator.
        
        Args:
            stm_weight: Weight for short-term memory relevance
            mtm_weight: Weight for mid-term memory relevance
            ltm_weight: Weight for long-term memory relevance
        """
        self.stm_weight = stm_weight
        self.mtm_weight = mtm_weight
        self.ltm_weight = ltm_weight
        
        # Normalize weights
        total = stm_weight + mtm_weight + ltm_weight
        self.stm_weight /= total
        self.mtm_weight /= total
        self.ltm_weight /= total
    
    def aggregate(self,
                  stm_context: List[Dict[str, Any]],
                  mtm_context: List[Dict[str, Any]],
                  ltm_context: Optional[List[Dict[str, Any]]] = None,
                  query_embedding: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Aggregate contexts from all memory layers.
        
        Args:
            stm_context: Short-term memory context
            mtm_context: Mid-term memory context
            ltm_context: Long-term memory context (optional)
            query_embedding: Query embedding for relevance scoring
            
        Returns:
            Aggregated context with ranking
        """
        aggregated_items = []
        
        # Process STM items
        for item in stm_context:
            aggregated_items.append({
                'content': item.get('content', ''),
                'source': 'short_term',
                'metadata': item.get('metadata', {}),
                'timestamp': item.get('timestamp', ''),
                'base_score': self.stm_weight,
                'relevance_score': item.get('similarity', 1.0) if query_embedding else 1.0
            })
        
        # Process MTM items
        for item in mtm_context:
            aggregated_items.append({
                'content': item.get('summary', ''),
                'source': 'mid_term',
                'metadata': item.get('metadata', {}),
                'timestamp': item.get('timestamp', ''),
                'base_score': self.mtm_weight,
                'relevance_score': item.get('relevance_score', 0.8) if query_embedding else 0.8
            })
        
        # Process LTM items (if provided)
        if ltm_context:
            for item in ltm_context:
                aggregated_items.append({
                    'content': item.get('content', ''),
                    'source': 'long_term',
                    'metadata': item.get('metadata', {}),
                    'timestamp': item.get('timestamp', ''),
                    'base_score': self.ltm_weight,
                    'relevance_score': item.get('relevance_score', 0.6) if query_embedding else 0.6
                })
        
        # Calculate final scores
        for item in aggregated_items:
            item['final_score'] = item['base_score'] * item['relevance_score']
        
        # Deduplicate based on content similarity
        deduplicated = self._deduplicate(aggregated_items)
        
        # Sort by final score
        deduplicated.sort(key=lambda x: x['final_score'], reverse=True)
        
        return {
            'items': deduplicated,
            'total_items': len(deduplicated),
            'stm_count': sum(1 for i in deduplicated if i['source'] == 'short_term'),
            'mtm_count': sum(1 for i in deduplicated if i['source'] == 'mid_term'),
            'ltm_count': sum(1 for i in deduplicated if i['source'] == 'long_term'),
        }
    
    def _deduplicate(self, items: List[Dict[str, Any]], 
                     threshold: float = 0.95) -> List[Dict[str, Any]]:
        """
        Remove duplicate or very similar items.
        
        Args:
            items: List of items to deduplicate
            threshold: Similarity threshold for considering items as duplicates
            
        Returns:
            Deduplicated list
        """
        if not items:
            return []
        
        deduplicated = []
        seen_contents = []
        
        for item in items:
            content = item['content'].lower().strip()
            
            # Check if similar to any seen content
            is_duplicate = False
            for seen in seen_contents:
                similarity = self._text_similarity(content, seen)
                if similarity > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(item)
                seen_contents.append(content)
        
        return deduplicated
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (Jaccard similarity).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0 to 1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())
        
        # Jaccard similarity
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0
    
    def format_for_llm(self, aggregated_context: Dict[str, Any], 
                       max_items: Optional[int] = None) -> str:
        """
        Format aggregated context for LLM consumption.
        
        Args:
            aggregated_context: Aggregated context dictionary
            max_items: Maximum number of items to include
            
        Returns:
            Formatted context string
        """
        items = aggregated_context['items']
        
        if max_items:
            items = items[:max_items]
        
        if not items:
            return ""
        
        parts = []
        parts.append("=== Context from Memory Layers ===\n")
        
        # Group by source
        stm_items = [i for i in items if i['source'] == 'short_term']
        mtm_items = [i for i in items if i['source'] == 'mid_term']
        ltm_items = [i for i in items if i['source'] == 'long_term']
        
        # Format STM
        if stm_items:
            parts.append("\n[Recent Conversation]")
            for i, item in enumerate(stm_items[:5], 1):
                parts.append(f"{i}. {item['content']} (score: {item['final_score']:.2f})")
        
        # Format MTM
        if mtm_items:
            parts.append("\n[Previous Context]")
            for i, item in enumerate(mtm_items[:3], 1):
                parts.append(f"{i}. {item['content']} (score: {item['final_score']:.2f})")
        
        # Format LTM
        if ltm_items:
            parts.append("\n[Long-term Knowledge]")
            for i, item in enumerate(ltm_items[:2], 1):
                parts.append(f"{i}. {item['content']} (score: {item['final_score']:.2f})")
        
        return "\n".join(parts)
