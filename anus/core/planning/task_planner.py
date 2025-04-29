"""
Task Planner module for LLM-based task planning.
"""

import uuid
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union

from anus.core.planning.base_planner import BasePlanner
from anus.models.base.base_model import BaseModel

class TaskPlanner(BasePlanner):
    """
    A planner that uses language models to create and manage task plans.
    
    Implements task breakdown, dependency tracking, and adaptive replanning.
    """
    
    def __init__(self, model: BaseModel, **kwargs):
        """
        Initialize a TaskPlanner instance.
        
        Args:
            model: The language model to use for planning.
            **kwargs: Additional configuration options for the planner.
        """
        super().__init__(**kwargs)
        self.model = model
        self.max_steps = kwargs.get("max_steps", 10)
    
    def create_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a plan for executing a task using the language model.
        
        Args:
            task: The task description.
            context: Optional context for planning.
            
        Returns:
            A plan dictionary with steps and metadata.
        """
        context = context or {}
        
        # Prepare the planning prompt
        prompt = self._create_planning_prompt(task, context)
        
        # Extract JSON schema for the plan
        plan_schema = {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "tool": {"type": "string"},
                            "tool_input": {"type": "object"},
                            "expected_output": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["name", "description", "tool"]
                    }
                },
                "reasoning": {"type": "string"},
                "estimated_steps": {"type": "integer"}
            },
            "required": ["steps", "reasoning"]
        }
        
        # Generate the plan using the model
        try:
            plan_data = self.model.extract_json(
                prompt=prompt,
                schema=plan_schema,
                system_message="You are a task planning assistant. Break down tasks into logical steps."
            )
            
            # Process the plan data
            return self._process_plan_data(task, plan_data)
            
        except Exception as e:
            logging.error(f"Error creating plan: {e}")
            # Return a minimal plan
            return {
                "id": str(uuid.uuid4()),
                "task": task,
                "status": "error",
                "error": str(e),
                "created_at": time.time(),
                "steps": [],
                "reasoning": "Error generating plan",
                "current_step_index": 0,
                "completed_steps": [],
                "metadata": {"context": context}
            }
    
    def replan(self, plan: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a plan based on execution feedback.
        
        Args:
            plan: The current plan.
            feedback: Feedback from execution.
            
        Returns:
            The updated plan.
        """
        # Extract current plan state
        task = plan.get("task", "")
        completed_steps = plan.get("completed_steps", [])
        remaining_steps = self._get_remaining_steps(plan)
        
        # Prepare the replanning prompt
        prompt = self._create_replanning_prompt(task, plan, feedback)
        
        # Extract JSON schema for the updated plan
        plan_schema = {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "tool": {"type": "string"},
                            "tool_input": {"type": "object"},
                            "expected_output": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["name", "description", "tool"]
                    }
                },
                "reasoning": {"type": "string"}
            },
            "required": ["steps", "reasoning"]
        }
        
        try:
            # Generate the updated plan
            updated_plan_data = self.model.extract_json(
                prompt=prompt,
                schema=plan_schema,
                system_message="You are a task planning assistant. Revise plans based on feedback."
            )
            
            # Merge the updated plan with the original plan
            updated_plan = plan.copy()
            updated_plan["steps"] = completed_steps + updated_plan_data.get("steps", [])
            updated_plan["reasoning"] = updated_plan_data.get("reasoning", "Plan updated based on feedback")
            updated_plan["updated_at"] = time.time()
            updated_plan["status"] = "updated"
            
            # Keep the current step index
            if len(completed_steps) < len(updated_plan["steps"]):
                updated_plan["current_step_index"] = len(completed_steps)
            else:
                updated_plan["current_step_index"] = 0
            
            # Add feedback to metadata
            if "metadata" not in updated_plan:
                updated_plan["metadata"] = {}
            updated_plan["metadata"]["feedback"] = feedback
            
            return updated_plan
            
        except Exception as e:
            logging.error(f"Error replanning: {e}")
            # Return the original plan with an error flag
            plan["status"] = "error"
            plan["error"] = str(e)
            return plan
    
    def get_next_step(self, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get the next step to execute from a plan.
        
        Args:
            plan: The current plan.
            
        Returns:
            The next step to execute, or None if the plan is complete.
        """
        steps = plan.get("steps", [])
        current_index = plan.get("current_step_index", 0)
        
        # Check if we've completed all steps
        if current_index >= len(steps):
            return None
        
        # Get the next step
        next_step = steps[current_index]
        
        # Check dependencies
        if "dependencies" in next_step and next_step["dependencies"]:
            completed_step_ids = [step.get("id") for step in plan.get("completed_steps", [])]
            
            # Check if all dependencies are satisfied
            for dep_id in next_step["dependencies"]:
                if dep_id not in completed_step_ids:
                    # Dependency not satisfied, try to find an alternative step
                    alt_step = self._find_executable_step(plan)
                    if alt_step:
                        return alt_step
                    else:
                        # Can't proceed, need replanning
                        logging.warning(f"Can't execute step {next_step.get('id')}: unsatisfied dependencies")
                        return None
        
        return next_step
    
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
        updated_plan = plan.copy()
        steps = updated_plan.get("steps", [])
        current_index = updated_plan.get("current_step_index", 0)
        
        # Find the step
        step_index = -1
        for i, step in enumerate(steps):
            if step.get("id") == step_id:
                step_index = i
                break
        
        if step_index == -1:
            logging.warning(f"Step {step_id} not found in plan")
            return plan
        
        # Update the step with result
        completed_step = steps[step_index].copy()
        completed_step["result"] = result
        completed_step["completed_at"] = time.time()
        
        # Add to completed steps
        if "completed_steps" not in updated_plan:
            updated_plan["completed_steps"] = []
        updated_plan["completed_steps"].append(completed_step)
        
        # Update current step index
        if step_index == current_index:
            updated_plan["current_step_index"] = current_index + 1
        
        # Check if plan is complete
        if updated_plan["current_step_index"] >= len(steps):
            updated_plan["status"] = "completed"
            updated_plan["completed_at"] = time.time()
        
        return updated_plan
    
    def _create_planning_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """
        Create a prompt for generating a plan.
        
        Args:
            task: The task description.
            context: Context information.
            
        Returns:
            A prompt string.
        """
        prompt = f"""
Task: {task}

I need a detailed plan to accomplish this task. Please break it down into specific steps.

For each step, include:
1. A clear name and description
2. The tool required (e.g., web_search, file_read, code_execution)
3. The expected input for the tool
4. Any dependencies on previous steps

Context information:
{json.dumps(context, indent=2)}

Please provide a structured plan with no more than {self.max_steps} steps.
"""
        return prompt
    
    def _create_replanning_prompt(self, task: str, plan: Dict[str, Any], feedback: Dict[str, Any]) -> str:
        """
        Create a prompt for replanning.
        
        Args:
            task: The task description.
            plan: The current plan.
            feedback: Feedback from execution.
            
        Returns:
            A prompt string.
        """
        # Extract completed steps
        completed_steps = plan.get("completed_steps", [])
        completed_steps_text = ""
        for i, step in enumerate(completed_steps):
            result = step.get("result", {})
            result_status = result.get("status", "unknown")
            result_summary = str(result.get("result", "No result"))[:100] + "..." if len(str(result.get("result", ""))) > 100 else str(result.get("result", "No result"))
            
            completed_steps_text += f"{i+1}. {step.get('name', 'Step')}: {result_status} - {result_summary}\n"
        
        # Extract remaining steps
        remaining_steps = self._get_remaining_steps(plan)
        remaining_steps_text = ""
        for i, step in enumerate(remaining_steps):
            remaining_steps_text += f"{i+1}. {step.get('name', 'Step')}: {step.get('description', 'No description')}\n"
        
        prompt = f"""
Task: {task}

I need to revise my plan based on execution feedback. 

Completed steps:
{completed_steps_text}

Current feedback:
{json.dumps(feedback, indent=2)}

Current remaining steps:
{remaining_steps_text}

Please provide an updated plan for the remaining steps, considering the feedback and results from completed steps.
"""
        return prompt
    
    def _process_plan_data(self, task: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw plan data into a structured plan.
        
        Args:
            task: The task description.
            plan_data: Raw plan data from the model.
            
        Returns:
            A structured plan dictionary.
        """
        steps = plan_data.get("steps", [])
        
        # Ensure each step has an ID and required fields
        for i, step in enumerate(steps):
            if "id" not in step:
                step["id"] = f"step-{i+1}-{str(uuid.uuid4())[:8]}"
            
            if "tool_input" not in step:
                step["tool_input"] = {}
            
            if "dependencies" not in step:
                step["dependencies"] = []
        
        # Create the plan structure
        plan = {
            "id": str(uuid.uuid4()),
            "task": task,
            "status": "created",
            "created_at": time.time(),
            "steps": steps,
            "reasoning": plan_data.get("reasoning", ""),
            "current_step_index": 0,
            "completed_steps": [],
            "metadata": {
                "estimated_steps": plan_data.get("estimated_steps", len(steps))
            }
        }
        
        return plan
    
    def _get_remaining_steps(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the remaining steps from a plan.
        
        Args:
            plan: The current plan.
            
        Returns:
            A list of remaining steps.
        """
        steps = plan.get("steps", [])
        current_index = plan.get("current_step_index", 0)
        
        if current_index >= len(steps):
            return []
        
        return steps[current_index:]
    
    def _find_executable_step(self, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a step that can be executed (all dependencies satisfied).
        
        Args:
            plan: The current plan.
            
        Returns:
            An executable step, or None if none found.
        """
        steps = plan.get("steps", [])
        current_index = plan.get("current_step_index", 0)
        completed_step_ids = [step.get("id") for step in plan.get("completed_steps", [])]
        
        # Look for steps after the current index
        for i in range(current_index, len(steps)):
            step = steps[i]
            dependencies = step.get("dependencies", [])
            
            # Check if all dependencies are satisfied
            dependencies_satisfied = True
            for dep_id in dependencies:
                if dep_id not in completed_step_ids:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                return step
        
        return None 