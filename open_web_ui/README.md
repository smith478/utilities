## Open Web UI

Open web UI offers a nice front end for various LLM and deep learning models (including speech to text, text to speech, etc.). The github repo can be found [here](https://github.com/open-webui/open-webui).

Setup is easy using docker:
```bash
docker run -d -p 3000:8080 --gpus all -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```
To use tools like web search, the `docker-compose.yaml` can be used with:
```bash
docker-compose up -d
```

## Notes on tools

1. Speech-to-Text (STT)
    - Whisper V3 (or a faster variant) for high quality speech transcriptions. Additional good options can be found [here](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard).
    - Integrate Whisper as a Python function tool within Open WebUI. Create a tool in Open WebUI that routes audio input to Whisper and returns the transcribed text.
    - Setup
        ```python
        from transformers import pipeline
        stt_pipeline = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
        transcription = stt_pipeline("audio_file.wav")
        ```
2. Text-to-Speech (TTS)
    - Coqui TTS
    - Tortoise TTS
    - StyleTTS
    - Setup
        ```python
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", gpu=True)
        tts.tts_to_file(text="Findings show a fractured humerus.", file_path="output.wav")
        ```
3. Web based search
    - Use search API (e.g. DuckDuckGo, [SearXNG](https://docs.openwebui.com/tutorials/web-search/searxng), Google PSE, Brave Search). More documentation can be found [here](https://docs.openwebui.com/category/-web-search).
        - Create Brave account and create an API key. In your project root, create a file named .env containing your Brave API key. Docker Compose will automatically load variables from this file.
    - Implementation:
        Build a tool that accepts a query and then calls the chosen API to return a summary of results.
        Optionally, add a semantic search layer using sentence embeddings (e.g., with Hugging Face’s transformers) to better rank the relevance of articles.
    - Configuration:
        Set up API keys and endpoints in the Open WebUI environment.
    - Semantic search with RAG
    - Fetch from specific sites (e.g. PubMed/PMC API)
        - Generate embeddings with models like SPECTER or BioBERT
        - Store in a vector DB (e.g., FAISS, Pinecone, Qdrant) for similarity search.
    - Tools
        - LangChain for RAG pipelines.
        - Serper API (Google Search) for real-time queries.
    - Setup
        ```python
        from langchain.document_loaders import PubMedLoader
        loader = PubMedLoader(query="canine hip dysplasia radiology")
        docs = loader.load()
        # Process with SPECTER embeddings and FAISS
        ```
4. Multimodal Image Analysis 
    - DINOv2
    - MONAI
    - CheXpert/CheXnet
    - CLIP/BLIP-2
    - Setup
        ```python
        import monai
        model = monai.networks.nets.DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)
        # Load DICOM images with pydicom and preprocess
        ```

## Using custom data for RAG based search 

Here we will look at an example using pubmed based search. For this to work we will need to dynamically use the user chat query. This can be done in open web UI with a custom pipeline. Here are some useful resources:
[Open web UI pipelines](https://docs.openwebui.com/pipelines/)
[RAG pipeline example](https://github.com/open-webui/pipelines/blob/main/examples/pipelines/rag/llamaindex_pipeline.py)
[Open web UI functions](https://docs.openwebui.com/features/plugin/functions/)

To run a standalone test on the RAG pipeline
```bash
DEBUG=1 python test_pubmed_rag.py
```