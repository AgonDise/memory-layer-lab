from typing import List, Dict, Any, Optional
import json

class Summarizer:
    """
    Module for summarizing conversation chunks.
    
    This can be configured to use different summarization strategies:
    - Simple extraction (first/last messages)
    - LLM-based summarization
    - Custom algorithms
    """
    
    def __init__(self, strategy: str = 'simple', llm_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the summarizer.
        
        Args:
            strategy: Summarization strategy ('simple', 'llm', 'custom')
            llm_config: Configuration for LLM-based summarization
        """
        self.strategy = strategy
        self.llm_config = llm_config or {}
    
    def summarize(self, messages: List[Dict[str, Any]]) -> str:
        """
        Summarize a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Summary string
        """
        if not messages:
            return ""
        
        if self.strategy == 'simple':
            return self._simple_summarize(messages)
        elif self.strategy == 'llm':
            return self._llm_summarize(messages)
        else:
            return self._simple_summarize(messages)
    
    def _simple_summarize(self, messages: List[Dict[str, Any]]) -> str:
        """
        Simple summarization: concatenate key messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Include first message
        if messages:
            first = messages[0]
            summary_parts.append(f"{first['role']}: {first['content'][:100]}")
        
        # Include middle messages count
        if len(messages) > 2:
            summary_parts.append(f"[... {len(messages) - 2} messages exchanged ...]")
        
        # Include last message
        if len(messages) > 1:
            last = messages[-1]
            summary_parts.append(f"{last['role']}: {last['content'][:100]}")
        
        return " | ".join(summary_parts)
    
    def _llm_summarize(self, messages: List[Dict[str, Any]]) -> str:
        """
        LLM-based summarization using an external API.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Summary string
        """
        # TODO: Implement actual LLM API call
        # This is a placeholder that simulates LLM summarization
        
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        # Mock summary for now
        return f"Summary of {len(messages)} messages: {conversation[:200]}..."
    
    def extract_key_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key topics from messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of key topics/keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        topics = set()
        
        for msg in messages:
            content = msg.get('content', '').lower()
            # Extract words longer than 5 characters as potential topics
            words = [w.strip('.,!?;:') for w in content.split()]
            topics.update([w for w in words if len(w) > 5])
        
        return list(topics)[:10]  # Return top 10
