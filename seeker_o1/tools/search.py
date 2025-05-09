"""
Search tool for basic web search simulation.

This tool simulates searching the web for information.
"""

import logging
import random
from typing import Dict, Any, Union, List

import requests
from typing import Any, Dict, Optional

from seeker_o1.tools.base.tool import BaseTool
from seeker_o1.tools.base.tool_result import ToolResult

class SearchTool(BaseTool):
    """
    A tool for simulating web searches.
    
    Seeker-o1 has the ability to surf the web for you.
    """
    
    name = "search"
    description = "Search the web for information"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        "required": ["query"]
    }
    
    # Mock search results for common queries
    _mock_results = {
        "seeker-o1": [
            "An ai multi agent system and superset of the seeker project",
            "SEEKER-O1: Agentic system",
            "10 facts about seeker-o1",
            "The Story Behind seeker-o1 model"
        ],
        "python": [
            "Python: A versatile, high-level programming language",
            "Wikipedia entry on Python (programming language)",
            "Official Python website for documentation and downloads",
            "Mastering Python: An Essential Learning Resource"
        ],
        "ai": [
            "Artificial Intelligence: Concepts, uses, and new developments",
            "AI's Future: Opportunities and Hurdles Ahead",
            "OpenAI: Pioneers in AI research and innovation",
            "How Artificial Intelligence Is Shaping the World in 2025"
        ],
        "calculator": [
            "Free Online Calculator for Everyday Math",
            "Advanced Scientific Calculator Tools",
            "From Abacus to Apps: The Evolution of Calculators",
            "Top Calculator Applications for Experts"
        ]
    }
    
    # Funny search messages
    _search_messages = [
        "SEEKER-O1 is scouring the internet for insights...",
        "SEEKER-O1 is delving deep to uncover results...",
        "SEEKER-O1 is casting a wide net for information...",
        "SEEKER-O1 is navigating the web in search of answers...",
        "SEEKER-O1 is extracting search results from the web..."
    ]
    
    def execute(self, query: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Execute the search tool.
        
        Args:
            query: The search query.
            **kwargs: Additional parameters (ignored).
            
        Returns:
            The search results.
        """
        try:
            # Log a funny search message
            if random.random() < 0.4:  # 40% chance
                logging.info(random.choice(self._search_messages))
            
            # Clean and lowercase the query for matching
            clean_query = query.lower().strip()
            
            # Check for exact matches in our mock database
            results = []
            exact_match = False
            
            for key, mock_results in self._mock_results.items():
                if key in clean_query:
                    results.extend(mock_results)
                    if key == clean_query:
                        exact_match = True
            
            # If no direct matches, generate a generic response
            if not results:
                results = [
                    f"Result 1 for '{query}'",
                    f"Article about {query} - Wikipedia",
                    f"The Complete Guide to {query}",
                    f"Latest News on {query}"
                ]
            
            # Add a cheeky comment for certain searches
            comment = None
            if "seeker-o1" in clean_query.lower() and not exact_match:
                comment = "I see you're interested in SEEKER-O1... the framework, right?"
            elif any(term in clean_query for term in ["joke", "humor", "funny"]):
                comment = "Looking for humor? SEEKER-O1 itself is often the butt of jokes."
            
            # Return as ToolResult
            result_dict = {
                "query": query,
                "results": results,
                "result_count": len(results)
            }
            
            if comment:
                result_dict['comment'] = comment
            
            return ToolResult.success(self.name, result_dict)
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in search tool: {e}")
            return {"status": "error", "error": f"Search error: {error_msg}"} 