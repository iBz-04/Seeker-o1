# CONTRIBUTING.md

# Contributing to Anus AI

Thank you for your interest in contributing to Anus AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by the [Anus AI Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/anus-ai/anus/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/anus-ai/anus/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

### Suggesting Enhancements

- Open a new issue with a clear title and detailed description.
- Provide specific examples and steps to demonstrate the enhancement.
- Explain why this enhancement would be useful to most Anus AI users.

### Your First Code Contribution

- Look for issues labeled "good first issue" or "help wanted" to find good starting points.
- Fork the repository and create a branch for your changes.
- Make your changes and submit a pull request.

### Pull Requests

- Fill in the required template.
- Do not include issue numbers in the PR title.
- Include screenshots and animated GIFs in your pull request whenever possible.
- Follow the coding standards.
- Document new code.
- End all files with a newline.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip or conda

### Setting Up Your Development Environment

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/anus.git
   cd anus
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate.
2. Update the CHANGELOG.md with details of changes.
3. The PR should work for Python 3.11 and above.
4. PRs require approval from at least one maintainer.
5. Once approved, a maintainer will merge your PR.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) for Python code style.
- Use [Black](https://github.com/psf/black) for code formatting.
- Use [isort](https://pycqa.github.io/isort/) for import sorting.
- Use [flake8](https://flake8.pycqa.org/) for linting.
- Use [mypy](https://mypy.readthedocs.io/) for type checking.

### Type Hints

- Use type hints for all function parameters and return values.
- Use `Optional` for parameters that can be `None`.
- Use `Union` for parameters that can be multiple types.
- Use `Any` sparingly and only when necessary.

### Documentation

- Write docstrings for all functions, classes, and modules.
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings.
- Keep documentation up-to-date with code changes.

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `chore`: Changes to the build process or auxiliary tools

## Testing

- Write tests for all new features and bug fixes.
- Run the test suite before submitting a pull request:
  ```bash
  pytest
  ```
- Aim for high test coverage.
- Write both unit tests and integration tests.

## Documentation

- Update documentation for all new features and changes.
- Write clear and concise documentation.
- Include examples where appropriate.
- Check for spelling and grammar errors.

## Community

Join our community to get help, share ideas, and contribute to the project:

- [Telegram Channel](https://t.me/goanus)

Thank you for contributing to Anus AI!
