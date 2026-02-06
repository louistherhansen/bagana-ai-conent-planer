"""
Webhook Security Module
Handles webhook signature verification and authorization.
"""

import hmac
import hashlib
import base64
from typing import Optional
import os


class WebhookSecurity:
    """Security utilities for webhook handling."""
    
    def __init__(self):
        self.webhook_secret = os.getenv("WEBHOOK_SECRET") or os.getenv("CREWAI_WEBHOOK_SECRET")
        self.api_key = os.getenv("WEBHOOK_API_KEY")
    
    def get_webhook_secret(self) -> Optional[str]:
        """Get webhook secret from environment."""
        return self.webhook_secret
    
    def verify_signature(
        self,
        body: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook signature.
        
        Supports multiple signature formats:
        - HMAC-SHA256 (most common)
        - Simple token comparison
        """
        if not signature or not secret:
            return False
        
        try:
            # Try HMAC-SHA256 verification
            expected_signature = hmac.new(
                secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (constant-time comparison)
            return hmac.compare_digest(
                signature,
                expected_signature
            ) or hmac.compare_digest(
                signature,
                f"sha256={expected_signature}"
            )
        
        except Exception:
            # Fallback to simple token comparison
            return signature == secret
    
    def verify_authorization(self, authorization: Optional[str]) -> bool:
        """Verify API key authorization."""
        if not self.api_key:
            # No API key configured, allow all (for development)
            return True
        
        if not authorization:
            return False
        
        # Support Bearer token format
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            return token == self.api_key
        
        # Support simple token
        return authorization == self.api_key
    
    def generate_signature(self, body: bytes, secret: str) -> str:
        """Generate webhook signature."""
        signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
