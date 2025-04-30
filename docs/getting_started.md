# Getting Started with seeker-o1 AI

This guide will help you get started with using the seeker-o1 AI framework for your projects.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

### Quick Installation

The easiest way to install seeker-o1 AI is via pip:

```bash
pip install seeker-o1-ai
```

### Development Installation

If you want to contribute to seeker-o1 AI or use the latest development version:

```bash
# Clone the repository
git clone https://github.com/seeker-o1-ai/seeker-o1.git
cd seeker-o1

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Configuration

After installation, you'll need to configure seeker-o1 AI with your API keys:

1. Create a configuration file:

```bash
seeker-o1 init
```

2. Edit the generated `.seeker-o1/config.yaml` file with your API keys:

```yaml
llm:
  provider: openai
  api_key: your_openai_api_key
  model: gpt-4o

# Optional: Configure other providers
anthropic:
  api_key: your_anthropic_api_key
```

## Your First seeker-o1 AI Project

### Simple Question Answering

Create a file named `simple_question.py`:

```python
from seeker-o1 import Agent

# Create a single agent
agent = Agent()

# Ask a simple question
response = agent.run("What is the capital of France?")
print(response)
```

Run the script:

```bash
python simple_question.py
```

### Web Search Example

Create a file named `web_search.py`:

```python
from seeker-o1 import Agent
from seeker-o1.tools import SearchTool

# Create an agent with search capabilities
agent = Agent(tools=[SearchTool()])

# Search for information
response = agent.run("Find the latest research on quantum computing")
print(response)
```

Run the script:

```bash
python web_search.py
```

### Multi-Agent Collaboration

Create a file named `multi_agent.py`:

```python
from seeker-o1 import Society, Agent

# Create specialized agents
researcher = Agent(role="researcher")
analyst = Agent(role="analyst")
writer = Agent(role="writer")

# Create a society of agents
society = Society(agents=[researcher, analyst, writer])

# Execute a complex task with collaboration
response = society.run(
    "Research the impact of artificial intelligence on healthcare, " 
    "analyze the findings, and write a comprehensive report"
)
print(response)
```

Run the script:

```bash
python multi_agent.py
```

## Using the Command-Line Interface

seeker-o1 AI comes with a powerful command-line interface:

```bash
# Run a simple task
seeker-o1 run "What is the population of Tokyo?"

# Run in interactive mode
seeker-o1 interactive

# Run with a specific configuration file
seeker-o1 run --config custom_config.yaml "Summarize this article: https://example.com/article"
```

## Next Steps

- Explore the [Documentation](https://seeker-o1-ai.github.io/docs) for more detailed information
- Check out the [Examples](https://github.com/nikmcfly/seeker-o1/tree/main/examples) directory for more use cases
- Join our [Community](https://t.me/goseeker-o1) to connect with other users and developers
- Consider [Contributing](https://github.com/nikmcfly/seeker-o1/blob/main/CONTRIBUTING.md) to the project

## Getting Help

If you encounter any issues or have questions:

- Check the [FAQ](https://seeker-o1-ai.github.io/docs/faq)
- Search for existing [Issues](https://github.com/nikmcfly/seeker-o1/issues)
- Ask for help in our [Telegram channel](https://t.me/goseeker-o1)
- Open a new [Issue](https://github.com/nikmcfly/seeker-o1/issues/new) if you found a bug
