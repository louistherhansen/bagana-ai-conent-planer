"""
Simple REST API for CrewAI — GET and POST only
Aligns with project-context/2.build/integration.md contract.

GET  /api/crew  — Health/description (no execution)
POST /api/crew  — Execute crew with JSON body { message?, user_input?, campaign_context?, language? }
Response: { status, output?, task_outputs? } or { status, error }
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent so crew.run is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="BAGANA AI Crew — Simple REST API",
    description="GET: health. POST: run CrewAI with JSON body.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREW_TIMEOUT_SEC = 300


class PostBody(BaseModel):
    message: Optional[str] = None
    user_input: Optional[str] = None
    campaign_context: Optional[str] = None
    language: Optional[str] = None

    class Config:
        extra = "ignore"


def get_python_cmd() -> str:
    import platform
    return "python3" if platform.system() != "Windows" else "python"


def run_crew_stdin(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Spawn python -m crew.run --stdin; write JSON to stdin, read JSON from stdout."""
    python_cmd = get_python_cmd()
    input_json = json.dumps(payload)
    try:
        result = subprocess.run(
            [python_cmd, "-m", "crew.run", "--stdin"],
            cwd=str(PROJECT_ROOT),
            input=input_json.encode(),
            capture_output=True,
            timeout=CREW_TIMEOUT_SEC,
            env={**dict(__import__("os").environ)},
        )
        out = result.stdout.decode().strip()
        if not out:
            err = result.stderr.decode().strip()
            return {"status": "error", "error": err or "No output from crew"}
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {"status": "error", "error": f"Invalid JSON: {out[:200]}"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Crew execution timed out"}
    except FileNotFoundError:
        return {"status": "error", "error": f"Python/crew not found: {python_cmd}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/api/crew")
def get_crew():
    """
    GET /api/crew — Health and description.
    Returns 200 with { status: "ok", message: "..." }.
    """
    return {
        "status": "ok",
        "message": "CrewAI REST API. POST /api/crew with JSON body { message } to run crew.",
    }


@app.post("/api/crew")
def post_crew(body: PostBody):
    """
    POST /api/crew — Run crew.
    Body: { message?, user_input?, campaign_context?, language? }
    Response: { status, output?, task_outputs? } or { status, error }.
    """
    message = body.message or body.user_input or body.campaign_context or ""
    if not (message and str(message).strip()):
        message = "No message provided."

    payload = {
        "user_input": message.strip(),
        "message": body.message,
        "campaign_context": body.campaign_context,
    }
    if body.language:
        payload["language"] = body.language
        payload["output_language"] = body.language

    result = run_crew_stdin(payload)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Crew failed"))

    return result


@app.get("/")
def root():
    return {"service": "BAGANA AI Crew REST API", "endpoints": ["GET /api/crew", "POST /api/crew"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
