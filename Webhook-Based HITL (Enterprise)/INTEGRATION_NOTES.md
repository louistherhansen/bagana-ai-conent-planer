# Integration Notes: Webhook-Based HITL (Enterprise)

## Connection to Integration Artifact

This folder implements an **enterprise-grade webhook-based HITL system** that extends the existing webhook infrastructure documented in `project-context/2.build/integration.md` and `app/api/crew/webhook/route.ts`.

## Architecture Comparison

### Current Webhook Implementation

```
CrewAI Cloud → POST /api/crew/webhook → Log only
```

**Limitations:**
- Basic logging only
- No state management
- No notification system
- No feedback handling

### Enterprise Webhook Implementation

```
CrewAI → Webhook Server → Event Processor → State Manager
                                    ↓
                            Notification Service
                                    ↓
                        Slack / Email / WebSocket
                                    
External Systems → Feedback API → Event Processor → Resume Execution
```

**Advantages:**
- Complete state management
- Multi-channel notifications
- Feedback handling
- Retry logic
- Security features
- Scalable architecture

## Integration Options

### Option 1: Replace Existing Webhook Route

Replace `app/api/crew/webhook/route.ts` with FastAPI webhook server:

1. **Deploy FastAPI Server**: Deploy webhook server separately
2. **Update CrewAI Config**: Point webhooks to FastAPI server
3. **Remove Next.js Route**: Deprecate `/api/crew/webhook`

**Pros:**
- Dedicated webhook handling
- Better scalability
- Enterprise features

**Cons:**
- Additional service to maintain
- Requires infrastructure changes

### Option 2: Enhance Existing Route

Enhance `app/api/crew/webhook/route.ts` with enterprise features:

1. **Add Event Processing**: Process webhooks asynchronously
2. **Add State Management**: Store checkpoints and executions
3. **Add Notifications**: Integrate Slack/Email
4. **Add Feedback Endpoint**: Handle feedback submissions

**Pros:**
- No new infrastructure
- Gradual enhancement
- Backward compatible

**Cons:**
- Next.js limitations for long-running tasks
- Less scalable

### Option 3: Hybrid Approach

Use FastAPI for webhooks, Next.js for API:

1. **FastAPI**: Handle all webhook events
2. **Next.js**: Handle API requests, proxy webhooks to FastAPI
3. **Shared State**: Use database/Redis for shared state

**Pros:**
- Best of both worlds
- Scalable webhook handling
- Unified API surface

**Cons:**
- More complex architecture
- Two services to maintain

## Recommended Approach

For BAGANA AI enterprise deployment, recommend **Option 1 (Replace)**:

1. **Phase 1**: Deploy FastAPI webhook server alongside Next.js
2. **Phase 2**: Update CrewAI to send webhooks to FastAPI
3. **Phase 3**: Migrate all webhook handling to FastAPI
4. **Phase 4**: Deprecate Next.js webhook route

## CrewAI Integration

### CrewAI Cloud

```typescript
// In app/api/crew/route.ts
const webhookConfig = {
  taskWebhookUrl: `${process.env.WEBHOOK_BASE_URL}/webhook/crewai?event=task`,
  stepWebhookUrl: `${process.env.WEBHOOK_BASE_URL}/webhook/crewai?event=step`,
  crewWebhookUrl: `${process.env.WEBHOOK_BASE_URL}/webhook/crewai?event=crew`
};

const result = await runCrewCloud(payload, {
  ...cloudConfig,
  ...webhookConfig
});
```

### Local Crew Execution

```python
# In crew/run.py or custom executor
from crew_webhook_integration import send_checkpoint_webhook

# At checkpoint point
send_checkpoint_webhook(
    webhook_url=os.getenv("WEBHOOK_BASE_URL") + "/webhook/crewai",
    checkpoint_id=checkpoint_id,
    checkpoint_name="after_planning",
    context=context,
    kickoff_id=kickoff_id,
    secret=os.getenv("WEBHOOK_SECRET")
)

# Wait for feedback (poll or use async)
feedback = await wait_for_feedback(checkpoint_id)
```

## Notification Integration

### Slack Setup

1. Create Slack App: https://api.slack.com/apps
2. Add Incoming Webhooks
3. Configure webhook URL in `.env`
4. (Optional) Add interactive buttons for approval

### Email Setup

1. Configure SMTP settings in `.env`
2. Use email service (SendGrid, AWS SES, etc.)
3. Templates for checkpoint notifications

### WebSocket Setup

1. Connect clients to `ws://your-domain.com/ws`
2. Receive real-time notifications
3. Update UI based on events

## Security Considerations

### Webhook Signature

Always verify webhook signatures:

```python
# Set WEBHOOK_SECRET in production
# Server automatically verifies all webhooks
```

### API Key Authentication

Protect feedback endpoints:

```python
# Set WEBHOOK_API_KEY in production
# All feedback submissions require valid API key
```

### Rate Limiting

Add rate limiting for production:

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook/crewai")
@limiter.limit("100/minute")
async def receive_webhook(...):
    ...
```

## State Management

### Current: In-Memory

```python
# webhook_event_processor.py uses in-memory storage
self._checkpoints: Dict[str, Dict[str, Any]] = {}
```

### Production: Database

```python
# Use PostgreSQL, MongoDB, or Redis
from sqlalchemy import create_engine
engine = create_engine('postgresql://...')

# Store checkpoints and executions in database
```

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  webhook-server:
    build: .
    ports:
      - "8001:8001"
    environment:
      - WEBHOOK_SECRET=${WEBHOOK_SECRET}
      - WEBHOOK_API_KEY=${WEBHOOK_API_KEY}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./logs:/app/logs
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webhook-server
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: webhook-server
        image: your-registry/webhook-server:latest
        env:
        - name: WEBHOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: webhook-secrets
              key: secret
```

## Monitoring

### Metrics

- Webhooks received per minute
- Processing time
- Error rate
- Pending checkpoints
- Notification delivery rate

### Alerts

- High error rate
- Webhook processing delays
- Notification failures
- Checkpoint timeouts

## Files Reference

- `webhook_server.py` - Main FastAPI application
- `webhook_event_processor.py` - Event processing logic
- `notification_service.py` - Notification channels
- `webhook_security.py` - Security utilities
- `crew_webhook_integration.py` - CrewAI integration helpers

## Next Steps

1. **Deploy**: Deploy webhook server to staging
2. **Test**: Test webhook reception and processing
3. **Configure**: Set up notification channels
4. **Integrate**: Connect CrewAI to send webhooks
5. **Monitor**: Set up monitoring and alerting
6. **Scale**: Add database backend for production

## Related

- See `app/api/crew/webhook/route.ts` for existing webhook implementation
- See `Full-Stack HITL with FastAPI Backend` for REST API approach
- See `Task-Level Human Input` and `Flow-Level Decorator` for simpler approaches
