# Integration Notes: Full-Stack HITL with FastAPI Backend

## Connection to Integration Artifact

This folder implements a **production-ready Full-Stack HITL backend** that complements the existing Next.js API routes documented in `project-context/2.build/integration.md`.

## Architecture Comparison

### Current Architecture (Next.js API Routes)

```
Frontend → Next.js API Route (/api/crew) → Python Subprocess → CrewAI
```

**Limitations:**
- Synchronous execution (blocks until complete)
- No state management
- No checkpoint support
- Limited scalability

### New Architecture (FastAPI HITL Backend)

```
Frontend → FastAPI Backend → Background Tasks → CrewAI
                ↓
         State Manager
                ↓
         Checkpoint System
                ↓
         Feedback API
```

**Advantages:**
- Async execution (non-blocking)
- Persistent state management
- Checkpoint support
- Scalable architecture
- Production-ready

## Integration Options

### Option 1: Replace Next.js API Routes

Replace `app/api/crew/route.ts` with FastAPI backend:

1. **Update Frontend**: Change API calls to FastAPI endpoints
2. **Remove Next.js Route**: Delete or deprecate `/api/crew`
3. **Use FastAPI**: All crew execution goes through FastAPI

**Pros:**
- Single backend for crew execution
- Better separation of concerns
- Easier to scale

**Cons:**
- Requires frontend changes
- Need to run separate FastAPI server

### Option 2: Hybrid Approach

Keep Next.js routes for simple execution, use FastAPI for HITL:

1. **Simple Execution**: Use Next.js `/api/crew` (no checkpoints)
2. **HITL Execution**: Use FastAPI `/api/crew/execute` (with checkpoints)

**Pros:**
- Backward compatible
- Gradual migration
- Best of both worlds

**Cons:**
- Two backends to maintain
- More complex architecture

### Option 3: Proxy Through Next.js

Next.js routes proxy to FastAPI:

```typescript
// app/api/crew/route.ts
export async function POST(request: NextRequest) {
  // Proxy to FastAPI if HITL requested
  if (body.checkpoints?.length > 0) {
    return fetch('http://localhost:8000/api/crew/execute', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }
  // Otherwise use existing logic
  return runCrew(body);
}
```

**Pros:**
- No frontend changes
- Unified API surface
- Easy migration

**Cons:**
- Additional network hop
- More complex routing

## Recommended Approach

For BAGANA AI, recommend **Option 2 (Hybrid)**:

1. **Phase 1**: Deploy FastAPI alongside Next.js
2. **Phase 2**: Update frontend to use FastAPI for HITL workflows
3. **Phase 3**: Migrate all execution to FastAPI over time

## Frontend Integration

### Update ChatRuntimeProvider

Modify `components/ChatRuntimeProvider.tsx`:

```typescript
// Add HITL support
const useHITL = process.env.NEXT_PUBLIC_USE_HITL === 'true';

if (useHITL && checkpoints.length > 0) {
  // Use FastAPI HITL backend
  return useHITLWorkflow();
} else {
  // Use existing Next.js API
  return useLocalRuntime(crewAdapter);
}
```

### Add HITL Components

Import from `frontend_integration.tsx`:

```typescript
import { 
  useHITLWorkflow, 
  CheckpointApproval 
} from '@/path/to/frontend_integration';
```

## Deployment

### Development

Run both servers:

```bash
# Terminal 1: Next.js
npm run dev

# Terminal 2: FastAPI
cd "Full-Stack HITL with FastAPI Backend"
python main.py
```

### Production

1. **FastAPI**: Deploy with uvicorn/gunicorn
2. **Next.js**: Deploy as usual (Vercel, etc.)
3. **State Storage**: Use Redis/PostgreSQL
4. **Load Balancer**: Route `/api/crew/*` to FastAPI

## State Management Migration

### Current: In-Memory

```python
# hitl_state_manager.py
self._executions: Dict[str, ExecutionStateData] = {}
```

### Production: Database

```python
# Use SQLAlchemy or similar
from sqlalchemy import create_engine
engine = create_engine('postgresql://...')

# Store executions in database
class Execution(Base):
    execution_id = Column(String, primary_key=True)
    state = Column(String)
    # ...
```

## Checkpoint Configuration

### Default Checkpoints

Match your workflow phases:

```python
# crew_integration.py
CHECKPOINTS = {
    "after_planning": {
        "phase": "planning",
        "description": "Review content plan"
    },
    "after_analysis": {
        "phase": "analysis", 
        "description": "Review sentiment and trends"
    }
}
```

### Custom Checkpoints

Add to `crew_integration.py`:

```python
async def _execute_phased(...):
    # Add custom checkpoint
    if "custom_checkpoint" in checkpoints:
        await self._execute_phase(
            execution_id=execution_id,
            phase_name="custom",
            inputs=inputs,
            checkpoint_name="custom_checkpoint",
            checkpoint_description="Custom review point"
        )
```

## API Compatibility

FastAPI endpoints maintain compatibility with Next.js API:

- Same request/response format
- Same error handling
- Same authentication (if added)

## Monitoring and Logging

Add logging:

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/api/crew/execute")
async def execute_crew(...):
    logger.info(f"Starting execution {execution_id}")
    # ...
```

Add metrics:

```python
from prometheus_client import Counter

execution_counter = Counter('crew_executions_total', 'Total crew executions')

@app.post("/api/crew/execute")
async def execute_crew(...):
    execution_counter.inc()
    # ...
```

## Security Considerations

1. **Authentication**: Add JWT/auth middleware
2. **Authorization**: Check user permissions for checkpoints
3. **Rate Limiting**: Limit execution requests per user
4. **Input Validation**: Validate all inputs
5. **CORS**: Configure properly for production

## Performance Optimization

1. **Connection Pooling**: Use async database connections
2. **Caching**: Cache execution status
3. **Background Tasks**: Use Celery for heavy tasks
4. **WebSocket**: Real-time updates instead of polling

## Files Reference

- `main.py` - FastAPI application
- `hitl_state_manager.py` - State management
- `crew_integration.py` - CrewAI integration
- `frontend_integration.tsx` - React components
- `requirements.txt` - Dependencies

## Next Steps

1. **Test Integration**: Run FastAPI alongside Next.js
2. **Update Frontend**: Add HITL components to chat UI
3. **Add Database**: Implement persistent state
4. **Deploy**: Set up production deployment
5. **Monitor**: Add logging and metrics

## Related

- See `Task-Level Human Input` for task-level patterns
- See `Flow-Level @human_feedback Decorator` for decorator patterns
- See `WebSocket Testing` for real-time patterns
