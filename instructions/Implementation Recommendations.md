# Implementation Recommendations for ANUS

This document provides specific implementation recommendations for adapting valuable concepts from OpenManus into the ANUS framework. These recommendations focus on practical implementation details while respecting and enhancing ANUS's current structure.

## Core Agent System

### BaseAgent Implementation

```python
# anus/core/agent/base_agent.py

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from anus.models.base_model import BaseModel as LLMModel
from anus.core.memory.base_memory import BaseMemory
from anus.core.schema import AgentState, Message

class BaseAgent(BaseModel, ABC):
    """
    Abstract base class for all ANUS agents.
    Provides foundational functionality for state management, memory, and execution.
    """
    # Core attributes
    name: str = Field(..., description="Unique name of the agent")
    description: Optional[str] = Field(None, description="Agent description")
    
    # Prompts
    system_prompt: Optional[str] = Field(None, description="System-level instruction prompt")
    next_step_prompt: Optional[str] = Field(None, description="Prompt for determining next action")
    
    # Dependencies
    llm: LLMModel = Field(default_factory=LLMModel, description="Language model instance")
    memory: BaseMemory = Field(default_factory=BaseMemory, description="Agent's memory store")
    state: AgentState = Field(default="idle", description="Current agent state")
    
    # Execution control
    max_steps: int = Field(default=15, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses
    
    @abstractmethod
    async def step(self) -> bool:
        """
        Execute a single step of the agent's reasoning process.
        Returns True if execution should continue, False if complete.
        Must be implemented by subclasses.
        """
        pass
    
    async def run(self, request: Optional[str] = None) -> str:
        """
        Execute the agent with the given request.
        Handles initialization, step execution, and result formatting.
        """
        # Initialize execution
        self.current_step = 0
        self.state = "running"
        
        # Add request to memory if provided
        if request:
            self.memory.add_user_message(request)
        
        # Execute steps until completion or max steps reached
        result = ""
        while self.current_step < self.max_steps and self.state == "running":
            self.current_step += 1
            continue_execution = await self.step()
            
            if not continue_execution:
                self.state = "finished"
                break
        
        # Format and return result
        result = self.memory.get_assistant_response()
        return result
```

### ToolAgent Implementation

```python
# anus/core/agent/tool_agent.py

from typing import Dict, List, Optional
from pydantic import Field

from anus.core.agent.base_agent import BaseAgent
from anus.core.schema import Message, ToolCall
from anus.tools.base.tool_collection import ToolCollection

class ToolAgent(BaseAgent):
    """
    Agent with tool execution capabilities.
    Can use various tools to accomplish tasks through function calling.
    """
    # Tool-related attributes
    available_tools: ToolCollection = Field(default_factory=ToolCollection)
    tool_choice: str = Field(default="auto", description="Tool choice strategy: 'none', 'auto', or 'required'")
    tool_calls: List[ToolCall] = Field(default_factory=list)
    
    async def step(self) -> bool:
        """
        Execute a single step of the agent's reasoning process.
        Includes thinking (deciding what to do) and acting (executing tools).
        """
        # Think: Decide what to do next
        thinking_complete = await self.think()
        if not thinking_complete:
            return False
        
        # Act: Execute decided actions
        action_result = await self.act()
        
        # Check if execution should continue
        if self.state != "running":
            return False
            
        return True
    
    async def think(self) -> bool:
        """Process current state and decide next actions using tools"""
        # Add next step prompt if available
        if self.next_step_prompt:
            self.memory.add_user_message(self.next_step_prompt)
        
        # Get response with tool options
        response = await self.llm.ask_with_tools(
            messages=self.memory.get_messages(),
            system_message=self.system_prompt,
            tools=self.available_tools.to_params(),
            tool_choice=self.tool_choice,
        )
        
        # Store tool calls for execution
        self.tool_calls = response.tool_calls
        
        # Check if thinking produced any tool calls
        if not self.tool_calls and self.tool_choice == "required":
            self.memory.add_assistant_message("Failed to determine next action.")
            return False
            
        return True
    
    async def act(self) -> str:
        """Execute tool calls determined during thinking phase"""
        if not self.tool_calls:
            return ""
            
        results = []
        for tool_call in self.tool_calls:
            result = await self.execute_tool(tool_call)
            results.append(result)
            
        # Add tool results to memory
        combined_result = "\n".join(results)
        self.memory.add_system_message(f"Tool execution results:\n{combined_result}")
        
        return combined_result
    
    async def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a specific tool call"""
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        
        # Check for special tools (like termination)
        if tool_name in self.special_tool_names:
            return await self._handle_special_tool(tool_name, tool_args)
        
        # Execute the tool via ToolCollection
        try:
            result = await self.available_tools.execute(name=tool_name, tool_input=tool_args)
            return f"Tool '{tool_name}' executed successfully: {result}"
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            return error_msg
```

### HybridAgent Implementation

```python
# anus/core/agent/hybrid_agent.py

from typing import Dict, List, Optional
from pydantic import Field

from anus.core.agent.tool_agent import ToolAgent
from anus.core.flow.consensus_flow import ConsensusFlow

class HybridAgent(ToolAgent):
    """
    Agent that can dynamically switch between single-agent and multi-agent modes
    based on task complexity and requirements.
    """
    # Multi-agent related attributes
    sub_agents: Dict[str, ToolAgent] = Field(default_factory=dict)
    collaboration_threshold: float = Field(default=0.7, description="Complexity threshold for switching modes")
    
    async def run(self, request: Optional[str] = None) -> str:
        """Execute the agent with dynamic mode selection"""
        if not request:
            return "No request provided"
            
        # Analyze task complexity
        complexity = await self._analyze_complexity(request)
        
        # Choose execution mode based on complexity
        if complexity > self.collaboration_threshold:
            return await self._run_collaborative(request)
        else:
            return await super().run(request)
    
    async def _analyze_complexity(self, request: str) -> float:
        """
        Analyze task complexity to determine execution mode.
        Returns a value between 0 and 1 representing task complexity.
        """
        # Use LLM to assess task complexity
        system_prompt = """
        You are a task complexity analyzer. Your job is to assess the complexity of a given task
        and return a score between 0 and 1, where:
        - 0-0.3: Simple tasks requiring minimal reasoning or tool use
        - 0.3-0.7: Moderate tasks requiring some reasoning and tool use
        - 0.7-1.0: Complex tasks requiring extensive reasoning, multiple tools, or specialized knowledge
        
        Analyze only the complexity, not the clarity or specificity of the request.
        Return only a numeric score between 0 and 1, with no explanation.
        """
        
        response = await self.llm.ask(
            messages=[{"role": "user", "content": request}],
            system_message=system_prompt,
            temperature=0.1,  # Low temperature for consistent assessment
        )
        
        # Extract numeric score from response
        try:
            score = float(response.content.strip())
            # Ensure score is within valid range
            return max(0.0, min(1.0, score))
        except ValueError:
            # Default to single-agent mode if parsing fails
            return 0.5
    
    async def _run_collaborative(self, request: str) -> str:
        """Execute request in collaborative multi-agent mode"""
        # Ensure sub-agents exist
        await self._ensure_sub_agents()
        
        # Create consensus flow with sub-agents
        flow = ConsensusFlow(agents=self.sub_agents)
        
        # Execute flow with request
        return await flow.execute(request)
    
    async def _ensure_sub_agents(self) -> None:
        """Create specialized sub-agents if they don't exist"""
        # Define standard roles if not already created
        standard_roles = {
            "researcher": "Specializes in information gathering and research",
            "coder": "Specializes in code writing and software development",
            "planner": "Specializes in task planning and organization",
            "critic": "Specializes in reviewing and improving solutions"
        }
        
        # Create missing sub-agents
        for role, description in standard_roles.items():
            if role not in self.sub_agents:
                # Create specialized agent with role-specific system prompt
                self.sub_agents[role] = await self._create_specialized_agent(role, description)
    
    async def _create_specialized_agent(self, role: str, description: str) -> ToolAgent:
        """Create a specialized agent for a specific role"""
        # Generate role-specific system prompt
        system_prompt = await self._generate_role_prompt(role, description)
        
        # Create agent with same tools but specialized prompt
        agent = ToolAgent(
            name=f"{self.name}_{role}",
            description=description,
            system_prompt=system_prompt,
            available_tools=self.available_tools,
            llm=self.llm,  # Use same LLM instance
        )
        
        return agent
    
    async def _generate_role_prompt(self, role: str, description: str) -> str:
        """Generate a specialized system prompt for a specific role"""
        base_prompt = f"""You are a specialized {role} agent. {description}.
        
        Focus on your specialized role while collaborating with other agents to solve complex tasks.
        Use the available tools effectively to accomplish your part of the task.
        """
        
        return base_prompt
```

## Planning System

### PlanningTool Implementation

```python
# anus/tools/planning/planning_tool.py

from typing import Dict, List, Optional
import time
import json
from pydantic import Field

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class PlanningTool(BaseTool):
    """
    A planning tool that allows the agent to create and manage plans for solving complex tasks.
    The tool provides functionality for creating plans, updating plan steps, and tracking progress.
    """
    name: str = "planning"
    description: str = """
    Create and manage plans for solving complex tasks. Supports:
    - Creating new plans with steps
    - Updating existing plans
    - Marking steps as completed
    - Listing available plans
    - Getting plan details
    """
    
    # Storage for plans
    plans: Dict[str, Dict] = Field(default_factory=dict)
    active_plan_id: Optional[str] = None
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": ["create", "update", "mark_step", "list", "get", "set_active", "delete"],
                "description": "The planning command to execute"
            },
            "plan_id": {
                "type": "string",
                "description": "Identifier for the plan (auto-generated if not provided)"
            },
            "title": {
                "type": "string",
                "description": "Title of the plan (for create/update)"
            },
            "steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of steps in the plan (for create/update)"
            },
            "step_index": {
                "type": "integer",
                "description": "Index of the step to update (for mark_step)"
            },
            "step_status": {
                "type": "string",
                "enum": ["not_started", "in_progress", "completed", "skipped"],
                "description": "Status to set for the step (for mark_step)"
            }
        },
        "required": ["command"]
    }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the planning tool with the given parameters"""
        command = kwargs.get("command")
        
        if command == "create":
            return self._create_plan(**kwargs)
        elif command == "update":
            return self._update_plan(**kwargs)
        elif command == "mark_step":
            return self._mark_step(**kwargs)
        elif command == "list":
            return self._list_plans()
        elif command == "get":
            return self._get_plan(kwargs.get("plan_id"))
        elif command == "set_active":
            return self._set_active_plan(kwargs.get("plan_id"))
        elif command == "delete":
            return self._delete_plan(kwargs.get("plan_id"))
        else:
            return ToolResult(
                success=False,
                message=f"Unknown planning command: {command}"
            )
    
    def _create_plan(self, **kwargs) -> ToolResult:
        """Create a new plan with the given parameters"""
        plan_id = kwargs.get("plan_id") or f"plan_{int(time.time())}"
        title = kwargs.get("title") or f"Plan {len(self.plans) + 1}"
        steps = kwargs.get("steps") or []
        
        # Create plan structure
        plan = {
            "id": plan_id,
            "title": title,
            "steps": steps,
            "step_statuses": ["not_started"] * len(steps),
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Store the plan
        self.plans[plan_id] = plan
        
        # Set as active plan if no active plan exists
        if not self.active_plan_id:
            self.active_plan_id = plan_id
        
        return ToolResult(
            success=True,
            message=f"Created plan '{title}' with ID {plan_id}",
            data={"plan_id": plan_id}
        )
```

### PlanningFlow Implementation

```python
# anus/core/flow/planning_flow.py

from typing import Dict, List, Optional, Tuple, Union
import time
from pydantic import Field

from anus.core.agent.base_agent import BaseAgent
from anus.core.flow.base_flow import BaseFlow
from anus.models.base_model import BaseModel as LLMModel
from anus.tools.planning.planning_tool import PlanningTool

class PlanningFlow(BaseFlow):
    """
    A flow that manages planning and execution of tasks using agents.
    Breaks down complex tasks into steps and executes them sequentially.
    """
    # Flow components
    llm: LLMModel = Field(default_factory=LLMModel)
    planning_tool: PlanningTool = Field(default_factory=PlanningTool)
    executor_keys: List[str] = Field(default_factory=list)
    
    # Plan tracking
    active_plan_id: str = Field(default_factory=lambda: f"plan_{int(time.time())}")
    current_step_index: Optional[int] = None
    
    async def execute(self, input_text: str) -> str:
        """Execute the planning flow with agents"""
        try:
            # Create initial plan if input provided
            if input_text:
                await self._create_initial_plan(input_text)
                
                # Verify plan was created successfully
                if self.active_plan_id not in self.planning_tool.plans:
                    return f"Failed to create plan for: {input_text}"
            
            result = ""
            while True:
                # Get current step to execute
                self.current_step_index, step_info = await self._get_current_step_info()
                
                # Exit if no more steps or plan completed
                if self.current_step_index is None:
                    result += await self._finalize_plan()
                    break
                
                # Execute current step with appropriate agent
                step_type = step_info.get("type") if step_info else None
                executor = self.get_executor(step_type)
                step_result = await self._execute_step(executor, step_info)
                result += step_result + "\n"
                
                # Check if agent wants to terminate
                if executor.state == "finished":
                    break
            
            return result
        except Exception as e:
            return f"Execution failed: {str(e)}"
    
    def get_executor(self, step_type: Optional[str] = None) -> BaseAgent:
        """
        Get an appropriate executor agent for the current step.
        Can be extended to select agents based on step type/requirements.
        """
        # If step type is provided and matches an agent key, use that agent
        if step_type and step_type in self.agents:
            return self.agents[step_type]
        
        # Otherwise use the first available executor or fall back to primary agent
        for key in self.executor_keys:
            if key in self.agents:
                return self.agents[key]
        
        # Fallback to primary agent
        return self.primary_agent
```

## Tool System

### BaseTool Implementation

```python
# anus/tools/base/tool.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class BaseTool(ABC, BaseModel):
    """
    Abstract base class for all tools in the ANUS framework.
    Provides foundation for tool definition, parameter specification, and execution.
    """
    name: str
    description: str
    parameters: Optional[Dict] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    async def __call__(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        return await self.execute(**kwargs)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.
        Must be implemented by subclasses.
        """
        pass
    
    def to_param(self) -> Dict:
        """Convert tool to function call format for LLM."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {
                    "type": "object",
                    "properties": {},
                }
            }
        }
```

### ToolCollection Implementation

```python
# anus/tools/base/tool_collection.py

from typing import Any, Dict, List, Optional
from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult, ToolFailure

class ToolCollection:
    """
    A collection of tools that can be used by agents.
    Provides unified interface for tool registration, discovery, and execution.
    """
    def __init__(self, *tools: BaseTool):
        self.tools = list(tools)
        self.tool_map = {tool.name: tool for tool in tools}
    
    def __iter__(self):
        return iter(self.tools)
    
    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the collection"""
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the collection"""
        if tool_name in self.tool_map:
            tool = self.tool_map.pop(tool_name)
            self.tools.remove(tool)
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tool_map.get(tool_name)
    
    def to_params(self) -> List[Dict[str, Any]]:
        """Convert all tools to function call format for LLM"""
        return [tool.to_param() for tool in self.tools]
    
    async def execute(self, *, name: str, tool_input: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool by name with the given input"""
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} not found")
        
        try:
            tool_input = tool_input or {}
            result = await tool(**tool_input)
            return result
        except Exception as e:
            return ToolFailure(error=f"Error executing tool {name}: {str(e)}")
```

### BrowserTool Implementation

```python
# anus/tools/web/browser_tool.py

from typing import Dict, Optional
import asyncio
from pydantic import Field

from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult, ToolFailure

class BrowserTool(BaseTool):
    """
    Tool for browser automation and web interaction.
    Provides capabilities for navigation, content extraction, and element interaction.
    """
    name: str = "browser"
    description: str = """
    Interact with a web browser to perform various actions such as navigation, 
    element interaction, content extraction, and tab management.
    """
    
    # Browser configuration
    headless: bool = Field(default=True, description="Whether to run browser in headless mode")
    browser_instance = None
    
    parameters: Dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "navigate", "click", "input_text", "screenshot", 
                    "get_html", "get_text", "read_links", "execute_js",
                    "scroll", "switch_tab", "new_tab", "close_tab", "refresh"
                ],
                "description": "The browser action to perform"
            },
            "url": {
                "type": "string",
                "description": "URL to navigate to (for navigate action)"
            },
            "element_index": {
                "type": "integer",
                "description": "Index of the element to interact with (for click/input actions)"
            },
            "text": {
                "type": "string",
                "description": "Text to input (for input_text action)"
            },
            "js_code": {
                "type": "string",
                "description": "JavaScript code to execute (for execute_js action)"
            },
            "direction": {
                "type": "string",
                "enum": ["up", "down", "left", "right"],
                "description": "Scroll direction (for scroll action)"
            },
            "tab_index": {
                "type": "integer",
                "description": "Tab index to switch to (for switch_tab action)"
            }
        },
        "required": ["action"]
    }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the browser tool with the given parameters"""
        action = kwargs.get("action")
        
        # Initialize browser if not already initialized
        if not self.browser_instance:
            await self._initialize_browser()
        
        try:
            if action == "navigate":
                return await self._navigate(kwargs.get("url"))
            elif action == "click":
                return await self._click(kwargs.get("element_index"))
            elif action == "input_text":
                return await self._input_text(kwargs.get("element_index"), kwargs.get("text"))
            elif action == "screenshot":
                return await self._screenshot()
            elif action == "get_html":
                return await self._get_html()
            elif action == "get_text":
                return await self._get_text()
            elif action == "read_links":
                return await self._read_links()
            elif action == "execute_js":
                return await self._execute_js(kwargs.get("js_code"))
            elif action == "scroll":
                return await self._scroll(kwargs.get("direction"))
            elif action == "switch_tab":
                return await self._switch_tab(kwargs.get("tab_index"))
            elif action == "new_tab":
                return await self._new_tab()
            elif action == "close_tab":
                return await self._close_tab()
            elif action == "refresh":
                return await self._refresh()
            else:
                return ToolFailure(error=f"Unknown browser action: {action}")
        except Exception as e:
            return ToolFailure(error=f"Browser action failed: {str(e)}")
    
    async def _initialize_browser(self) -> None:
        """Initialize the browser instance"""
        # Implementation would use a browser automation library like Playwright
        # This is a placeholder for the actual implementation
        self.browser_instance = {"initialized": True}
```

## Model Integration

### BaseModel Implementation

```python
# anus/models/base_model.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pydantic import BaseModel as PydanticBaseModel, Field

class Message(PydanticBaseModel):
    """Represents a message in a conversation"""
    role: str
    content: str

class ToolCall(PydanticBaseModel):
    """Represents a tool call from the model"""
    id: str
    type: str = "function"
    function: Dict

class ModelResponse(PydanticBaseModel):
    """Represents a response from a language model"""
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

class BaseModel(PydanticBaseModel, ABC):
    """
    Abstract base class for language model integrations.
    Provides unified interface for different model providers.
    """
    provider: str = "openai"  # Default provider
    model_name: str = "gpt-4o"  # Default model
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    
    @abstractmethod
    async def ask(
        self, 
        messages: List[Union[Dict, Message]], 
        system_message: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Send a request to the language model and get a response.
        Basic version without tool calling.
        """
        pass
    
    @abstractmethod
    async def ask_with_tools(
        self,
        messages: List[Union[Dict, Message]],
        system_message: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> ModelResponse:
        """
        Send a request to the language model with tools and get a response.
        Supports function/tool calling.
        """
        pass
```

### OpenAIModel Implementation

```python
# anus/models/openai_model.py

from typing import Dict, List, Optional, Union
import json
import os
from pydantic import Field

from anus.models.base_model import BaseModel, Message, ModelResponse, ToolCall

class OpenAIModel(BaseModel):
    """
    OpenAI API integration for language models.
    Supports GPT-4 and other OpenAI models.
    """
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    base_url: Optional[str] = Field(default="https://api.openai.com/v1")
    
    async def ask(
        self, 
        messages: List[Union[Dict, Message]], 
        system_message: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """Send a request to OpenAI API and get a response"""
        import openai
        
        # Set up client
        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Prepare messages
        formatted_messages = self._format_messages(messages, system_message)
        
        # Set parameters
        params = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        # Send request
        response = await client.chat.completions.create(**params)
        
        # Process response
        content = response.choices[0].message.content
        
        return ModelResponse(content=content)
    
    async def ask_with_tools(
        self,
        messages: List[Union[Dict, Message]],
        system_message: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> ModelResponse:
        """Send a request to OpenAI API with tools and get a response"""
        import openai
        
        # Set up client
        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Prepare messages
        formatted_messages = self._format_messages(messages, system_message)
        
        # Set parameters
        params = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
            
            # Set tool_choice based on parameter
            if tool_choice == "required":
                params["tool_choice"] = {"type": "function", "function": {"name": tools[0]["function"]["name"]}}
            elif tool_choice == "none":
                params["tool_choice"] = "none"
            else:  # "auto"
                params["tool_choice"] = "auto"
        
        # Send request
        response = await client.chat.completions.create(**params)
        
        # Process response
        message = response.choices[0].message
        content = message.content
        
        # Process tool calls if present
        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        type="function",
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    )
                )
        
        return ModelResponse(content=content, tool_calls=tool_calls)
    
    def _format_messages(
        self,
        messages: List[Union[Dict, Message]],
        system_message: Optional[str] = None
    ) -> List[Dict]:
        """Format messages for OpenAI API"""
        formatted_messages = []
        
        # Add system message if provided
        if system_message:
            formatted_messages.append({"role": "system", "content": system_message})
        
        # Add other messages
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(msg)
            else:
                formatted_messages.append({"role": msg.role, "content": msg.content})
        
        return formatted_messages
```

## Memory System

### BaseMemory Implementation

```python
# anus/core/memory/base_memory.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Represents a message in the agent's memory"""
    role: str
    content: str

class BaseMemory(BaseModel):
    """
    Base class for agent memory systems.
    Provides storage and retrieval of conversation history.
    """
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = 100
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory"""
        self.messages.append(Message(role=role, content=content))
        
        # Trim if exceeding max messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to memory"""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to memory"""
        self.add_message("assistant", content)
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to memory"""
        self.add_message("system", content)
    
    def get_messages(self) -> List[Message]:
        """Get all messages in memory"""
        return self.messages
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message in memory"""
        if not self.messages:
            return None
        return self.messages[-1]
    
    def get_assistant_response(self) -> str:
        """Get the last assistant response"""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return ""
    
    def clear(self) -> None:
        """Clear all messages from memory"""
        self.messages = []
```

### HybridMemory Implementation

```python
# anus/core/memory/hybrid_memory.py

from typing import Dict, List, Optional
import json
import os
from pydantic import Field

from anus.core.memory.base_memory import BaseMemory, Message

class HybridMemory(BaseMemory):
    """
    Hybrid memory system with both short-term and long-term storage.
    Provides persistent storage for conversations and context.
    """
    persistence: bool = Field(default=False, description="Whether to persist memory to disk")
    storage_path: Optional[str] = Field(default=None, description="Path to store persistent memory")
    
    # Long-term memory storage
    long_term_memories: Dict[str, List[Dict]] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Set default storage path if not provided
        if self.persistence and not self.storage_path:
            self.storage_path = os.path.expanduser("~/.anus/memory")
        
        # Load persistent memory if enabled
        if self.persistence:
            self._load_persistent_memory()
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to memory and persist if enabled"""
        super().add_message(role, content)
        
        # Persist memory if enabled
        if self.persistence:
            self._save_persistent_memory()
    
    def add_to_long_term(self, category: str, data: Dict) -> None:
        """Add data to long-term memory"""
        if category not in self.long_term_memories:
            self.long_term_memories[category] = []
        
        self.long_term_memories[category].append(data)
        
        # Persist memory if enabled
        if self.persistence:
            self._save_persistent_memory()
    
    def get_from_long_term(self, category: str) -> List[Dict]:
        """Get data from long-term memory by category"""
        return self.long_term_memories.get(category, [])
    
    def search_long_term(self, category: str, query: str) -> List[Dict]:
        """Search long-term memory for relevant information"""
        # Simple keyword search implementation
        # Could be enhanced with vector search or other techniques
        results = []
        for item in self.get_from_long_term(category):
            item_str = json.dumps(item).lower()
            if query.lower() in item_str:
                results.append(item)
        return results
    
    def _load_persistent_memory(self) -> None:
        """Load memory from persistent storage"""
        try:
            # Ensure directory exists
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Load short-term memory
            st_path = os.path.join(self.storage_path, "short_term.json")
            if os.path.exists(st_path):
                with open(st_path, "r") as f:
                    data = json.load(f)
                    self.messages = [Message(**msg) for msg in data]
            
            # Load long-term memory
            lt_path = os.path.join(self.storage_path, "long_term.json")
            if os.path.exists(lt_path):
                with open(lt_path, "r") as f:
                    self.long_term_memories = json.load(f)
        except Exception as e:
            print(f"Error loading persistent memory: {e}")
    
    def _save_persistent_memory(self) -> None:
        """Save memory to persistent storage"""
        try:
            # Ensure directory exists
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Save short-term memory
            st_path = os.path.join(self.storage_path, "short_term.json")
            with open(st_path, "w") as f:
                json.dump([msg.dict() for msg in self.messages], f)
            
            # Save long-term memory
            lt_path = os.path.join(self.storage_path, "long_term.json")
            with open(lt_path, "w") as f:
                json.dump(self.long_term_memories, f)
        except Exception as e:
            print(f"Error saving persistent memory: {e}")
```

## Integration Strategy

### Main Entry Point

```python
# anus/main.py

import argparse
import asyncio
import os
import sys
from typing import Dict, Optional

from anus.core.agent.hybrid_agent import HybridAgent
from anus.core.config import AgentConfig
from anus.ui.cli import CLI

async def main():
    """Main entry point for the ANUS framework"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ANUS - Autonomous Networked Utility System")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "multi"], help="Agent mode")
    parser.add_argument("--task", type=str, help="Task description")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = CLI(verbose=args.verbose)
    cli.display_welcome()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.mode:
        config.mode = args.mode
    
    # Initialize agent
    agent = create_agent(config)
    
    # Execute task if provided
    if args.task:
        result = await agent.run(args.task)
        cli.display_result(result)
        return
    
    # Start interactive mode
    await cli.start_interactive_mode(agent)

def load_config(config_path: str) -> AgentConfig:
    """Load configuration from file"""
    # Implementation would load YAML/JSON config
    # This is a placeholder for the actual implementation
    return AgentConfig()

def create_agent(config: AgentConfig) -> HybridAgent:
    """Create agent based on configuration"""
    # Create agent with appropriate tools and configuration
    agent = HybridAgent(
        name=config.name,
        collaboration_threshold=0.7 if config.mode == "multi" else 1.0,  # Force single mode if specified
    )
    
    # Initialize tools based on configuration
    initialize_tools(agent, config)
    
    return agent

def initialize_tools(agent: HybridAgent, config: AgentConfig) -> None:
    """Initialize tools based on configuration"""
    # Implementation would create and add tools based on config
    # This is a placeholder for the actual implementation
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration System

```python
# anus/core/config.py

from typing import Dict, Optional
import os
import yaml
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """Configuration for language models"""
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096

class MemoryConfig(BaseModel):
    """Configuration for memory systems"""
    type: str = "hybrid"  # "short_term", "long_term", "hybrid"
    persistence: bool = False
    storage_path: Optional[str] = None

class ToolConfig(BaseModel):
    """Configuration for tools"""
    browser: Dict = Field(default_factory=lambda: {"headless": True})
    code: Dict = Field(default_factory=lambda: {"sandbox": True})
    # Other tool configurations

class AgentConfig(BaseModel):
    """Configuration for agents"""
    name: str = "anus"
    mode: str = "single"  # "single", "multi"
    model: ModelConfig = Field(default_factory=ModelConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    max_steps: int = 30

def load_config(config_path: str) -> AgentConfig:
    """Load configuration from YAML file"""
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        return AgentConfig.parse_obj(config_data)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return AgentConfig()

def save_config(config: AgentConfig, config_path: str) -> bool:
    """Save configuration to YAML file"""
    try:
        with open(config_path, "w") as f:
            yaml.dump(config.dict(), f)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
```

## Implementation Roadmap

### Phase 1: Core Framework (Week 1-2)

1. **Setup Project Structure**
   - Create directory structure
   - Set up package configuration
   - Configure development environment

2. **Implement Base Classes**
   - BaseAgent
   - BaseTool and ToolCollection
   - BaseMemory
   - BaseModel

3. **Implement Core Agent Types**
   - ToolAgent
   - Basic HybridAgent

4. **Implement Model Integration**
   - OpenAIModel
   - Model router

5. **Implement Configuration System**
   - Configuration classes
   - YAML loading/saving

### Phase 2: Tool Ecosystem (Week 3-4)

1. **Implement Basic Tools**
   - PlanningTool
   - Basic web tools
   - File operation tools
   - Information retrieval tools

2. **Implement Browser Automation**
   - BrowserTool
   - Navigation and interaction
   - Content extraction

3. **Implement Code Execution**
   - Python execution sandbox
   - Code analysis tools

4. **Implement Document Processing**
   - PDF parsing
   - Text extraction

### Phase 3: Advanced Features (Week 5-6)

1. **Enhance HybridAgent**
   - Task complexity analysis
   - Dynamic mode switching

2. **Implement Multi-Agent Collaboration**
   - Specialized agent roles
   - ConsensusFlow
   - Voting mechanisms

3. **Enhance Memory System**
   - HybridMemory
   - Persistence
   - Search capabilities

4. **Implement Resource Allocation**
   - ResourcePlanner
   - Optimization algorithms

### Phase 4: User Interfaces (Week 7-8)

1. **Enhance CLI**
   - Interactive mode
   - Progress visualization
   - History browsing

2. **Implement Web Interface**
   - Basic web server
   - Dashboard
   - Visualization components

3. **Implement API**
   - RESTful endpoints
   - Authentication
   - Documentation

4. **Final Integration and Testing**
   - End-to-end testing
   - Performance optimization
   - Documentation completion
