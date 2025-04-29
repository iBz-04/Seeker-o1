"""
Base Memory module that defines the common interface for memory systems.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class BaseMemory(ABC):
    """
    Abstract base class for memory systems in the ANUS framework.
    
    Provides the core functionality and interface that all memory types must implement.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a BaseMemory instance.
        
        Args:
            **kwargs: Additional configuration options for the memory system.
        """
        self.config = kwargs
    
    @abstractmethod
    def add(self, item: Dict[str, Any]) -> str:
        """
        Add an item to memory and return its identifier.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            A string identifier for the added item.
        """
        pass
    
    @abstractmethod
    def get(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from memory by its identifier.
        
        Args:
            identifier: The identifier of the item to retrieve.
            
        Returns:
            The retrieved item, or None if not found.
        """
        pass
    
    @abstractmethod
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memory for items matching the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of matching items.
        """
        pass
    
    @abstractmethod
    def update(self, identifier: str, item: Dict[str, Any]) -> bool:
        """
        Update an item in memory.
        
        Args:
            identifier: The identifier of the item to update.
            item: The updated item.
            
        Returns:
            True if the update was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """
        Delete an item from memory.
        
        Args:
            identifier: The identifier of the item to delete.
            
        Returns:
            True if the deletion was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all items from memory.
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            A dictionary containing memory statistics.
        """
        pass 