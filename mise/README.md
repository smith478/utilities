# Getting Started with mise
Mise is a tool that serves the following purposes (from the [github repo](https://github.com/jdx/mise)):
- Like asdf (or nvm or pyenv but for any language) it manages dev tools like node, python, cmake, terraform, and hundreds more.
- Like direnv it manages environment variables for different project directories.
- Like make it manages tasks used to build and test projects.

## Installation

First, install mise using one of these methods:

```bash
# For macOS using Homebrew
brew install mise

# For Linux/WSL using curl
curl https://mise.run | sh
```

## Basic Commands

### Initialize mise
```bash
# Initialize mise in your project
mise init

# Create a .mise.toml file
mise use python@latest
```

### Managing Python Versions

```bash
# List available Python versions
mise ls python

# Install specific Python version
mise use python@3.11

# Show current Python version
mise current python
```

### Creating Virtual Environments

```bash
# Create a new virtual environment for your project
mise virtualenv create my-project

# Activate the virtual environment (automatic when using mise shell)
mise shell
```

### Managing Dependencies

Create a requirements.txt file:
```txt
flask==3.0.0
requests==2.31.0
```

Install dependencies:
```bash
mise install
```

## Practical Examples

### Example 1: Setting up a New Project
```bash
# Create and enter project directory
mkdir my-flask-app
cd my-flask-app

# Initialize mise and set Python version
mise init
mise use python@3.11

# Create virtual environment
mise virtualenv create flask-env

# Install Flask
mise install flask

# Verify installation
mise run python -c "import flask; print(flask.__version__)"
```

### Example 2: Managing Multiple Python Versions
```bash
# Project A with Python 3.9
cd project-a
mise use python@3.9
mise virtualenv create env-3.9

# Project B with Python 3.11
cd ../project-b
mise use python@3.11
mise virtualenv create env-3.11
```

### Example 3: Running Scripts
Add to .mise.toml:
```toml
[tasks]
start = "python app.py"
test = "pytest"
lint = "flake8"
```

Run tasks:
```bash
mise run start
mise run test
mise run lint
```

## Best Practices

1. Always create a `.mise.toml` file in your project root
2. Use virtual environments for project isolation
3. Pin your Python version in `.mise.toml`
4. Include environment-specific dependencies in requirements.txt
5. Use mise tasks for common operations

## Example

Here we will create a simple example project using JAX

Create a new directory for the project:
```bash
mkdir jax-example
cd jax-example
```

Create a mise.toml file
```yaml
[tool.mise]
python = "3.10"

[tools]
python = "3.10"
```

Create a requirements.txt file with the Python library dependencies
```
jax
jaxlib
numpy
matplotlib
```

Create and activate the environment
```bash
mise install
mise shell
```

Install dependencies
```bash
pip install -r requirements.txt
```

Verify installation
```bash
python -c "import jax; print(jax.__version__)"
```