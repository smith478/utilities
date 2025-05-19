from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI
import os

ALLOWED_DIR = "agent_files"
if not os.path.exists(ALLOWED_DIR):
    os.makedirs(ALLOWED_DIR)

@tool
def manage_file(action: str, filename: str, content: str = None) -> str:
    """A tool to read, write, or append text to files in a specific directory.
    Args:
        action: The action to perform: "read", "write", or "append".
        filename: The name of the file (e.g., "notes.txt").
        content: The text content to write or append (required for "write" and "append").
    """
    filepath = os.path.join(ALLOWED_DIR, filename)

    # Basic path traversal prevention
    if not os.path.abspath(filepath).startswith(os.path.abspath(ALLOWED_DIR)):
        return "Error: Invalid filename or path."

    try:
        if action == "write":
            if content is None: return "Error: Content is required for write action."
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {filename}."
        elif action == "append":
            if content is None: return "Error: Content is required for append action."
            with open(filepath, 'a') as f:
                f.write(content + "\n")
            return f"Successfully appended to {filename}."
        elif action == "read":
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return f.read()
            else:
                return f"Error: File {filename} not found."
        else:
            return "Error: Invalid action. Use 'read', 'write', or 'append'."
    except Exception as e:
        return f"Error managing file {filename}: {str(e)}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
custom_role_conversions=None,
)


# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[manage_file, image_generation_tool, get_current_time_in_timezone, final_answer], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()