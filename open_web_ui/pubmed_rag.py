from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
import os
from pydantic import BaseModel

class Pipeline:

    class Valves(BaseModel):
        LLAMAINDEX_OLLAMA_BASE_URL: str
        LLAMAINDEX_MODEL_NAME: str
        LLAMAINDEX_EMBEDDING_MODEL_NAME: str

    def __init__(self):
        self.valves = self.Valves(
            **{
                "LLAMAINDEX_OLLAMA_BASE_URL": os.getenv("LLAMAINDEX_OLLAMA_BASE_URL", "http://localhost:11434"),
                "LLAMAINDEX_MODEL_NAME": os.getenv("LLAMAINDEX_MODEL_NAME", "llama3"),
                "LLAMAINDEX_EMBEDDING_MODEL_NAME": os.getenv("LLAMAINDEX_EMBEDDING_MODEL_NAME", "nomic-embed-text"),
            }
        )

    async def on_startup(self):
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama
        from llama_index.core import Settings

        Settings.embed_model = OllamaEmbedding(
            model_name=self.valves.LLAMAINDEX_EMBEDDING_MODEL_NAME,
            base_url=self.valves.LLAMAINDEX_OLLAMA_BASE_URL,
        )
        Settings.llm = Ollama(
            model=self.valves.LLAMAINDEX_MODEL_NAME,
            base_url=self.valves.LLAMAINDEX_OLLAMA_BASE_URL,
        )

    async def on_shutdown(self):
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        from langchain_community.document_loaders import PubMedLoader
        from llama_index.core import VectorStoreIndex
        from llama_index.core.schema import Document as LlamaindexDocument

        # Load PubMed documents
        loader = PubMedLoader(query=user_message, load_max_docs=3)
        langchain_docs = loader.load()

        # Convert to LlamaIndex documents
        llama_docs = [LlamaindexDocument(
            text=doc.page_content,
            metadata=doc.metadata
        ) for doc in langchain_docs]

        # Create and query index
        index = VectorStoreIndex.from_documents(llama_docs)
        query_engine = index.as_query_engine(streaming=True)
        response = query_engine.query(user_message)

        return response.response_gen