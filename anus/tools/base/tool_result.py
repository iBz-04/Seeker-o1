"""
Tool Result module for standardized result handling.
"""

from typing import Dict, List, Any, Optional, Union
import time

class ToolResult:
    """
    Standardized container for tool execution results.
    
    Provides consistent structure and metadata for tool results.
    """
    
    def __init__(
        self, 
        tool_name: str,
        status: str = "success",
        result: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a ToolResult instance.
        
        Args:
            tool_name: Name of the tool that produced the result.
            status: Status of the tool execution ("success" or "error").
            result: The actual result data.
            error: Error message if status is "error".
            metadata: Additional metadata about the execution.
        """
        self.tool_name = tool_name
        self.status = status
        self.result = result
        self.error = error
        self.metadata = metadata or {}
        
        # Add timestamp
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a dictionary.
        
        Returns:
            A dictionary representation of the result.
        """
        result_dict = {
            "tool_name": self.tool_name,
            "status": self.status,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
        
        if self.status == "success":
            result_dict["result"] = self.result
        elif self.status == "error":
            result_dict["error"] = self.error
        
        return result_dict
    
    @classmethod
    def success(cls, tool_name: str, result: Any, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        Create a successful result.
        
        Args:
            tool_name: Name of the tool.
            result: The result data.
            metadata: Additional metadata.
            
        Returns:
            A ToolResult instance with success status.
        """
        return cls(tool_name=tool_name, status="success", result=result, metadata=metadata)
    
    @classmethod
    def error(cls, tool_name: str, error: str, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """
        Create an error result.
        
        Args:
            tool_name: Name of the tool.
            error: The error message.
            metadata: Additional metadata.
            
        Returns:
            A ToolResult instance with error status.
        """
        return cls(tool_name=tool_name, status="error", error=error, metadata=metadata)
    
    def is_success(self) -> bool:
        """
        Check if the result is successful.
        
        Returns:
            True if the status is "success", False otherwise.
        """
        return self.status == "success"
    
    def is_error(self) -> bool:
        """
        Check if the result is an error.
        
        Returns:
            True if the status is "error", False otherwise.
        """
        return self.status == "error" 