import os
from typing import Dict, Any

# Memory Configuration
MEMORY_CONFIG = {
    'short_term': {
        'max_size': 10,  # Number of recent messages to keep in short-term memory
        'ttl': 3600,     # Time-to-live in seconds (1 hour)
    },
    'mid_term': {
        'max_size': 100,  # Number of summarized chunks to keep
        'summarize_every': 5,  # Summarize after this many messages
    },
    'long_term': {
        'enabled': False,  # Placeholder for future implementation
    }
}

# LLM Configuration
LLM_CONFIG = {
    'provider': 'openai',
    'openai': {
        'api_key': os.getenv('OPENAI_API_KEY', ''),  # Get from environment
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7,
    },
    'anthropic': {
        'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'model': 'claude-2',
    },
    'mock': {
        'enabled': False,
    }
}

# Database Configuration
DATABASE_CONFIG = {
    'type': 'sqlite',  # Options: 'sqlite', 'postgres', 'mysql'
    'name': 'memory_db.sqlite',
    'host': 'localhost',
    'port': 5432,
    'user': '',
    'password': '',
}

# Neo4j Configuration (for MTM and LTM)
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'test123',
    'databases': {
        'temporal': 'temporal_kg',  # MTM: commit timeline
        'knowledge': 'longterm_kg',  # LTM: knowledge graph
    },
    'enabled': False,  # Set to True when Neo4j is running
}

# Vector Database Configuration (for LTM semantic search)
VECTOR_DB_CONFIG = {
    'backend': 'simple',  # simple | faiss | chromadb | qdrant | weaviate
    'embedding_dim': 384,
    'index_path': 'vector_index',
    'enabled': False,  # Set to True to enable
}

# LLM Configuration
LLM_CONFIG = {
    'provider': 'openai',  # openai | anthropic | mock
    'openai': {
        'api_key': None,  # Set to your API key or use OPENAI_API_KEY env var
        'model': 'gpt-3.5-turbo',  # gpt-3.5-turbo | gpt-4 | gpt-4-turbo
        'max_tokens': 500,
        'temperature': 0.7,
    },
    'anthropic': {
        'api_key': None,  # Set to your API key or use ANTHROPIC_API_KEY env var
        'model': 'claude-3-sonnet-20240229',  # claude-3-opus | claude-3-sonnet | claude-3-haiku
        'max_tokens': 500,
        'temperature': 0.7,
    },
    'system_prompt': """You are a helpful AI assistant with access to conversation memory.
Use the provided context to give accurate and relevant responses.
If the context doesn't contain relevant information, say so politely.""",
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file': 'memory_layer.log',
}

def get_config() -> Dict[str, Any]:
    """Return the complete configuration."""
    return {
        'memory': MEMORY_CONFIG,
        'llm': LLM_CONFIG,
        'database': DATABASE_CONFIG,
        'neo4j': NEO4J_CONFIG,
        'vector_db': VECTOR_DB_CONFIG,
        'logging': LOGGING_CONFIG,
    }
