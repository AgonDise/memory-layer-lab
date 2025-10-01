#!/usr/bin/env python3
"""
Environment Variable Loader

Loads configuration from .env file.
"""

import os
from pathlib import Path
from typing import Optional


def load_env_file(env_path: Optional[str] = None) -> dict:
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file (default: .env in project root)
        
    Returns:
        Dictionary of environment variables
    """
    if env_path is None:
        # Try to find .env in project root
        current = Path(__file__).parent.parent
        env_path = current / ".env"
    else:
        env_path = Path(env_path)
    
    env_vars = {}
    
    if not env_path.exists():
        print(f"⚠️  .env file not found at {env_path}")
        print(f"   Copy .env.example to .env and fill in your credentials")
        return env_vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                env_vars[key] = value
                # Also set in os.environ
                os.environ[key] = value
    
    return env_vars


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get environment variable with fallback to default.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(key, default)


def require_env(key: str) -> str:
    """
    Get required environment variable, raise error if not found.
    
    Args:
        key: Environment variable name
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If environment variable not found
    """
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' not found. "
                        f"Please set it in .env file.")
    return value


class EnvConfig:
    """Environment configuration with validation."""
    
    def __init__(self, env_path: Optional[str] = None):
        """Load and validate environment configuration."""
        self.env_vars = load_env_file(env_path)
        self._validate()
    
    def _validate(self):
        """Validate required environment variables."""
        # Check Neo4j config
        if self.neo4j_uri and self.neo4j_user:
            if not self.neo4j_password:
                print("⚠️  Warning: NEO4J_PASSWORD not set")
        
        # Check OpenAI config
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not set")
    
    # Neo4j properties
    @property
    def neo4j_uri(self) -> Optional[str]:
        return get_env('NEO4J_URI')
    
    @property
    def neo4j_user(self) -> Optional[str]:
        return get_env('NEO4J_USER')
    
    @property
    def neo4j_password(self) -> Optional[str]:
        return get_env('NEO4J_PASSWORD')
    
    @property
    def neo4j_database(self) -> str:
        return get_env('NEO4J_DATABASE', 'neo4j')
    
    @property
    def neo4j_timeout(self) -> int:
        return int(get_env('NEO4J_TIMEOUT', '120'))
    
    # OpenAI properties
    @property
    def openai_api_key(self) -> Optional[str]:
        return get_env('OPENAI_API_KEY')
    
    @property
    def model_name(self) -> str:
        return get_env('MODEL_NAME', 'gpt-4-turbo-preview')
    
    @property
    def openai_api_base(self) -> str:
        return get_env('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary (without sensitive data)."""
        return {
            'neo4j_uri': self.neo4j_uri,
            'neo4j_user': self.neo4j_user,
            'neo4j_database': self.neo4j_database,
            'neo4j_timeout': self.neo4j_timeout,
            'model_name': self.model_name,
            'openai_api_base': self.openai_api_base,
        }


# Global config instance
_config = None


def get_config() -> EnvConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = EnvConfig()
    return _config


def main():
    """Test environment loading."""
    print("Loading environment configuration...")
    config = EnvConfig()
    
    print("\n✅ Configuration loaded:")
    print(f"  Neo4j URI: {config.neo4j_uri}")
    print(f"  Neo4j User: {config.neo4j_user}")
    print(f"  Neo4j DB: {config.neo4j_database}")
    print(f"  Neo4j Timeout: {config.neo4j_timeout}s")
    print(f"  Model: {config.model_name}")
    print(f"  OpenAI API: {'✅ Set' if config.openai_api_key else '❌ Not set'}")


if __name__ == "__main__":
    main()
