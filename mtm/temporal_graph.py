from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TemporalGraph:
    """
    Temporal Graph for Mid-term Memory.
    
    Lưu dòng thời gian commit, checkpoints, thay đổi code.
    Node types: Commit, Checkpoint
    Edges: NEXT, AFFECTS
    """
    
    def __init__(self, neo4j_driver=None, database: str = 'temporal_kg'):
        """
        Initialize temporal graph.
        
        Args:
            neo4j_driver: Neo4j driver instance (optional)
            database: Database name in Neo4j
        """
        self.driver = neo4j_driver
        self.database = database
        self.enabled = neo4j_driver is not None
        
        # Mock storage if Neo4j not available
        self.commits = []
        self.checkpoints = []
    
    def add_commit(self, 
                   commit_id: str,
                   message: str,
                   timestamp: str,
                   affected_files: List[str],
                   author: Optional[str] = None) -> bool:
        """
        Add a commit node to temporal graph.
        
        Args:
            commit_id: Commit hash
            message: Commit message
            timestamp: Commit timestamp
            affected_files: List of affected file paths
            author: Author name
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_commit_neo4j(
                commit_id, message, timestamp, affected_files, author
            )
        else:
            # Mock storage
            commit = {
                'id': commit_id,
                'message': message,
                'timestamp': timestamp,
                'affected_files': affected_files,
                'author': author or 'unknown'
            }
            self.commits.append(commit)
            logger.debug(f"Added commit (mock): {commit_id}")
            return True
    
    def _add_commit_neo4j(self, 
                          commit_id: str,
                          message: str,
                          timestamp: str,
                          affected_files: List[str],
                          author: str) -> bool:
        """Add commit to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                # Create commit node
                session.run("""
                    MERGE (c:Commit {id: $id})
                    SET c.message = $message,
                        c.timestamp = $timestamp,
                        c.author = $author
                """, id=commit_id, message=message, 
                    timestamp=timestamp, author=author)
                
                # Create relationships to affected files
                for file_path in affected_files:
                    session.run("""
                        MERGE (f:File {name: $file_path})
                        MERGE (c:Commit {id: $commit_id})
                        MERGE (c)-[:AFFECTS]->(f)
                    """, file_path=file_path, commit_id=commit_id)
                
                logger.info(f"Added commit to Neo4j: {commit_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding commit to Neo4j: {e}")
            return False
    
    def get_commits_affecting_file(self, 
                                    file_path: str,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get commits affecting a specific file.
        
        Args:
            file_path: File path to query
            limit: Maximum number of results
            
        Returns:
            List of commit dictionaries
        """
        if self.enabled:
            return self._get_commits_neo4j(file_path, limit)
        else:
            # Mock query
            results = [
                c for c in self.commits
                if file_path in c.get('affected_files', [])
            ]
            return results[:limit]
    
    def _get_commits_neo4j(self, file_path: str, limit: int) -> List[Dict[str, Any]]:
        """Query commits from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (c:Commit)-[:AFFECTS]->(f:File {name: $file_path})
                    RETURN c.id AS id, 
                           c.message AS message,
                           c.timestamp AS timestamp,
                           c.author AS author
                    ORDER BY c.timestamp DESC
                    LIMIT $limit
                """, file_path=file_path, limit=limit)
                
                commits = [dict(record) for record in result]
                return commits
        except Exception as e:
            logger.error(f"Error querying Neo4j: {e}")
            return []
    
    def add_checkpoint(self,
                       checkpoint_id: str,
                       description: str,
                       timestamp: str,
                       commit_id: Optional[str] = None) -> bool:
        """
        Add a checkpoint node.
        
        Args:
            checkpoint_id: Checkpoint identifier
            description: Checkpoint description
            timestamp: Checkpoint timestamp
            commit_id: Related commit ID
            
        Returns:
            Success status
        """
        if self.enabled:
            return self._add_checkpoint_neo4j(
                checkpoint_id, description, timestamp, commit_id
            )
        else:
            checkpoint = {
                'id': checkpoint_id,
                'description': description,
                'timestamp': timestamp,
                'commit_id': commit_id
            }
            self.checkpoints.append(checkpoint)
            logger.debug(f"Added checkpoint (mock): {checkpoint_id}")
            return True
    
    def _add_checkpoint_neo4j(self,
                              checkpoint_id: str,
                              description: str,
                              timestamp: str,
                              commit_id: str) -> bool:
        """Add checkpoint to Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                session.run("""
                    MERGE (cp:Checkpoint {id: $id})
                    SET cp.description = $description,
                        cp.timestamp = $timestamp
                """, id=checkpoint_id, description=description, timestamp=timestamp)
                
                # Link to commit if provided
                if commit_id:
                    session.run("""
                        MATCH (cp:Checkpoint {id: $checkpoint_id})
                        MATCH (c:Commit {id: $commit_id})
                        MERGE (cp)-[:LINKED_TO]->(c)
                    """, checkpoint_id=checkpoint_id, commit_id=commit_id)
                
                logger.info(f"Added checkpoint to Neo4j: {checkpoint_id}")
                return True
        except Exception as e:
            logger.error(f"Error adding checkpoint to Neo4j: {e}")
            return False
    
    def get_timeline(self, 
                     start_time: Optional[str] = None,
                     end_time: Optional[str] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get timeline of commits and checkpoints.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            limit: Maximum results
            
        Returns:
            Timeline items
        """
        if self.enabled:
            return self._get_timeline_neo4j(start_time, end_time, limit)
        else:
            # Mock timeline
            timeline = self.commits + self.checkpoints
            timeline.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return timeline[:limit]
    
    def _get_timeline_neo4j(self, 
                            start_time: str,
                            end_time: str,
                            limit: int) -> List[Dict[str, Any]]:
        """Get timeline from Neo4j."""
        try:
            with self.driver.session(database=self.database) as session:
                query = """
                    MATCH (n)
                    WHERE (n:Commit OR n:Checkpoint)
                    RETURN n.id AS id,
                           labels(n)[0] AS type,
                           n.timestamp AS timestamp,
                           n.message AS message,
                           n.description AS description
                    ORDER BY n.timestamp DESC
                    LIMIT $limit
                """
                result = session.run(query, limit=limit)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error querying timeline: {e}")
            return []
    
    def clear(self) -> None:
        """Clear all temporal data."""
        if self.enabled:
            try:
                with self.driver.session(database=self.database) as session:
                    session.run("MATCH (n) WHERE n:Commit OR n:Checkpoint DETACH DELETE n")
                logger.info("Cleared temporal graph in Neo4j")
            except Exception as e:
                logger.error(f"Error clearing Neo4j: {e}")
        else:
            self.commits = []
            self.checkpoints = []
