# Integration Notes: REST API (Simple GET/POST)

## Link to integration.md

This folder implements the **same REST contract** described in **project-context/2.build/integration.md** (§5, §6, §7):

- **GET /api/crew** — Health/description; returns `{ status: "ok", message: "..." }`.
- **POST /api/crew** — Run crew; body `message` (or `user_input` / `campaign_context`); response `{ status, output?, task_outputs? }` or `{ status: "error", error }`.

## Two implementations of the same contract

| Implementation | Location | Purpose |
|----------------|----------|---------|
| Next.js API route | `app/api/crew/route.ts` | Used by the chat UI (ChatRuntimeProvider → POST /api/crew). |
| Standalone Python API | This folder (`api_server.py`) | Standalone server on port 8002; same GET/POST contract. |

Both call the same backend: `python -m crew.run --stdin` with JSON in/out.

## When to use which

- **Next.js route**: Use when the app is running (`npm run dev`); frontend uses it by default.
- **Standalone Python API**: Use when you want to run crew without Next.js (scripts, other services, or a second port).

## Optional: point frontend at Python API

To have the chat UI call the Python server instead of the Next.js route:

1. Run `python api_server.py` (port 8002).
2. In the frontend, set the base URL for the crew API to `http://localhost:8002` (e.g. via env or adapter config) so POST goes to `http://localhost:8002/api/crew`.

Contract stays the same, so no change to request/response shapes.

## Summary

- **integration.md** defines the GET/POST contract.
- **app/api/crew/route.ts** implements it for the Next.js app.
- **This folder** implements the same contract as a standalone Python REST API for CrewAI.
