"""
Configuration Manager for Memory Layer Lab.

Provides centralized configuration management with:
- Hot reload capability
- Config validation
- Easy access to settings
- Runtime updates
"""

import yaml
import os
from typing import Any, Dict, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Centralized configuration manager.
    """
    
    def __init__(self, config_file: str = "config/system_config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to config file
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"Config file not found: {self.config_file}")
                logger.info("Using default configuration")
                self._load_defaults()
                return
            
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            
            logger.info(f"✅ Loaded config from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            logger.info("Using default configuration")
            self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration."""
        self.config = {
            'short_term_memory': {
                'max_items': 10,
                'retention_time': 300,
                'auto_compress': True
            },
            'mid_term_memory': {
                'max_chunks': 100,
                'chunk_size': 5,
                'retention_time': 3600,
                'auto_archive': True,
                'importance_threshold': 0.5
            },
            'compression': {
                'enabled': True,
                'strategy': 'score_based',
                'max_tokens': 1000,
                'preserve_recent': 3,
                'preserve_important': True,
                'importance_weight': 0.4,
                'recency_weight': 0.3,
                'relevance_weight': 0.3
            },
            'semantic_search': {
                'enabled': True,
                'use_real_embeddings': True,
                'embedding_dim': 384,
                'similarity_threshold': 0.6,
                'top_k_stm': 5,
                'top_k_mtm': 3,
                'top_k_ltm': 5
            },
            'aggregation': {
                'weights': {
                    'stm': 0.5,
                    'mtm': 0.3,
                    'ltm': 0.2
                },
                'max_total_items': 50,
                'max_total_tokens': 2000
            },
            'response_generation': {
                'model': 'gpt-4o-mini',
                'temperature': 0.7,
                'max_tokens': 500
            },
            'langfuse': {
                'enabled': False
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path (e.g., "compression.max_tokens")
            default: Default value if key not found
            
        Returns:
            Configuration value
            
        Example:
            >>> config = ConfigManager()
            >>> config.get("compression.max_tokens")
            1000
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any, save: bool = False):
        """
        Set configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path
            value: Value to set
            save: Save to file immediately
            
        Example:
            >>> config.set("compression.max_tokens", 2000)
            >>> config.set("compression.strategy", "mmr", save=True)
        """
        keys = key_path.split('.')
        current = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set value
        current[keys[-1]] = value
        
        if save:
            self.save()
        
        logger.debug(f"Set {key_path} = {value}")
    
    def update(self, updates: Dict[str, Any], save: bool = False):
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of key_path: value pairs
            save: Save to file immediately
            
        Example:
            >>> config.update({
            ...     "compression.max_tokens": 2000,
            ...     "compression.strategy": "mmr"
            ... }, save=True)
        """
        for key_path, value in updates.items():
            self.set(key_path, value, save=False)
        
        if save:
            self.save()
    
    def save(self, file_path: Optional[str] = None):
        """
        Save configuration to file.
        
        Args:
            file_path: Optional custom file path
        """
        save_path = file_path or self.config_file
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"✅ Saved config to {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        self._load_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., "compression")
            
        Returns:
            Section configuration dictionary
        """
        return self.config.get(section, {})
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate compression weights sum to ~1.0
        agg_weights = self.get("aggregation.weights", {})
        if agg_weights:
            total = sum(agg_weights.values())
            if abs(total - 1.0) > 0.01:
                errors.append(f"Aggregation weights sum to {total}, should be 1.0")
        
        # Validate numeric ranges
        if self.get("response_generation.temperature", 0) < 0:
            errors.append("Temperature must be >= 0")
        
        if self.get("semantic_search.similarity_threshold", 0) < 0 or \
           self.get("semantic_search.similarity_threshold", 0) > 1:
            errors.append("Similarity threshold must be between 0 and 1")
        
        # Validate Langfuse config if enabled
        if self.get("langfuse.enabled", False):
            if not self.get("langfuse.public_key"):
                errors.append("Langfuse enabled but public_key not set")
            if not self.get("langfuse.secret_key"):
                errors.append("Langfuse enabled but secret_key not set")
        
        # Validate Neo4j config if enabled
        if self.get("neo4j.enabled", False):
            if not self.get("neo4j.uri"):
                errors.append("Neo4j enabled but uri not set")
            if not self.get("neo4j.password"):
                errors.append("Neo4j enabled but password not set")
        
        return errors
    
    def print_config(self, section: Optional[str] = None):
        """
        Print configuration in readable format.
        
        Args:
            section: Optional section to print (prints all if None)
        """
        if section:
            config_to_print = {section: self.get_section(section)}
        else:
            config_to_print = self.config
        
        print("="*80)
        print("CONFIGURATION")
        print("="*80)
        print(yaml.dump(config_to_print, default_flow_style=False, indent=2))
        print("="*80)
    
    def export_template(self, file_path: str):
        """
        Export current config as template.
        
        Args:
            file_path: Output file path
        """
        try:
            with open(file_path, 'w') as f:
                f.write("# Memory Layer Lab Configuration Template\n")
                f.write("# Generated from current settings\n\n")
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"✅ Exported template to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
    
    def reset_section(self, section: str):
        """
        Reset a section to defaults.
        
        Args:
            section: Section name to reset
        """
        defaults = ConfigManager()  # Load defaults
        if section in defaults.config:
            self.config[section] = defaults.config[section]
            logger.info(f"Reset section: {section}")
        else:
            logger.warning(f"Unknown section: {section}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self.config.copy()
    
    def __repr__(self):
        sections = list(self.config.keys())
        return f"ConfigManager(sections={sections}, file='{self.config_file}')"


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get global configuration manager instance.
    
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config():
    """Reload global configuration."""
    global _config_manager
    if _config_manager:
        _config_manager.reload()
    else:
        _config_manager = ConfigManager()


# Convenience functions
def get_value(key_path: str, default: Any = None) -> Any:
    """Get config value (convenience function)."""
    return get_config().get(key_path, default)


def set_value(key_path: str, value: Any, save: bool = False):
    """Set config value (convenience function)."""
    get_config().set(key_path, value, save)


def get_section(section: str) -> Dict[str, Any]:
    """Get config section (convenience function)."""
    return get_config().get_section(section)
