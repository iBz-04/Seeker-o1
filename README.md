
<div align="center">
   <h1>Seeker-o1 </h1>
</div>

<p align="center">
  <img src="https://res.cloudinary.com/diekemzs9/image/upload/v1746009112/extension_icon_1024px_jedbgf.png" alt="Seeker-o1 Logo" width="200"/>
</p>



## Table of Contents

- [Introduction](#-introduction)
- [Why Seeker-o1?](#-why-seeker-o1)
- [Features & Capabilities](#-features--capabilities)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Community](#-community)
- [License](#-license)

## 🌟 Introduction

**Seeker-o1**  is a powerful, flexible, and accessible open-source AI agent system designed to revolutionize task automation. It is also an upgrade and extension of  [@Seeker](https://github.com/iBz-04/Seeker)

Seeker-o1 empowers users to create AI agents that can:

- Execute tasks through natural language instructions
- Process text inputs
- Perform basic calculations
- Run code in a controlled environment

Whether you're a developer looking to build AI-powered applications, a researcher exploring agent-based systems, or an enthusiast interested in the latest AI technologies, Seeker-o1 provides the tools and flexibility you need to succeed.

## 💡 Why Seeker-o1?

- **Truly Open Source**: No barriers, no invite codes, just pure open-source goodness
- **Flexible Tool Architecture**: Easily create and add new tools to expand functionality
- **Transparent Operation**: Clear explanations of all agent actions and decisions
- **Cross-Platform**: Works across different operating systems and environments

## ✨ Features & Capabilities

### 🧠 AI Agent Architecture

- **Single-Agent System**: Process and execute tasks with a single agent
- **Tool Integration**: Use a variety of tools to accomplish tasks
- **Memory Management**: Basic context retention during conversation

### 🛠️ Current Tool Ecosystem

- **Text Processing**:
  - Character counting
  - Word counting
  - Text transformation (uppercase, lowercase, capitalize, reverse)

- **Code Execution**:
  - Python code execution
  - Output capture and analysis

- **Calculations**:
  - Basic arithmetic operations
  - Expression evaluation

### 🔄 API Integration

- **OpenAI API Support**: Seamless integration with GPT models


Seeker-o1 supports multiple installation methods to accommodate different user preferences and environments.

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git

### Installation:

```bash
# Clone the repository
git clone https://github.com/iBz-04/Seeker-o1.git
cd Seeker-o1

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Configuration

After installation, you'll need to configure Seeker-o1 with your API keys:

1. Create a `.env` file in the project root
2. Add your API keys:

```
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Quick Start

Once installed, you can start using Seeker-o1 with the provided examples:

```python
from seeker_o1.core.agent.tool_agent import ToolAgent

# Create an agent with calculator capabilities
agent = ToolAgent(tools=["calculator"])

# Execute a calculation
response = agent.execute("Calculate 2 + 2 * 3")
print(response)
```

## 📋 Usage Examples

### Basic Examples

#### Text Processing

```python
from seeker_o1.core.agent.tool_agent import ToolAgent

# Create an agent with text processing capabilities
agent = ToolAgent(tools=["text"])

# Process text
response = agent.execute("Count words in 'Hello, world!'")
print(response)
```

#### Code Execution

```python
from seeker_o1.core.agent.tool_agent import ToolAgent

# Create an agent with code execution capabilities
agent = ToolAgent(tools=["code"])

# Execute Python code
response = agent.execute("Run code ```print('Hello, world!')```")
print(response)
```

## 📖 Documentation

For more detailed information, please refer to the documentation in the `docs/` directory.

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get involved.

## 👥 Community

Join our community to discuss Seeker-o1, get help, and share your projects:

- [GitHub Discussions](https://github.com/nikmcfly/Seeker-o1/discussions)
- [Telegram Group](https://t.me/seeker_o1)

## 📄 License

Seeker-o1 is released under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 Seeker-o1 / Omnisoft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
