## Setup

We will create a python environment for this using `uv`

```bash
uv venv hf
source hf/bin/activate
uv pip install 'smolagents[litellm]' ollama jupyterlab duckduckgo-search opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-smolagents
```