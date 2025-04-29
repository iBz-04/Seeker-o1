"""
Short-term memory module for the Seeker O1 framework.

Because even an O1 needs to remember what it just processed.
"""

from typing import Dict, List, Any, Optional, Union
import uuid
import time
import heapq
import logging
import random
from collections import deque

from seeker_o1.core.memory.base_memory import BaseMemory

logger = logging.getLogger(__name__)

class ShortTermMemory(BaseMemory):
    """
    In-memory implementation of the BaseMemory interface.
    
    Provides a volatile memory store with automatic pruning of old items.
    
    Just like the human O1, it's good at handling recent input but tends to 
    forget older stuff if not regularly refreshed.
    """
    
    # Funny memory-related messages
    _memory_messages = [
        "Seeker O1 short-term memory retaining item...",
        "Storing this for quick retrieval from your Seeker O1...",
        "This item is now tightly held in Seeker O1 memory...",
        "Squeezing this into Seeker O1 short-term storage...",
        "Seeker O1 will remember this, at least for a little while..."
    ]
    
    def __init__(
        self, 
        capacity: int = 1000, 
        ttl: int = 3600,  # Time to live in seconds
        **kwargs
    ):
        """
        Initialize a ShortTermMemory instance.
        
        Args:
            capacity: Maximum number of items to store.
            ttl: Time to live for items in seconds.
            **kwargs: Additional configuration options.
        """
        super().__init__(**kwargs)
        self.capacity = capacity
        self.ttl = ttl
        self.items: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.creation_times: Dict[str, float] = {}
        self.lru_queue: List[tuple] = []  # Priority queue for LRU eviction
        
        if capacity < 100:
            logger.warning(f"Seeker O1 short-term memory capacity of {capacity} is quite small. Performance may suffer.")
        elif capacity > 10000:
            logger.warning(f"Seeker O1 short-term memory capacity of {capacity} is unusually large. Hope you have enough RAM!")
        
        logger.info(f"Seeker O1 short-term memory initialized with capacity for {capacity} items and {ttl}s retention")
    
    def add(self, item: Any):
        """Add an item to the memory, potentially displacing the oldest if full."""
        if len(self.memory) >= self.capacity:
            removed_item = self.memory.popleft()
            logger.debug(f"Short-term memory full. Discarded oldest item: {removed_item}")
        
        self.memory.append(item)
        logger.debug(f"Added to short-term memory: {item}")
    
    def get_all(self) -> List[Any]:
        """
        Retrieve all items from memory.
        
        Returns:
            A list of all items in memory.
        """
        return list(self.memory)
    
    def get(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item from memory by its identifier.
        
        Updates the access time of the item to prevent it from being evicted.
        
        Args:
            identifier: The identifier of the item to retrieve.
            
        Returns:
            The retrieved item, or None if not found.
        """
        # Prune expired items
        self._prune_expired()
        
        # Check if the item exists
        if identifier not in self.items:
            logger.debug(f"Seeker O1 has no recollection of item {identifier[:8]}...")
            return None
        
        # Update access time
        self.access_times[identifier] = time.time()
        
        # Return the item
        logger.debug(f"Seeker O1 recalls this item perfectly!")
        return self.items[identifier]
    
    def search(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memory for items matching the query.
        
        Simple implementation that checks for exact matches on query fields.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of matching items.
        """
        # Prune expired items
        self._prune_expired()
        
        logger.debug(f"Seeker O1 is probing deeply for matching items...")
        
        results = []
        
        for identifier, item in self.items.items():
            # Check if all query fields match
            is_match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    is_match = False
                    break
            
            if is_match:
                # Update access time
                self.access_times[identifier] = time.time()
                
                # Add to results
                results.append({
                    "id": identifier,
                    "item": item,
                    "created_at": self.creation_times[identifier]
                })
                
                # Check limit
                if len(results) >= limit:
                    break
        
        # Sort by recency
        results.sort(key=lambda x: x["created_at"], reverse=True)
        
        if not results:
            logger.debug("Seeker O1 found nothing that matches. How disappointing.")
        else:
            logger.debug(f"Seeker O1 successfully extracted {len(results)} matching items!")
        
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
        # Prune expired items
        self._prune_expired()
        
        # Check if the item exists
        if identifier not in self.items:
            logger.debug(f"Seeker O1 can't update what it doesn't have (identifier: {identifier[:8]})")
            return False
        
        # Update the item
        self.items[identifier] = item
        
        # Update access time
        self.access_times[identifier] = time.time()
        
        logger.debug(f"Seeker O1 memory successfully updated with fresh content")
        return True
    
    def delete(self, identifier: str) -> bool:
        """
        Delete an item from memory.
        
        Args:
            identifier: The identifier of the item to delete.
            
        Returns:
            True if the deletion was successful, False otherwise.
        """
        # Check if the item exists
        if identifier not in self.items:
            return False
        
        # Delete the item
        del self.items[identifier]
        del self.access_times[identifier]
        del self.creation_times[identifier]
        
        # Note: The item will remain in the LRU queue, but will be skipped when it's popped
        
        logger.debug(f"Seeker O1 has purged this item from its memory")
        return True
    
    def clear(self) -> None:
        """
        Clear all items from memory.
        """
        old_count = len(self.items)
        self.items = {}
        self.access_times = {}
        self.creation_times = {}
        self.lru_queue = []
        
        logger.info(f"Seeker O1 memory has been completely flushed of {old_count} items. Fresh and clean!")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            A dictionary containing memory statistics.
        """
        utilization = len(self.items) / self.capacity if self.capacity > 0 else 0
        
        # Add a funny message based on utilization
        if utilization > 0.9:
            status = "Seeker O1 memory is nearly full! Things are getting tight in here."
        elif utilization > 0.7:
            status = "Seeker O1 memory is filling up nicely."
        elif utilization > 0.4:
            status = "Seeker O1 memory has plenty of room for more."
        else:
            status = "Seeker O1 memory is mostly empty. Feed me more data!"
            
        return {
            "type": "short_term",
            "capacity": self.capacity,
            "ttl": self.ttl,
            "current_size": len(self.items),
            "utilization": utilization,
            "status": status
        }
    
    def _prune_expired(self) -> None:
        """
        Remove items that have exceeded their time to live.
        """
        current_time = time.time()
        expired_identifiers = []
        
        for identifier, creation_time in self.creation_times.items():
            if current_time - creation_time > self.ttl:
                expired_identifiers.append(identifier)
        
        if expired_identifiers:
            for identifier in expired_identifiers:
                self.delete(identifier)
            
            logger.debug(f"Seeker O1 has expelled {len(expired_identifiers)} expired items from memory")
    
    def _evict_lru(self) -> None:
        """
        Evict the least recently used item from memory.
        """
        while self.lru_queue:
            _, identifier = heapq.heappop(self.lru_queue)
            
            # Skip if the item has been deleted
            if identifier not in self.items:
                continue
            
            # Delete the item
            item_name = self.items[identifier].get("name", "unknown")
            self.delete(identifier)
            logger.debug(f"Seeker O1 had to push out '{item_name}' to make room for new content")
            break 