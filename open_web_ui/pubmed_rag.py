from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import os

class Pipeline:

    class Valves(BaseModel):
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    def __init__(self):
        self.valves = self.Valves()
        self.embed_model = None
        self.llm = None

    async def on_startup(self):
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama
        
        self.llm = Ollama(model=self.valves.OLLAMA_MODEL)
        self.embed_model = OllamaEmbedding(model_name=self.valves.EMBEDDING_MODEL)

    async def on_shutdown(self):
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        from langchain_community.document_loaders import PubMedLoader
        from llama_index.core import VectorStoreIndex
        from llama_index.core.schema import Document as LlamaindexDocument

        # PubMed retrieval
        loader = PubMedLoader(query=user_message, load_max_docs=3)
        docs = loader.load()
        
        # Convert to LlamaIndex format
        llama_docs = [LlamaindexDocument(
            text=d.page_content,
            metadata=d.metadata
        ) for d in docs]

        # Create index
        index = VectorStoreIndex.from_documents(
            llama_docs,
            embed_model=self.embed_model
        )
        
        # Query engine
        query_engine = index.as_query_engine(
            llm=self.llm,
            streaming=True
        )
        
        return query_engine.query(user_message).response_gen