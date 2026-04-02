"""
FastAPI server for the compliance audit environment.

Starts a server on port 7860 that agents can connect to via WebSocket.
The server handles episode management, grading, and state tracking.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from root
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi.responses import HTMLResponse
from openenv.core.env_server import create_app

from models import ComplianceAction, ComplianceObservation
from server.compliance_environment import ComplianceEnvironment


# Create the FastAPI app
# The create_app factory handles all the WebSocket routing and state management
app = create_app(
    env=lambda: ComplianceEnvironment(),
    action_cls=ComplianceAction,
    observation_cls=ComplianceObservation,
    env_name="compliance-audit-env"
)


# Add a landing page at the root
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
            <strong>WebSocket Connection:</strong> <code>/ws</code><br>
            Connect your agent here to interact with the environment
        </div>
        
        <div class="endpoint">
            <strong>API Documentation:</strong> <a href="/docs"><code>/docs</code></a><br>
            Interactive API documentation (Swagger UI)
        </div>
        
        <div class="endpoint">
            <strong>Health Check:</strong> <a href="/health"><code>/health</code></a><br>
            Server status endpoint
        </div>
        
        <h2>Quick Start</h2>
        <pre><code>from client import EnvClient
from models import ComplianceAction

client = EnvClient(url="ws://localhost:7860/ws")
obs = client.reset(task="easy")
print(f"Company: {obs.company_name}")</code></pre>
        
        <h2>Tasks</h2>
        <ul>
            <li><strong>Easy:</strong> Straightforward violation detection (F1 scoring)</li>
            <li><strong>Medium:</strong> Category-based detection (partial credit)</li>
            <li><strong>Hard:</strong> Detection + compliant rewrites (composite scoring)</li>
        </ul>
        
        <p><a href="https://github.com/openenv-ai/openenv-core" target="_blank">Built with openenv-core</a> | <a href="https://huggingface.co/spaces/tusharpawar21/compliance-audit-env" target="_blank">View on HuggingFace</a></p>
    </body>
    </html>
    """


def main():
    """Main entry point for the server."""
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    # Run the server on port 7860 (HuggingFace Spaces standard)
    main()
