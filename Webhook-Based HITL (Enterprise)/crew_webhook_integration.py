"""
CrewAI Webhook Integration
Configures CrewAI to send webhooks for HITL checkpoints.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def configure_crew_webhooks(
    webhook_base_url: str,
    checkpoint_webhook_path: str = "/webhook/crewai"
) -> Dict[str, str]:
    """
    Configure webhook URLs for CrewAI execution.
    
    Returns webhook configuration dict to pass to crew.kickoff() or CrewAI Cloud.
    """
    base_url = webhook_base_url.rstrip("/")
    webhook_url = f"{base_url}{checkpoint_webhook_path}"
    
    return {
        "taskWebhookUrl": f"{webhook_url}?event=task",
        "stepWebhookUrl": f"{webhook_url}?event=step",
        "crewWebhookUrl": f"{webhook_url}?event=crew"
    }


def create_checkpoint_webhook_payload(
    checkpoint_id: str,
    checkpoint_name: str,
    context: Dict[str, Any],
    kickoff_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create webhook payload for checkpoint event."""
    return {
        "event_type": "checkpoint.required",
        "checkpoint_id": checkpoint_id,
        "checkpoint_name": checkpoint_name,
        "kickoff_id": kickoff_id,
        "context": context,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


def send_checkpoint_webhook(
    webhook_url: str,
    checkpoint_id: str,
    checkpoint_name: str,
    context: Dict[str, Any],
    kickoff_id: Optional[str] = None,
    secret: Optional[str] = None
):
    """
    Send checkpoint webhook manually (for custom integrations).
    """
    import httpx
    from webhook_security import WebhookSecurity
    
    payload = create_checkpoint_webhook_payload(
        checkpoint_id=checkpoint_id,
        checkpoint_name=checkpoint_name,
        context=context,
        kickoff_id=kickoff_id
    )
    
    headers = {"Content-Type": "application/json"}
    
    # Add signature if secret provided
    if secret:
        security = WebhookSecurity()
        body_bytes = json.dumps(payload).encode()
        signature = security.generate_signature(body_bytes, secret)
        headers["X-CrewAI-Signature"] = signature
    
    # Send webhook
    response = httpx.post(webhook_url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()


# Example: Integrate with crew/run.py
def integrate_with_crew_run():
    """
    Example integration code for crew/run.py
    
    Add this to your crew execution to send webhooks:
    """
    code_example = """
    # In crew/run.py, modify kickoff() function:
    
    from webhook_integration import configure_crew_webhooks, send_checkpoint_webhook
    
    def kickoff(inputs: dict | None = None) -> dict:
        # ... existing code ...
        
        # Configure webhooks
        webhook_config = configure_crew_webhooks(
            webhook_base_url=os.getenv("WEBHOOK_BASE_URL", "http://localhost:8001")
        )
        
        # Add webhook URLs to inputs
        inputs["webhook_config"] = webhook_config
        
        # Execute crew
        crew = build_crew()
        result = crew.kickoff(inputs=inputs)
        
        # Send checkpoint webhooks at specific points
        # (This would be integrated into task callbacks or phase boundaries)
        
        return result
    """
    
    return code_example
