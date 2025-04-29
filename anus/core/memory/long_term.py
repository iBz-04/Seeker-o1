"""
Long-term memory module for the ANUS framework.
"""

from typing import Dict, List, Any, Optional, Union
import uuid
import time
import json
import os
import logging
from pathlib import Path

from anus.core.memory.base_memory import BaseMemory

class LongTermMemory(BaseMemory):
    """
    Persistent implementation of the BaseMemory interface.
    
    Provides a file-based persistent memory store.
    """
    
    def __init__(
        self, 
        storage_path: Optional[str] = None,
        index_in_memory: bool = True,
        **kwargs
    ):
        """
        Initialize a LongTermMemory instance.
        
        Args:
            storage_path: Path to store memory files. If None, uses a default location.
            index_in_memory: Whether to keep an in-memory index for faster searches.
            **kwargs: Additional configuration options.
        """
        super().__init__(**kwargs)
        
        # Set storage path
        if storage_path is None:
            home_dir = os.path.expanduser("~")
            storage_path = os.path.join(home_dir, ".anus", "memory")
        
        self.storage_path = storage_path
        self.index_in_memory = index_in_memory
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Create indexes
        self.index: Dict[str, Dict[str, Any]] = {}
        
        # Load index from disk if using in-memory indexing
        if self.index_in_memory:
            self._load_index()
    
    def add(self, item: Dict[str, Any]) -> str:
        """
        Add an item to memory and return its identifier.
        
        Args:
            item: The item to add to memory.
            
        Returns:
            A string identifier for the added item.
        """
        # Generate a unique identifier
        identifier = str(uuid.uuid4())
        
        # Add metadata
        item_with_metadata = item.copy()
        item_with_metadata["_meta"] = {
            "id": identifier,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Save the item to disk
        self._save_item(identifier, item_with_metadata)
        
        # Update the index
        if self.index_in_memory:
            self.index[identifier] = item_with_metadata
        
        return identifier
    
    def get(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from memory by its identifier.
        
        Args:
            identifier: The identifier of the item to retrieve.
            
        Returns:
            The retrieved item, or None if not found.
        """
        # Check in-memory index first if available
        if self.index_in_memory and identifier in self.index:
            return self.index[identifier]
        
        # Otherwise, load from disk
        item_path = self._get_item_path(identifier)
        if not os.path.exists(item_path):
            return None
        
        try:
            with open(item_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading item {identifier}: {e}")
            return None
    
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memory for items matching the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of matching items.
        """
        results = []
        
        # If using in-memory index, search there
        if self.index_in_memory:
            for identifier, item in self.index.items():
                if self._matches_query(item, query):
                    results.append({
                        "id": identifier,
                        "item": item,
                        "created_at": item.get("_meta", {}).get("created_at", 0)
                    })
                    
                    if len(results) >= limit:
                        break
        else:
            # Otherwise, scan the storage directory
            for item_file in os.listdir(self.storage_path):
                if not item_file.endswith(".json"):
                    continue
                
                identifier = item_file[:-5]  # Remove .json extension
                item = self.get(identifier)
                
                if item and self._matches_query(item, query):
                    results.append({
                        "id": identifier,
                        "item": item,
                        "created_at": item.get("_meta", {}).get("created_at", 0)
                    })
                    
                    if len(results) >= limit:
                        break
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x["created_at"], reverse=True)
        
        return results
    
    def update(self, identifier: str, item: Dict[str, Any]) -> bool:
        """
        Update an item in memory.
        
        Args:
            identifier: The identifier of the item to update.
            item: The updated item.
            
        Returns:
            True if the update was successful, False otherwise.
        """
        # Check if the item exists
        existing_item = self.get(identifier)
        if existing_item is None:
            return False
        
        # Preserve metadata
        item_with_metadata = item.copy()
        if "_meta" in existing_item:
            item_with_metadata["_meta"] = existing_item["_meta"]
            item_with_metadata["_meta"]["updated_at"] = time.time()
        else:
            item_with_metadata["_meta"] = {
                "id": identifier,
                "created_at": time.time(),
                "updated_at": time.time()
            }
        
        # Save the updated item
        self._save_item(identifier, item_with_metadata)
        
        # Update the index
        if self.index_in_memory:
            self.index[identifier] = item_with_metadata
        
        return True
    
    def delete(self, identifier: str) -> bool:
        """
        Delete an item from memory.
        
        Args:
            identifier: The identifier of the item to delete.
            
        Returns:
            True if the deletion was successful, False otherwise.
        """
        item_path = self._get_item_path(identifier)
        if not os.path.exists(item_path):
            return False
        
        try:
            os.remove(item_path)
            
            # Update the index
            if self.index_in_memory and identifier in self.index:
                del self.index[identifier]
            
            return True
        except Exception as e:
            logging.error(f"Error deleting item {identifier}: {e}")
            return False
    
    def clear(self) -> None:
        """
        Clear all items from memory.
        """
        for item_file in os.listdir(self.storage_path):
            if not item_file.endswith(".json"):
                continue
            
            try:
                os.remove(os.path.join(self.storage_path, item_file))
            except Exception as e:
                logging.error(f"Error deleting file {item_file}: {e}")
        
        # Clear the index
        if self.index_in_memory:
            self.index = {}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            A dictionary containing memory statistics.
        """
        # Count the number of items
        if self.index_in_memory:
            item_count = len(self.index)
        else:
            item_count = len([f for f in os.listdir(self.storage_path) if f.endswith(".json")])
        
        # Get the total size of all items
        total_size = sum(
            os.path.getsize(os.path.join(self.storage_path, f)) 
            for f in os.listdir(self.storage_path) 
            if os.path.isfile(os.path.join(self.storage_path, f)) and f.endswith(".json")
        )
        
        return {
            "type": "long_term",
            "storage_path": self.storage_path,
            "index_in_memory": self.index_in_memory,
            "item_count": item_count,
            "total_size_bytes": total_size
        }
    
    def _get_item_path(self, identifier: str) -> str:
        """
        Get the file path for an item.
        
        Args:
            identifier: The identifier of the item.
            
        Returns:
            The file path for the item.
        """
        return os.path.join(self.storage_path, f"{identifier}.json")
    
    def _save_item(self, identifier: str, item: Dict[str, Any]) -> None:
        """
        Save an item to disk.
        
        Args:
            identifier: The identifier of the item.
            item: The item to save.
        """
        item_path = self._get_item_path(identifier)
        
        try:
            with open(item_path, "w") as f:
                json.dump(item, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving item {identifier}: {e}")
    
    def _load_index(self) -> None:
        """
        Load the index from disk.
        """
        self.index = {}
        
        for item_file in os.listdir(self.storage_path):
            if not item_file.endswith(".json"):
                continue
            
            identifier = item_file[:-5]  # Remove .json extension
            
            try:
                with open(os.path.join(self.storage_path, item_file), "r") as f:
                    item = json.load(f)
                    self.index[identifier] = item
            except Exception as e:
                logging.error(f"Error loading index for {identifier}: {e}")
    
    def _matches_query(self, item: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        Check if an item matches a query.
        
        Args:
            item: The item to check.
            query: The query to match against.
            
        Returns:
            True if the item matches the query, False otherwise.
        """
        for key, value in query.items():
            # Handle nested keys with dot notation
            if "." in key:
                parts = key.split(".")
                curr = item
                for part in parts:
                    if isinstance(curr, dict) and part in curr:
                        curr = curr[part]
                    else:
                        return False
                
                if curr != value:
                    return False
            # Handle simple keys
            elif key not in item or item[key] != value:
                return False
        
        return True 