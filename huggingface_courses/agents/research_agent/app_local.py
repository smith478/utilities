import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from smolagents import CodeAgent, DuckDuckGoSearchTool, FinalAnswerTool, Tool, tool
from smolagents.models import LiteLLMModel

# Global storage for research sessions (in a real app, you'd use a database)
RESEARCH_SESSIONS = {}
CURRENT_SESSION_ID = None

@tool
def start_research_session(topic: str) -> str:
    """
    Start a new research session on a given topic.
    
    Args:
        topic: The research topic to investigate
    
    Returns:
        Research session ID
    """
    global CURRENT_SESSION_ID
    
    # Create unique session ID
    timestamp = int(time.time())
    topic_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
    session_id = f"research_{topic_hash}_{timestamp}"
    
    # Initialize session
    RESEARCH_SESSIONS[session_id] = {
        "id": session_id,
        "topic": topic,
        "started_at": timestamp,
        "status": "active",
        "notes": [],
        "search_queries": [],
        "findings": [],
        "artifacts": []
    }
    
    CURRENT_SESSION_ID = session_id
    return f"Started research session '{session_id}' for topic: {topic}"

@tool
def add_research_note(note: str) -> str:
    """
    Add a note to the current research session.
    
    Args:
        note: The research note to add
    
    Returns:
        Confirmation message
    """
    if not CURRENT_SESSION_ID or CURRENT_SESSION_ID not in RESEARCH_SESSIONS:
        return "No active research session. Please start a research session first."
    
    RESEARCH_SESSIONS[CURRENT_SESSION_ID]["notes"].append({
        "content": note,
        "timestamp": int(time.time())
    })
    
    return f"Added note to research session: {note[:50]}..."

@tool
def record_finding(finding: str, source: str = "analysis") -> str:
    """
    Record a key finding from the research.
    
    Args:
        finding: The key finding or insight
        source: Source of the finding (e.g., 'web_search', 'analysis', 'synthesis')
    
    Returns:
        Confirmation message
    """
    if not CURRENT_SESSION_ID or CURRENT_SESSION_ID not in RESEARCH_SESSIONS:
        return "No active research session. Please start a research session first."
    
    RESEARCH_SESSIONS[CURRENT_SESSION_ID]["findings"].append({
        "content": finding,
        "source": source,
        "timestamp": int(time.time())
    })
    
    return f"Recorded finding: {finding[:50]}..."

@tool
def save_research_artifact(content: str, filename: str, artifact_type: str = "text") -> str:
    """
    Save content as a research artifact.
    
    Args:
        content: The content to save
        filename: Name for the artifact file
        artifact_type: Type of artifact (text, summary, analysis, etc.)
    
    Returns:
        Success message with file path
    """
    if not CURRENT_SESSION_ID or CURRENT_SESSION_ID not in RESEARCH_SESSIONS:
        return "No active research session. Please start a research session first."
    
    # Create artifacts directory if it doesn't exist
    artifacts_dir = Path("research_artifacts") / CURRENT_SESSION_ID
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the file
    file_path = artifacts_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Record in session
    RESEARCH_SESSIONS[CURRENT_SESSION_ID]["artifacts"].append({
        "filename": filename,
        "type": artifact_type,
        "path": str(file_path),
        "created_at": int(time.time())
    })
    
    return f"Saved artifact '{filename}' to {file_path}"

@tool
def get_research_status() -> str:
    """
    Get the current status of the active research session.
    
    Returns:
        Summary of current research session
    """
    if not CURRENT_SESSION_ID or CURRENT_SESSION_ID not in RESEARCH_SESSIONS:
        return "No active research session."
    
    session = RESEARCH_SESSIONS[CURRENT_SESSION_ID]
    
    status = f"""
Current Research Session: {session['id']}
Topic: {session['topic']}
Status: {session['status']}
Started: {time.ctime(session['started_at'])}

Notes: {len(session['notes'])} recorded
Search Queries: {len(session['search_queries'])} performed  
Key Findings: {len(session['findings'])} identified
Artifacts: {len(session['artifacts'])} saved

Recent Notes:
"""
    
    # Add last 3 notes
    for note in session['notes'][-3:]:
        status += f"- {note['content'][:100]}...\n"
    
    return status

class ResearchPlannerTool(Tool):
    name = "research_planner"
    description = """
    Creates a structured research plan for a given topic with actionable steps.
    """
    
    inputs = {
        "topic": {
            "type": "string", 
            "description": "The research topic to create a plan for"
        },
        "depth": {
            "type": "string",
            "description": "Research depth: 'overview', 'detailed', or 'comprehensive'",
            "nullable": True
        }
    }
    
    output_type = "string"
    
    def forward(self, topic: str, depth: str = "detailed"):
        plans = {
            "overview": [
                f"1. Initial search for '{topic}' to understand basic concepts",
                "2. Identify 3-5 key subtopics or aspects",
                "3. Gather basic information on each subtopic",
                "4. Create a brief summary of findings"
            ],
            "detailed": [
                f"1. Comprehensive search for '{topic}' and related terms",
                "2. Identify key concepts, definitions, and scope",
                "3. Research current state and recent developments",
                "4. Analyze different perspectives or approaches",
                "5. Look for case studies or practical examples",
                "6. Identify gaps or areas needing further research",
                "7. Synthesize findings into structured analysis"
            ],
            "comprehensive": [
                f"1. Literature review: Search for '{topic}' across multiple sources",
                "2. Historical context and background research",
                "3. Current state analysis and recent developments",
                "4. Comparative analysis of different approaches/methods",
                "5. Case studies and practical applications",
                "6. Expert opinions and thought leadership",
                "7. Challenges, limitations, and criticisms",
                "8. Future trends and implications",
                "9. Synthesis and gap analysis",
                "10. Comprehensive report generation"
            ]
        }
        
        plan_steps = plans.get(depth.lower(), plans["detailed"])
        
        research_plan = f"Research Plan for '{topic}' ({depth} level):\n\n"
        research_plan += "\n".join(plan_steps)
        research_plan += f"\n\nEstimated time: {len(plan_steps) * 10-15} minutes"
        
        return research_plan

@tool
def complete_research_session() -> str:
    """
    Complete the current research session and generate a final summary.
    
    Returns:
        Final research summary
    """
    if not CURRENT_SESSION_ID or CURRENT_SESSION_ID not in RESEARCH_SESSIONS:
        return "No active research session to complete."
    
    session = RESEARCH_SESSIONS[CURRENT_SESSION_ID]
    
    # Mark as completed
    session["status"] = "completed"
    session["completed_at"] = int(time.time())
    
    # Generate summary
    duration = session["completed_at"] - session["started_at"]
    
    summary = f"""
=== RESEARCH SESSION COMPLETE ===

Topic: {session['topic']}
Session ID: {session['id']}
Duration: {duration // 60} minutes, {duration % 60} seconds

=== SUMMARY ===
- {len(session['notes'])} research notes recorded
- {len(session['search_queries'])} searches performed
- {len(session['findings'])} key findings identified
- {len(session['artifacts'])} artifacts created

=== KEY FINDINGS ===
"""
    
    for i, finding in enumerate(session['findings'], 1):
        summary += f"{i}. {finding['content']} (Source: {finding['source']})\n"
    
    summary += "\n=== ARTIFACTS CREATED ===\n"
    for artifact in session['artifacts']:
        summary += f"- {artifact['filename']} ({artifact['type']})\n"
    
    # Save final summary
    if session['artifacts']:  # Only save if we have artifacts directory
        summary_file = f"final_summary_{session['id']}.txt"
        save_research_artifact(summary, summary_file, "final_summary")
    
    return summary

def create_research_agent():
    """Create and configure the research agent with all tools."""
    
    # Use Ollama with LiteLLM - make sure you have ollama running locally
    # You can start ollama and pull a model like: ollama pull llama3.1:8b
    model = LiteLLMModel(model_id="ollama/llama3.1:8b")
    
    agent = CodeAgent(
        tools=[
            DuckDuckGoSearchTool(),
            start_research_session,
            add_research_note,
            record_finding,
            save_research_artifact,
            get_research_status,
            ResearchPlannerTool(),
            complete_research_session,
            FinalAnswerTool()
        ],
        model=model,
        max_steps=20,
        verbosity_level=2
    )
    
    return agent

# Example usage
if __name__ == "__main__":
    # Create the research agent
    research_agent = create_research_agent()
    
    # Example research task
    research_topic = "Impact of artificial intelligence on software development workflows"
    
    research_request = f"""
    I need you to conduct research on: '{research_topic}'
    
    Please:
    1. Start a research session for this topic
    2. Create a detailed research plan
    3. Conduct web searches to gather information
    4. Take notes on key findings as you research
    5. Record the most important insights
    6. Create a summary document of your findings
    7. Complete the research session with a final report
    
    Focus on current trends, practical applications, and implications for developers.
    """
    
    print("Starting research agent...")
    result = research_agent.run(research_request)
    print("\n" + "="*50)
    print("RESEARCH COMPLETE")
    print("="*50)