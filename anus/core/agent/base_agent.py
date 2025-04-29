"""
Base Agent module that defines the common interface for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import uuid
import time

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the ANUS framework.
    
    Provides the core functionality and interface that all agent types must implement.
    """
    
    def __init__(self, name: Optional[str] = None, **kwargs):
        """
        Initialize a BaseAgent instance.
        
        Args:
            name: Optional name for the agent. If not provided, a UUID will be generated.
            **kwargs: Additional configuration options for the agent.
        """
        self.id = str(uuid.uuid4())
        self.name = name or f"agent-{self.id[:8]}"
        self.created_at = time.time()
        self.state: Dict[str, Any] = {"status": "initialized"}
        self.history: List[Dict[str, Any]] = []
        self.config = kwargs
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task and return the result.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the execution result and metadata.
        """
        pass
    
    def update_state(self, **kwargs) -> None:
        """
        Update the agent's state with new values.
        
        Args:
            **kwargs: Key-value pairs to update in the state.
        """
        self.state.update(kwargs)
        
    def log_action(self, action: str, details: Dict[str, Any]) -> None:
        """
        Log an action performed by the agent.
        
        Args:
            action: The name of the action.
            details: Details about the action.
        """
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details
        }
        self.history.append(log_entry)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            A dictionary containing agent information.
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "state": self.state,
            "history_length": len(self.history)
        } 