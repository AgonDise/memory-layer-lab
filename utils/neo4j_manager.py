"""
Neo4j Connection Manager with connection pooling and retry logic.
"""

from typing import Optional, Dict, Any, List
import time
import logging
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError, SessionExpired
from utils.env_loader import get_config

logger = logging.getLogger(__name__)


class Neo4jManager:
    """
    Manages Neo4j database connections with pooling and retry logic.
    """
    
    def __init__(self, 
                 uri: str,
                 username: str,
                 password: str,
                 database: str = "neo4j",
                 max_connection_lifetime: int = 3600,
                 max_connection_pool_size: int = 50,
                 connection_acquisition_timeout: int = 60,
                 encrypted: bool = False,
                 max_retry_time: int = 30,
                 initial_retry_delay: float = 1.0):
        """
        Initialize Neo4j connection manager.
        
        Args:
            uri: Neo4j URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password
            database: Database name
            max_connection_lifetime: Max connection lifetime in seconds
            max_connection_pool_size: Max connections in pool
            connection_acquisition_timeout: Timeout for acquiring connection
            encrypted: Use encrypted connection
            max_retry_time: Max time to retry failed operations
            initial_retry_delay: Initial delay between retries
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.max_retry_time = max_retry_time
        self.initial_retry_delay = initial_retry_delay
        
        # Connection configuration
        self.config = {
            "max_connection_lifetime": max_connection_lifetime,
            "max_connection_pool_size": max_connection_pool_size,
            "connection_acquisition_timeout": connection_acquisition_timeout,
            "encrypted": encrypted,
        }
        
        self.driver: Optional[Driver] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Connecting to Neo4j at {self.uri}...")
            
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                **self.config
            )
            
            # Test connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS test")
                result.single()
            
            self._connected = True
            logger.info("✅ Successfully connected to Neo4j")
            return True
            
        except AuthError as e:
            logger.error(f"❌ Authentication failed: {e}")
            self._connected = False
            return False
        except ServiceUnavailable as e:
            logger.error(f"❌ Neo4j service unavailable: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Close Neo4j connection."""
        if self.driver:
            try:
                self.driver.close()
                self._connected = False
                logger.info("Disconnected from Neo4j")
            except Exception as e:
                logger.error(f"Error disconnecting from Neo4j: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to Neo4j."""
        if not self.driver or not self._connected:
            return False
        
        try:
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1").single()
            return True
        except:
            self._connected = False
            return False
    
    def get_session(self) -> Optional[Session]:
        """
        Get a new Neo4j session.
        
        Returns:
            Neo4j session or None if not connected
        """
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            return self.driver.session(database=self.database)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    def execute_query(self, 
                     query: str, 
                     parameters: Optional[Dict[str, Any]] = None,
                     retry: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a Cypher query with retry logic.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            retry: Enable retry on failure
            
        Returns:
            List of result records or None on failure
        """
        parameters = parameters or {}
        
        retry_delay = self.initial_retry_delay
        start_time = time.time()
        
        while True:
            try:
                session = self.get_session()
                if not session:
                    if not retry:
                        return None
                    raise ServiceUnavailable("Could not get session")
                
                with session:
                    result = session.run(query, parameters)
                    records = [dict(record) for record in result]
                    return records
                    
            except (ServiceUnavailable, SessionExpired) as e:
                if not retry:
                    logger.error(f"Query failed: {e}")
                    return None
                
                elapsed = time.time() - start_time
                if elapsed >= self.max_retry_time:
                    logger.error(f"Query failed after {elapsed:.1f}s: {e}")
                    return None
                
                logger.warning(f"Query failed, retrying in {retry_delay:.1f}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                
                # Try to reconnect
                self.disconnect()
                self.connect()
                
            except Exception as e:
                logger.error(f"Query failed: {e}")
                return None
    
    def execute_write(self,
                     query: str,
                     parameters: Optional[Dict[str, Any]] = None,
                     retry: bool = True) -> bool:
        """
        Execute a write query (CREATE, UPDATE, DELETE).
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            retry: Enable retry on failure
            
        Returns:
            True if successful, False otherwise
        """
        result = self.execute_query(query, parameters, retry)
        return result is not None
    
    def batch_execute(self,
                     queries: List[str],
                     parameters_list: Optional[List[Dict[str, Any]]] = None,
                     batch_size: int = 100) -> int:
        """
        Execute multiple queries in batches.
        
        Args:
            queries: List of Cypher queries
            parameters_list: List of parameters for each query
            batch_size: Number of queries per batch
            
        Returns:
            Number of successfully executed queries
        """
        if not parameters_list:
            parameters_list = [{}] * len(queries)
        
        if len(queries) != len(parameters_list):
            logger.error("Queries and parameters lists must have same length")
            return 0
        
        success_count = 0
        total = len(queries)
        
        for i in range(0, total, batch_size):
            batch_queries = queries[i:i+batch_size]
            batch_params = parameters_list[i:i+batch_size]
            
            logger.info(f"Executing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            for query, params in zip(batch_queries, batch_params):
                if self.execute_write(query, params):
                    success_count += 1
        
        logger.info(f"Executed {success_count}/{total} queries successfully")
        return success_count
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Neo4j connection.
        
        Returns:
            Dictionary with health status
        """
        health = {
            "connected": False,
            "uri": self.uri,
            "database": self.database,
            "version": None,
            "error": None
        }
        
        try:
            if not self.is_connected():
                health["error"] = "Not connected"
                return health
            
            # Get version
            result = self.execute_query("CALL dbms.components() YIELD name, versions, edition")
            if result:
                for record in result:
                    if record.get('name') == 'Neo4j Kernel':
                        health["version"] = record.get('versions', [None])[0]
                        health["edition"] = record.get('edition')
            
            # Check database access
            result = self.execute_query(f"MATCH (n) RETURN count(n) as count LIMIT 1")
            if result is not None:
                health["connected"] = True
                health["node_count"] = result[0].get('count', 0) if result else 0
            
        except Exception as e:
            health["error"] = str(e)
            logger.error(f"Health check failed: {e}")
        
        return health
    
    def create_indexes(self, index_definitions: List[Dict[str, Any]]) -> int:
        """
        Create indexes for performance optimization.
        
        Args:
            index_definitions: List of index definitions
                Example: [
                    {"label": "Fact", "property": "embedding", "type": "vector"},
                    {"label": "Message", "property": "timestamp", "type": "btree"}
                ]
        
        Returns:
            Number of indexes created
        """
        created = 0
        
        for idx_def in index_definitions:
            label = idx_def.get('label')
            prop = idx_def.get('property')
            idx_type = idx_def.get('type', 'btree')
            
            if not label or not prop:
                logger.warning(f"Invalid index definition: {idx_def}")
                continue
            
            try:
                index_name = f"idx_{label.lower()}_{prop.lower()}"
                
                if idx_type == 'vector':
                    # Vector index for embeddings
                    query = f"""
                    CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                    FOR (n:{label})
                    ON n.{prop}
                    OPTIONS {{
                        indexConfig: {{
                            `vector.dimensions`: 384,
                            `vector.similarity_function`: 'cosine'
                        }}
                    }}
                    """
                else:
                    # Regular index
                    query = f"""
                    CREATE INDEX {index_name} IF NOT EXISTS
                    FOR (n:{label})
                    ON (n.{prop})
                    """
                
                if self.execute_write(query, retry=False):
                    logger.info(f"✅ Created index: {index_name}")
                    created += 1
                    
            except Exception as e:
                logger.error(f"Failed to create index for {label}.{prop}: {e}")
        
        return created
    
    def __enter__(self):
        """Context manager entry."""
        if not self.is_connected():
            self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def __repr__(self):
        status = "connected" if self._connected else "disconnected"
        return f"Neo4jManager(uri='{self.uri}', database='{self.database}', status='{status}')"


def create_neo4j_manager_from_env() -> Neo4jManager:
    """
    Create Neo4jManager from environment variables.
    
    Returns:
        Configured Neo4jManager instance
        
    Raises:
        ValueError: If required environment variables not set
    """
    config = get_config()
    
    if not config.neo4j_uri:
        raise ValueError("NEO4J_URI not set in environment")
    if not config.neo4j_user:
        raise ValueError("NEO4J_USER not set in environment")
    if not config.neo4j_password:
        raise ValueError("NEO4J_PASSWORD not set in environment")
    
    return Neo4jManager(
        uri=config.neo4j_uri,
        username=config.neo4j_user,
        password=config.neo4j_password,
        database=config.neo4j_database,
        max_connection_lifetime=int(get_config().env_vars.get('NEO4J_MAX_CONNECTION_LIFETIME', 3600)),
        connection_acquisition_timeout=config.neo4j_timeout
    )
