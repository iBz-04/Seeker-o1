"""
Base Planner module that defines the common interface for task planning.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BasePlanner(ABC):
    """
    Abstract base class for planners in the ANUS framework.
    
    Provides the core functionality for breaking down tasks into steps.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a BasePlanner instance.
        
        Args:
            **kwargs: Additional configuration options for the planner.
        """
        self.config = kwargs
    
    @abstractmethod
    def create_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a plan for executing a task.
        
        Args:
            task: The task description.
            context: Optional context for planning.
            
        Returns:
            A plan dictionary with steps and metadata.
        """
        pass
    
    @abstractmethod
    def replan(self, plan: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a plan based on execution feedback.
        
        Args:
            plan: The current plan.
            feedback: Feedback from execution.
            
        Returns:
            The updated plan.
        """
        pass
    
    @abstractmethod
    def get_next_step(self, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get the next step to execute from a plan.
        
        Args:
            plan: The current plan.
            
        Returns:
            The next step to execute, or None if the plan is complete.
        """
        pass
    
    @abstractmethod
    def mark_step_complete(self, plan: Dict[str, Any], step_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark a step as complete in a plan.
        
        Args:
            plan: The current plan.
            step_id: The ID of the completed step.
            result: The result of the step execution.
            
        Returns:
            The updated plan.
        """
        pass 