# ANUS Architecture Design Based on OpenManus Concepts

## Overview

This document outlines a proposed architecture for the ANUS (Autonomous Networked Utility System) framework, thoughtfully adapting valuable concepts from OpenManus while enhancing them to fulfill ANUS's unique vision. The design maintains ANUS's intended structure while incorporating OpenManus's proven architectural patterns.

## Core Architecture

### Agent System

```
anus/
├── core/
│   ├── agent/
│   │   ├── base_agent.py       # Abstract foundation with core functionality
│   │   ├── react_agent.py      # Reasoning capabilities extension
│   │   ├── tool_agent.py       # Tool execution capabilities
│   │   └── hybrid_agent.py     # New: Switching between single/multi modes
│   ├── memory/
│   │   ├── base_memory.py      # Memory interface
│   │   ├── short_term.py       # Short-term memory implementation
│   │   └── long_term.py        # Long-term memory with persistence
│   └── orchestrator.py         # Agent coordination and management
```

#### Key Enhancements:
1. **HybridAgent**: Extends OpenManus's agent hierarchy with the ability to dynamically switch between single-agent and multi-agent modes based on task complexity
2. **Enhanced Memory System**: Expands OpenManus's basic memory with short-term and long-term memory components
3. **Orchestrator**: New component for coordinating multiple agents, not present in OpenManus

### Planning System

```
anus/
├── core/
│   ├── planning/
│   │   ├── base_planner.py     # Abstract planner interface
│   │   ├── task_planner.py     # Task breakdown and planning
│   │   ├── resource_planner.py # Resource allocation planning
│   │   └── plan.py             # Plan representation and tracking
│   └── flow/
│       ├── base_flow.py        # Abstract flow interface
│       ├── planning_flow.py    # Planning-based execution flow
│       ├── parallel_flow.py    # New: Parallel execution flow
│       └── consensus_flow.py   # New: Multi-agent consensus flow
```

#### Key Enhancements:
1. **Resource Planning**: Adds resource allocation capabilities to OpenManus's planning system
2. **Parallel Flow**: New flow type for executing steps in parallel when appropriate
3. **Consensus Flow**: New flow type for multi-agent collaboration with voting mechanisms

### Tool System

```
anus/
├── tools/
│   ├── base/
│   │   ├── tool.py             # Abstract tool foundation
│   │   ├── tool_result.py      # Standardized result handling
│   │   └── tool_collection.py  # Tool management
│   ├── web/
│   │   ├── browser.py          # Browser automation
│   │   ├── scraper.py          # Web content extraction
│   │   └── auth.py             # Authentication handling
│   ├── data/
│   │   ├── search.py           # Information retrieval
│   │   ├── document.py         # Document processing
│   │   └── database.py         # Database interactions
│   ├── code/
│   │   ├── executor.py         # Code execution sandbox
│   │   ├── analyzer.py         # Code analysis
│   │   └── generator.py        # Code generation
│   └── multimodal/
│       ├── image.py            # Image processing
│       ├── audio.py            # Audio processing
│       └── video.py            # Video processing
```

#### Key Enhancements:
1. **Categorized Tools**: Organizes tools into logical categories beyond OpenManus's flat structure
2. **Expanded Capabilities**: Adds new tool types for document processing, code analysis, and multimodal content
3. **Authentication Handling**: Adds specialized support for web authentication scenarios

### Model Integration

```
anus/
├── models/
│   ├── base_model.py           # Abstract model interface
│   ├── openai_model.py         # OpenAI API integration
│   ├── open_source_model.py    # Open-source model support
│   ├── local_model.py          # Local model deployment
│   └── model_router.py         # Dynamic model selection
```

#### Key Enhancements:
1. **Model Abstraction**: Extends OpenManus's LLM abstraction with support for multiple model types
2. **Model Router**: Adds dynamic model selection based on task requirements
3. **Local Deployment**: Adds support for running models locally for privacy and reduced costs

### User Interface

```
anus/
├── ui/
│   ├── cli.py                  # Command-line interface
│   ├── web/                    # Web interface components
│   │   ├── server.py           # Web server implementation
│   │   ├── static/             # Static assets
│   │   └── templates/          # HTML templates
│   └── api.py                  # RESTful API for integration
```

#### Key Enhancements:
1. **Multiple Interfaces**: Expands beyond OpenManus's CLI to include web and API interfaces
2. **Interactive Mode**: Adds support for interactive conversations and task monitoring
3. **API Integration**: Enables embedding ANUS in other applications

## Integration Points

### Configuration System

```python
# config.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

class ModelConfig(BaseModel):
    provider: str = "openai"
    model_name: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    
class MemoryConfig(BaseModel):
    type: str = "hybrid"  # "short_term", "long_term", "hybrid"
    persistence: bool = False
    storage_path: Optional[str] = None
    
class ToolConfig(BaseModel):
    browser: Dict = Field(default_factory=lambda: {"headless": True})
    code: Dict = Field(default_factory=lambda: {"sandbox": True})
    # Other tool configurations
    
class AgentConfig(BaseModel):
    name: str = "anus"
    mode: str = "single"  # "single", "multi"
    model: ModelConfig = Field(default_factory=ModelConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    max_steps: int = 30
```

### Agent Orchestration

```python
# orchestrator.py
from typing import Dict, List, Optional
from anus.core.agent.base_agent import BaseAgent
from anus.core.agent.hybrid_agent import HybridAgent
from anus.core.flow.base_flow import BaseFlow
from anus.core.flow.planning_flow import PlanningFlow
from anus.core.flow.consensus_flow import ConsensusFlow

class AgentOrchestrator:
    """Coordinates multiple agents and manages execution flows"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, BaseAgent] = {}
        self.primary_agent = self._create_primary_agent()
        
    def execute_task(self, task: str, mode: str = "single") -> str:
        """Execute a task using appropriate agents and flow"""
        if mode == "single":
            return self._execute_single_agent(task)
        else:
            return self._execute_multi_agent(task)
            
    def _execute_single_agent(self, task: str) -> str:
        """Execute task with single agent using planning flow"""
        flow = PlanningFlow(agents={"primary": self.primary_agent})
        return flow.execute(task)
        
    def _execute_multi_agent(self, task: str) -> str:
        """Execute task with multiple specialized agents"""
        # Create specialized agents if needed
        self._ensure_specialized_agents()
        
        # Use consensus flow for multi-agent execution
        flow = ConsensusFlow(agents=self.agents)
        return flow.execute(task)
        
    def _ensure_specialized_agents(self) -> None:
        """Create specialized agents if they don't exist"""
        roles = ["researcher", "coder", "planner", "critic"]
        for role in roles:
            if role not in self.agents:
                self.agents[role] = self._create_agent_for_role(role)
```

### Tool Registration

```python
# tool_registry.py
from typing import Dict, Type
from anus.tools.base.tool import BaseTool

class ToolRegistry:
    """Registry for tool discovery and instantiation"""
    
    _tools: Dict[str, Type[BaseTool]] = {}
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """Register a tool class"""
        cls._tools[tool_class.__name__] = tool_class
        return tool_class
        
    @classmethod
    def get_tool(cls, name: str) -> Type[BaseTool]:
        """Get a tool class by name"""
        if name not in cls._tools:
            raise ValueError(f"Tool {name} not registered")
        return cls._tools[name]
        
    @classmethod
    def create_tool(cls, name: str, **kwargs) -> BaseTool:
        """Create a tool instance by name"""
        tool_class = cls.get_tool(name)
        return tool_class(**kwargs)
        
    @classmethod
    def list_tools(cls) -> Dict[str, Type[BaseTool]]:
        """List all registered tools"""
        return cls._tools.copy()

# Usage example
@ToolRegistry.register
class BrowserTool(BaseTool):
    name = "browser"
    description = "Interact with web browser"
    # Implementation...
```

## Enhanced Concepts

### Hybrid Agent System

```python
# hybrid_agent.py
from typing import Dict, List, Optional
from anus.core.agent.tool_agent import ToolAgent
from anus.core.memory.base_memory import BaseMemory

class HybridAgent(ToolAgent):
    """
    Agent that can dynamically switch between single-agent and multi-agent modes
    based on task complexity and requirements.
    """
    
    name: str = "hybrid"
    description: str = "A versatile agent that can work alone or collaborate"
    
    # Additional fields for multi-agent mode
    sub_agents: Dict[str, ToolAgent] = {}
    collaboration_threshold: float = 0.7  # Complexity threshold for switching modes
    
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
        """Analyze task complexity to determine execution mode"""
        # Implementation using LLM to assess task complexity
        # Returns a value between 0 and 1
        
    async def _run_collaborative(self, request: str) -> str:
        """Execute request in collaborative multi-agent mode"""
        # Implementation of multi-agent collaboration
        # Creates sub-agents if needed, coordinates their work
```

### Consensus Mechanism

```python
# consensus_flow.py
from typing import Dict, List, Optional
from anus.core.agent.base_agent import BaseAgent
from anus.core.flow.base_flow import BaseFlow

class ConsensusFlow(BaseFlow):
    """
    Flow that coordinates multiple agents to reach consensus on complex tasks
    through voting and collaborative decision-making.
    """
    
    voting_threshold: float = 0.6  # Minimum agreement percentage for consensus
    max_rounds: int = 3  # Maximum voting rounds before fallback
    
    async def execute(self, input_text: str) -> str:
        """Execute the consensus flow with multiple agents"""
        # Break down the task
        task_components = await self._break_down_task(input_text)
        
        results = []
        for component in task_components:
            # Get solutions from all agents
            solutions = await self._gather_solutions(component)
            
            # Reach consensus through voting
            consensus = await self._reach_consensus(solutions)
            
            # Execute the consensus solution
            result = await self._execute_consensus(consensus, component)
            results.append(result)
            
        # Combine results
        return self._combine_results(results)
        
    async def _gather_solutions(self, task: str) -> Dict[str, str]:
        """Gather solutions from all agents"""
        solutions = {}
        for name, agent in self.agents.items():
            solution = await agent.run(task)
            solutions[name] = solution
        return solutions
        
    async def _reach_consensus(self, solutions: Dict[str, str]) -> str:
        """Reach consensus through voting mechanism"""
        # Implementation of voting and consensus algorithm
```

### Resource Allocation

```python
# resource_planner.py
from typing import Dict, List, Optional
from anus.core.planning.base_planner import BasePlanner

class ResourcePlanner(BasePlanner):
    """
    Planner that allocates computational resources based on task requirements
    and optimizes execution efficiency.
    """
    
    async def allocate_resources(self, plan: Dict) -> Dict:
        """Allocate resources to plan steps based on requirements"""
        enhanced_plan = plan.copy()
        
        # Analyze resource requirements for each step
        for i, step in enumerate(enhanced_plan.get("steps", [])):
            resources = await self._analyze_step_resources(step)
            enhanced_plan["step_resources"] = enhanced_plan.get("step_resources", [])
            enhanced_plan["step_resources"].append(resources)
            
        # Optimize resource allocation across steps
        enhanced_plan = await self._optimize_allocation(enhanced_plan)
        
        return enhanced_plan
        
    async def _analyze_step_resources(self, step: str) -> Dict:
        """Analyze resource requirements for a step"""
        # Implementation to determine CPU, memory, model, and tool requirements
        
    async def _optimize_allocation(self, plan: Dict) -> Dict:
        """Optimize resource allocation across steps"""
        # Implementation to balance resources and identify parallelization opportunities
```

## Implementation Strategy

The implementation strategy focuses on progressive enhancement, starting with core components and gradually adding advanced features:

1. **Phase 1: Core Framework**
   - Implement base agent, memory, and tool abstractions
   - Create basic planning system
   - Develop configuration system
   - Build CLI interface

2. **Phase 2: Tool Ecosystem**
   - Implement web interaction tools
   - Add information retrieval capabilities
   - Create document processing tools
   - Develop code execution sandbox

3. **Phase 3: Advanced Features**
   - Implement hybrid agent system
   - Add multi-agent collaboration
   - Develop consensus mechanisms
   - Create resource allocation system

4. **Phase 4: User Interfaces**
   - Enhance CLI with interactive features
   - Develop web interface
   - Create API for integration
   - Add visualization components

This phased approach ensures a solid foundation before adding more complex features, allowing for testing and refinement at each stage.
