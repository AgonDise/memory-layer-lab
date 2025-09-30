import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MemoryStorage:
    """
    Handles persistent storage of memory state to file or database.
    """
    
    def __init__(self, storage_type: str = 'file', storage_path: str = 'memory_state.json'):
        """
        Initialize memory storage.
        
        Args:
            storage_type: Type of storage ('file', 'sqlite', 'postgres')
            storage_path: Path to storage location
        """
        self.storage_type = storage_type
        self.storage_path = storage_path
        
        if storage_type == 'file':
            # Ensure directory exists
            Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, memory_state: Dict[str, Any]) -> bool:
        """
        Save memory state to storage.
        
        Args:
            memory_state: Dictionary containing memory state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.storage_type == 'file':
                return self._save_to_file(memory_state)
            elif self.storage_type == 'sqlite':
                return self._save_to_sqlite(memory_state)
            else:
                logger.warning(f"Storage type '{self.storage_type}' not implemented")
                return False
        except Exception as e:
            logger.error(f"Error saving memory state: {e}")
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load memory state from storage.
        
        Returns:
            Dictionary containing memory state, or None if not found
        """
        try:
            if self.storage_type == 'file':
                return self._load_from_file()
            elif self.storage_type == 'sqlite':
                return self._load_from_sqlite()
            else:
                logger.warning(f"Storage type '{self.storage_type}' not implemented")
                return None
        except Exception as e:
            logger.error(f"Error loading memory state: {e}")
            return None
    
    def _save_to_file(self, memory_state: Dict[str, Any]) -> bool:
        """Save memory state to JSON file."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(memory_state, f, indent=2, ensure_ascii=False)
        logger.info(f"Memory state saved to {self.storage_path}")
        return True
    
    def _load_from_file(self) -> Optional[Dict[str, Any]]:
        """Load memory state from JSON file."""
        if not os.path.exists(self.storage_path):
            logger.info(f"No existing memory state found at {self.storage_path}")
            return None
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            memory_state = json.load(f)
        
        logger.info(f"Memory state loaded from {self.storage_path}")
        return memory_state
    
    def _save_to_sqlite(self, memory_state: Dict[str, Any]) -> bool:
        """Save memory state to SQLite database."""
        # TODO: Implement SQLite storage
        logger.warning("SQLite storage not implemented yet")
        return False
    
    def _load_from_sqlite(self) -> Optional[Dict[str, Any]]:
        """Load memory state from SQLite database."""
        # TODO: Implement SQLite loading
        logger.warning("SQLite storage not implemented yet")
        return None
    
    def exists(self) -> bool:
        """Check if storage location exists."""
        if self.storage_type == 'file':
            return os.path.exists(self.storage_path)
        return False
    
    def delete(self) -> bool:
        """Delete the storage."""
        try:
            if self.storage_type == 'file' and os.path.exists(self.storage_path):
                os.remove(self.storage_path)
                logger.info(f"Deleted storage at {self.storage_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting storage: {e}")
            return False
