# Advanced Usage Guide

This document provides advanced usage examples and techniques for getting the most out of the Anus AI framework.

## Table of Contents
- [Multi-Agent Collaboration](#multi-agent-collaboration)
- [Custom Tool Development](#custom-tool-development)
- [Advanced Configuration](#advanced-configuration)
- [Memory Management](#memory-management)
- [Performance Optimization](#performance-optimization)
- [Integration with External Systems](#integration-with-external-systems)
- [Deployment Strategies](#deployment-strategies)

## Multi-Agent Collaboration

### Creating Specialized Agent Roles

You can create specialized agents with different roles to handle complex tasks:

```python
from anus import Agent, Society

# Create specialized agents
researcher = Agent(
    role="researcher",
    tools=["search", "browser"],
    model="gpt-4o"
)

analyst = Agent(
    role="analyst",
    tools=["code", "document"],
    model="claude-3-opus"
)

writer = Agent(
    role="writer",
    tools=["document"],
    model="gpt-4o"
)

# Create a society of agents
society = Society(
    agents=[researcher, analyst, writer],
    coordination_strategy="consensus"
)

# Execute a complex task with collaboration
response = society.run(
    "Research the impact of artificial intelligence on healthcare, " 
    "analyze the findings, and write a comprehensive report"
)
```

### Custom Coordination Strategies

Anus supports different coordination strategies for multi-agent collaboration:

```python
# Consensus strategy - all agents must agree on decisions
society = Society(
    agents=[agent1, agent2, agent3],
    coordination_strategy="consensus"
)

# Hierarchical strategy - one agent leads and delegates to others
society = Society(
    agents=[leader_agent, worker_agent1, worker_agent2],
    coordination_strategy="hierarchical",
    leader_agent_id=leader_agent.id
)

# Autonomous strategy - agents work independently and share results
society = Society(
    agents=[agent1, agent2, agent3],
    coordination_strategy="autonomous"
)
```

### Inter-Agent Communication

You can customize how agents communicate with each other:

```python
from anus import Society, Agent, CommunicationProtocol

# Create a custom communication protocol
protocol = CommunicationProtocol(
    message_format="structured",
    synchronization="async",
    logging=True
)

# Create a society with the custom protocol
society = Society(
    agents=[agent1, agent2, agent3],
    communication_protocol=protocol
)
```

## Custom Tool Development

### Creating a Custom Tool

You can create custom tools by extending the `BaseTool` class:

```python
from anus.tools import BaseTool
from typing import Dict, Any

class WeatherTool(BaseTool):
    """Tool for getting weather information."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.name = "weather_tool"
        self.description = "Gets weather information for a location"
    
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given parameters."""
        location = params.get("location")
        if not location:
            return {"error": "Location parameter is required"}
        
        # Implement weather API call here
        # ...
        
        return {
            "location": location,
            "temperature": 72,
            "conditions": "sunny",
            "humidity": 45
        }

# Use the custom tool
from anus import Agent

agent = Agent(tools=[WeatherTool(api_key="your_api_key")])
response = agent.run("What's the weather like in New York?")
```

### Tool Registration System

You can register custom tools with the tool registry:

```python
from anus.tools import register_tool, get_tool

# Register your custom tool
register_tool("weather", WeatherTool)

# Get the tool from the registry
weather_tool_class = get_tool("weather")
weather_tool = weather_tool_class(api_key="your_api_key")
```

### Tool Composition

You can compose multiple tools together:

```python
from anus.tools import ComposedTool, SearchTool, DocumentTool

# Create a composed tool that combines search and document processing
research_tool = ComposedTool(
    name="research_tool",
    tools=[SearchTool(), DocumentTool()],
    description="Searches for information and processes documents"
)

agent = Agent(tools=[research_tool])
```

## Advanced Configuration

### Environment-Specific Configuration

You can create different configurations for different environments:

```python
from anus import Config, Agent

# Development configuration
dev_config = Config.from_file("config.dev.yaml")

# Production configuration
prod_config = Config.from_file("config.prod.yaml")

# Choose configuration based on environment
import os
env = os.getenv("ANUS_ENV", "development")
config = dev_config if env == "development" else prod_config

agent = Agent(config=config)
```

### Dynamic Configuration

You can modify configuration at runtime:

```python
from anus import Agent, Config

# Create initial configuration
config = Config(
    llm={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7,
    }
)

# Create agent with initial config
agent = Agent(config=config)

# Modify configuration at runtime
agent.config.update({
    "llm": {
        "temperature": 0.2  # Lower temperature for more focused responses
    }
})

# Configuration changes take effect on next run
response = agent.run("Generate a creative story")
```

### Configuration Profiles

You can create and switch between configuration profiles:

```python
from anus import Agent, ConfigProfile

# Create configuration profiles
creative_profile = ConfigProfile(
    name="creative",
    llm={
        "temperature": 0.8,
        "top_p": 0.9
    }
)

precise_profile = ConfigProfile(
    name="precise",
    llm={
        "temperature": 0.2,
        "top_p": 0.5
    }
)

# Create agent with default configuration
agent = Agent()

# Switch to creative profile for creative tasks
agent.apply_profile(creative_profile)
creative_response = agent.run("Write a poem about AI")

# Switch to precise profile for factual tasks
agent.apply_profile(precise_profile)
precise_response = agent.run("Explain quantum computing")
```

## Memory Management

### Persistent Memory

You can save and load agent memory:

```python
from anus import Agent

# Create agent with persistent memory
agent = Agent(memory_type="persistent", memory_path="./agent_memory")

# Run some tasks
agent.run("Remember that my favorite color is blue")
agent.run("My birthday is on March 15")

# Save memory explicitly (also happens automatically on shutdown)
agent.save_memory()

# Later, create a new agent that loads the saved memory
new_agent = Agent(memory_type="persistent", memory_path="./agent_memory")

# The new agent remembers previous information
response = new_agent.run("What is my favorite color and when is my birthday?")
# Response will include blue and March 15
```

### Memory Types

Anus supports different types of memory:

```python
# Ephemeral memory (default) - lasts only for the current session
agent = Agent(memory_type="ephemeral")

# Persistent memory - saved to disk and can be loaded later
agent = Agent(memory_type="persistent", memory_path="./agent_memory")

# Vector memory - uses vector embeddings for more efficient retrieval
agent = Agent(memory_type="vector", memory_path="./vector_memory")

# Hybrid memory - combines different memory types
agent = Agent(memory_type="hybrid", memory_config={
    "short_term": "ephemeral",
    "long_term": "vector",
    "path": "./hybrid_memory"
})
```

### Memory Operations

You can perform operations on agent memory:

```python
# Add information to memory
agent.memory.add("User likes chocolate ice cream")

# Query memory
results = agent.memory.query("What does the user like?")

# Clear memory
agent.memory.clear()

# Get memory statistics
stats = agent.memory.stats()
print(f"Memory size: {stats['size']}, Items: {stats['items']}")
```

## Performance Optimization

### Batch Processing

You can process multiple tasks in batch for better performance:

```python
from anus import Agent

agent = Agent()

tasks = [
    "Summarize the benefits of exercise",
    "List 5 healthy breakfast ideas",
    "Explain the importance of sleep",
    "Provide tips for stress management",
    "Describe the benefits of meditation"
]

# Process tasks in batch
results = agent.batch_run(tasks, max_concurrency=3)

for task, result in zip(tasks, results):
    print(f"Task: {task}")
    print(f"Result: {result}")
    print("---")
```

### Caching

You can enable caching to improve performance for repeated tasks:

```python
from anus import Agent, CacheConfig

# Configure caching
cache_config = CacheConfig(
    enabled=True,
    ttl=3600,  # Cache entries expire after 1 hour
    max_size=1000  # Maximum number of cache entries
)

# Create agent with caching
agent = Agent(cache_config=cache_config)

# First call will execute normally
result1 = agent.run("What is the capital of France?")

# Second call with the same input will use cached result
result2 = agent.run("What is the capital of France?")  # Much faster
```

### Streaming Responses

You can stream responses for better user experience:

```python
from anus import Agent

agent = Agent()

# Stream the response
for chunk in agent.stream_run("Write a short story about a robot learning to feel emotions"):
    print(chunk, end="", flush=True)
```

## Integration with External Systems

### API Integration

You can expose Anus AI as an API:

```python
from fastapi import FastAPI
from anus import Agent
from pydantic import BaseModel

app = FastAPI()
agent = Agent()

class TaskRequest(BaseModel):
    task: str
    mode: str = "single"

@app.post("/run")
async def run_task(request: TaskRequest):
    response = agent.run(request.task, mode=request.mode)
    return {"result": response}

# Run with: uvicorn api:app --host 0.0.0.0 --port 8000
```

### Database Integration

You can integrate Anus with databases:

```python
import sqlite3
from anus import Agent

# Create a database connection
conn = sqlite3.connect("anus_data.db")
cursor = conn.cursor()

# Create a table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    task TEXT,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Create an agent
agent = Agent()

# Run a task and store the result
task = "Explain the theory of relativity"
result = agent.run(task)

# Store in database
cursor.execute("INSERT INTO tasks (task, result) VALUES (?, ?)", (task, result))
conn.commit()

# Query the database
cursor.execute("SELECT * FROM tasks")
for row in cursor.fetchall():
    print(row)

# Close the connection
conn.close()
```

### Webhook Integration

You can set up webhooks for asynchronous processing:

```python
from anus import Agent, WebhookConfig
import requests

# Configure webhooks
webhook_config = WebhookConfig(
    success_url="https://example.com/webhooks/success",
    failure_url="https://example.com/webhooks/failure",
    headers={"Authorization": "Bearer your_token"}
)

# Create agent with webhook configuration
agent = Agent(webhook_config=webhook_config)

# Run task asynchronously
task_id = agent.run_async("Generate a marketing plan for a new product")

# The result will be sent to the success or failure webhook
# You can also check the status
status = agent.get_task_status(task_id)
print(f"Task status: {status}")
```

## Deployment Strategies

### Docker Deployment

You can deploy Anus AI using Docker:

```bash
# Build the Docker image
docker build -t anus-ai .

# Run the container
docker run -p 8000:8000 -v ./config:/app/config -v ./data:/app/data anus-ai
```

### Kubernetes Deployment

For more complex deployments, you can use Kubernetes:

```yaml
# anus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anus-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: anus-ai
  template:
    metadata:
      labels:
        app: anus-ai
    spec:
      containers:
      - name: anus-ai
        image: anus-ai:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: config-volume
        configMap:
          name: anus-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: anus-data-pvc
```

### Serverless Deployment

You can deploy Anus AI as a serverless function:

```python
# AWS Lambda function
import json
from anus import Agent

agent = Agent()

def lambda_handler(event, context):
    task = event.get('task')
    if not task:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Task parameter is required'})
        }
    
    try:
        result = agent.run(task)
        return {
            'statusCode': 200,
            'body': json.dumps({'result': result})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

## Conclusion

This advanced usage guide demonstrates the flexibility and power of the Anus AI framework. By leveraging these advanced features, you can build sophisticated AI agent systems tailored to your specific needs.

For more information, refer to the [API Reference](api_reference.md) and [Architecture Overview](architecture_overview.md) documents.
