from typing import Dict, Any, List, Optional
from .knowledge_graph import LTMKnowledgeGraph
from .vecdb import VectorDatabase
import logging

logger = logging.getLogger(__name__)

class LTMQuery:
    """
    Unified query interface for Long-term Memory.
    
    Combines queries from both Knowledge Graph and Vector Database.
    """
    
    def __init__(self,
                 knowledge_graph: LTMKnowledgeGraph,
                 vector_db: VectorDatabase):
        """
        Initialize LTM query interface.
        
        Args:
            knowledge_graph: LTM knowledge graph instance
            vector_db: Vector database instance
        """
        self.knowledge = knowledge_graph
        self.vecdb = vector_db
    
    def query_design_knowledge(self,
                               module: str,
                               include_semantic: bool = True) -> Dict[str, Any]:
        """
        Query design knowledge for a module.
        
        Args:
            module: Module name
            include_semantic: Include semantic search results
            
        Returns:
            Design knowledge dictionary
        """
        result = {
            'module': module,
            'design_docs': [],
            'semantic_matches': []
        }
        
        # Query knowledge graph
        docs = self.knowledge.query_design_docs(module)
        result['design_docs'] = docs
        
        # Query vector DB for semantic matches
        if include_semantic and self.vecdb.enabled:
            # Would need to generate embedding for module name
            # For now, just return empty
            pass
        
        return result
    
    def query_concepts(self,
                       concept_id: str,
                       depth: int = 2) -> Dict[str, Any]:
        """
        Query concept hierarchy and related knowledge.
        
        Args:
            concept_id: Concept ID
            depth: Traversal depth
            
        Returns:
            Concept hierarchy dictionary
        """
        hierarchy = self.knowledge.query_concept_hierarchy(concept_id, depth)
        
        return {
            'concept_id': concept_id,
            'hierarchy': hierarchy,
            'total_related': len(hierarchy)
        }
    
    def semantic_search(self,
                        query_embedding: List[float],
                        top_k: int = 5,
                        filter_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search in vector database.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results
            filter_category: Filter by category
            
        Returns:
            List of semantic matches
        """
        if not self.vecdb.enabled:
            return []
        
        # Search in vector database
        results = self.vecdb.search(query_embedding, top_k)
        
        # Filter by category if specified
        if filter_category:
            results = [
                r for r in results
                if r.get('metadata', {}).get('category') == filter_category
            ]
        
        return results
    
    def get_ltm_context(self,
                        query: str,
                        query_embedding: List[float],
                        top_k: int = 3) -> Dict[str, Any]:
        """
        Get LTM context for a given query.
        
        This is the main method called by the orchestrator.
        
        Args:
            query: User query
            query_embedding: Query embedding vector
            top_k: Number of top results
            
        Returns:
            LTM context dictionary
        """
        context = {
            'knowledge_graph': [],
            'semantic_search': []
        }
        
        # Semantic search in vector DB
        if self.vecdb.enabled:
            semantic_results = self.vecdb.search(query_embedding, top_k)
            context['semantic_search'] = [
                {
                    'content': item.get('content', '')[:200],  # Truncate
                    'score': item.get('score', 0.0),
                    'metadata': item.get('metadata', {})
                }
                for item in semantic_results
            ]
        
        # Query knowledge graph for related concepts
        # (In a real implementation, would extract concepts from query)
        # For now, return empty
        
        return context
    
    def add_document_to_ltm(self,
                            doc_id: str,
                            content: str,
                            embedding: List[float],
                            doc_type: str = 'document',
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a document to long-term memory.
        
        Args:
            doc_id: Document ID
            content: Document content
            embedding: Document embedding
            doc_type: Document type
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        # Add to vector database
        meta = metadata or {}
        meta['type'] = doc_type
        
        success = self.vecdb.add_document(doc_id, content, embedding, meta)
        
        if success:
            logger.info(f"Added document to LTM: {doc_id}")
        
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get LTM statistics."""
        return {
            'vector_db': self.vecdb.get_stats(),
            'knowledge_graph_enabled': self.knowledge.enabled,
        }
