import asyncio
from pubmed_rag import Pipeline
from llama_index.core import Settings

async def main():
    pipeline = Pipeline()
    await pipeline.on_startup()

    # Test embedding model access
    sample_text = "Test embedding"
    try:
        embeddings = await pipeline.embed_model.aget_query_embedding(sample_text)
        print(f"\nEmbedding test successful (dimension: {len(embeddings)})")
    except AttributeError:
        print("\n⚠️ Embedding model not properly initialized!")
        return

    # Verify settings
    print(f"Embedding model: {type(Settings.embed_model).__name__}")
    print(f"LLM model: {type(Settings.llm).__name__}")
    
    test_query = "What are recent advancements in CRISPR gene editing?"

    # Test embedding model
    sample_text = "Test embedding"
    embeddings = await pipeline.embed_model.aget_query_embedding(sample_text)
    print(f"\nEmbedding test (dimension: {len(embeddings)}): {embeddings[:3]}...\n")
    
    print("Testing PubMed RAG Pipeline:")
    print(f"Query: {test_query}\n")
    
    # Show retrieved documents
    from langchain_community.document_loaders import PubMedLoader
    loader = PubMedLoader(query=test_query, load_max_docs=3)
    docs = loader.load()
    
    print("Retrieved Documents:")
    for i, doc in enumerate(docs):
        print(f"\nDocument {i+1}:")
        print(f"Title: {doc.metadata.get('Title', 'No title')}")
        print(f"Publication Date: {doc.metadata.get('Publication_Date', 'Unknown date')}")
        print(f"Summary: {doc.page_content[:300]}...\n")

    # Get response
    print("\nGenerated Response:")
    response_gen = pipeline.query(test_query)
    for chunk in response_gen:
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())