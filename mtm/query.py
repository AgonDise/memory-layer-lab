from typing import Dict, Any, List, Optional
from .temporal_graph import TemporalGraph
from .knowledge_graph import KnowledgeGraph
import logging

logger = logging.getLogger(__name__)

class MTMQuery:
    """
    Unified query interface for Mid-term Memory.
    
    Combines queries from both Temporal Graph and Knowledge Graph.
    """
    
    def __init__(self, 
                 temporal_graph: TemporalGraph,
                 knowledge_graph: KnowledgeGraph):
        """
        Initialize MTM query interface.
        
        Args:
            temporal_graph: Temporal graph instance
            knowledge_graph: Knowledge graph instance
        """
        self.temporal = temporal_graph
        self.knowledge = knowledge_graph
    
    def query_code_history(self, 
                           file_path: str,
                           limit: int = 10) -> Dict[str, Any]:
        """
        Query complete history of a code file.
        
        Args:
            file_path: File path to query
            limit: Maximum results
            
        Returns:
            Dictionary with temporal and knowledge info
        """
        # Get commits affecting this file
        commits = self.temporal.get_commits_affecting_file(file_path, limit)
        
        # Get functions/classes in this file
        # (This would need file parsing in real implementation)
        
        return {
            'file_path': file_path,
            'commits': commits,
            'total_commits': len(commits),
        }
    
    def query_function_context(self,
                               function_name: str,
                               include_calls: bool = True,
                               include_history: bool = True) -> Dict[str, Any]:
        """
        Query complete context for a function.
        
        Args:
            function_name: Function name
            include_calls: Include call relationships
            include_history: Include commit history
            
        Returns:
            Function context dictionary
        """
        context = {
            'function': function_name,
            'calls': [],
            'history': []
        }
        
        if include_calls:
            context['calls'] = self.knowledge.get_function_calls(function_name)
        
        if include_history:
            # Would need to find which file contains this function
            # Then query temporal graph
            pass
        
        return context
    
    def query_related_code(self,
                          query: str,
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query code related to a search query.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of related code items
        """
        # Search in knowledge graph
        related = self.knowledge.get_related_concepts(query, limit)
        
        return related
    
    def get_mtm_context(self,
                        query: str,
                        top_k: int = 5) -> Dict[str, Any]:
        """
        Get MTM context for a given query.
        
        This is the main method called by the orchestrator.
        
        Args:
            query: User query
            top_k: Number of top results
            
        Returns:
            MTM context dictionary
        """
        context = {
            'temporal_graph': [],
            'knowledge_graph': [],
        }
        
        # Query temporal graph (recent activity)
        timeline = self.temporal.get_timeline(limit=top_k)
        context['temporal_graph'] = [
            {
                'type': item.get('type', 'commit'),
                'id': item.get('id', ''),
                'timestamp': item.get('timestamp', ''),
                'message': item.get('message') or item.get('description', ''),
            }
            for item in timeline
        ]
        
        # Query knowledge graph (related concepts)
        related = self.knowledge.get_related_concepts(query, limit=top_k)
        context['knowledge_graph'] = [
            {
                'name': item.get('name', ''),
                'type': item.get('type', ''),
                'relationship': item.get('relationship', ''),
            }
            for item in related
        ]
        
        return context
