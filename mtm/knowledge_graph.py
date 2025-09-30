from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Knowledge Graph for Mid-term Memory.
    
    Lưu quan hệ ngữ nghĩa giữa function, class, module.
    Node types: Function, Class, Module, Concept
    Edges: CALLS, BELONGS_TO, RELATED_TO
    """
    
    def __init__(self, neo4j_driver=None, database: str = 'temporal_kg'):
        """
        Initialize knowledge graph.
        
        Args:
            neo4j_driver: Neo4j driver instance (optional)
            database: Database name in Neo4j
        """
        self.driver = neo4j_driver
        self.database = database
        self.enabled = neo4j_driver is not None
        
        # Mock storage
        self.nodes = {}  # {id: node_data}
        self.edges = []  # [(from_id, edge_type, to_id)]
    
    def add_function(self,
                     name: str,
                     module: str,
                     file_path: str,
                     signature: Optional[str] = None,
                     doc: Optional[str] = None) -> bool:
        """
        Add a function node.
        
        Args:
            name: Function name
            module: Module name
            file_path: File path
            signature: Function signature
            doc: Documentation string
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_function_neo4j(name, module, file_path, signature, doc)
        else:
            node_id = f"function:{module}.{name}"
            self.nodes[node_id] = {
                'type': 'Function',
                'name': name,
                'module': module,
                'file_path': file_path,
                'signature': signature,
                'doc': doc
            }
            logger.debug(f"Added function (mock): {node_id}")
            return True
    
    def _add_function_neo4j(self,
                            name: str,
                            module: str,
                            file_path: str,
                            signature: str,
                            doc: str) -> bool:
        """Add function to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MERGE (f:Function {name: $name, module: $module})
                    SET f.file_path = $file_path,
                        f.signature = $signature,
                        f.doc = $doc
                """, name=name, module=module, file_path=file_path,
                    signature=signature, doc=doc)
                
                # Link to module
                session.run("""
                    MATCH (f:Function {name: $name, module: $module})
                    MERGE (m:Module {name: $module})
                    MERGE (f)-[:BELONGS_TO]->(m)
                """, name=name, module=module)
                
                logger.info(f"Added function to Neo4j: {module}.{name}")
                return True
        except Exception as e:
            logger.error(f"Error adding function to Neo4j: {e}")
            return False
    
    def add_class(self,
                  name: str,
                  module: str,
                  file_path: str,
                  methods: Optional[List[str]] = None,
                  doc: Optional[str] = None) -> bool:
        """
        Add a class node.
        
        Args:
            name: Class name
            module: Module name
            file_path: File path
            methods: List of method names
            doc: Documentation string
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_class_neo4j(name, module, file_path, methods, doc)
        else:
            node_id = f"class:{module}.{name}"
            self.nodes[node_id] = {
                'type': 'Class',
                'name': name,
                'module': module,
                'file_path': file_path,
                'methods': methods or [],
                'doc': doc
            }
            logger.debug(f"Added class (mock): {node_id}")
            return True
    
    def _add_class_neo4j(self,
                         name: str,
                         module: str,
                         file_path: str,
                         methods: List[str],
                         doc: str) -> bool:
        """Add class to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MERGE (c:Class {name: $name, module: $module})
                    SET c.file_path = $file_path,
                        c.doc = $doc
                """, name=name, module=module, file_path=file_path, doc=doc)
                
                # Link to module
                session.run("""
                    MATCH (c:Class {name: $name, module: $module})
                    MERGE (m:Module {name: $module})
                    MERGE (c)-[:BELONGS_TO]->(m)
                """, name=name, module=module)
                
                logger.info(f"Added class to Neo4j: {module}.{name}")
                return True
        except Exception as e:
            logger.error(f"Error adding class to Neo4j: {e}")
            return False
    
    def add_call_relationship(self,
                              caller: str,
                              callee: str,
                              call_type: str = 'CALLS') -> bool:
        """
        Add a CALLS relationship between functions.
        
        Args:
            caller: Caller function ID
            callee: Callee function ID
            call_type: Relationship type
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_call_neo4j(caller, callee, call_type)
        else:
            self.edges.append((caller, call_type, callee))
            logger.debug(f"Added call (mock): {caller} -> {callee}")
            return True
    
    def _add_call_neo4j(self, caller: str, callee: str, call_type: str) -> bool:
        """Add call relationship to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run(f"""
                    MATCH (caller:Function {{name: $caller}})
                    MATCH (callee:Function {{name: $callee}})
                    MERGE (caller)-[:{call_type}]->(callee)
                """, caller=caller, callee=callee)
                
                logger.info(f"Added call relationship: {caller} -> {callee}")
                return True
        except Exception as e:
            logger.error(f"Error adding call relationship: {e}")
            return False
    
    def get_function_calls(self, function_name: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        Get functions called by a given function.
        
        Args:
            function_name: Function name
            depth: Traversal depth
            
        Returns:
            List of called functions
        """
        if self.enabled:
            return self._get_calls_neo4j(function_name, depth)
        else:
            # Mock query
            calls = [
                {'from': e[0], 'type': e[1], 'to': e[2]}
                for e in self.edges
                if e[0] == function_name
            ]
            return calls
    
    def _get_calls_neo4j(self, function_name: str, depth: int) -> List[Dict[str, Any]]:
        """Query function calls from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH path = (f:Function {name: $name})-[:CALLS*1..%d]->(called:Function)
                    RETURN called.name AS function,
                           called.module AS module,
                           length(path) AS depth
                    ORDER BY depth
                """ % depth, name=function_name)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error querying function calls: {e}")
            return []
    
    def get_related_concepts(self, concept: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get concepts related to a given concept.
        
        Args:
            concept: Concept name
            limit: Maximum results
            
        Returns:
            List of related concepts
        """
        if self.enabled:
            return self._get_related_neo4j(concept, limit)
        else:
            # Mock query
            related = [
                {'from': e[0], 'relation': e[1], 'to': e[2]}
                for e in self.edges
                if concept in e[0] or concept in e[2]
            ]
            return related[:limit]
    
    def _get_related_neo4j(self, concept: str, limit: int) -> List[Dict[str, Any]]:
        """Query related concepts from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (n)-[r:RELATED_TO]-(related)
                    WHERE n.name CONTAINS $concept
                    RETURN related.name AS name,
                           labels(related)[0] AS type,
                           type(r) AS relationship
                    LIMIT $limit
                """, concept=concept, limit=limit)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error querying related concepts: {e}")
            return []
    
    def clear(self) -> None:
        """Clear all knowledge graph data."""
        if self.enabled:
            try:
                with self.driver.session(database=self.database) as session:
                    session.run("""
                        MATCH (n) 
                        WHERE n:Function OR n:Class OR n:Module OR n:Concept 
                        DETACH DELETE n
                    """)
                logger.info("Cleared knowledge graph in Neo4j")
            except Exception as e:
                logger.error(f"Error clearing Neo4j: {e}")
        else:
            self.nodes = {}
            self.edges = []
