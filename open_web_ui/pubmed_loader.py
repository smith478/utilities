from langchain_community.document_loaders import PubMedLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize Hugging Face embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Example model
)

# PubMed Query (will be replaced by user input)
query = "machine learning in healthcare"  # Placeholder, will be overridden
max_docs = 10  # Adjust as needed

# Load PubMed data
loader = PubMedLoader(query=query, load_max_docs=max_docs)
docs = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = text_splitter.split_documents(docs)

# Initialize Chroma vector store
vector_store = Chroma(
    collection_name="open-webui",  # Match Open Web UI's collection
    persist_directory="/app/backend/data",  # Mounted volume path
    embedding_function=embeddings
)

# Add documents to Chroma
vector_store.add_documents(split_docs)
vector_store.persist()