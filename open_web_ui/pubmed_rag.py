from typing import Union, Generator, Iterator
from pydantic import BaseModel
from llama_index.core import Settings

class Pipeline:

    class Valves(BaseModel):
        LLAMAINDEX_OLLAMA_BASE_URL: str
        LLAMAINDEX_MODEL_NAME: str
        LLAMAINDEX_EMBEDDING_MODEL_NAME: str

    def __init__(self):
        self.valves = self.Valves(
            **{
                "LLAMAINDEX_OLLAMA_BASE_URL": "http://localhost:11434",
                "LLAMAINDEX_MODEL_NAME": "llama3.2", # "phi4-mini"
                "LLAMAINDEX_EMBEDDING_MODEL_NAME": "nomic-embed-text",
            }
        )
        self.embed_model = None
        self.llm = None

    async def on_startup(self):
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama

        # Initialize and store components
        self.embed_model = OllamaEmbedding(
            model_name=self.valves.LLAMAINDEX_EMBEDDING_MODEL_NAME,
            base_url=self.valves.LLAMAINDEX_OLLAMA_BASE_URL
        )
        self.llm = Ollama(
            model=self.valves.LLAMAINDEX_MODEL_NAME,
            base_url=self.valves.LLAMAINDEX_OLLAMA_BASE_URL
        )

        # Configure global settings
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm

    def query(self, user_message: str) -> Union[str, Generator, Iterator]:
        from langchain_community.document_loaders import PubMedLoader
        from llama_index.core import VectorStoreIndex
        from llama_index.core.schema import Document as LlamaindexDocument

        loader = PubMedLoader(query=user_message, load_max_docs=3)
        langchain_docs = loader.load()

        llama_docs = [LlamaindexDocument(
            text=doc.page_content,
            metadata=doc.metadata
        ) for doc in langchain_docs]

        # Create index with explicit components
        index = VectorStoreIndex.from_documents(
            llama_docs,
            embed_model=self.embed_model,
            llm=self.llm
        )

        query_engine = index.as_query_engine(
            streaming=True,
            llm=self.llm,
            embed_model=self.embed_model
        )

        response = query_engine.query(user_message)
        return response.response_gen