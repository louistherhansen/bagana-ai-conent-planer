# BAGANA AI — System Architecture Document (SAD)

**Document version:** 1.0  
**Source:** PRD (prd.md), MRD (mrd.md), Usecase.txt  
**Template:** .cursor/templates/sad-template.md  
**Persona:** @system.arch  
**Adapter:** crewai (AAMAD_ADAPTER)

---

## Context & Instructions

This SAD defines the system architecture for BAGANA AI, an AI-powered content strategy platform for KOL/influencer/content creator agencies. It is derived from the PRD, MRD, and use case and follows the AAMAD SAD template. The architecture supports an MVP (Phase 1: CLI or minimal UI) with a defined path to Phase 3 (Next.js + assistant-ui). All PRD requirements are mapped to architectural components; CrewAI is the execution adapter.

**Use case (anchor):**  
BAGANA AI is an AI-powered platform designed for KOL, influencer, and content creator agencies to manage content strategy at scale through integrated content planning, sentiment analysis, and market trend insights. It enables agencies to create structured multi-talent content plans, optimize messaging and engagement, and deliver data-driven campaigns more efficiently without increasing manual workload.

---

## 1. MVP Architecture Philosophy & Principles

### MVP Design Principles

- **Customer Feedback First:** Deploy quickly to validate core value proposition (unified planning + sentiment + trends) with 2–5 agency or in-house creator teams (PRD §9).
- **Modern LLM Interface Path:** MVP may use CLI or minimal UI (PRD §6); target state uses assistant-ui for production-grade AI chat experience when frontend is in scope (Phase 2/3).
- **Automated Deployment:** CI/CD from day one to enable rapid iteration; pipeline and gates defined in §5.
- **Observable by Default:** Logging, tracing, and audit trail for crew runs and artifact writes (PRD §3, §5; MRD §4).

### Core vs. Future Features Decision Framework

- **Phase 1 (MVP):** Core agents (content planner, sentiment analyst, trend researcher); one crew for “plan + sentiment + trends”; essential integrations (sentiment, one trend source); CLI or minimal UI; logging and basic audit (PRD §8).
- **Phase 2 (Enhanced):** Messaging optimization (F5), reporting/dashboards (F6), optional calendar/brief integrations (F7); production hardening, full NFRs (PRD §8).
- **Phase 3 (Scale):** Advanced analytics (F8), more platforms/regions (F9), custom models/rules (F10); full Next.js + assistant-ui when adopted (template Phase 3).
- **Validation Focus:** Prove product-market fit and core workflow (F1–F4) before scaling complexity (MRD Critical Decision Points).

### Technical Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **CrewAI over alternatives** | PRD and MRD specify CrewAI; supports multi-agent crews, sequential/hierarchical flows, tools; adapter rules (.cursor/rules/adapter-crewai.mdc) define contract. |
| **Next.js App Router (when UI in scope)** | App Router provides modern React patterns, server components, and API routes in one codebase; aligns with template and future assistant-ui integration. |
| **assistant-ui (Phase 3)** | Production-grade LLM chat interface; reduces custom chat build; supports streaming and tool components for agent results (template §3). |
| **Single primary crew for MVP** | One crew (plan → sentiment → trend enrichment) suffices for P0; optional reporting crew deferred to P1 (PRD §3, Assumptions). |
| **Real-time streaming** | For interactive flows, streaming responses from CrewAI through API layer to client improve perceived performance and UX when web UI is used. |

---

## 2. Multi-Agent System Specification

### Agent Architecture Requirements

- **Count:** 3–4 specialized agents maximum for MVP (PRD §3): content_planner, sentiment_analyst, trend_researcher; optional report_summarizer in P1.
- **Roles, goals, backstories:** Defined in PRD §3 Core Agent Definitions; refined in config (e.g. config/agents.yaml) per adapter-crewai: role domain-specific and action-oriented; goal measurable and outcome-focused; backstory concise and concrete.
- **Collaboration:** Sequential flow for MVP: plan creation → sentiment and trend enrichment → optimization suggestions; no delegation unless SAD explicitly requires it (PRD §3; adapter: allow_delegation=false for build personas).
- **Memory:** Per-campaign/epic; no cross-project by default. sentiment_analyst and trend_researcher scoped to current run; content_planner per-campaign; report_summarizer memory=false (PRD §3; adapter: memory=False for reproducible artifacts unless justified).
- **Tools:** Whitelisted only. content_planner: file I/O, plan schema validation, calendar/brief loaders. sentiment_analyst: sentiment APIs or models, file I/O, schema validation. trend_researcher: approved web/API tools with rate limits, file I/O. report_summarizer (P1): file I/O, template renderers (PRD §3; adapter: bind only tools needed per task).

### Task Orchestration Specification

- **Task dependencies:** Plan task → outputs (e.g. plan artifact) as context to Sentiment and Trend tasks; optional merge then to Report task (P1). Explicit Task.context for inter-task data; no reliance on conversation memory for artifact production.
- **Expected outputs:** Each task declares expected_output with target file path and required template headings; self-check verifies headings; on mismatch write Diagnostic and halt (adapter Tasks and Outputs).
- **Context passing:** PRD, SAD, SFS, user stories and prior task outputs passed via Task.context; variable placeholders in YAML (e.g. {campaign_id}, {brief_path}) bound at runtime.
- **Error handling:** Retries per adapter (max_retry_limit ≥ 2); on iteration/time limits or missing prerequisites write Halt and Report with blockers (AAMAD Failure Policy).
- **Performance:** max_iter ≤ 12 for MVP tasks; max_execution_time and token limits per persona; response time target for typical interactive tasks &lt; 30s (PRD §5; SAD §7).

### CrewAI Framework Configuration

- **Crew composition:** One crew for “plan and optimize”: content_planner → (sentiment_analyst, trend_researcher) with shared plan context; process sequential for deterministic builds (adapter: prefer sequential; hierarchical only if SAD documents it).
- **Memory and caching:** memory=False default for reproducibility; CREWAI_STORAGE_DIR project-scoped if memory enabled; caching per framework and env.
- **Logging:** verbose=False for production; step_callback and Trace Log under project-context/2.build/logs; Prompt Trace and Audit in artifact (adapter Memory and Logging).
- **Integration with Next.js:** When frontend is in scope, Next.js API routes call Python CrewAI service layer (subprocess or separate service); JSON-serializable request/response; streaming supported for interactive flows.

---

## 3. Frontend Architecture Specification (Next.js + assistant-ui)

*MVP may ship with CLI or minimal UI (PRD §6). The following applies when frontend is in scope (Phase 2/3).*

### Technology Stack Requirements

- **Framework:** Next.js 14+ with App Router.
- **UI:** assistant-ui for LLM chat interface; shadcn/ui for shared components.
- **Styling:** Tailwind CSS.
- **Type safety:** TypeScript across frontend and API boundary.
- **State:** Zustand for client-side state where needed.

### Application Structure Requirements

- **App Router:** app/ with routes for chat, plans, reports (when F6 in scope); API routes under app/api/ for CrewAI proxy and streaming.
- **API route organization:** e.g. app/api/crew/route.ts (or /plan, /analyze) calling Python CrewAI layer; streaming via ReadableStream where applicable.
- **Components:** Reusable UI elements; custom assistant-ui components for agent result display (e.g. plan snippet, sentiment summary, trend card).
- **Layout:** Main chat or dashboard layout; navigation for plans and reports when P1 features exist.

### assistant-ui Integration Specifications

- **Custom tool components:** Map agent outputs (plans, sentiment results, trend insights) to display components within chat.
- **Streaming:** Consume streaming API responses for real-time updates during crew execution.
- **User interaction:** User provides campaign/brief inputs and options; agents produce structured outputs; errors and limits surface as diagnostics.
- **Theming:** Align with Tailwind and shadcn; accessibility (ARIA) and responsive layout for desktop/mobile.

### User Interface Requirements

- **Main interface:** Chat-centric for “plan and optimize” workflow; optional dashboard for analytics/reports (P1).
- **Responsive and accessibility:** WCAG-aligned; loading states and error handling for API and crew failures.
- **Future work:** Advanced dashboards and BI deferred to P2 (PRD F8).

---

## 4. Backend Architecture Specification

### API Architecture Requirements

- **Next.js API routes:** Serve as gateway to CrewAI layer; accept JSON (e.g. campaign context, brief paths, options); return JSON or streamed response.
- **Streaming:** Support for streaming crew output when UI is interactive; error propagation and user-visible messages on failure.
- **Request/response:** Typed payloads; validation at API boundary (e.g. Zod or similar); rate limiting and security middleware per §8.
- **Logging:** Request/response logging and correlation with crew run IDs; no secrets in logs.

### Database Architecture Specification

- **Data models:** Conversation/session metadata (when UI stores history); plans, analyses, and reports as structured artifacts (file or DB-stored per schema).
- **Technology:** SQLite for MVP simplicity; schema and access pattern designed for PostgreSQL migration path (template §4; PRD §8).
- **Migrations:** Schema management via migrations (e.g. Prisma or similar); retention and cleanup policies for sessions and temp artifacts defined in ops.
- **Backup:** Backup and recovery requirements per org; no secrets in DB.

### CrewAI Integration Layer Requirements

- **Python service layer:** Agent orchestration via CrewAI; agents and tasks loaded from YAML (config/agents.yaml, config/tasks.yaml) per adapter; no inline agent/task definitions in code.
- **Configuration:** Env-based (e.g. API keys, model names); .env.example with required vars; validation at startup.
- **Tools:** Custom tools (file I/O, schema validation, sentiment/trend clients) implemented and bound per YAML; pre-run tool presence check to avoid KeyError (adapter).
- **Monitoring:** Log agent/task lifecycle and performance; token usage and model in Audit block of artifacts.

### Authentication & Security Specifications

- **Authentication:** When multi-user is required, NextAuth.js or equivalent; scope to SAD and org policy (PRD §5).
- **Secrets:** No secrets in artifacts or logs; API keys and sensitive config from environment variables only.
- **Input validation:** Sanitize and validate all inputs at API and agent entry-points; guard against prompt-injection in quoted user content (adapter).
- **Rate limiting:** Applied at API and, where relevant, to external sentiment/trend APIs; policies documented in SAD §8.
- **CORS and headers:** Secure headers and CORS configuration for API and app.

---

## 5. DevOps & Deployment Architecture

### CI/CD Pipeline Requirements

- **Automation:** GitHub Actions (or org-standard) for build, test, and deploy.
- **Build:** Next.js build and optimization; Python env for CrewAI layer; dependency and env validation.
- **Testing:** Unit tests for API and business logic; integration tests for API and CrewAI layer; E2E for critical user flows when UI exists (template §9).
- **Gates:** Deployment gates (e.g. tests pass, no critical secrets); approval process for production per org.
- **Rollback:** Documented rollback and blue-green or equivalent where required.

### AWS App Runner (or Equivalent) Configuration

- **Compute/memory:** Sized for MVP scale (CrewAI runtime + model calls); defined in infra code or runbook.
- **Scaling:** Auto-scaling policies and performance targets per SAD §7.
- **Health:** Health-check endpoints for app and dependency readiness; monitoring and alerting (§5 Monitoring).
- **Secrets:** Environment variable and secrets management; no secrets in code or artifacts.

### Infrastructure as Code

- **Templates:** Terraform or CloudFormation (or org standard) for compute, network, and storage; staging and production separation.
- **Backup/DR:** Backup and disaster recovery procedures documented; cost and resource monitoring.

### Monitoring & Observability

- **APM:** Application performance monitoring for API and crew runs; latency and success rate.
- **Logs:** Log aggregation and analysis; Trace Log and Audit for agent runs under project-context/2.build/logs and artifacts.
- **Analytics:** User behavior and event collection when UI is in scope; privacy-compliant and anonymized where required.
- **Alerting:** Alerts on failure rates, latency SLO breaches, and critical errors; dashboards for operational visibility.

---

## 6. Data Flow & Integration Architecture

### Request/Response Flow Specification

- **User request:** User input (campaign, briefs, options) → frontend (or CLI) → API route → CrewAI layer → crew.kickoff() (or equivalent).
- **Data transformation:** API payloads mapped to crew inputs; crew outputs (plans, sentiment, trends) mapped to API response or stream chunks; JSON-serializable for frontend.
- **Streaming:** Real-time chunks from crew execution streamed to client when supported; error propagation and user feedback on failure.
- **Caching:** Caching strategies for repeated reads (e.g. trend/sentiment cache) where beneficial and within rate limits.

### External Integration Requirements

- **Sentiment:** Internal or third-party sentiment API; rate limits and timeouts; env-based config; fallback or graceful degradation per MRD risk matrix.
- **Trend/data sources:** Approved web/API tools with rate limits; attribution and error handling; defined in config and SAD.
- **Calendar/brief (P1):** Optional import/export; formats and systems per PRD Open Questions; sync and consistency requirements documented when adopted.

### Analytics & Feedback Architecture

- **Events:** User interaction and task completion events when UI exists; stored in compliance with privacy and retention policy.
- **Feedback:** Feedback data models and storage for beta and post-launch; used for iteration (PRD §9, template §10).
- **Real-time dashboard:** Optional real-time dashboard updates for ops and, in P1, for reporting (F6).

---

## 7. Performance & Scalability Specifications

### Performance Requirements

- **Response time:** Typical interactive tasks (e.g. plan creation, single analysis) &lt; 30s target (PRD §5); streaming to improve perceived latency where applicable.
- **Throughput/concurrency:** Batch and concurrent run limits defined per MVP scale; constrained by external API rate limits and LLM cost (MRD §2).
- **Database:** Query optimization and indexing for session and artifact access; CDN for static assets when frontend is deployed.

### Scalability Architecture

- **Horizontal scaling:** Triggers and policies for scaling app and CrewAI workers per SAD and infra; load balancing when multi-instance.
- **Database scaling:** Path to read replicas and sharding when moving beyond SQLite/single DB (template §7).
- **Microservices:** Current design single deployment for MVP; separation points for crew vs. API vs. frontend documented for future growth.

### Resource Optimization

- **Token usage:** max_iter and context limits per adapter; token usage recorded in Audit; optimization of prompts and context size.
- **Cost:** Rate limits and timeouts to control LLM and external API cost; budget alerting and monitoring (MRD §4).

---

## 8. Security & Compliance Architecture

### Security Framework Requirements

- **Authentication and authorization:** Per SAD and org policy; NextAuth.js or equivalent when multi-user (PRD §5).
- **Encryption:** Data encrypted in transit (TLS); at rest per platform and org standards.
- **API security:** Input validation and sanitization; no secrets in artifacts or logs; security scanning and vulnerability management in pipeline.
- **Incident response:** Security monitoring and incident response per org.

### Data Privacy & Compliance

- **User data:** Handling and retention aligned to privacy and compliance (e.g. GDPR where applicable); PRD §5.
- **Retention and deletion:** Policies documented; audit logging and compliance reporting where required.
- **Consent:** User consent and preferences when personal data is processed (e.g. analytics, feedback).

---

## 9. Testing & Quality Assurance Specifications

### Testing Strategy Requirements

- **Unit:** Coverage for API handlers, validation, and core business logic; standards and thresholds in pipeline.
- **Integration:** API and CrewAI layer integration tests; DB and external service mocking where appropriate.
- **E2E:** End-to-end tests for core workflows (create plan → sentiment/trend → view result) when UI and API are stable (template §9).
- **Performance:** Load and performance tests for API and crew runs within MVP targets.
- **Security:** Vulnerability and secret scanning in CI; security testing per org.

### Quality Gates & Validation

- **Code quality:** Linting and formatting; TypeScript and Python type checks; deployment validation and smoke tests.
- **Artifact quality:** Template headings and schema compliance; self-check and guardrails per adapter; Diagnostic on failure.
- **Accessibility:** Accessibility testing when UI is in scope (template §9).

---

## 10. MVP Launch & Feedback Strategy

### Beta Testing Framework

- **Selection:** 2–5 agency or in-house creator teams (PRD §9).
- **Scenarios:** Multi-talent plan creation, sentiment and trend runs, end-to-end workflow.
- **Feedback:** Collection and analysis; feature flags for gradual rollout where applicable.
- **Success:** Completed runs, artifact quality, qualitative feedback (PRD §9).

### User Experience Optimization

- **Onboarding:** Low-friction onboarding; help and documentation when UI is in scope.
- **Feedback loop:** User feedback and feature request handling; retention and engagement tracking post-launch.
- **Support:** Customer support and escalation paths per org.

### Business Metrics & Analytics

- **KPIs:** Time to produce/update multi-talent plan; campaign performance indicators; agency adoption (PRD §7).
- **Technical metrics:** Crew run success rate, latency, resource usage; artifact validity and audit completeness (PRD §7).
- **Dashboards:** Operational and, in P1, business-facing dashboards (F6) per template §10.

---

## Implementation Guidance for AI Development Agents

### Phase 2 Development Priorities (aligned with PRD phases)

1. **Foundation:** Project structure (Next.js if UI; Python CrewAI); TypeScript and Tailwind when frontend in scope.
2. **CrewAI backend:** Agent and task YAML config; Python orchestration; tool implementation and binding.
3. **API layer:** Next.js API routes (or minimal HTTP API) connecting clients to CrewAI layer; streaming support.
4. **Database:** Prisma (or equivalent) with SQLite; schema for sessions and artifacts as needed.
5. **assistant-ui (Phase 2/3):** Chat interface with streaming and tool components when moving off CLI/minimal UI.
6. **Authentication:** When required, NextAuth.js or org standard.
7. **Testing:** Jest (and Playwright for E2E when UI exists); initial test suites for API and crew.
8. **CI/CD:** GitHub Actions (or org standard) with deployment to AWS App Runner or equivalent.

### Critical Architecture Decisions to Implement

- **Server vs. client components:** Use Next.js Server Components where appropriate; Client Components for interactive chat and state (when assistant-ui in scope).
- **Error boundaries:** Fallback UI and error boundaries for app and crew failures.
- **Database schema:** Design for MVP with clear path to PostgreSQL and future scaling.
- **API design:** RESTful or RPC-style with consistent error responses and types.
- **Type safety:** End-to-end TypeScript types from API to frontend; Python types for CrewAI layer.

### MVP Scope Boundaries

- **In scope:** Core content marketing workflow — plan creation, sentiment analysis, trend insights, integrated workflow (F1–F4); single primary crew; CLI or minimal UI; essential security and observability.
- **Out of scope for MVP:** Complex user/tenant management; advanced BI; enterprise security features; full assistant-ui (optional for Phase 2); optional report_summarizer and F5–F7 (P1).

---

## Architecture Validation Checklist

- [x] All PRD requirements mapped to architectural components (F1–F4 → crew, agents, API, storage).
- [x] CrewAI agents designed for content marketing domain (content_planner, sentiment_analyst, trend_researcher).
- [x] assistant-ui integration path specified for Phase 2/3 when UI is in scope.
- [x] Next.js and API design aligned with template and PRD; MVP allows CLI/minimal UI.
- [x] Database schema supports required queries and PostgreSQL migration path.
- [x] API design with validation, error handling, and streaming where needed.
- [x] Security measures appropriate for MVP; secrets and compliance per PRD and adapter.
- [x] CI/CD and monitoring support rapid iteration and deployment.
- [x] Analytics and feedback support launch and improvement (PRD §7, §9).
- [x] Architecture supports transition from MVP to full production (phases and scaling path).

---

## Sources

- **Usecase.txt** — BAGANA AI use case (content strategy at scale; planning, sentiment, trends; multi-talent plans; efficiency without proportional manual workload).
- **project-context/1.define/prd.md** — Product requirements, agent definitions, P0–P2 features, NFRs, phases, success metrics.
- **project-context/1.define/mrd.md** — Market context, technical feasibility, user journey, production requirements, risk matrix.
- **.cursor/templates/sad-template.md** — AAMAD SAD structure and section headings.
- **.cursor/rules/adapter-crewai.mdc** — CrewAI adapter contract (agents, tasks, tools, logging, quality gates).

---

## Assumptions

*For downstream resolution, see [assumptions-and-open-questions.md](assumptions-and-open-questions.md).*

- MVP may deliver CLI or minimal UI; full Next.js + assistant-ui is Phase 2/3 (PRD §6, §8).
- Sentiment and trend data sources and APIs are selected in implementation with rate limits and cost validated (PRD Open Questions).
- Single primary crew (plan + sentiment + trends) is sufficient for MVP; optional reporting crew is P1 (PRD Assumptions).
- AAMAD_ADAPTER=crewai for this release; architecture aligns with CrewAI runtime semantics (system-arch.md).
- Org standards apply for cloud provider, auth, and compliance; SAD references them where specific choices are deferred.

---

## Open Questions

*For downstream resolution, see [assumptions-and-open-questions.md](assumptions-and-open-questions.md).*

- Exact sentiment and trend APIs/sources, rate limits, and cost (PRD Open Questions; MRD).
- Preferred calendar/brief formats and systems for F7 (P1) (PRD Open Questions).
- Geographic and language scope for v1 (PRD, MRD).
- Formal ROI model and baseline metrics for efficiency and manual workload (MRD Open Questions).
- Timeline and milestones (project plan).

---

## Audit

| Timestamp   | Persona       | Action     | Adapter |
|------------|----------------|------------|---------|
| 2025-02-01 | @system.arch   | create-sad | crewai  |

SAD generated from prd.md, mrd.md, Usecase.txt, and .cursor/templates/sad-template.md. No code fences around machine-parsed sections.
