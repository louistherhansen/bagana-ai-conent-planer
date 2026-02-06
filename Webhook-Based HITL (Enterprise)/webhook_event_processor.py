"""
Webhook Event Processor
Processes and stores webhook events with retry logic and error handling.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json
from enum import Enum


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEventProcessor:
    """Processes webhook events with enterprise features."""
    
    def __init__(self):
        self._events: Dict[str, Dict[str, Any]] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        self._executions: Dict[str, Dict[str, Any]] = {}
        self._retry_queue: list = []
        self._max_retries = 3
        self._retry_delay = 5  # seconds
    
    async def process_event(self, event_type: str, payload: Dict[str, Any]):
        """Process a webhook event."""
        event_id = f"{event_type}_{payload.get('kickoff_id', 'unknown')}_{datetime.utcnow().timestamp()}"
        
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
            "status": EventStatus.PROCESSING.value,
            "created_at": datetime.utcnow().isoformat(),
            "retry_count": 0
        }
        
        self._events[event_id] = event
        
        try:
            # Process based on event type
            if "checkpoint" in event_type:
                await self._process_checkpoint_event(payload)
            elif "task" in event_type:
                await self._process_task_event(payload)
            elif "crew" in event_type:
                await self._process_crew_event(payload)
            
            event["status"] = EventStatus.COMPLETED.value
            event["processed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            event["status"] = EventStatus.FAILED.value
            event["error"] = str(e)
            
            # Retry logic
            if event["retry_count"] < self._max_retries:
                event["retry_count"] += 1
                event["status"] = EventStatus.RETRYING.value
                await self._schedule_retry(event_id, event)
            else:
                # Max retries exceeded
                await self.handle_error(event_type, payload, str(e))
    
    async def _process_checkpoint_event(self, payload: Dict[str, Any]):
        """Process checkpoint event."""
        checkpoint_id = payload.get("checkpoint_id")
        if checkpoint_id:
            await self.store_checkpoint(
                checkpoint_id=checkpoint_id,
                kickoff_id=payload.get("kickoff_id"),
                checkpoint_name=payload.get("checkpoint_name", "unknown"),
                context=payload.get("context", {})
            )
    
    async def _process_task_event(self, payload: Dict[str, Any]):
        """Process task event."""
        task_id = payload.get("task_id")
        kickoff_id = payload.get("kickoff_id")
        
        if task_id and kickoff_id:
            await self.store_task_result(
                kickoff_id=kickoff_id,
                task_id=task_id,
                result=payload.get("result", {})
            )
    
    async def _process_crew_event(self, payload: Dict[str, Any]):
        """Process crew event."""
        kickoff_id = payload.get("kickoff_id")
        
        if kickoff_id:
            if payload.get("status") == "complete":
                await self.store_crew_result(
                    kickoff_id=kickoff_id,
                    result=payload.get("result", {})
                )
            elif payload.get("status") == "error":
                await self.store_error(
                    kickoff_id=kickoff_id,
                    error=payload.get("error", "Unknown error")
                )
    
    async def store_checkpoint(
        self,
        checkpoint_id: str,
        kickoff_id: Optional[str],
        checkpoint_name: str,
        context: Dict[str, Any]
    ):
        """Store checkpoint state."""
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "kickoff_id": kickoff_id,
            "checkpoint_name": checkpoint_name,
            "context": context,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "feedback": None
        }
        
        self._checkpoints[checkpoint_id] = checkpoint
        
        # Update execution state
        if kickoff_id:
            if kickoff_id not in self._executions:
                self._executions[kickoff_id] = {
                    "kickoff_id": kickoff_id,
                    "status": "running",
                    "checkpoints": [],
                    "created_at": datetime.utcnow().isoformat()
                }
            
            self._executions[kickoff_id]["checkpoints"].append(checkpoint_id)
            self._executions[kickoff_id]["current_checkpoint"] = checkpoint_id
            self._executions[kickoff_id]["status"] = "waiting_feedback"
    
    async def store_task_result(
        self,
        kickoff_id: str,
        task_id: str,
        result: Dict[str, Any]
    ):
        """Store task result."""
        if kickoff_id not in self._executions:
            self._executions[kickoff_id] = {
                "kickoff_id": kickoff_id,
                "status": "running",
                "tasks": {},
                "created_at": datetime.utcnow().isoformat()
            }
        
        if "tasks" not in self._executions[kickoff_id]:
            self._executions[kickoff_id]["tasks"] = {}
        
        self._executions[kickoff_id]["tasks"][task_id] = result
    
    async def store_crew_result(
        self,
        kickoff_id: str,
        result: Dict[str, Any]
    ):
        """Store crew completion result."""
        if kickoff_id not in self._executions:
            self._executions[kickoff_id] = {
                "kickoff_id": kickoff_id,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
        
        self._executions[kickoff_id]["status"] = "completed"
        self._executions[kickoff_id]["result"] = result
        self._executions[kickoff_id]["completed_at"] = datetime.utcnow().isoformat()
    
    async def store_error(
        self,
        kickoff_id: str,
        error: str
    ):
        """Store error."""
        if kickoff_id not in self._executions:
            self._executions[kickoff_id] = {
                "kickoff_id": kickoff_id,
                "status": "error",
                "created_at": datetime.utcnow().isoformat()
            }
        
        self._executions[kickoff_id]["status"] = "error"
        self._executions[kickoff_id]["error"] = error
        self._executions[kickoff_id]["failed_at"] = datetime.utcnow().isoformat()
    
    async def process_feedback(
        self,
        checkpoint_id: str,
        action: str,
        feedback: Optional[str] = None
    ):
        """Process feedback for a checkpoint."""
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint["status"] = action
        checkpoint["feedback"] = feedback
        checkpoint["resolved_at"] = datetime.utcnow().isoformat()
        
        # Update execution state
        kickoff_id = checkpoint.get("kickoff_id")
        if kickoff_id and kickoff_id in self._executions:
            self._executions[kickoff_id]["current_checkpoint"] = None
            
            if action == "stop":
                self._executions[kickoff_id]["status"] = "stopped"
            elif action in ["continue", "skip"]:
                self._executions[kickoff_id]["status"] = "running"
    
    async def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint information."""
        return self._checkpoints.get(checkpoint_id)
    
    async def get_execution_status(self, kickoff_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status."""
        return self._executions.get(kickoff_id)
    
    async def _schedule_retry(self, event_id: str, event: Dict[str, Any]):
        """Schedule event retry."""
        self._retry_queue.append({
            "event_id": event_id,
            "event": event,
            "retry_at": datetime.utcnow().timestamp() + self._retry_delay
        })
    
    async def handle_error(self, event_type: str, payload: Dict[str, Any], error: str):
        """Handle processing error."""
        # Log error (in production, use proper logging)
        print(f"Error processing event {event_type}: {error}")
        # Could send to error tracking service (Sentry, etc.)
    
    def get_pending_count(self) -> int:
        """Get count of pending events."""
        return len([e for e in self._events.values() if e["status"] == EventStatus.PENDING.value])
    
    def get_processed_count(self) -> int:
        """Get count of processed events."""
        return len([e for e in self._events.values() if e["status"] == EventStatus.COMPLETED.value])
