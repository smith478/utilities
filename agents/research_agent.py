import os
import json
import time
import requests
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

class ResearchAgent:
    def __init__(self, 
                 model_name: str = "llama3",
                 data_dir: str = "/data",
                 ollama_url: str = "http://host.docker.internal:11434"):
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.ollama_url = ollama_url
        self.current_research_id = None
        self.research_context = {}
        
        # Create data directories if they don't exist
        self.artifacts_dir = self.data_dir / "artifacts"
        self.research_dir = self.data_dir / "research"
        self.artifacts_dir.mkdir(exist_ok=True, parents=True)
        self.research_dir.mkdir(exist_ok=True, parents=True)
    
    def _call_model(self, prompt: str, system: str = "", stream: bool = False) -> Dict[str, Any]:
        """Call the Ollama API with the given prompt and system message."""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system,
            "stream": stream
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        return response.json()
    
    def start_research(self, topic: str) -> str:
        """Start a new research session on the given topic."""
        # Create a unique ID for this research session
        timestamp = int(time.time())
        topic_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
        research_id = f"research_{topic_hash}_{timestamp}"
        
        # Create a directory for this research
        research_path = self.research_dir / research_id
        research_path.mkdir(exist_ok=True)
        
        # Initialize the research context
        self.current_research_id = research_id
        self.research_context = {
            "id": research_id,
            "topic": topic,
            "started_at": timestamp,
            "status": "started",
            "steps_completed": [],
            "current_step": "planning",
            "artifacts": [],
            "notes": [],
            "search_queries": [],
            "references": []
        }
        
        # Save the initial context
        self._save_research_context()
        
        # Generate a research plan
        plan = self._generate_research_plan(topic)
        self.research_context["plan"] = plan
        self._save_research_context()
        
        return research_id
    
    def _generate_research_plan(self, topic: str) -> List[Dict[str, str]]:
        """Generate a structured research plan for the topic."""
        system_prompt = """
        You are a research planning assistant. Given a research topic, create a structured
        plan with clear steps. Each step should be actionable and specific. Focus on:
        1. Initial exploration and concept definition
        2. Information gathering strategies
        3. Analysis methods
        4. Synthesis and deliverable creation
        
        Return the plan as a structured list of steps in JSON format.
        """
        
        user_prompt = f"Create a detailed research plan for the topic: {topic}"
        
        response = self._call_model(user_prompt, system_prompt)
        
        # Extract JSON from the response
        try:
            # Try to parse the entire response as JSON
            plan = json.loads(response["response"])
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the text
            try:
                text = response["response"]
                json_start = text.find('[')
                json_end = text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = text[json_start:json_end]
                    plan = json.loads(json_str)
                else:
                    # Fallback to generating a simple plan
                    plan = [
                        {"step": 1, "name": "Initial Research", "description": f"Gather basic information about {topic}"},
                        {"step": 2, "name": "Deep Dive", "description": "Explore key concepts and gather detailed information"},
                        {"step": 3, "name": "Analysis", "description": "Analyze and synthesize the gathered information"},
                        {"step": 4, "name": "Summary Creation", "description": "Create a comprehensive summary of findings"}
                    ]
            except:
                # Final fallback
                plan = [
                    {"step": 1, "name": "Initial Research", "description": f"Gather basic information about {topic}"},
                    {"step": 2, "name": "Deep Dive", "description": "Explore key concepts and gather detailed information"},
                    {"step": 3, "name": "Analysis", "description": "Analyze and synthesize the gathered information"},
                    {"step": 4, "name": "Summary Creation", "description": "Create a comprehensive summary of findings"}
                ]
        
        return plan
    
    def _save_research_context(self):
        """Save the current research context to disk."""
        if not self.current_research_id:
            return
            
        context_path = self.research_dir / self.current_research_id / "context.json"
        with open(context_path, 'w') as f:
            json.dump(self.research_context, f, indent=2)
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search the web for information related to the query."""
        # This is a placeholder; in a real implementation, you would:
        # 1. Use a search API (like SerpAPI, Google Custom Search, etc.)
        # 2. Process and extract relevant information
        
        # For demonstration, let's simulate a search response
        search_results = []
        try:
            # Here you would implement actual web search
            # For example using requests to call a search API
            
            # Record the search query
            if self.current_research_id:
                self.research_context["search_queries"].append({
                    "query": query,
                    "timestamp": int(time.time())
                })
                self._save_research_context()
                
            # Simulated results for demonstration
            search_results = [
                {"title": f"Result for {query} - 1", "url": "https://example.com/1", "snippet": "This is a simulated search result."},
                {"title": f"Result for {query} - 2", "url": "https://example.com/2", "snippet": "Another simulated search result."}
            ]
        except Exception as e:
            print(f"Search error: {e}")
            
        return search_results[:num_results]
    
    def run_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Run code and return the result."""
        result = {"success": False, "output": "", "error": ""}
        
        if language.lower() != "python":
            result["error"] = f"Language {language} is not supported yet."
            return result
            
        try:
            # Create a temporary file to run the code
            code_file = self.artifacts_dir / f"code_{int(time.time())}.py"
            with open(code_file, 'w') as f:
                f.write(code)
                
            # Run the code and capture output
            process = subprocess.run(
                ["python", str(code_file)], 
                capture_output=True, 
                text=True,
                timeout=30  # Set a timeout for safety
            )
            
            if process.returncode == 0:
                result["success"] = True
                result["output"] = process.stdout
            else:
                result["error"] = process.stderr
                
        except subprocess.TimeoutExpired:
            result["error"] = "Code execution timed out"
        except Exception as e:
            result["error"] = str(e)
            
        return result
    
    def save_artifact(self, content: str, filename: str, artifact_type: str = "text") -> str:
        """Save content as an artifact file."""
        if not self.current_research_id:
            raise ValueError("No active research session")
            
        # Ensure the filename is safe
        safe_filename = Path(filename).name
        
        # Create the artifact path
        artifact_path = self.artifacts_dir / self.current_research_id / safe_filename
        artifact_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Write the content
        with open(artifact_path, 'w') as f:
            f.write(content)
            
        # Record this artifact in the research context
        artifact_info = {
            "filename": safe_filename,
            "type": artifact_type,
            "created_at": int(time.time()),
            "path": str(artifact_path.relative_to(self.data_dir))
        }
        
        self.research_context["artifacts"].append(artifact_info)
        self._save_research_context()
        
        return str(artifact_path)
    
    def add_note(self, note: str) -> None:
        """Add a research note to the current session."""
        if not self.current_research_id:
            raise ValueError("No active research session")
            
        self.research_context["notes"].append({
            "content": note,
            "timestamp": int(time.time())
        })
        
        self._save_research_context()
    
    def generate_summary(self) -> str:
        """Generate a summary of the research findings."""
        if not self.current_research_id:
            raise ValueError("No active research session")
            
        # Prepare context for the summary
        context = {
            "topic": self.research_context["topic"],
            "notes": [note["content"] for note in self.research_context["notes"]],
            "artifacts": [a["filename"] for a in self.research_context["artifacts"]],
            "references": self.research_context["references"]
        }
        
        system_prompt = """
        You are a research summarization assistant. Generate a comprehensive summary
        of the research findings provided in the context. Include:
        
        1. An executive summary
        2. Key findings and insights
        3. Methodological approach
        4. Limitations and areas for further research
        
        Structure the summary in a clear, academic format.
        """
        
        user_prompt = f"Generate a research summary for topic: {context['topic']}\n\nResearch context: {json.dumps(context, indent=2)}"
        
        response = self._call_model(user_prompt, system_prompt)
        summary = response["response"]
        
        # Save the summary as an artifact
        summary_filename = f"summary_{int(time.time())}.md"
        self.save_artifact(summary, summary_filename, "summary")
        
        return summary
    
    def complete_research(self) -> Dict[str, Any]:
        """Mark the current research as complete and return a final report."""
        if not self.current_research_id:
            raise ValueError("No active research session")
            
        # Generate a final summary
        summary = self.generate_summary()
        
        # Update the research status
        self.research_context["status"] = "completed"
        self.research_context["completed_at"] = int(time.time())
        self._save_research_context()
        
        # Prepare the final report
        final_report = {
            "research_id": self.current_research_id,
            "topic": self.research_context["topic"],
            "summary": summary,
            "artifacts": self.research_context["artifacts"],
            "duration_seconds": self.research_context["completed_at"] - self.research_context["started_at"]
        }
        
        # Save the final report
        report_path = self.research_dir / self.current_research_id / "final_report.json"
        with open(report_path, 'w') as f:
            json.dump(final_report, f, indent=2)
            
        return final_report
    
    def load_research(self, research_id: str) -> bool:
        """Load a previous research session."""
        research_path = self.research_dir / research_id
        context_path = research_path / "context.json"
        
        if not context_path.exists():
            return False
            
        try:
            with open(context_path, 'r') as f:
                self.research_context = json.load(f)
                
            self.current_research_id = research_id
            return True
        except Exception as e:
            print(f"Error loading research: {e}")
            return False
    
    def list_research_sessions(self) -> List[Dict[str, Any]]:
        """List all research sessions with basic metadata."""
        sessions = []
        
        for research_dir in self.research_dir.iterdir():
            if not research_dir.is_dir():
                continue
                
            context_path = research_dir / "context.json"
            if not context_path.exists():
                continue
                
            try:
                with open(context_path, 'r') as f:
                    context = json.load(f)
                    
                sessions.append({
                    "id": context["id"],
                    "topic": context["topic"],
                    "status": context["status"],
                    "started_at": context["started_at"],
                    "completed_at": context.get("completed_at")
                })
            except Exception as e:
                print(f"Error reading research session {research_dir.name}: {e}")
                
        return sessions