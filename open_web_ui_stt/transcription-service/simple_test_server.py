from fastapi import FastAPI
import uvicorn
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-server")

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "Server is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "env_vars": dict(os.environ)}

if __name__ == "__main__":
    logger.info("Starting test server")
    uvicorn.run(app, host="0.0.0.0", port=8000)