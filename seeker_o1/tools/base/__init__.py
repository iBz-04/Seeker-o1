"""
Base Tool module for the seeker-o1 framework.

This module contains base classes for tools:
- BaseTool: Abstract base class for all tools
- ToolResult: Standardized container for tool results
- ToolCollection: Utility for managing collections of tools
"""

from seeker_o1.tools.base.tool import BaseTool
from seeker_o1.tools.base.tool_result import ToolResult
from seeker_o1.tools.base.tool_collection import ToolCollection

__all__ = ["BaseTool", "ToolResult", "ToolCollection"] 