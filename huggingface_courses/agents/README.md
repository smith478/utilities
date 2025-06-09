Course [link](https://huggingface.co/learn/agents-course/unit0/onboarding)

For this course we can use Ollama for model hosting. For example,

```python
from smolagents import LiteLLMModel

model = LiteLLMModel(
    model_id="ollama_chat/qwen2:7b",  # Or try other Ollama-supported models
    api_base="http://127.0.0.1:11434",  # Default Ollama local server
    num_ctx=8192,
)
```

To use LiteLLM, be sure to install the package:
```bash
pip install litellm
```