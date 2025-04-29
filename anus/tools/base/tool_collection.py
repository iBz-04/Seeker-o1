"""
Tool Collection module for managing collections of tools.
"""

from typing import Dict, List, Any, Optional, Type, Union
import importlib
import inspect
import logging
import os
import pkgutil

from anus.tools.base.tool import BaseTool

class ToolCollection:
    """
    A collection of tools with registration and discovery capabilities.
    
    Provides functionality for:
    - Registering tools
    - Loading tools dynamically
    - Tool discovery
    - Tool execution
    """
    
    def __init__(self):
        """
        Initialize a ToolCollection instance.
        """
        self.tools: Dict[str, BaseTool] = {}
        self.tool_classes: Dict[str, Type[BaseTool]] = {}
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        
        Args:
            tool: The tool instance to register.
        """
        self.tools[tool.name] = tool
        logging.info(f"Registered tool: {tool.name}")
    
    def register_tool_class(self, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class for later instantiation.
        
        Args:
            tool_class: The tool class to register.
        """
        name = getattr(tool_class, "name", tool_class.__name__.lower())
        self.tool_classes[name] = tool_class
        logging.info(f"Registered tool class: {name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool.
            
        Returns:
            The tool instance, or None if not found.
        """
        # Check if the tool is already instantiated
        if name in self.tools:
            return self.tools[name]
        
        # Check if we have the tool class and can instantiate it
        if name in self.tool_classes:
            try:
                tool = self.tool_classes[name]()
                self.register_tool(tool)
                return tool
            except Exception as e:
                logging.error(f"Error instantiating tool {name}: {e}")
                return None
        
        # Tool not found
        return None
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name.
        
        Args:
            name: The name of the tool to execute.
            **kwargs: Input parameters for the tool.
            
        Returns:
            The result of the tool execution, or an error message.
        """
        tool = self.get_tool(name)
        
        if tool is None:
            error_msg = f"Tool not found: {name}"
            logging.error(error_msg)
            return {"status": "error", "error": error_msg}
        
        try:
            # Validate input
            if not tool.validate_input(**kwargs):
                error_msg = f"Invalid input for tool {name}"
                logging.error(error_msg)
                return {"status": "error", "error": error_msg}
            
            # Execute the tool
            result = tool.execute(**kwargs)
            return {"status": "success", "result": result}
        except Exception as e:
            error_msg = f"Error executing tool {name}: {str(e)}"
            logging.error(error_msg)
            return {"status": "error", "error": error_msg}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools.
        
        Returns:
            A list of tool information dictionaries.
        """
        tool_info = []
        
        # Add instantiated tools
        for name, tool in self.tools.items():
            info = {
                "name": name,
                "description": getattr(tool, "description", "No description available"),
                "parameters": getattr(tool, "parameters", {})
            }
            tool_info.append(info)
        
        # Add non-instantiated tool classes
        for name, tool_class in self.tool_classes.items():
            if name not in self.tools:
                info = {
                    "name": name,
                    "description": getattr(tool_class, "description", "No description available"),
                    "parameters": getattr(tool_class, "parameters", {})
                }
                tool_info.append(info)
        
        return tool_info
    
    def discover_tools(self, package_name: str = "anus.tools") -> int:
        """
        Discover tools in the specified package.
        
        Args:
            package_name: The package to search for tools.
            
        Returns:
            The number of tools discovered.
        """
        count = 0
        
        try:
            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
                if is_pkg:
                    # Recursively discover tools in subpackages
                    count += self.discover_tools(name)
                else:
                    # Import the module
                    try:
                        module = importlib.import_module(name)
                        
                        # Find tool classes in the module
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            
                            # Check if it's a tool class
                            if (
                                inspect.isclass(attr) and 
                                issubclass(attr, BaseTool) and 
                                attr != BaseTool
                            ):
                                self.register_tool_class(attr)
                                count += 1
                    except Exception as e:
                        logging.error(f"Error discovering tools in module {name}: {e}")
        except Exception as e:
            logging.error(f"Error discovering tools in package {package_name}: {e}")
        
        return count 