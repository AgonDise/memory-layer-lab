from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class LTMKnowledgeGraph:
    """
    Long-term Knowledge Graph.
    
    Lưu kiến thức bền vững: design docs, module relationships, domain knowledge.
    Sử dụng database riêng trong Neo4j (longterm_kg).
    """
    
    def __init__(self, neo4j_driver=None, database: str = 'longterm_kg'):
        """
        Initialize LTM knowledge graph.
        
        Args:
            neo4j_driver: Neo4j driver instance (optional)
            database: Database name in Neo4j
        """
        self.driver = neo4j_driver
        self.database = database
        self.enabled = neo4j_driver is not None
        
        # Mock storage
        self.knowledge = {}
    
    def add_design_doc(self,
                       doc_id: str,
                       title: str,
                       content: str,
                       version: str,
                       related_modules: Optional[List[str]] = None) -> bool:
        """
        Add a design document.
        
        Args:
            doc_id: Document ID
            title: Document title
            content: Document content
            version: Version string
            related_modules: Related module names
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_design_doc_neo4j(
                doc_id, title, content, version, related_modules
            )
        else:
            self.knowledge[doc_id] = {
                'type': 'DesignDoc',
                'title': title,
                'content': content,
                'version': version,
                'related_modules': related_modules or []
            }
            logger.debug(f"Added design doc (mock): {doc_id}")
            return True
    
    def _add_design_doc_neo4j(self,
                              doc_id: str,
                              title: str,
                              content: str,
                              version: str,
                              related_modules: List[str]) -> bool:
        """Add design doc to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MERGE (d:DesignDoc {id: $id})
                    SET d.title = $title,
                        d.content = $content,
                        d.version = $version
                """, id=doc_id, title=title, content=content, version=version)
                
                # Link to modules
                if related_modules:
                    for module in related_modules:
                        session.run("""
                            MATCH (d:DesignDoc {id: $doc_id})
                            MERGE (m:Module {name: $module})
                            MERGE (d)-[:DESCRIBES]->(m)
                        """, doc_id=doc_id, module=module)
                
                logger.info(f"Added design doc to Neo4j: {doc_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding design doc to Neo4j: {e}")
            return False
    
    def add_domain_concept(self,
                          concept_id: str,
                          name: str,
                          description: str,
                          category: str,
                          related_concepts: Optional[List[str]] = None) -> bool:
        """
        Add a domain concept.
        
        Args:
            concept_id: Concept ID
            name: Concept name
            description: Concept description
            category: Category (e.g., 'architecture', 'pattern', 'principle')
            related_concepts: Related concept IDs
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_concept_neo4j(
                concept_id, name, description, category, related_concepts
            )
        else:
            self.knowledge[concept_id] = {
                'type': 'Concept',
                'name': name,
                'description': description,
                'category': category,
                'related': related_concepts or []
            }
            logger.debug(f"Added concept (mock): {concept_id}")
            return True
    
    def _add_concept_neo4j(self,
                          concept_id: str,
                          name: str,
                          description: str,
                          category: str,
                          related_concepts: List[str]) -> bool:
        """Add concept to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MERGE (c:Concept {id: $id})
                    SET c.name = $name,
                        c.description = $description,
                        c.category = $category
                """, id=concept_id, name=name, 
                    description=description, category=category)
                
                # Link to related concepts
                if related_concepts:
                    for related_id in related_concepts:
                        session.run("""
                            MATCH (c1:Concept {id: $concept_id})
                            MERGE (c2:Concept {id: $related_id})
                            MERGE (c1)-[:RELATED_TO]->(c2)
                        """, concept_id=concept_id, related_id=related_id)
                
                logger.info(f"Added concept to Neo4j: {concept_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding concept to Neo4j: {e}")
            return False
    
    def query_design_docs(self, module_name: str) -> List[Dict[str, Any]]:
        """
        Query design documents for a module.
        
        Args:
            module_name: Module name
            
        Returns:
            List of design documents
        """
        if self.enabled:
            return self._query_docs_neo4j(module_name)
        else:
            # Mock query
            docs = [
                v for k, v in self.knowledge.items()
                if v.get('type') == 'DesignDoc' and 
                   module_name in v.get('related_modules', [])
            ]
            return docs
    
    def _query_docs_neo4j(self, module_name: str) -> List[Dict[str, Any]]:
        """Query design docs from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (d:DesignDoc)-[:DESCRIBES]->(m:Module {name: $module})
                    RETURN d.id AS id,
                           d.title AS title,
                           d.version AS version,
                           d.content AS content
                """, module=module_name)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error querying design docs: {e}")
            return []
    
    def query_concept_hierarchy(self, concept_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        """
        Query concept hierarchy.
        
        Args:
            concept_id: Root concept ID
            depth: Traversal depth
            
        Returns:
            Concept hierarchy
        """
        if self.enabled:
            return self._query_hierarchy_neo4j(concept_id, depth)
        else:
            # Mock query
            if concept_id in self.knowledge:
                return [self.knowledge[concept_id]]
            return []
    
    def _query_hierarchy_neo4j(self, concept_id: str, depth: int) -> List[Dict[str, Any]]:
        """Query concept hierarchy from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH path = (c:Concept {id: $id})-[:RELATED_TO*0..%d]-(related:Concept)
                    RETURN related.id AS id,
                           related.name AS name,
                           related.category AS category,
                           length(path) AS depth
                    ORDER BY depth
                """ % depth, id=concept_id)
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error querying concept hierarchy: {e}")
            return []
    
    def clear(self) -> None:
        """Clear all LTM knowledge graph data."""
        if self.enabled:
            try:
                with self.driver.session(database=self.database) as session:
                    session.run("""
                        MATCH (n)
                        WHERE n:DesignDoc OR n:Concept OR n:Module
                        DETACH DELETE n
                    """)
                logger.info("Cleared LTM knowledge graph in Neo4j")
            except Exception as e:
                logger.error(f"Error clearing Neo4j: {e}")
        else:
            self.knowledge = {}
