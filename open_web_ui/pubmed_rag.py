from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import os

class Pipeline:
    name = "PubMed RAG"
    description = "Retrieval-Augmented Generation using PubMed articles"
    
    class Valves(BaseModel):
        OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        PUBMED_IP: str = os.getenv("PUBMED_IP", "130.14.29.110")

    def __init__(self):
        self.valves = self.Valves()
        self.embed_model = None
        self.llm = None
        
        # Set up hostname resolution immediately
        self._setup_dns_resolution()

    def _setup_dns_resolution(self):
        """Configure DNS resolution for PubMed"""
        import socket
        from urllib3.util import connection

        # Original connection function
        _orig_create_connection = connection.create_connection
        
        # Store pubmed IP from environment variable
        pubmed_ip = self.valves.PUBMED_IP
        
        # Patched connection function
        def patched_create_connection(address, *args, **kwargs):
            host, port = address
            if host == "pubmed.ncbi.nlm.nih.gov":
                print(f"Resolving pubmed.ncbi.nlm.nih.gov to {pubmed_ip}")
                return _orig_create_connection((pubmed_ip, port), *args, **kwargs)
            return _orig_create_connection((host, port), *args, **kwargs)
        
        # Apply the patch
        connection.create_connection = patched_create_connection
        
        # Also add to hosts dictionary for other libraries
        if not hasattr(socket, '_orig_gethostbyname'):
            socket._orig_gethostbyname = socket.gethostbyname
            socket.gethostbyname = lambda x: pubmed_ip if x == "pubmed.ncbi.nlm.nih.gov" else socket._orig_gethostbyname(x)

    async def on_startup(self):
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama
        
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.llm = Ollama(model=self.valves.OLLAMA_MODEL, base_url=ollama_base_url)
        self.embed_model = OllamaEmbedding(model_name=self.valves.EMBEDDING_MODEL, base_url=ollama_base_url)
        print(f"Pipeline initialized with models: {self.valves.OLLAMA_MODEL} and {self.valves.EMBEDDING_MODEL}")

    async def on_shutdown(self):
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        from langchain_community.document_loaders import PubMedLoader
        from llama_index.core import VectorStoreIndex
        from llama_index.core.schema import Document as LlamaindexDocument
        
        try:
            print(f"Processing query: {user_message}")
            
            # Use modified requests session with retries
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            # Create PubMed loader without the incompatible parameter
            loader = PubMedLoader(
                query=user_message, 
                load_max_docs=3
            )
            
            print("Loading documents from PubMed...")
            docs = loader.load()
            print(f"Loaded {len(docs)} documents from PubMed")
            
            if not docs:
                return iter(["No relevant documents found in PubMed for your query. Please try a different medical or scientific topic."])
            
            # Limit document content to avoid excessive token usage
            truncated_docs = []
            for doc in docs:
                if len(doc.page_content) > 4000:
                    doc.page_content = doc.page_content[:4000] + "..."
                truncated_docs.append(doc)
            
            llama_docs = [
                LlamaindexDocument(
                    text=d.page_content,
                    metadata=d.metadata
                ) for d in truncated_docs
            ]
            
            print("Creating vector index...")
            index = VectorStoreIndex.from_documents(
                llama_docs,
                embed_model=self.embed_model
            )
            
            print("Querying index...")
            query_engine = index.as_query_engine(
                llm=self.llm,
                streaming=True
            )
            
            return query_engine.query(user_message).response_gen
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in pipeline: {str(e)}")
            print(error_trace)
            return iter([f"Error accessing PubMed: {str(e)}\n\nPlease try again with a different query or contact the administrator."])