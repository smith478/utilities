import asyncio
from pubmed_rag import Pipeline

async def main():
    # Initialize pipeline
    pipeline = Pipeline()
    
    # Simulate Open WebUI startup
    await pipeline.on_startup()
    
    # Test query
    test_query = "What are recent advancements in CRISPR gene editing?"
    
    # Run the pipeline
    response_gen = pipeline.pipe(
        user_message=test_query,
        model_id="llama3.2",
        messages=[],
        body={}
    )
    
    # Print streaming response
    print("Response:")
    for chunk in response_gen:
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())