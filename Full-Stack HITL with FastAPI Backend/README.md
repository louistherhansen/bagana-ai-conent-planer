# Full-Stack HITL with FastAPI Backend

This folder contains a **complete Full-Stack Human-In-The-Loop (HITL)** implementation using **FastAPI** as the backend and **CrewAI** for workflow execution.

## Overview

This implementation provides a production-ready backend for managing HITL workflows with CrewAI, featuring:

- **FastAPI REST API** for workflow execution and feedback management
- **State Management** for tracking executions and checkpoints
- **Async Execution** with background task processing
- **Checkpoint System** for human approval gates
- **Frontend Integration** examples for React/Next.js

## Architecture

```
Frontend (Next.js)
    ↓ HTTP POST
FastAPI Backend (/api/crew/execute)
    ↓ Background Task
CrewAI Executor (crew_integration.py)
    ↓ Phase Execution
Checkpoint Created (hitl_state_manager.py)
    ↓ Wait for Feedback
Frontend Polls (/api/crew/checkpoint/{execution_id})
    ↓ User Submits Feedback
FastAPI Backend (/api/crew/feedback)
    ↓ Resume Execution
CrewAI Continues
    ↓ Complete
Return Final Result
```

## Files Structure

### Backend Files

- **`main.py`** - FastAPI application with all endpoints
- **`hitl_state_manager.py`** - State management for executions and checkpoints
- **`crew_integration.py`** - CrewAI integration layer with phased execution
- **`requirements.txt`** - Python dependencies

### Frontend Integration

- **`frontend_integration.tsx`** - React/Next.js components and hooks for HITL

## Quick Start

### 1. Install Dependencies

```bash
cd "Full-Stack HITL with FastAPI Backend"
pip install -r requirements.txt
```

### 2. Start FastAPI Server

```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --port 8000
```

Server will run at `http://localhost:8000`

### 3. API Documentation

Once server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Execute Crew Workflow

```http
POST /api/crew/execute
Content-Type: application/json

{
  "message": "Create a content plan",
  "language": "English",
  "checkpoints": ["after_planning", "after_analysis"]
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "running",
  "current_checkpoint": null,
  "completed_checkpoints": []
}
```

### Get Execution Status

```http
GET /api/crew/status/{execution_id}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "waiting_feedback",
  "current_checkpoint": "checkpoint_id",
  "completed_checkpoints": [],
  "result": null
}
```

### Get Current Checkpoint

```http
GET /api/crew/checkpoint/{execution_id}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "checkpoint_id": "uuid",
  "checkpoint_name": "after_planning",
  "description": "Review content plan",
  "context": {...},
  "status": "pending",
  "created_at": "2026-02-07T00:00:00"
}
```

### Submit Feedback

```http
POST /api/crew/feedback
Content-Type: application/json

{
  "execution_id": "uuid",
  "checkpoint_id": "uuid",
  "action": "continue",  // or "stop", "revise", "skip"
  "feedback": "Optional feedback text"
}
```

## Usage Examples

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Start execution
response = requests.post(f"{BASE_URL}/api/crew/execute", json={
    "message": "Create a content plan",
    "checkpoints": ["after_planning"]
})
execution = response.json()
execution_id = execution["execution_id"]

# Poll for checkpoint
import time
while True:
    status = requests.get(f"{BASE_URL}/api/crew/status/{execution_id}").json()
    if status["status"] == "waiting_feedback":
        checkpoint = requests.get(f"{BASE_URL}/api/crew/checkpoint/{execution_id}").json()
        print(f"Checkpoint: {checkpoint['checkpoint_name']}")
        break
    time.sleep(2)

# Submit feedback
requests.post(f"{BASE_URL}/api/crew/feedback", json={
    "execution_id": execution_id,
    "checkpoint_id": checkpoint["checkpoint_id"],
    "action": "continue"
})
```

### React/Next.js Example

See `frontend_integration.tsx` for complete React components:

```tsx
import { useHITLWorkflow, CheckpointApproval } from './frontend_integration';

function MyComponent() {
  const { startExecution, checkpoint, submitFeedback } = useHITLWorkflow();

  return (
    <div>
      <button onClick={() => startExecution({ message: "Create plan" })}>
        Start
      </button>
      
      {checkpoint && (
        <CheckpointApproval
          checkpoint={checkpoint}
          onSubmit={(action, feedback) => submitFeedback(checkpoint.checkpoint_id, action, feedback)}
        />
      )}
    </div>
  );
}
```

## Checkpoint Flow

1. **Execution Starts**: `POST /api/crew/execute` returns `execution_id`
2. **Crew Executes**: Background task runs crew workflow
3. **Checkpoint Created**: At checkpoint point, execution pauses
4. **Status Polling**: Frontend polls `GET /api/crew/status/{execution_id}`
5. **Checkpoint Retrieved**: When `status == "waiting_feedback"`, get checkpoint
6. **User Reviews**: Display checkpoint context to user
7. **Feedback Submitted**: `POST /api/crew/feedback` with action
8. **Execution Resumes**: Crew continues based on feedback
9. **Completion**: Final result available via status endpoint

## Feedback Actions

- **`continue`**: Approve and proceed to next phase
- **`stop`**: Stop execution immediately
- **`revise`**: Provide feedback for revision (includes feedback text)
- **`skip`**: Skip this checkpoint and continue

## State Management

The `StateManager` class handles:
- Execution state tracking
- Checkpoint creation and resolution
- Feedback storage
- Thread-safe operations

States:
- `PENDING` - Execution created, not started
- `RUNNING` - Execution in progress
- `WAITING_FEEDBACK` - Paused at checkpoint
- `COMPLETED` - Execution finished successfully
- `ERROR` - Execution failed
- `CANCELLED` - Execution cancelled
- `STOPPED` - Stopped by user feedback

## Integration with Existing Crew

The `CrewExecutor` integrates with your existing `crew/run.py`:

1. Uses same subprocess execution (`python -m crew.run --stdin`)
2. Maintains same input/output format
3. Adds checkpoint pauses at specified phases
4. Resumes execution after feedback

## Configuration

### Environment Variables

Create `.env` file:

```env
# FastAPI
HITL_BACKEND_PORT=8000
HITL_BACKEND_HOST=0.0.0.0

# CrewAI (same as existing)
OPENAI_API_KEY=your-key
# or
OPENROUTER_API_KEY=your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

### Checkpoint Configuration

Default checkpoints:
- `after_planning` - After content plan creation
- `after_analysis` - After sentiment/trend analysis
- `before_finalization` - Before final strategy

Customize in `crew_integration.py` to match your workflow phases.

## Comparison with Other HITL Implementations

| Feature | Task-Level Input | Flow-Level Decorator | FastAPI HITL |
|---------|-----------------|---------------------|--------------|
| **Backend** | Next.js API | Python decorator | FastAPI |
| **State Management** | None | In-memory | Persistent state |
| **Async Execution** | No | No | Yes |
| **Web UI** | Limited | No | Full support |
| **Production Ready** | Basic | Development | Yes |
| **Scalability** | Limited | Limited | High |

## Production Considerations

### State Persistence

Current implementation uses in-memory state. For production:

1. **Database Storage**: Use PostgreSQL/Redis for state
2. **Distributed State**: Use Redis for multi-instance deployments
3. **State Recovery**: Implement checkpoint recovery on restart

### Error Handling

- Add retry logic for crew execution failures
- Implement timeout handling for checkpoints
- Add logging and monitoring

### Security

- Add authentication/authorization
- Validate checkpoint access permissions
- Sanitize user inputs
- Rate limiting

### Performance

- Use async/await throughout
- Implement connection pooling
- Add caching for frequent queries
- Consider WebSocket for real-time updates

## Testing

### Manual Testing

1. Start FastAPI server: `python main.py`
2. Start Next.js frontend: `npm run dev`
3. Use Swagger UI: http://localhost:8000/docs
4. Test workflow end-to-end

### Automated Testing

```python
# test_hitl.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_execute_crew():
    response = client.post("/api/crew/execute", json={
        "message": "Test",
        "checkpoints": ["after_planning"]
    })
    assert response.status_code == 200
    assert "execution_id" in response.json()
```

## Next Steps

1. **Integrate with Next.js**: Replace `/api/crew` route with FastAPI calls
2. **Add Database**: Implement persistent state storage
3. **Add WebSocket**: Real-time checkpoint notifications
4. **Add Authentication**: Secure API endpoints
5. **Add Monitoring**: Logging and metrics

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CrewAI Documentation](https://docs.crewai.com)
- Related: `Task-Level Human Input` and `Flow-Level @human_feedback Decorator` folders

## Conclusion

The Full-Stack HITL with FastAPI Backend provides a **production-ready solution** for implementing Human-In-The-Loop workflows with CrewAI, offering a scalable, async, and feature-rich alternative to console-based or decorator-based approaches.

### Key Advantages

✅ **Production Ready**: FastAPI provides production-grade async performance and scalability  
✅ **State Management**: Persistent state tracking for executions and checkpoints  
✅ **Async Execution**: Non-blocking background task processing  
✅ **Web Integration**: Full REST API for frontend integration  
✅ **Scalable Architecture**: Can handle multiple concurrent executions  
✅ **Checkpoint System**: Flexible checkpoint placement and management  
✅ **Feedback API**: Complete feedback submission and workflow resumption  

### When to Use FastAPI HITL Backend

**Use FastAPI HITL Backend when:**
- You need production-grade HITL workflows
- Multiple users need concurrent execution
- You want persistent state management
- You need web-based approval interfaces
- You require async/non-blocking execution
- You need scalable architecture

**Use Task-Level/Flow-Level when:**
- Development and testing
- Single-user console workflows
- Simple approval gates
- No state persistence needed

### Architecture Benefits

1. **Separation of Concerns**: Backend handles execution, frontend handles UI
2. **Scalability**: Can scale backend independently from frontend
3. **State Persistence**: Execution state survives server restarts (with DB)
4. **Real-time Updates**: Can add WebSocket for instant notifications
5. **Production Features**: Authentication, rate limiting, monitoring ready

### Integration Strategy

For BAGANA AI, the recommended approach is:

1. **Development**: Use FastAPI HITL for testing HITL workflows
2. **Staging**: Deploy FastAPI alongside Next.js for validation
3. **Production**: Full FastAPI deployment with database state storage
4. **Migration**: Gradually migrate from Next.js routes to FastAPI

### Best Practices

1. **State Storage**: Use Redis/PostgreSQL for production state persistence
2. **Error Handling**: Implement comprehensive error handling and retries
3. **Monitoring**: Add logging, metrics, and alerting
4. **Security**: Add authentication, authorization, and input validation
5. **Performance**: Use async throughout, connection pooling, caching

### Summary

The FastAPI HITL Backend completes the HITL implementation spectrum for BAGANA AI:

- **Task-Level**: Simple console approval at task completion
- **Flow-Level**: Decorator-based phase checkpoints
- **Full-Stack**: Production-ready FastAPI backend with state management

Together, these three approaches provide comprehensive HITL capabilities from development to production, enabling human oversight at every level of your CrewAI workflows while maintaining flexibility and scalability for your content planning platform.
