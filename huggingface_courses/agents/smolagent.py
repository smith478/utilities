from smolagents import CodeAgent, DuckDuckGoSearchTool
from smolagents.models import LiteLLMModel
import os

# Make sure your Ollama server is running
# Initialize the model, pointing to your local Ollama instance
# The model name should be prefixed with "ollama_chat/"
local_model = LiteLLMModel(model_id="ollama_chat/qwen3:8b")

# Create the agent with the local model and search tool
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=local_model)

# Run the agent with your prompt
agent.run("Search for the best music recommendations for a party at the Wayne's mansion.")