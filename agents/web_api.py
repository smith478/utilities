from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os

from agent import ResearchAgent

app = FastAPI(title="Research Agent API")
research_agent = ResearchAgent(
    model_name=os.environ.get("OLLAMA_MODEL", "llama3"),
    data_dir=os.environ.get("DATA_DIR", "/data"),
    ollama_url=os.environ.get("OLLAMA_URL", "http://host.docker.internal:11434")
)

class ResearchRequest(BaseModel):
    topic: str

class SearchRequest(BaseModel):
    query: str
    num_results: int = 5

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

class ArtifactRequest(BaseModel):
    content: str
    filename: str
    artifact_type: str = "text"

class NoteRequest(BaseModel):
    content: str

@app.post("/research/start", response_model=Dict[str, str])
async def start_research(request: ResearchRequest):
    try:
        research_id = research_agent.start_research(request.topic)
        return {"research_id": research_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/research/{research_id}/status", response_model=Dict[str, Any])
async def get_research_status(research_id: str):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    return {
        "research_id": research_id,
        "status": research_agent.research_context.get("status", "unknown"),
        "topic": research_agent.research_context.get("topic", ""),
        "current_step": research_agent.research_context.get("current_step", ""),
        "artifact_count": len(research_agent.research_context.get("artifacts", [])),
        "note_count": len(research_agent.research_context.get("notes", []))
    }

@app.post("/research/{research_id}/search", response_model=List[Dict[str, str]])
async def search_web(research_id: str, request: SearchRequest):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    results = research_agent.search_web(request.query, request.num_results)
    return results

@app.post("/research/{research_id}/code/run", response_model=Dict[str, Any])
async def run_code(research_id: str, request: CodeExecutionRequest):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    result = research_agent.run_code(request.code, request.language)
    return result

@app.post("/research/{research_id}/artifact", response_model=Dict[str, str])
async def save_artifact(research_id: str, request: ArtifactRequest):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    try:
        path = research_agent.save_artifact(request.content, request.filename, request.artifact_type)
        return {"status": "saved", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/{research_id}/note", response_model=Dict[str, str])
async def add_note(research_id: str, request: NoteRequest):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    try:
        research_agent.add_note(request.content)
        return {"status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/{research_id}/summary", response_model=Dict[str, str])
async def generate_summary(research_id: str):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    try:
        summary = research_agent.generate_summary()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/{research_id}/complete", response_model=Dict[str, Any])
async def complete_research(research_id: str):
    if not research_agent.load_research(research_id):
        raise HTTPException(status_code=404, detail="Research session not found")
    
    try:
        report = research_agent.complete_research()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/research/list", response_model=List[Dict[str, Any]])
async def list_research_sessions():
    return research_agent.list_research_sessions()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)