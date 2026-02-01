# BAGANA AI — Setup Artifact (project skeleton)

**Document version:** 1.0  
**Persona:** @project.mgr  
**Invocation:** *setup-project  
**Sources:** PRD (prd.md), MRD (mrd.md), SAD (sad.md), Usecase.txt  
**Output:** project-context/2.build/setup.md (this file)

---

## Context

Setup creates the project skeleton per PRD and SAD. No application logic is implemented here; implementation is owned by Backend, Frontend, Integration, and QA epics per [epics-index](.cursor/rules/epics-index.mdc).

**Use case (anchor):**  
BAGANA AI is an AI-powered platform designed for KOL, influencer, and content creator agencies to manage content strategy at scale through integrated content planning, sentiment analysis, and market trend insights. It enables agencies to create structured multi-talent content plans, optimize messaging and engagement, and deliver data-driven campaigns more efficiently without increasing manual workload.

---

## 1. Folder structure created

```
bagana-ai-conent-planer/
├─ .cursor/                    # (existing) agents, rules, templates
├─ config/                     # CrewAI agent and task config (SAD §2)
│   ├─ agents.yaml             # Agent definitions stub
│   └─ tasks.yaml              # Task definitions stub
├─ crew/                       # Python CrewAI orchestration layer (SAD §4)
│   ├─ __init__.py
│   └─ run.py                  # Entrypoint stub; Backend implements kickoff
├─ project-context/
│   ├─ 1.define/              # (existing) prd, mrd, sad, etc.
│   └─ 2.build/
│       ├─ logs/               # Trace Log and agent run logs (SAD §2, §5)
│       │   └─ .gitkeep
│       └─ setup.md             # This file
├─ env.example                 # Extended with LLM and integration placeholders
├─ requirements.txt            # Python deps: crewai, pyyaml
├─ Usecase.txt                 # (existing)
└─ README.md                   # (existing)
```

**Deferred to other epics:**
- **Frontend (Phase 2/3):** `app/` (Next.js App Router), `app/api/` for API routes — SAD §3; *develop-fe*.
- **Backend:** Prisma/schema, DB migrations, tool implementations — SAD §4; *develop-be*.
- **Integration:** API ↔ CrewAI wiring, streaming — SAD §6; *integrate-api*.

---

## 2. Steps performed

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Created `config/` and stub `agents.yaml`, `tasks.yaml` (agent/task IDs and placeholders from PRD §3, SAD §2). | SAD §2 (Agent Architecture, CrewAI Configuration) |
| 2 | Created `crew/` with `__init__.py` and `run.py` stub (load config paths; placeholder `kickoff`; no CrewAI logic). | SAD §4 (CrewAI Integration Layer) |
| 3 | Created `project-context/2.build/logs/` with `.gitkeep` for Trace Log. | SAD §2, §5 (Logging) |
| 4 | Added `requirements.txt` with crewai, pyyaml. | SAD §4; PRD §3 |
| 5 | Extended `env.example` with AAMAD_ADAPTER, OPENAI_API_KEY, CREWAI_STORAGE_DIR, SENTIMENT_API_KEY, TREND_API_KEY placeholders. | SAD §4 (Configuration), §6 (External Integration) |
| 6 | Wrote this setup.md. | epics-index: Setup → setup.md |

---

## 3. File roles and downstream owners

| Path | Purpose | Downstream owner |
|------|---------|------------------|
| **config/agents.yaml** | Agent definitions (role, goal, backstory); tools bound in code per adapter. | Backend: refine attributes, add llm, tools, memory; bind tools in crew code. |
| **config/tasks.yaml** | Task definitions (description, expected_output, context, agent ref). | Backend: add full expected_output (path + headings), context bindings; wire to crew. |
| **crew/run.py** | Entrypoint to load config and run crew. | Backend: implement Crew build from YAML, tool binding, kickoff(), streaming, Trace Log, Audit. |
| **project-context/2.build/logs/** | Directory for Trace Log and agent run logs. | Backend: write step_callback and Trace Log here; adapter rules. |
| **env.example** | Required env var names; no secrets. | Backend/Integration: add vars when sentiment/trend APIs chosen; document in setup if needed. |
| **requirements.txt** | Python dependencies for CrewAI layer. | Backend: pin versions; add tool deps (e.g. requests for APIs). |

---

## 4. Verification

- [x] config/agents.yaml and config/tasks.yaml exist and reference PRD §3 agents (content_planner, sentiment_analyst, trend_researcher).
- [x] crew/ contains Python package with run.py stub; no application logic (no CrewAI kickoff implementation).
- [x] project-context/2.build/logs/ exists for Trace Log.
- [x] env.example includes AAMAD_ADAPTER and placeholders for LLM and integrations; no secrets.
- [x] requirements.txt includes crewai and pyyaml.
- [x] setup.md documents structure, steps, and downstream ownership.

---

## 5. Next steps (other epics)

- **Backend (*develop-be):** Implement crew build from config, tool implementations (file I/O, schema validation, sentiment/trend clients), kickoff(), Audit and Trace Log per adapter.
- **Frontend (*develop-fe):** When UI in scope, create Next.js app structure (app/, app/api/), assistant-ui, per SAD §3.
- **Integration (*integrate-api):** Wire API routes to CrewAI layer; streaming; validation.
- **QA (*qa):** Test crew run and artifact validity per SAD §9.

---

## Sources

- **project-context/1.define/prd.md** — Requirements, agent definitions (§3), P0 scope (F1–F4).
- **project-context/1.define/mrd.md** — Technical feasibility, risk matrix.
- **project-context/1.define/sad.md** — Architecture, config layout (§2), CrewAI layer (§4), env and logging.
- **Usecase.txt** — BAGANA AI use case.
- **.cursor/rules/epics-index.mdc** — Setup epic, output artifact setup.md.
- **.cursor/agents/project-mgr.md** — *setup-project; no application code.

---

## Assumptions

- MVP can start with CLI or minimal UI; Next.js app structure is created in Frontend epic when UI is in scope (PRD §6, SAD A3).
- Agent and task YAML are stubs; Backend epic refines and wires to CrewAI (SAD §2).
- Sentiment and trend API keys and endpoints are added to .env when chosen (SAD Open Questions Q1).

---

## Audit

| Timestamp   | Persona       | Action        |
|------------|----------------|---------------|
| 2025-02-01 | @project.mgr   | *setup-project |

Setup skeleton created per PRD and SAD. No code fences around machine-parsed sections.
