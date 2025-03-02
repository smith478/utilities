FROM ghcr.io/open-webui/open-webui:main

RUN apt-get update && apt-get install -y \
    dnsutils \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    llama-index \
    llama-index-llms-ollama \
    llama-index-embeddings-ollama \
    langchain-community \
    python-dotenv \
    xmltodict