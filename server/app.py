"""
FastAPI server for the compliance audit environment.

Starts a server on port 7860 that agents can connect to via HTTP and WebSocket.
The server handles episode management, grading, and state tracking.

Version: 2.0.0 - Custom FastAPI app with global state (like passed projects)
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

# Add parent directory to path so we can import from root
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from models import ComplianceAction, ComplianceObservation
from server.compliance_environment import ComplianceEnvironment


# Load openenv.yaml configuration
def load_openenv_config():
    """Load the openenv.yaml configuration file."""
    config_path = Path(__file__).parent.parent / "openenv.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# Global environment instance (persists state between requests)
_env: Optional[ComplianceEnvironment] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize environment on startup."""
    global _env
    _env = ComplianceEnvironment()
    yield
    _env = None


app = FastAPI(
    title="Compliance Audit Environment",
    description="OpenEnv environment for training AI agents to identify GDPR violations.",
    version="2.0.0",
    lifespan=lifespan,
)


def get_env() -> ComplianceEnvironment:
    """Get the environment instance."""
    global _env
    if _env is None:
        _env = ComplianceEnvironment()
    return _env


# Request/Response models
class ResetRequest(BaseModel):
    task_id: str = "easy"
    difficulty: Optional[str] = None  # Alias for task_id


class StepRequest(BaseModel):
    action: ComplianceAction


class ResetResponse(BaseModel):
    observation: dict
    reward: float = 0.0
    done: bool = False


class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool


# ---------------------------------------------------------------------------
# Core endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/reset")
async def reset(request: Optional[ResetRequest] = None):
    """Reset the environment for a new episode."""
    env = get_env()
    task_id = "easy"
    if request:
        task_id = request.difficulty or request.task_id
    
    try:
        observation = env.reset(task_id)
        return {
            "observation": observation.model_dump(),
            "reward": 0.0,
            "done": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step")
async def step(request: StepRequest):
    """Execute an action in the environment."""
    env = get_env()
    
    try:
        observation = env.step(request.action)
        return {
            "observation": observation.model_dump(),
            "reward": observation.reward,
            "done": observation.done
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
async def get_state():
    """Get the current state without taking an action."""
    env = get_env()
    if env._episode_state is None:
        return {"state": None, "info": {"step": 0, "max_steps": 3, "difficulty": "easy"}}
    
    return {
        "state": {
            "doc_id": env._episode_state.document["doc_id"],
            "company_name": env._episode_state.document["company_name"],
            "step_num": env._episode_state.step_num,
            "task_name": env._episode_state.task_name,
        },
        "info": {
            "step": env._episode_state.step_num,
            "max_steps": 3,
            "difficulty": env._episode_state.task_name,
        }
    }


# ---------------------------------------------------------------------------
# /tasks endpoint
# ---------------------------------------------------------------------------

@app.get("/tasks")
async def get_tasks():
    """Get list of available tasks."""
    config = load_openenv_config()
    tasks_config = config.get("tasks", [])
    
    if isinstance(tasks_config, list) and len(tasks_config) > 0:
        if isinstance(tasks_config[0], dict):
            return {"tasks": tasks_config}
    
    return {"tasks": []}


# ---------------------------------------------------------------------------
# /grader endpoint
# ---------------------------------------------------------------------------

@app.get("/grader")
async def get_grader():
    """Get current grader score for the active episode."""
    env = get_env()
    
    if env._episode_state is None:
        return {
            "score": 0.0,
            "step": 0,
            "max_steps": 3,
            "difficulty": "easy",
            "done": False,
        }
    
    return {
        "score": env._episode_state.previous_score if hasattr(env._episode_state, 'previous_score') else 0.0,
        "step": env._episode_state.step_num,
        "max_steps": 3,
        "difficulty": env._episode_state.task_name,
        "done": env._episode_state.step_num >= 3,
    }


# ---------------------------------------------------------------------------
# /graders endpoint
# ---------------------------------------------------------------------------

@app.get("/graders")
async def get_graders():
    """Get all grader configurations."""
    config = load_openenv_config()
    graders_config = config.get("graders", {})
    
    return {
        "graders": graders_config,
        "count": len(graders_config),
        "tasks_with_graders": ["easy", "medium", "hard"]
    }


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance Audit Environment</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #2563eb; }
            .badge { 
                display: inline-block;
                padding: 4px 12px;
                background: #10b981;
                color: white;
                border-radius: 12px;
                font-size: 14px;
                margin-left: 10px;
            }
            .endpoint {
                background: #f3f4f6;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #2563eb;
            }
            code {
                background: #1f2937;
                color: #10b981;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🔍 Compliance Audit Environment <span class="badge">RUNNING</span></h1>
        
        <p>A reinforcement learning environment for training AI agents to identify GDPR violations in privacy policies.</p>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <strong>Reset:</strong> <code>POST /reset</code><br>
            Start a new episode with {"task_id": "easy|medium|hard"}
        </div>
        
        <div class="endpoint">
            <strong>Step:</strong> <code>POST /step</code><br>
            Execute an action and get reward
        </div>
        
        <div class="endpoint">
            <strong>Tasks:</strong> <a href="/tasks"><code>GET /tasks</code></a><br>
            List available tasks with graders
        </div>
        
        <div class="endpoint">
            <strong>Grader:</strong> <a href="/grader"><code>GET /grader</code></a><br>
            Get current grader score
        </div>
        
        <div class="endpoint">
            <strong>Health Check:</strong> <a href="/health"><code>/health</code></a><br>
            Server status endpoint
        </div>
        
        <div class="endpoint">
            <strong>API Documentation:</strong> <a href="/docs"><code>/docs</code></a><br>
            Interactive API documentation (Swagger UI)
        </div>
        
        <h2>Tasks</h2>
        <ul>
            <li><strong>Easy:</strong> Straightforward violation detection (F1 scoring)</li>
            <li><strong>Medium:</strong> Category-based detection (partial credit)</li>
            <li><strong>Hard:</strong> Detection + compliant rewrites (composite scoring)</li>
        </ul>
        
        <p><a href="https://huggingface.co/spaces/tusharpawar21/compliance-audit-env" target="_blank">View on HuggingFace</a></p>
    </body>
    </html>
    """


def main():
    """Main entry point for the server."""
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
