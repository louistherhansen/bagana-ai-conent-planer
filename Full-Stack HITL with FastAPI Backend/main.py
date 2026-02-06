"""
FastAPI Backend for Full-Stack Human-In-The-Loop (HITL) Workflows
Provides REST API endpoints for CrewAI execution with human feedback checkpoints.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
import asyncio
from datetime import datetime
from enum import Enum
import sys
from pathlib import Path

# Add parent directory to path for crew imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hitl_state_manager import (
    CheckpointState,
    ExecutionState,
    StateManager,
    FeedbackAction
)
from crew_integration import CrewExecutor

app = FastAPI(
    title="BAGANA AI HITL Backend",
    description="Human-In-The-Loop API for CrewAI workflows",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize state manager and crew executor
state_manager = StateManager()
crew_executor = CrewExecutor(state_manager)


# Request/Response Models
class CrewRequest(BaseModel):
    """Request model for crew execution."""
    message: Optional[str] = None
    user_input: Optional[str] = None
    campaign_context: Optional[str] = None
    language: Optional[str] = None
    checkpoints: Optional[List[str]] = Field(
        default=["after_planning", "after_analysis"],
        description="List of checkpoint names to enable"
    )


class FeedbackRequest(BaseModel):
    """Request model for submitting human feedback."""
    execution_id: str
    checkpoint_id: str
    action: str = Field(..., description="continue, stop, revise, skip")
    feedback: Optional[str] = None


class CheckpointResponse(BaseModel):
    """Response model for checkpoint information."""
    execution_id: str
    checkpoint_id: str
    checkpoint_name: str
    description: str
    context: Dict[str, Any]
    status: str
    created_at: str


class ExecutionStatusResponse(BaseModel):
    """Response model for execution status."""
    execution_id: str
    status: str
    current_checkpoint: Optional[str]
    completed_checkpoints: List[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "BAGANA AI HITL Backend",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "active_executions": len(state_manager.get_active_executions()),
        "pending_checkpoints": len(state_manager.get_pending_checkpoints())
    }


@app.post("/api/crew/execute", response_model=ExecutionStatusResponse)
async def execute_crew(
    request: CrewRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute CrewAI workflow with HITL checkpoints.
    
    Returns execution_id immediately and processes in background.
    Use /api/crew/status/{execution_id} to check progress.
    """
    execution_id = str(uuid.uuid4())
    
    # Prepare inputs
    inputs = {
        "user_input": request.user_input or request.message or "No input provided",
        "message": request.message,
        "campaign_context": request.campaign_context,
    }
    if request.language:
        inputs["language"] = request.language
        inputs["output_language"] = request.language
    
    # Initialize execution state
    state_manager.create_execution(
        execution_id=execution_id,
        inputs=inputs,
        checkpoints=request.checkpoints
    )
    
    # Start execution in background
    background_tasks.add_task(
        crew_executor.execute_with_hitl,
        execution_id=execution_id,
        inputs=inputs,
        checkpoints=request.checkpoints
    )
    
    return ExecutionStatusResponse(
        execution_id=execution_id,
        status="running",
        current_checkpoint=None,
        completed_checkpoints=[],
        result=None,
        error=None
    )


@app.get("/api/crew/status/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """Get current status of an execution."""
    execution = state_manager.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return ExecutionStatusResponse(
        execution_id=execution_id,
        status=execution.state.value,
        current_checkpoint=execution.current_checkpoint,
        completed_checkpoints=execution.completed_checkpoints,
        result=execution.result,
        error=execution.error
    )


@app.get("/api/crew/checkpoint/{execution_id}", response_model=CheckpointResponse)
async def get_current_checkpoint(execution_id: str):
    """Get current pending checkpoint for an execution."""
    checkpoint = state_manager.get_pending_checkpoint(execution_id)
    
    if not checkpoint:
        execution = state_manager.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        if execution.state == ExecutionState.COMPLETED:
            raise HTTPException(status_code=400, detail="Execution already completed")
        if execution.state == ExecutionState.ERROR:
            raise HTTPException(status_code=400, detail="Execution failed")
        raise HTTPException(status_code=204, detail="No pending checkpoint")
    
    return CheckpointResponse(
        execution_id=checkpoint.execution_id,
        checkpoint_id=checkpoint.checkpoint_id,
        checkpoint_name=checkpoint.checkpoint_name,
        description=checkpoint.description,
        context=checkpoint.context,
        status=checkpoint.status.value,
        created_at=checkpoint.created_at.isoformat()
    )


@app.post("/api/crew/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit human feedback for a checkpoint.
    
    Actions:
    - continue: Proceed to next stage
    - stop: Stop execution
    - revise: Provide feedback for revision
    - skip: Skip this checkpoint
    """
    # Validate action
    try:
        action = FeedbackAction(request.action.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {[a.value for a in FeedbackAction]}"
        )
    
    # Submit feedback
    success = state_manager.submit_feedback(
        execution_id=request.execution_id,
        checkpoint_id=request.checkpoint_id,
        action=action,
        feedback=request.feedback
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Checkpoint not found or already processed"
        )
    
    # Resume execution if action is continue or skip
    if action in [FeedbackAction.CONTINUE, FeedbackAction.SKIP]:
        # Trigger execution continuation (in background)
        asyncio.create_task(
            crew_executor.resume_execution(request.execution_id)
        )
    
    return {
        "status": "feedback_received",
        "action": action.value,
        "execution_id": request.execution_id,
        "checkpoint_id": request.checkpoint_id
    }


@app.get("/api/crew/executions")
async def list_executions():
    """List all executions (for debugging/admin)."""
    executions = state_manager.list_executions()
    return {
        "executions": [
            {
                "execution_id": e.execution_id,
                "status": e.state.value,
                "created_at": e.created_at.isoformat(),
                "current_checkpoint": e.current_checkpoint
            }
            for e in executions
        ]
    }


@app.delete("/api/crew/execution/{execution_id}")
async def cancel_execution(execution_id: str):
    """Cancel a running execution."""
    success = state_manager.cancel_execution(execution_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {"status": "cancelled", "execution_id": execution_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
