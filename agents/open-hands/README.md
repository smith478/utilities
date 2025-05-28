## Setup

To get started using docker, pull the image:
```bash
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik
```

Next run the container with:
```bash
docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e LLM_custom_llm_provider=ollama \
    -e LLM_ollama_base_url=http://host.docker.internal:11434 \
    -e LLM_model=devstral:24b \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.39
```

Port mapping: -p 3000:3000 makes the OpenHands app available at http://localhost:3000.

After launching the application you will need to update the model settings. This can be done by clicking the gear icon on the bottom left, going to `LLM`, then toggle the `Advanced` option. Set:
- `Custom Model` to `ollama/devstral:24b`
- `Base URL` to `http://host.docker.internal:11434`
- `API Key` to `none`

## Github connection
In the settings (gear icon) there is a `Git` tab that allows you to set a GitHub Token. You can then instruct OpenHands to clone your repo by providing the repo URL.

## Local connection
From OpenHands documentation: A useful feature is the ability to connect to your local filesystem. To mount your filesystem into the runtime:

```bash
export SANDBOX_VOLUMES=/path/to/your/code:/workspace:rw

docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e LLM_custom_llm_provider=ollama \
    -e LLM_ollama_base_url=http://host.docker.internal:11434 \
    -e LLM_model=devstral:24b \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=$SANDBOX_VOLUMES \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.39
```

## Running on a GPU
If Ollama was running you will need to stop the current Ollama service and restart it with the correct environment variable.
```bash
sudo systemctl stop ollama
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

Now we can start the docker container.
```bash
docker run -it --rm --pull=always \
    --gpus all \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e LLM_custom_llm_provider=ollama \
    -e LLM_ollama_base_url=http://host.docker.internal:11434 \
    -e LLM_model=devstral:24b \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.39
```
or, if you prefer `localhost` instead of `host.docker.internal`:
```bash
docker run -it --rm --pull=always \
    --gpus all \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e LLM_custom_llm_provider=ollama \
    -e LLM_ollama_base_url=http://localhost:11434 \
    -e LLM_model=devstral:24b \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.39
```
If you also want your local code mounted in the GPU-enabled container:
```bash
export SANDBOX_VOLUMES=/path/to/your/code:/workspace:rw

sudo docker run -it --rm --pull=always \
    --gpus all \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.39-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e LLM_custom_llm_provider=ollama \
    -e LLM_ollama_base_url=http://localhost:11434 \
    -e LLM_model=devstral:24b \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=$SANDBOX_VOLUMES \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.39
```

NOTE: The GPU option above does not seem to work. An alternative approach is to use vLLM to create an OpenAI-compatible endpoint and then connect to that.
