"""
Base Tool module that defines the common interface for all tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

class BaseTool(ABC):
    """
    Abstract base class for all tools in the ANUS framework.
    
    Provides the core functionality and interface that all tool types must implement.
    """
    
    name = "base_tool"
    description = "Base class for all tools"
    
    def __init__(self, **kwargs):
        """
        Initialize a BaseTool instance.
        
        Args:
            **kwargs: Additional configuration options for the tool.
        """
        self.config = kwargs
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool's function.
        
        Args:
            **kwargs: Input parameters for the tool.
            
        Returns:
            The result of the tool execution.
        """
        pass
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate the input parameters.
        
        Args:
            **kwargs: Input parameters to validate.
            
        Returns:
            True if the input is valid, False otherwise.
        """
        # Base implementation is a pass-through
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's parameter schema.
        
        Returns:
            A dictionary describing the tool's parameters.
        """
        # Base implementation returns a simple schema
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {}
        } 