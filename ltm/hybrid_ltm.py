#!/usr/bin/env python3
"""
Hybrid LTM: VectorDB + Knowledge Graph

Combines semantic search (VectorDB) with structured relationships (Neo4j Graph).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class QueryStrategy(Enum):
    """Query execution strategy."""
    VECTOR_FIRST = "vector_first"      # Vector → Graph expansion
    GRAPH_FIRST = "graph_first"        # Graph → Vector enrichment
    PARALLEL = "parallel"              # Both simultaneously
    VECTOR_ONLY = "vector_only"        # Only semantic search
    GRAPH_ONLY = "graph_only"          # Only graph query


@dataclass
class HybridResult:
    """Combined result from both databases."""
    semantic_matches: List[Dict[str, Any]]  # From VectorDB
    graph_relations: List[Dict[str, Any]]   # From Graph
    combined_score: float
    strategy_used: QueryStrategy
    metadata: Dict[str, Any]


class HybridLTM:
    """
    Hybrid Long-Term Memory combining VectorDB and Knowledge Graph.
    
    Architecture:
        VectorDB (FAISS/ChromaDB) - Semantic search by embeddings
        Graph (Neo4j) - Structured relationships
        Coordinator - Combines both for powerful queries
    """
    
    def __init__(self, vector_db=None, graph_db=None):
        """
        Initialize hybrid LTM.
        
        Args:
            vector_db: VectorDB instance (FAISS, ChromaDB, etc.)
            graph_db: Neo4j manager instance
        """
        self.vector_db = vector_db
        self.graph_db = graph_db
        self._embedding_cache = {}
    
    def add(self, content: str, metadata: Dict[str, Any], 
            embedding: Optional[List[float]] = None) -> Dict[str, str]:
        """
        Add to both VectorDB and Knowledge Graph.
        
        Args:
            content: Text content
            metadata: Metadata including category, tags, etc.
            embedding: Pre-computed embedding (optional)
            
        Returns:
            Dict with vector_id and graph_entity_id
        """
        # 1. Generate embedding if not provided
        if embedding is None:
            embedding = self._generate_embedding(content)
        
        # 2. Create graph entity first (to get ID)
        graph_entity_id = self._create_graph_entity(content, metadata)
        
        # 3. Add to VectorDB with graph link
        vector_id = self._add_to_vector_db(
            content=content,
            embedding=embedding,
            metadata={
                **metadata,
                'graph_entity_id': graph_entity_id
            }
        )
        
        # 4. Update graph entity with vector link
        self._update_graph_vector_link(graph_entity_id, vector_id)
        
        # 5. Create relationships in graph
        self._create_graph_relationships(graph_entity_id, metadata)
        
        return {
            'vector_id': vector_id,
            'graph_entity_id': graph_entity_id
        }
    
    def query(self, query: str, 
              strategy: QueryStrategy = QueryStrategy.PARALLEL,
              top_k: int = 5,
              expand_graph: bool = True) -> HybridResult:
        """
        Query both databases using specified strategy.
        
        Args:
            query: Query string
            strategy: Query execution strategy
            top_k: Number of results to return
            expand_graph: Whether to expand graph relationships
            
        Returns:
            HybridResult with combined results
        """
        if strategy == QueryStrategy.VECTOR_FIRST:
            return self._vector_first_query(query, top_k, expand_graph)
        
        elif strategy == QueryStrategy.GRAPH_FIRST:
            return self._graph_first_query(query, top_k)
        
        elif strategy == QueryStrategy.PARALLEL:
            return self._parallel_query(query, top_k)
        
        elif strategy == QueryStrategy.VECTOR_ONLY:
            results = self._vector_search(query, top_k)
            return HybridResult(
                semantic_matches=results,
                graph_relations=[],
                combined_score=0.0,
                strategy_used=strategy,
                metadata={}
            )
        
        elif strategy == QueryStrategy.GRAPH_ONLY:
            results = self._graph_search(query)
            return HybridResult(
                semantic_matches=[],
                graph_relations=results,
                combined_score=0.0,
                strategy_used=strategy,
                metadata={}
            )
    
    def _vector_first_query(self, query: str, top_k: int, 
                           expand: bool) -> HybridResult:
        """
        Strategy: Vector search → Graph expansion.
        
        Use case: Start broad (semantic), then get precise relationships.
        """
        # 1. Vector search
        vector_results = self._vector_search(query, top_k)
        
        if not expand or not vector_results:
            return HybridResult(
                semantic_matches=vector_results,
                graph_relations=[],
                combined_score=0.0,
                strategy_used=QueryStrategy.VECTOR_FIRST,
                metadata={'expanded': False}
            )
        
        # 2. Extract entity IDs
        entity_ids = [
            r.get('metadata', {}).get('graph_entity_id')
            for r in vector_results
            if r.get('metadata', {}).get('graph_entity_id')
        ]
        
        # 3. Graph expansion
        graph_results = []
        if entity_ids:
            graph_results = self._expand_graph_entities(entity_ids)
        
        # 4. Combine
        return HybridResult(
            semantic_matches=vector_results,
            graph_relations=graph_results,
            combined_score=self._calculate_combined_score(vector_results, graph_results),
            strategy_used=QueryStrategy.VECTOR_FIRST,
            metadata={
                'expanded': True,
                'entity_count': len(entity_ids)
            }
        )
    
    def _graph_first_query(self, query: str, top_k: int) -> HybridResult:
        """
        Strategy: Graph query → Vector enrichment.
        
        Use case: Precise query (e.g., "commits by author"), enrich with content.
        """
        # 1. Graph search
        graph_results = self._graph_search(query)
        
        # 2. Get vector IDs from graph nodes
        vector_ids = [
            node.get('vector_id')
            for node in graph_results
            if node.get('vector_id')
        ]
        
        # 3. Fetch vector content
        vector_results = []
        if vector_ids and self.vector_db:
            vector_results = [
                self.vector_db.get_by_id(vid)
                for vid in vector_ids[:top_k]
                if vid
            ]
        
        return HybridResult(
            semantic_matches=vector_results,
            graph_relations=graph_results,
            combined_score=self._calculate_combined_score(vector_results, graph_results),
            strategy_used=QueryStrategy.GRAPH_FIRST,
            metadata={'vector_enriched': len(vector_results) > 0}
        )
    
    def _parallel_query(self, query: str, top_k: int) -> HybridResult:
        """
        Strategy: Query both databases simultaneously.
        
        Use case: Complex queries needing both approaches.
        """
        import concurrent.futures
        
        # Run both queries in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            vector_future = executor.submit(self._vector_search, query, top_k)
            graph_future = executor.submit(self._graph_search, query)
            
            vector_results = vector_future.result()
            graph_results = graph_future.result()
        
        return HybridResult(
            semantic_matches=vector_results,
            graph_relations=graph_results,
            combined_score=self._calculate_combined_score(vector_results, graph_results),
            strategy_used=QueryStrategy.PARALLEL,
            metadata={'parallel': True}
        )
    
    def get_related(self, entity_id: str, 
                   relationship_types: Optional[List[str]] = None,
                   max_depth: int = 2) -> Dict[str, Any]:
        """
        Get all related entities from graph + their vector content.
        
        Args:
            entity_id: Graph entity ID
            relationship_types: Types of relationships to follow
            max_depth: Maximum traversal depth
            
        Returns:
            Dict with related entities and their content
        """
        # 1. Graph traversal
        cypher = self._build_traversal_query(entity_id, relationship_types, max_depth)
        graph_results = self._execute_graph_query(cypher)
        
        # 2. Enrich with vector content
        enriched = []
        for node in graph_results:
            vector_id = node.get('vector_id')
            if vector_id and self.vector_db:
                content = self.vector_db.get_by_id(vector_id)
                enriched.append({
                    'node': node,
                    'content': content.get('content'),
                    'embedding': content.get('embedding')
                })
            else:
                enriched.append({'node': node})
        
        return {
            'entity_id': entity_id,
            'related': enriched,
            'count': len(enriched)
        }
    
    def find_path(self, start_id: str, end_id: str, 
                  max_length: int = 5) -> List[Dict[str, Any]]:
        """
        Find path between two entities in knowledge graph.
        
        Args:
            start_id: Start entity ID
            end_id: End entity ID
            max_length: Maximum path length
            
        Returns:
            List of paths with nodes and relationships
        """
        if not self.graph_db:
            return []
        
        cypher = f"""
        MATCH path = shortestPath(
            (start {{id: $start_id}})-[*..{max_length}]-(end {{id: $end_id}})
        )
        RETURN path, length(path) as length
        ORDER BY length
        LIMIT 5
        """
        
        results = self._execute_graph_query(cypher, {
            'start_id': start_id,
            'end_id': end_id
        })
        
        return results
    
    # Private helper methods
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        # Check cache
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        # Generate new embedding
        try:
            from utils.real_embedding import RealEmbeddingGenerator
            embedder = RealEmbeddingGenerator()
            embedding = embedder.generate(text)
        except:
            # Fallback to mock
            import hashlib, random
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            random.seed(h)
            embedding = [random.random() for _ in range(384)]
        
        # Cache
        self._embedding_cache[text] = embedding
        return embedding
    
    def _create_graph_entity(self, content: str, metadata: Dict[str, Any]) -> str:
        """Create entity in knowledge graph."""
        if not self.graph_db:
            # Generate mock ID
            import uuid
            return f"graph_{uuid.uuid4().hex[:12]}"
        
        category = metadata.get('category', 'unknown')
        entity_id = metadata.get('id', f"entity_{uuid.uuid4().hex[:12]}")
        
        # Create node based on category
        if category == 'function':
            cypher = """
            CREATE (f:Function {
                id: $id,
                name: $name,
                file_path: $file_path,
                description: $description
            })
            RETURN f.id as id
            """
            params = {
                'id': entity_id,
                'name': metadata.get('function_name', 'unknown'),
                'file_path': metadata.get('file_path', ''),
                'description': content[:200]
            }
        
        elif category == 'commit_log':
            cypher = """
            CREATE (c:Commit {
                id: $id,
                hash: $hash,
                message: $message,
                author: $author
            })
            RETURN c.id as id
            """
            params = {
                'id': entity_id,
                'hash': metadata.get('git_commit', ''),
                'message': content[:200],
                'author': metadata.get('author', '')
            }
        
        else:
            # Generic node
            cypher = """
            CREATE (n:Entity {
                id: $id,
                category: $category,
                content: $content
            })
            RETURN n.id as id
            """
            params = {
                'id': entity_id,
                'category': category,
                'content': content[:200]
            }
        
        result = self._execute_graph_query(cypher, params)
        return entity_id
    
    def _add_to_vector_db(self, content: str, embedding: List[float],
                         metadata: Dict[str, Any]) -> str:
        """Add to vector database."""
        if not self.vector_db:
            import uuid
            return f"vec_{uuid.uuid4().hex[:12]}"
        
        return self.vector_db.add(
            content=content,
            embedding=embedding,
            metadata=metadata
        )
    
    def _update_graph_vector_link(self, graph_id: str, vector_id: str):
        """Update graph entity with vector ID link."""
        if not self.graph_db:
            return
        
        cypher = """
        MATCH (n {id: $graph_id})
        SET n.vector_id = $vector_id
        """
        self._execute_graph_query(cypher, {
            'graph_id': graph_id,
            'vector_id': vector_id
        })
    
    def _create_graph_relationships(self, entity_id: str, metadata: Dict[str, Any]):
        """Create relationships in graph based on metadata."""
        if not self.graph_db:
            return
        
        graph_links = metadata.get('graph_links', [])
        
        for link in graph_links:
            rel_type = link.get('type', 'RELATED_TO')
            target_id = link.get('target')
            
            if target_id:
                cypher = f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                CREATE (source)-[:{rel_type}]->(target)
                """
                self._execute_graph_query(cypher, {
                    'source_id': entity_id,
                    'target_id': target_id
                })
    
    def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search vector database."""
        if not self.vector_db:
            return []
        
        embedding = self._generate_embedding(query)
        return self.vector_db.search(embedding, top_k=top_k)
    
    def _graph_search(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge graph."""
        if not self.graph_db:
            return []
        
        # Simple full-text search on graph
        cypher = """
        MATCH (n)
        WHERE n.name CONTAINS $query 
           OR n.description CONTAINS $query
           OR n.message CONTAINS $query
        RETURN n
        LIMIT 10
        """
        return self._execute_graph_query(cypher, {'query': query})
    
    def _expand_graph_entities(self, entity_ids: List[str]) -> List[Dict[str, Any]]:
        """Expand graph entities with their relationships."""
        if not self.graph_db or not entity_ids:
            return []
        
        cypher = """
        MATCH (n) WHERE n.id IN $ids
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, r, m
        LIMIT 50
        """
        return self._execute_graph_query(cypher, {'ids': entity_ids})
    
    def _build_traversal_query(self, entity_id: str, 
                              rel_types: Optional[List[str]],
                              max_depth: int) -> str:
        """Build Cypher query for graph traversal."""
        if rel_types:
            rel_clause = '|'.join(rel_types)
            pattern = f"[:{rel_clause}*1..{max_depth}]"
        else:
            pattern = f"[*1..{max_depth}]"
        
        return f"""
        MATCH (start {{id: $entity_id}})
        MATCH (start)-{pattern}-(related)
        RETURN DISTINCT related
        LIMIT 20
        """
    
    def _execute_graph_query(self, cypher: str, 
                            params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute Cypher query on graph database."""
        if not self.graph_db:
            return []
        
        try:
            return self.graph_db.execute_read(cypher, params or {})
        except Exception as e:
            print(f"Graph query error: {e}")
            return []
    
    def _calculate_combined_score(self, vector_results: List, 
                                  graph_results: List) -> float:
        """Calculate combined relevance score."""
        if not vector_results and not graph_results:
            return 0.0
        
        # Simple scoring: average of both
        vector_score = len(vector_results) / 10  # Normalize
        graph_score = len(graph_results) / 10
        
        return (vector_score + graph_score) / 2
    
    def __repr__(self):
        vec_status = "✅" if self.vector_db else "❌"
        graph_status = "✅" if self.graph_db else "❌"
        return f"HybridLTM(VectorDB: {vec_status}, Graph: {graph_status})"
