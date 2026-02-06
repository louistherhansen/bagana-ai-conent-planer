"""
Notification Service for Enterprise HITL
Sends notifications via multiple channels: Slack, Email, WebSocket, etc.
"""

from typing import Dict, Any, Optional, List
import asyncio
import httpx
from datetime import datetime


class NotificationService:
    """Enterprise notification service for HITL workflows."""
    
    def __init__(self):
        self.slack_webhook_url = None  # Set from env: SLACK_WEBHOOK_URL
        self.email_config = None  # Set from env: SMTP config
        self.websocket_clients: List[Any] = []
    
    async def send_event_notification(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send notification for any event."""
        # Send to all configured channels
        tasks = []
        
        if self.slack_webhook_url:
            tasks.append(self.send_slack_notification(event_type, payload))
        
        if self.email_config:
            tasks.append(self.send_email_notification(event_type, payload))
        
        # Send WebSocket notifications
        tasks.append(self.send_websocket_notification(event_type, payload))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_checkpoint_notification(
        self,
        checkpoint_id: str,
        checkpoint_name: str,
        context: Dict[str, Any]
    ):
        """Send notification for checkpoint requiring approval."""
        message = f"🔍 Checkpoint Required: {checkpoint_name}\n"
        message += f"Checkpoint ID: {checkpoint_id}\n"
        message += f"Context: {json.dumps(context, indent=2)[:500]}"
        
        payload = {
            "event_type": "checkpoint_required",
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint_name,
            "context": context,
            "message": message
        }
        
        await self.send_event_notification("checkpoint.required", payload)
    
    async def send_completion_notification(
        self,
        kickoff_id: str,
        result: Dict[str, Any]
    ):
        """Send notification for crew completion."""
        message = f"✅ Crew Execution Completed\n"
        message += f"Kickoff ID: {kickoff_id}\n"
        message += f"Status: {result.get('status', 'complete')}"
        
        payload = {
            "event_type": "crew_completed",
            "kickoff_id": kickoff_id,
            "result": result,
            "message": message
        }
        
        await self.send_event_notification("crew.completed", payload)
    
    async def send_failure_notification(
        self,
        kickoff_id: str,
        error: str
    ):
        """Send notification for crew failure."""
        message = f"❌ Crew Execution Failed\n"
        message += f"Kickoff ID: {kickoff_id}\n"
        message += f"Error: {error}"
        
        payload = {
            "event_type": "crew_failed",
            "kickoff_id": kickoff_id,
            "error": error,
            "message": message
        }
        
        await self.send_event_notification("crew.failed", payload)
    
    async def send_slack_notification(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send notification to Slack."""
        if not self.slack_webhook_url:
            return
        
        try:
            message = payload.get("message", f"Event: {event_type}")
            
            slack_payload = {
                "text": message,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    }
                ]
            }
            
            # Add action buttons for checkpoints
            if event_type == "checkpoint.required":
                slack_payload["blocks"].append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approve"},
                            "style": "primary",
                            "value": f"approve_{payload.get('checkpoint_id')}",
                            "action_id": "approve_checkpoint"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Reject"},
                            "style": "danger",
                            "value": f"reject_{payload.get('checkpoint_id')}",
                            "action_id": "reject_checkpoint"
                        }
                    ]
                })
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    self.slack_webhook_url,
                    json=slack_payload,
                    timeout=10.0
                )
        
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
    
    async def send_email_notification(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send notification via email."""
        if not self.email_config:
            return
        
        # In production, use proper email library (aiosmtplib, etc.)
        # For now, just log
        print(f"Email notification: {event_type}")
        print(f"Payload: {payload}")
    
    async def send_websocket_notification(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send notification via WebSocket to connected clients."""
        if not self.websocket_clients:
            return
        
        message = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected clients
        disconnected = []
        for client in self.websocket_clients:
            try:
                await client.send_json(message)
            except Exception:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.websocket_clients.remove(client)
    
    def register_websocket_client(self, client: Any):
        """Register a WebSocket client for real-time notifications."""
        self.websocket_clients.append(client)
    
    def unregister_websocket_client(self, client: Any):
        """Unregister a WebSocket client."""
        if client in self.websocket_clients:
            self.websocket_clients.remove(client)
