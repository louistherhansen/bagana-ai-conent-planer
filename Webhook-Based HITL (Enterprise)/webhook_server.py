"""
Enterprise Webhook Server for HITL Workflows
Handles webhook events from CrewAI with enterprise-grade features:
- Webhook signature verification
- Retry logic
- Event queuing
- Notification integrations
- Audit logging
"""

from fastapi import FastAPI, HTTPException, Request, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import hmac
import hashlib
import json
import time
from datetime import datetime
from enum import Enum
import asyncio
from webhook_event_processor import WebhookEventProcessor
from notification_service import NotificationService
from webhook_security import WebhookSecurity

app = FastAPI(
    title="BAGANA AI Enterprise Webhook Server",
    description="Enterprise-grade webhook handling for CrewAI HITL workflows",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
event_processor = WebhookEventProcessor()
notification_service = NotificationService()
security = WebhookSecurity()


class WebhookEventType(Enum):
    """Webhook event types."""
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    STEP_STARTED = "step.started"
    STEP_COMPLETED = "step.completed"
    CREW_STARTED = "crew.started"
    CREW_COMPLETED = "crew.completed"
    CREW_FAILED = "crew.failed"
    CHECKPOINT_REQUIRED = "checkpoint.required"


class WebhookPayload(BaseModel):
    """Webhook payload model."""
    event_type: Optional[str] = None
    kickoff_id: Optional[str] = None
    task_id: Optional[str] = None
    step_id: Optional[str] = None
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    checkpoint_id: Optional[str] = None
    checkpoint_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "BAGANA AI Enterprise Webhook Server",
        "status": "running",
        "version": "2.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "pending_events": event_processor.get_pending_count(),
        "processed_events": event_processor.get_processed_count()
    }


@app.post("/webhook/crewai")
async def receive_crewai_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_crewai_signature: Optional[str] = Header(None, alias="X-CrewAI-Signature"),
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret")
):
    """
    Receive webhook from CrewAI Cloud or local crew execution.
    
    Supports:
    - Signature verification
    - Event processing
    - Notification dispatch
    - Retry logic
    """
    try:
        # Get raw body for signature verification
        body_bytes = await request.body()
        body = await request.json()
        
        # Verify webhook signature
        secret = security.get_webhook_secret()
        if secret:
            signature = x_crewai_signature or x_webhook_secret
            if not signature or not security.verify_signature(body_bytes, signature, secret):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse webhook payload
        payload = WebhookPayload(**body)
        
        # Determine event type
        event_type = payload.event_type
        if not event_type:
            # Infer from payload structure
            if payload.checkpoint_id:
                event_type = WebhookEventType.CHECKPOINT_REQUIRED.value
            elif payload.status == "complete":
                event_type = WebhookEventType.CREW_COMPLETED.value
            elif payload.status == "error":
                event_type = WebhookEventType.CREW_FAILED.value
            else:
                event_type = WebhookEventType.CREW_STARTED.value
        
        # Process event in background
        background_tasks.add_task(
            process_webhook_event,
            event_type=event_type,
            payload=payload.dict(),
            raw_body=body
        )
        
        # Return immediately (webhook best practice)
        return JSONResponse(
            status_code=200,
            content={"received": True, "event_type": event_type}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error but return 200 to prevent retries for malformed requests
        return JSONResponse(
            status_code=200,
            content={"received": False, "error": str(e)}
        )


async def process_webhook_event(
    event_type: str,
    payload: Dict[str, Any],
    raw_body: Dict[str, Any]
):
    """
    Process webhook event asynchronously.
    """
    try:
        # Add timestamp if missing
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.utcnow().isoformat()
        
        # Process event based on type
        if event_type == WebhookEventType.CHECKPOINT_REQUIRED.value:
            await handle_checkpoint_required(payload)
        elif event_type == WebhookEventType.TASK_COMPLETED.value:
            await handle_task_completed(payload)
        elif event_type == WebhookEventType.CREW_COMPLETED.value:
            await handle_crew_completed(payload)
        elif event_type == WebhookEventType.CREW_FAILED.value:
            await handle_crew_failed(payload)
        else:
            # Generic event handling
            await event_processor.process_event(event_type, payload)
        
        # Send notifications
        await notification_service.send_event_notification(event_type, payload)
        
    except Exception as e:
        # Log error and potentially retry
        await event_processor.handle_error(event_type, payload, str(e))


async def handle_checkpoint_required(payload: Dict[str, Any]):
    """Handle checkpoint required event."""
    checkpoint_id = payload.get("checkpoint_id")
    checkpoint_name = payload.get("checkpoint_name", "unknown")
    context = payload.get("context", {})
    kickoff_id = payload.get("kickoff_id")
    
    # Store checkpoint state
    await event_processor.store_checkpoint(
        checkpoint_id=checkpoint_id,
        kickoff_id=kickoff_id,
        checkpoint_name=checkpoint_name,
        context=context
    )
    
    # Send notification to approvers
    await notification_service.send_checkpoint_notification(
        checkpoint_id=checkpoint_id,
        checkpoint_name=checkpoint_name,
        context=context
    )


async def handle_task_completed(payload: Dict[str, Any]):
    """Handle task completed event."""
    task_id = payload.get("task_id")
    result = payload.get("result", {})
    kickoff_id = payload.get("kickoff_id")
    
    # Store task result
    await event_processor.store_task_result(
        kickoff_id=kickoff_id,
        task_id=task_id,
        result=result
    )


async def handle_crew_completed(payload: Dict[str, Any]):
    """Handle crew completed event."""
    kickoff_id = payload.get("kickoff_id")
    result = payload.get("result", {})
    
    # Store final result
    await event_processor.store_crew_result(
        kickoff_id=kickoff_id,
        result=result
    )
    
    # Send completion notification
    await notification_service.send_completion_notification(
        kickoff_id=kickoff_id,
        result=result
    )


async def handle_crew_failed(payload: Dict[str, Any]):
    """Handle crew failed event."""
    kickoff_id = payload.get("kickoff_id")
    error = payload.get("error", "Unknown error")
    
    # Store error
    await event_processor.store_error(
        kickoff_id=kickoff_id,
        error=error
    )
    
    # Send failure notification
    await notification_service.send_failure_notification(
        kickoff_id=kickoff_id,
        error=error
    )


@app.post("/webhook/feedback")
async def receive_feedback_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None)
):
    """
    Receive feedback for a checkpoint.
    
    This endpoint is called by external systems (Slack, email, web UI)
    to submit human feedback for checkpoints.
    """
    try:
        # Verify authorization
        if not security.verify_authorization(authorization):
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        body = await request.json()
        checkpoint_id = body.get("checkpoint_id")
        action = body.get("action")  # continue, stop, revise, skip
        feedback = body.get("feedback")
        
        if not checkpoint_id or not action:
            raise HTTPException(status_code=400, detail="Missing checkpoint_id or action")
        
        # Process feedback
        background_tasks.add_task(
            event_processor.process_feedback,
            checkpoint_id=checkpoint_id,
            action=action,
            feedback=feedback
        )
        
        return {"status": "feedback_received", "checkpoint_id": checkpoint_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhook/checkpoint/{checkpoint_id}")
async def get_checkpoint(checkpoint_id: str):
    """Get checkpoint information."""
    checkpoint = await event_processor.get_checkpoint(checkpoint_id)
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return checkpoint


@app.get("/webhook/status/{kickoff_id}")
async def get_execution_status(kickoff_id: str):
    """Get execution status."""
    status = await event_processor.get_execution_status(kickoff_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
