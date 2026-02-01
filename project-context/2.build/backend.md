# BAGANA AI — Backend Artifact

**Document version:** 1.0  
**Persona:** @backend.eng  
**Invocation:** *develop-be, *define-agents, *implement-endpoint, *document-backend  
**Sources:** PRD (prd.md), SAD (sad.md), frontend.md, setup.md, Usecase.txt  
**Output:** project-context/2.build/backend.md (this file)

---

## Context

This document records the *develop-be review of the CrewAI backend against PRD, SAD, frontend expectations, and the use case. It summarizes current implementation status, gaps, adapter compliance, and recommended next steps.

**Use case (anchor):**  
BAGANA AI is an AI-powered platform designed for KOL, influencer, and content creator agencies to manage content strategy at scale through integrated content planning, sentiment analysis, and market trend insights.

---

## 1. Implementation Summary

| Dimension | Status | Notes |
|-----------|--------|-------|
| **CrewAI orchestration** | Done | `crew/run.py` parses YAML, builds Crew, implements kickoff() |
| **Agent config (YAML)** | Done | 3 agents with llm, allow_delegation, verbose, max_iter, max_execution_time, max_retry_limit |
| **Task config (YAML)** | Done | 3 tasks with descriptions, expected_output (path + headings), context_from bindings |
| **Tool binding** | Done | Stub tools in crew/tools.py; bound per agent in run.py; pre-run check in build_crew() |
| **API endpoint** | Done | POST /api/crew invokes crew via subprocess; ChatRuntimeProvider wired to API |
| **Trace Log** | Done | step_callback writes to project-context/2.build/logs/trace.log |
| **Audit block** | Deferred | To be appended by agents to artifact outputs (P1) |

**Verdict:** CrewAI backend scaffolded and operational. Run `python -m crew.run [message]` to execute crew. Requires OPENAI_API_KEY in .env.

---

## 2. Traceability to PRD

### P0 Features (F1–F4)

| PRD requirement | Backend component | Status |
|-----------------|-------------------|--------|
| **F1 — Multi-talent content plans** | content_planner agent, plan_content task | Done: agent + task; output_file plan.md; plan_schema_validator stub |
| **F2 — Sentiment analysis** | sentiment_analyst agent, analyze_sentiment task | Done: agent + task; output_file sentiment.md; sentiment_schema_validator stub |
| **F3 — Market trend insights** | trend_researcher agent, research_trends task | Done: agent + task; output_file trends.md; trend_schema_validator stub |
| **F4 — Integrated workflow** | Sequential crew (plan → sentiment → trend) | Done: Crew built; plan → sentiment/trends with context |

### Agent definitions (PRD §3)

| Agent | PRD role/goal/backstory | agents.yaml | Gap |
|-------|-------------------------|-------------|-----|
| content_planner | ✓ | ✓ role, goal, backstory, llm, allow_delegation, max_iter, tools | Done |
| sentiment_analyst | ✓ | ✓ role, goal, backstory, llm, allow_delegation, max_iter, tools | Done |
| trend_researcher | ✓ | ✓ role, goal, backstory, llm, allow_delegation, max_iter, tools | Done |
| report_summarizer | P1 | Commented | Correctly deferred |

---

## 3. Traceability to SAD

### SAD §2 Multi-Agent System Specification

| SAD requirement | Implementation | Status |
|-----------------|----------------|--------|
| Agents loaded from config/agents.yaml | YAML parsed; Agent objects built | Done |
| Tasks loaded from config/tasks.yaml | YAML parsed; Task objects built | Done |
| Sequential flow: plan → sentiment → trend | Tasks with context_from; Crew sequential | Done |
| allow_delegation=false | Set in agents.yaml | Done |
| memory | Not used (reproducibility) | OK |
| max_iter ≤ 12 for MVP | Set to 12 in agents.yaml | Done |
| Task.context for inter-task data | context_from: [plan_content] resolved in code | Done |
| expected_output with path + headings | Full headings in tasks.yaml | Done |
| Tools whitelisted, bound in code | crew/tools.py; AGENT_TOOLS mapping in run.py | Done |
| CREWAI_STORAGE_DIR project-scoped | env.example has placeholder | OK |

### SAD §4 Backend Architecture Specification

| SAD requirement | Implementation | Status |
|-----------------|----------------|--------|
| Python service layer; agents/tasks from YAML | crew/run.py; build_crew() from YAML | Done |
| Env-based config; .env.example | env.example present | OK |
| Tools bound per YAML; pre-run check | AGENT_TOOLS; fail on missing tools | Done |
| Trace Log under project-context/2.build/logs | step_callback writes trace.log | Done |
| Audit block in artifacts | Deferred; agents output to files | P1 |

### SAD §6 Data Flow

| SAD requirement | Implementation | Status |
|-----------------|----------------|--------|
| API route accepts JSON (campaign, briefs, options) | POST /api/crew; body { message, user_input?, campaign_context? } | Done |
| Streaming support | Not implemented | P1 |
| JSON-serializable response | { status, output, task_outputs } or { status, error } | Done |

---

## 4. Traceability to Frontend

| Frontend expectation | Backend status |
|----------------------|----------------|
| `/api/crew` exists | ✓ route.ts present |
| POST for chat/crew invocation | ✓ POST handler invokes crew; returns JSON |
| Integration epic wires to CrewAI | Done: ChatRuntimeProvider uses crewAdapter calling /api/crew |
| Mock adapter in ChatRuntimeProvider | Replaced with crewAdapter |

---

## 5. Adapter Compliance (adapter-crewai.mdc)

| Adapter rule | Status |
|--------------|--------|
| Agents declare llm/provider/model | llm: openai in agents.yaml | Done |
| role, goal, backstory present | ✓ | Done |
| allow_delegation=false | Set in agents.yaml | Done |
| verbose=False (prod) | Set in agents.yaml and Crew | Done |
| max_iter ≤ 12 | Set to 12 in agents.yaml | Done |
| max_retry_limit ≥ 2 | Set to 2 in agents.yaml | Done |
| Tools in YAML, bound in code | Bound in run.py per AGENT_TOOLS | Done |
| Pre-run tool presence check | build_crew() validates | Done |
| expected_output with path + headings | Full in tasks.yaml | Done |
| No code fences around machine-parsed sections | Instruction in expected_output | Done |
| memory | Not used | OK |
| CREWAI_STORAGE_DIR when memory | env.example OK | OK |
| Temp-write-then-atomic-replace | CrewAI handles output_file | OK |
| Audit block in artifact | Deferred to P1 | P1 |
| Step callback / Trace Log | step_callback → trace.log | Done |
| No secrets in artifacts/logs | OK | OK |

---

## 6. Use Case Alignment

**Usecase.txt:** BAGANA AI enables agencies to manage content strategy at scale through content planning, sentiment analysis, and market trend insights; structured multi-talent plans; data-driven campaigns without proportional manual workload.

**Backend alignment:**  
- content_planner → structured plans ✓ (concept)  
- sentiment_analyst → sentiment analysis ✓ (concept)  
- trend_researcher → market trend insights ✓ (concept)  
- Single crew for integrated workflow ✓ (design)

Implementation complete; crew.kickoff() executes plan → sentiment → trends workflow. Requires OPENAI_API_KEY.

---

## 7. File Inventory

| Path | Purpose | Status |
|------|---------|--------|
| crew/run.py | load_config(), build_crew(), kickoff(); CLI entrypoint | Done |
| crew/tools.py | Stub tools: plan/sentiment/trend validators; report_template_renderer, calendar_brief_loader (P1) | Done |
| crew/stubs.py | Backlog stubs: SentimentAPIClient, TrendAPIClient, MessagingOptimizer, ReportTemplateRenderer, CalendarBriefLoader, AnalyticsEngine, CustomRulesEvaluator; build_report_summarizer_agent_stub | Done |
| config/stubs.yaml | Stub config for report_summarizer, report_summarize, messaging_optimizer (P1) | Done |
| crew/__init__.py | Package init | Minimal |
| config/agents.yaml | Agent definitions (adapter-compliant) | Done |
| config/tasks.yaml | Task definitions (context_from, output_file) | Done |
| requirements.txt | crewai, pyyaml | Present |
| app/api/crew/route.ts | Chat API; spawns Python crew.run --stdin; returns JSON | Done |
| project-context/2.build/logs/ | Trace Log | trace.log written by step_callback |

---

## 8. Gaps and Recommendations

### Completed (*develop-be scaffold)

1. ~~Parse YAML config~~ — Done in load_config(), _load_yaml()
2. ~~Build Crew from config~~ — Done in build_crew()
3. ~~Implement kickoff()~~ — Done; returns { status, output, task_outputs } or { status, error }
4. ~~Complete agents.yaml~~ — Done; llm, allow_delegation, max_iter, etc.
5. ~~Complete tasks.yaml~~ — Done; descriptions, expected_output, context_from
6. ~~Tool binding~~ — Done; crew/tools.py, AGENT_TOOLS in run.py
7. ~~Trace Log~~ — Done; step_callback → trace.log
8. ~~CLI entrypoint~~ — `python -m crew.run [message]`
9. ~~Chat API endpoint~~ — POST /api/crew; crew.run --stdin mode; ChatRuntimeProvider wired

### Priority 2 (future)

10. **Audit block** — Append Audit to artifact outputs (P1).
11. **Pin versions** — requirements.txt pin crewai, pyyaml.
12. **Streaming** — Real-time crew output chunks (P1).

### Prohibited (per backend-eng)

- Database, persistent storage, analytics
- External integrations (sentiment/trend APIs) — use stubs only
- Non-MVP features (report_summarizer, F5–F10)

---

## 9. Backlog Stub Inventory (*stub-nonmvp)

| Stub | Location | PRD ref | Purpose |
|------|----------|---------|---------|
| SentimentAPIClient | crew/stubs.py | F2 | External sentiment API; use SENTIMENT_API_KEY when implemented |
| TrendAPIClient | crew/stubs.py | F3 | External trend/data API; use TREND_API_KEY when implemented |
| MessagingOptimizer | crew/stubs.py | F5 | Messaging optimization suggestions |
| ReportTemplateRenderer | crew/stubs.py | F6 | Render plan+sentiment+trends into report |
| CalendarBriefLoader | crew/stubs.py | F7 | Import/export calendar and brief |
| AnalyticsEngine | crew/stubs.py | F8 | Performance and attribution analytics |
| CustomRulesEvaluator | crew/stubs.py | F10 | Configurable sentiment/trend rules |
| build_report_summarizer_agent_stub | crew/stubs.py | P1 | Agent config for report_summarizer |
| build_report_summarize_task_stub | crew/stubs.py | P1 | Task config for report_summarize |
| report_template_renderer | crew/tools.py | F6 | CrewAI tool for report_summarizer |
| calendar_brief_loader | crew/tools.py | F7 | CrewAI tool for calendar/brief import |
| config/stubs.yaml | config/ | P1 | YAML config for report_summarizer, report_summarize, messaging_optimizer |

Stubs return placeholders only; no real API calls or persistence.

---

## 10. Chat API Specification (*implement-endpoint)

### Endpoint

- **POST** `/api/crew`
- **GET** `/api/crew` — Returns API description (status: ok)

### Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | No | User chat message (primary input) |
| user_input | string | No | Alias for message; used if message omitted |
| campaign_context | string | No | Additional campaign context |

At least one of message, user_input, or campaign_context should be provided. Defaults to "No message provided." if all empty.

### Response (success)

```json
{
  "status": "complete",
  "output": "<crew raw output string>",
  "task_outputs": [{"task": "plan_content", "output": "..."}, ...]
}
```

### Response (error)

```json
{
  "status": "error",
  "error": "<error message>"
}
```

HTTP 500 on crew failure or timeout.

### Implementation

- **Route:** `app/api/crew/route.ts`
- **Invocation:** Spawns `python -m crew.run --stdin` with JSON payload on stdin
- **Timeout:** 120 seconds
- **Python mode:** `--stdin` reads JSON from stdin, writes JSON result to stdout
- **Frontend:** `ChatRuntimeProvider` uses `crewAdapter` that POSTs last user message to `/api/crew` and renders `output` as assistant reply

### Prerequisites

- `OPENAI_API_KEY` in `.env`
- Python with crewai installed; `python` or `python3` in PATH

---

## 11. Deferred Work

| Item | Owner | Notes |
|------|-------|-------|
| ~~API ↔ CrewAI wiring~~ | Done | POST /api/crew → crew.run --stdin |
| Streaming from crew to client | P1 | Real-time chunks |
| Sentiment/trend API integration | Integration / Backend | Stub clients in crew/stubs.py |
| report_summarizer agent | P1 | Config in config/stubs.yaml; wire when P1 |
| Database/schema for plans | Out of scope | Backend-eng prohibited |

---

## Sources

- **project-context/1.define/prd.md** — F1–F4, agent definitions (§3), P0 scope.
- **project-context/1.define/sad.md** — Backend (§4), Multi-Agent (§2), Data Flow (§6).
- **project-context/1.define/mrd.md** — Technical feasibility.
- **project-context/2.build/frontend.md** — API expectations, deferred wiring.
- **project-context/2.build/setup.md** — Structure, file roles, downstream owners.
- **Usecase.txt** — Product anchor.
- **.cursor/agents/backend-eng.md** — Persona, actions, prohibited actions.
- **.cursor/rules/adapter-crewai.mdc** — CrewAI adapter contract.

---

## Assumptions

- Backend owns CrewAI Python layer and chat API; ChatRuntimeProvider wired to /api/crew.
- Sentiment and trend tools can be stubs (no real API calls) per prohibited-actions; env placeholders remain for future.
- report_summarizer and F5–F10 are P1/P2; not in scope for *develop-be.
- API route (app/api/crew/route.ts) is scaffolded by Frontend; Backend provides the Python interface for Integration to call.

---

## Open Questions

- ~~Next.js → Python invocation~~ Resolved: subprocess (`python -m crew.run --stdin`).
- Preferred artifact output paths for plan, sentiment, trend (e.g. project-context/2.build/artifacts/plan.md)?
- Schema for plan/sentiment/trend artifacts (template headings) — to be defined in tasks expected_output.

---

## Audit

| Timestamp   | Persona       | Action        |
|------------|----------------|---------------|
| 2025-02-02 | @backend.eng   | *develop-be review |
| 2025-02-02 | @backend.eng   | *develop-be scaffold |
| 2025-02-02 | @backend.eng   | *stub-nonmvp |
| 2025-02-02 | @backend.eng   | *implement-endpoint |

Backend scaffolded. CrewAI crew and agents implemented. Chat API POST /api/crew wired; ChatRuntimeProvider uses crewAdapter. Backlog stubs in crew/stubs.py, crew/tools.py, config/stubs.yaml. No code fences around machine-parsed sections.
