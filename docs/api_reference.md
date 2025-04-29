# API Reference

This document provides a comprehensive reference for the Anus AI API.

## Core Components

### Agent

The `Agent` class is the primary interface for interacting with the Anus AI system.

```python
from anus import Agent

agent = Agent(
    model="gpt-4o",
    tools=["search", "browser", "code"],
    memory_type="persistent",
    verbose=True
)
```

#### Parameters

- `model` (str, optional): The LLM model to use. Defaults to "gpt-4o".
- `tools` (list, optional): List of tools to enable. Defaults to None.
- `memory_type` (str, optional): Type of memory to use. Options: "ephemeral", "persistent". Defaults to "ephemeral".
- `verbose` (bool, optional): Whether to print verbose output. Defaults to False.
- `config` (Config, optional): Custom configuration object. Defaults to None.

#### Methods

##### run

```python
response = agent.run("Find the latest news about artificial intelligence")
```

**Parameters:**
- `task` (str): The task to execute.
- `mode` (str, optional): Execution mode. Options: "sync", "async". Defaults to "sync".
- `output_format` (str, optional): Format for the output. Options: "text", "markdown", "json". Defaults to "text".

**Returns:**
- `str`: The agent's response to the task.

##### chat

```python
response = agent.chat("What is the capital of France?")
```

**Parameters:**
- `message` (str): The message to send to the agent.
- `context` (dict, optional): Additional context for the conversation. Defaults to None.

**Returns:**
- `str`: The agent's response to the message.

##### save_memory

```python
agent.save_memory("memory.json")
```

**Parameters:**
- `path` (str): Path to save the memory to.

**Returns:**
- `bool`: True if successful, False otherwise.

##### load_memory

```python
agent.load_memory("memory.json")
```

**Parameters:**
- `path` (str): Path to load the memory from.

**Returns:**
- `bool`: True if successful, False otherwise.

### Society

The `Society` class enables multi-agent collaboration.

```python
from anus import Society, Agent

researcher = Agent(role="researcher")
analyst = Agent(role="analyst")
writer = Agent(role="writer")

society = Society(
    agents=[researcher, analyst, writer],
    coordination_strategy="consensus",
    verbose=True
)
```

#### Parameters

- `agents` (list): List of Agent objects.
- `coordination_strategy` (str, optional): Strategy for agent coordination. Options: "consensus", "hierarchical", "autonomous". Defaults to "consensus".
- `verbose` (bool, optional): Whether to print verbose output. Defaults to False.
- `config` (Config, optional): Custom configuration object. Defaults to None.

#### Methods

##### run

```python
response = society.run("Research the impact of AI on healthcare")
```

**Parameters:**
- `task` (str): The task to execute.
- `mode` (str, optional): Execution mode. Options: "sync", "async". Defaults to "sync".
- `output_format` (str, optional): Format for the output. Options: "text", "markdown", "json". Defaults to "text".

**Returns:**
- `str`: The society's response to the task.

##### add_agent

```python
society.add_agent(new_agent)
```

**Parameters:**
- `agent` (Agent): The agent to add to the society.

**Returns:**
- `bool`: True if successful, False otherwise.

##### remove_agent

```python
society.remove_agent(agent_id)
```

**Parameters:**
- `agent_id` (str): ID of the agent to remove.

**Returns:**
- `bool`: True if successful, False otherwise.

### Config

The `Config` class provides configuration options for the Anus AI system.

```python
from anus import Config

config = Config(
    llm={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.7,
    },
    memory={
        "type": "persistent",
        "path": "./agent_memory",
    },
    tools={
        "browser": {"headless": False},
        "code": {"sandbox": True},
    }
)
```

#### Parameters

- `llm` (dict, optional): LLM configuration.
- `memory` (dict, optional): Memory configuration.
- `tools` (dict, optional): Tool configuration.
- `ui` (dict, optional): UI configuration.
- `logging` (dict, optional): Logging configuration.

## Tools

### SearchTool

```python
from anus.tools import SearchTool

search_tool = SearchTool(
    engine="google",
    max_results=5
)
```

#### Parameters

- `engine` (str, optional): Search engine to use. Options: "google", "bing", "duckduckgo". Defaults to "google".
- `max_results` (int, optional): Maximum number of results to return. Defaults to 5.

### BrowserTool

```python
from anus.tools import BrowserTool

browser_tool = BrowserTool(
    headless=True,
    timeout=30
)
```

#### Parameters

- `headless` (bool, optional): Whether to run the browser in headless mode. Defaults to True.
- `timeout` (int, optional): Timeout in seconds for browser operations. Defaults to 30.

### DocumentTool

```python
from anus.tools import DocumentTool

document_tool = DocumentTool(
    supported_formats=["pdf", "docx", "xlsx"]
)
```

#### Parameters

- `supported_formats` (list, optional): List of supported document formats. Defaults to ["pdf", "docx", "xlsx", "pptx"].

### CodeTool

```python
from anus.tools import CodeTool

code_tool = CodeTool(
    sandbox=True,
    timeout=10
)
```

#### Parameters

- `sandbox` (bool, optional): Whether to run code in a sandbox. Defaults to True.
- `timeout` (int, optional): Timeout in seconds for code execution. Defaults to 10.

## Command-Line Interface

The Anus AI CLI provides a command-line interface for interacting with the system.

### Commands

#### run

```bash
anus run "Find the latest news about artificial intelligence"
```

**Options:**
- `--config`: Path to configuration file.
- `--mode`: Agent mode (single or multi).
- `--verbose`: Enable verbose output.
- `--output`: Output format (text, markdown, json).

#### interactive

```bash
anus interactive
```

**Options:**
- `--config`: Path to configuration file.
- `--mode`: Agent mode (single or multi).
- `--verbose`: Enable verbose output.

#### init

```bash
anus init
```

**Options:**
- `--force`: Overwrite existing configuration.
- `--minimal`: Create minimal configuration.

#### version

```bash
anus version
```

Displays the current version of Anus AI.

## Error Handling

Anus AI provides a comprehensive error handling system.

### AnusError

Base class for all Anus AI errors.

### ConfigError

Raised when there is an issue with the configuration.

### ModelError

Raised when there is an issue with the LLM model.

### ToolError

Raised when there is an issue with a tool.

### MemoryError

Raised when there is an issue with the memory system.

## Examples

### Basic Usage

```python
from anus import Agent

agent = Agent()
response = agent.run("What is the capital of France?")
print(response)
```

### Multi-Agent Collaboration

```python
from anus import Society, Agent

researcher = Agent(role="researcher")
analyst = Agent(role="analyst")
writer = Agent(role="writer")

society = Society(agents=[researcher, analyst, writer])
response = society.run("Research the impact of AI on healthcare")
print(response)
```

### Custom Configuration

```python
from anus import Agent, Config

config = Config(
    llm={
        "provider": "anthropic",
        "model": "claude-3-opus",
        "temperature": 0.7,
    },
    memory={
        "type": "persistent",
        "path": "./agent_memory",
    },
    tools={
        "browser": {"headless": False},
        "code": {"sandbox": True},
    }
)

agent = Agent(config=config)
response = agent.run("Create an interactive data visualization for climate change data")
print(response)
```
