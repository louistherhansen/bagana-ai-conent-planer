# REST API Integration (Simple GET/POST)

Minimal REST API for CrewAI aligned with **project-context/2.build/integration.md**: one **GET** and one **POST** endpoint to run the crew.

## Contract (from integration.md)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/crew` | GET | — | `{ status: "ok", message: "..." }` |
| `/api/crew` | POST | JSON: `message?`, `user_input?`, `campaign_context?`, `language?` | `{ status, output?, task_outputs? }` or `{ status: "error", error }` |

- **GET** — Health/description only; no execution.
- **POST** — Runs `python -m crew.run --stdin` with the JSON body; returns full JSON when crew finishes (no streaming).

## Files

- **`api_server.py`** — FastAPI app: GET/POST `/api/crew`, spawns `crew.run --stdin`.
- **`example_clients.py`** — Python examples: `get_crew()`, `post_crew(message, ...)`.
- **`README.md`** — This file.

## Quick start

1. From project root, install deps if needed:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

2. Run the API (port 8002):
   ```bash
   cd "REST API Integration (Simple GET-POST)"
   python api_server.py
   ```
   Or: `uvicorn api_server:app --host 0.0.0.0 --port 8002`

3. **GET** (health):
   ```bash
   curl http://localhost:8002/api/crew
   ```
   Expect: `{"status":"ok","message":"..."}`

4. **POST** (run crew):
   ```bash
   curl -X POST http://localhost:8002/api/crew -H "Content-Type: application/json" -d "{\"message\":\"Create a short content plan.\"}"
   ```
   Expect: JSON with `status`, `output`, `task_outputs` (or `status: "error"` and `error`).

## Example clients

**Python** (see `example_clients.py`):

```python
from example_clients import get_crew, post_crew

get_crew()                    # GET /api/crew
post_crew("Your brief here")  # POST /api/crew
```

**JavaScript (fetch)**:

```javascript
// GET
const resGet = await fetch('http://localhost:8002/api/crew');
const dataGet = await resGet.json();

// POST
const resPost = await fetch('http://localhost:8002/api/crew', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Create a content plan.' })
});
const dataPost = await resPost.json();
```

## Relation to existing app

- **Next.js** already implements this contract at `app/api/crew/route.ts` (GET + POST, same payload/response).
- This folder is a **standalone Python REST API** that uses the same contract so you can:
  - Run crew without Next.js (e.g. port 8002).
  - Test or integrate from any HTTP client.
  - Reuse the same GET/POST semantics in scripts or other services.

## Environment

- Ensure `.env` has `OPENAI_API_KEY` (or OpenRouter keys) and that `python -m crew.run --stdin` works from the project root.
- Timeout for POST is 300 seconds (configurable in `api_server.py`).

## Conclusion

This folder provides a **minimal REST API** for CrewAI: **GET** for health and **POST** for running the crew, using the same request/response contract as in integration.md and the Next.js route.

### Key Takeaways

✅ **Same Contract Everywhere**: GET/POST semantics match `app/api/crew/route.ts` and integration.md—one contract for frontend, scripts, and standalone server.  
✅ **Standalone Option**: Run crew without Next.js; useful for scripts, CI, or a separate service on port 8002.  
✅ **Minimal Surface**: Only two endpoints; no auth, streaming, or HITL—ideal as a reference or lightweight gateway.  
✅ **Easy to Integrate**: Any HTTP client (curl, Python, fetch, Postman) can call GET/POST with standard JSON.

### When to Use This API

**Use this simple REST API when:**
- You need to run the crew from scripts or another service without starting the full Next.js app.
- You want a reference implementation of the integration.md contract.
- You are testing or prototyping with a minimal API surface (GET + POST only).
- You prefer a single Python process (FastAPI) instead of Next.js for the crew gateway.

**Use the Next.js route (`app/api/crew`) when:**
- The chat UI and full app are running; the frontend already uses this route.
- You need the same contract but served from the same origin as the app (no CORS, same port).

**Consider other integrations when:**
- You need HITL, streaming, or webhooks → see Task-Level Human Input, Flow-Level Decorator, FastAPI HITL Backend, or Webhook-Based HITL.
- You need more endpoints or auth → extend this API or use the Full-Stack HITL backend.

### Comparison with Other Integrations

| Approach | Endpoints | Use Case |
|----------|-----------|----------|
| **This folder (Simple GET/POST)** | GET + POST `/api/crew` | Standalone crew gateway, scripts, same contract as integration.md |
| **Next.js route** | GET + POST `/api/crew` | Same contract; used by chat UI when app is running |
| **FastAPI HITL Backend** | Execute, status, checkpoint, feedback | Production HITL with state and feedback API |
| **Webhook-Based HITL** | Webhook + feedback endpoints | Enterprise, event-driven, external systems |

### Next Steps

1. **Run the server**: `python api_server.py` (port 8002).  
2. **Call GET**: Verify health with `curl http://localhost:8002/api/crew`.  
3. **Call POST**: Run crew with a JSON body containing `message` (or `user_input`).  
4. **Reuse in scripts**: Use `example_clients.py` or your own HTTP client.  
5. **Extend if needed**: Add auth, streaming, or more routes in `api_server.py`, or switch to FastAPI HITL / Webhook implementations for advanced flows.

### Summary

The Simple GET/POST REST API is the **lightweight, contract-aligned** way to run CrewAI from outside the Next.js app. It keeps the same integration.md contract (GET for health, POST for execution) so you can run the crew standalone, test from any client, or use it as the base for a custom gateway. For more advanced needs (HITL, streaming, webhooks), use the dedicated folders in this project; for “just run the crew over HTTP,” this implementation is enough.
