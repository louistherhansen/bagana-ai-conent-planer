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

## Stakeholders and Concerns (ISO/IEC/IEEE 42010)

| Stakeholder | Role | Primary concerns |
|-------------|------|-------------------|
| **Agency ops managers** | End user / buyer | Coordination at scale; time to plan; consistency across talents; audit trail and reproducibility. |
| **Content strategists** | End user | Quality of plans and briefs; sentiment and trend inputs; messaging optimization; integration with existing tools. |
| **Campaign managers** | End user | Campaign–talent alignment; performance visibility; reporting; approval and brand safety. |
| **Development team** | Builder | Maintainability; adapter contract; testability; CI/CD and deployment; cost and latency control. |
| **Operations / DevOps** | Operator | Deployment, monitoring, alerting; secrets and config; scaling and cost; incident response. |
| **Product / business** | Owner | MVP scope; product–market fit; beta feedback; roadmap (P1/P2) and success metrics. |
| **Compliance / legal** | Reviewer | Data privacy (e.g. GDPR); retention and deletion; consent; no secrets in artifacts. |

**Correspondence:** Concerns are addressed in the architectural views (§§2–6), quality attributes (§7 and Quality Attributes Summary), constraints, and risks below; traceability to PRD/MRD is maintained throughout.

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

## Architectural Views (Views and Beyond)

Views below use primary presentation + element catalog + rationale; they correspond to §§2–6 and support stakeholder concerns.

### Logical View

**Primary presentation:** System as components and their responsibilities.

| Element | Type | Responsibility |
|--------|------|----------------|
| **Content Planner Agent** | Agent | Produce/update structured content plans (calendars, briefs, messaging) from campaign context. |
| **Sentiment Analyst Agent** | Agent | Analyze content/briefs for sentiment and tone; surface risks and opportunities. |
| **Trend Researcher Agent** | Agent | Gather and summarize market/trend insights for plans and briefs. |
| **Report Summarizer Agent** | Agent (P1) | Produce human-readable summaries/reports from plan + sentiment + trend outputs. |
| **Crew (Plan + Sentiment + Trends)** | Crew | Orchestrate agents sequentially; pass context; produce plans and enriched artifacts. |
| **API layer** | Component | Gateway between client (CLI/UI) and CrewAI layer; validation, streaming, auth. |
| **CrewAI integration layer** | Component | Load agents/tasks from YAML; run crew; bind tools; log and audit. |
| **Storage** | Component | Plans, analyses, reports (file/DB); session metadata when UI stores history. |

**Rationale:** Logical decomposition aligns with PRD §3 agent definitions and single-crew MVP scope; API and storage support F1–F4 and future UI.

### Process / Runtime View

**Primary presentation:** Request flow and runtime behavior.

| Element | Description |
|--------|-------------|
| **Request path** | User input → API (or CLI) → CrewAI layer → crew.kickoff() → tasks run sequentially (plan → sentiment/trend) → outputs written; streamed to client when UI. |
| **Context passing** | Task.context carries PRD/SAD/SFS, user input, prior task outputs; no reliance on conversation memory for artifacts. |
| **Error path** | Retries per adapter; on limit/prerequisite failure: Halt and Report, Diagnostic written; API returns user-visible error. |
| **Concurrency** | MVP: single crew run per request; batch/concurrency limits per §7; external API rate limits constrain throughput. |

**Rationale:** Sequential process ensures deterministic, auditable builds; streaming improves perceived latency for interactive UI.

### Deployment View

**Primary presentation:** Nodes and deployment units.

| Element | Description |
|--------|-------------|
| **MVP** | Single deployment unit (e.g. AWS App Runner or equivalent): Next.js app (when UI) + API routes; Python CrewAI service (subprocess or same host); SQLite (or file-based) storage. |
| **Scaling path** | Horizontal scaling of app/API; CrewAI workers; DB migration to PostgreSQL, read replicas/sharding when needed (§7). |
| **Environments** | Staging and production; secrets and config via env; no secrets in code or artifacts. |
| **CI/CD** | GitHub Actions (or org standard); build, test, deploy; gates and rollback per §5. |

**Rationale:** Single deployment for MVP minimizes complexity; separation points (API, crew, DB) documented for future scaling.

### Data View

**Primary presentation:** Key data and flow between components.

| Element | Description |
|--------|-------------|
| **Inputs** | Campaign context, brief paths, options (user/API); PRD/SAD/SFS (context). |
| **Artifacts** | Plans (schema-valid), sentiment results, trend summaries, reports (P1); file or DB per schema; temp-write-then-atomic-replace. |
| **Sessions** | When UI: conversation/session metadata; retention and cleanup per policy. |
| **External** | Sentiment API responses; trend/data source outputs; rate-limited, env-configured. |
| **Audit** | Artifact Audit block (persona, task, model, temperature, token usage); Trace Log under project-context/2.build/logs. |

**Rationale:** Data model supports F1–F4, reproducibility, and compliance; no secrets in artifacts or logs.

**Correspondence rules:** Logical view elements map to §2 (agents, crew), §4 (API, CrewAI layer, DB). Process view maps to §2 (orchestration), §6 (data flow). Deployment view maps to §5. Data view maps to §4 (DB), §6 (flows), adapter (audit).

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

### Quality Attributes Summary

| Quality attribute | Priority | Scenario / target | Addressed in |
|-------------------|----------|--------------------|--------------|
| **Performance** | High | Interactive tasks (e.g. plan creation, single analysis) &lt; 30s; streaming for perceived latency | §7; §2 (max_iter, time limits); §6 (streaming) |
| **Scalability** | Medium | MVP: single instance; path to horizontal scaling, DB read replicas/sharding | §7; Deployment View |
| **Security** | High | No secrets in artifacts/logs; auth per org; input validation; encryption in transit/at rest | §8; §4 (Auth & Security) |
| **Modifiability** | High | Agent/task config in YAML; adapter contract; clear separation API / CrewAI / storage | §2; §4; Logical View |
| **Testability** | High | Unit (API, logic); integration (API + CrewAI); E2E when UI; artifact schema/guardrails | §9 |
| **Availability** | Medium | 99%+ target for MVP per PRD §5; health checks, monitoring, rollback | §5; §7 |
| **Usability** | High | Clear human–agent boundary; errors surface as diagnostics; WCAG when UI | §3; §6; PRD §6 |
| **Auditability** | High | Audit block in artifacts; Trace Log; Prompt Trace; provenance and template compliance | §2; §4; adapter rules |

**Rationale:** Priorities align with PRD NFRs (§5), MRD production requirements, and AAMAD reproducibility/audit requirements.

---

## Constraints

| Constraint | Source | Effect |
|------------|--------|--------|
| **CrewAI as execution framework** | PRD §3; AAMAD_ADAPTER=crewai | Agents, tasks, and tools must conform to adapter-crewai.mdc; YAML config; no inline agent/task code. |
| **No secrets in artifacts or logs** | PRD §5; AAMAD core; adapter | All sensitive config (API keys, model secrets) from environment variables only; no embedding in plans, reports, or Trace Log. |
| **Single primary crew for MVP** | PRD §3, Assumptions | No delegation; sequential flow; optional reporting crew deferred to P1. |
| **P0 scope (F1–F4)** | PRD §4, §8 | MVP delivers multi-talent plans, sentiment analysis, trend insights, integrated workflow only; F5–F10 deferred. |
| **Schema and template compliance** | Adapter; AAMAD | Expected outputs with required headings; self-check and guardrails; Diagnostic on failure; no code fences around machine-parsed sections. |
| **Org standards** | SAD references | Cloud provider, auth, compliance, backup/DR, and incident response follow org policy where specified. |
| **External API rate limits and cost** | MRD §2, risk matrix | Sentiment and trend integrations must respect rate limits and timeouts; usage monitored; fallback or graceful degradation. |

**Rationale:** Constraints ensure reproducibility, security, and alignment with PRD/MRD and adapter contract; deviations must be documented and justified.

---

## Architectural Risks

| Risk | Level | Description | Mitigation |
|------|-------|-------------|------------|
| **External API cost/availability** | High | Sentiment and trend APIs may be costly or unavailable; impacts crew completion and cost | Rate limits, timeouts, fallbacks; env-based config; usage monitoring; MRD risk matrix. |
| **Scope creep / unclear MVP** | High | Feature creep delays launch and obscures value | Lock P0 (F1–F4) per PRD; defer P1/P2 to later phases; MVP Scope Boundaries in SAD. |
| **LLM latency/cost** | Medium | Model calls drive latency and cost; context overflow possible | max_iter and time limits per adapter; token usage in Audit; optimize prompts; monitor usage (§7). |
| **User adoption and trust** | Medium | Agencies may resist tool change or doubt outputs | Beta with 2–5 teams; clear ROI narrative; phased rollout; human-in-the-loop for approvals (PRD §6). |
| **Calendar/brief format fragmentation** | Low | F7 (P1) integrations may face diverse formats | Define preferred formats in SAD when F7 is adopted; optional F7. |
| **Data and compliance** | Medium | User data handling must meet privacy (e.g. GDPR) and retention | Data Privacy & Compliance §8; retention and deletion policies; consent where required. |

**Traceability:** Risks align with MRD Risk Assessment Matrix and PRD §8 Risk Mitigation; ownership and review per org.

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
- [x] SAD completeness (stakeholders/concerns, views, quality attributes, decisions, constraints, risks) validated per [validation-sad-completeness.md](validation-sad-completeness.md) (ISO/IEC/IEEE 42010, Views and Beyond).

---

## Sources

- **Usecase.txt** — BAGANA AI use case (content strategy at scale; planning, sentiment, trends; multi-talent plans; efficiency without proportional manual workload).
- **project-context/1.define/prd.md** — Product requirements, agent definitions, P0–P2 features, NFRs, phases, success metrics.
- **project-context/1.define/mrd.md** — Market context, technical feasibility, user journey, production requirements, risk matrix.
- **.cursor/templates/sad-template.md** — AAMAD SAD structure and section headings.
- **.cursor/rules/adapter-crewai.mdc** — CrewAI adapter contract (agents, tasks, tools, logging, quality gates).

---

## Assumptions (for downstream resolution)

The following assumptions are recorded here and in the shared register [assumptions-and-open-questions.md](assumptions-and-open-questions.md). When resolved, update that register with artifact reference and date; SAD remains the architecture reference.

| ID | Assumption | Downstream owner |
|----|------------|------------------|
| A1 | Target users are agency/content strategists and campaign managers; market size and persona details are inferred (no deep research report). | Product / MRD update (optional) |
| A2 | CrewAI is the execution framework; agent list and tools are finalized in SAD and adapter config (config/agents.yaml, config/tasks.yaml). | SAD, adapter config ✓ (this document) |
| A3 | MVP can start with CLI or minimal UI; full web/mobile UX is P1/P2 (PRD §6, §8). | Frontend, SAD ✓ (this document) |
| A4 | Sentiment and trend data sources will be chosen in implementation with security and cost constraints; SAD defines integration pattern and rate-limit policy. | Backend / Integration |
| A5 | One primary crew (plan + sentiment + trends) is sufficient for MVP; optional reporting crew is P1 (PRD Assumptions). | SAD ✓ (this document) |
| A6 | MVP success criteria: core crew stable, P0 (F1–F4) complete, NFRs met; beta feedback will refine priorities. | QA, project plan |
| A7 | AAMAD_ADAPTER=crewai for this release; architecture aligns with CrewAI runtime semantics. | SAD ✓ (this document) |
| A8 | Org standards apply for cloud provider, auth, compliance, backup/DR; SAD references them where specific choices are deferred. | Ops, project plan |

---

## Open Questions (for downstream resolution)

The following open questions are recorded here and in [assumptions-and-open-questions.md](assumptions-and-open-questions.md). Resolve in the owning artifact and log resolution in that register.

| ID | Open question | Downstream owner |
|----|----------------|------------------|
| Q1 | Exact sentiment and trend APIs/sources and their rate limits and cost. | SAD (integration pattern), Backend/Integration, budgeting |
| Q2 | Preferred calendar/brief formats and systems for F7 (P1). | SAD (when F7 adopted), Integration |
| Q3 | Geographic and language scope for v1. | Product / SAD (i18n, data residency) |
| Q4 | Formal ROI model and baseline metrics for “efficiency” and “manual workload.” | Product / project plan, sales |
| Q5 | Timeline and milestones. | Project plan |
| Q6 | Specific health-check endpoints and SLO thresholds for API and crew runs. | SAD §5/§7, Ops |
| Q7 | NextAuth.js (or equivalent) provider and scopes when multi-user is required. | SAD §8, Frontend/Backend |

**Note:** When Q1 or Q2 are resolved, update the SAD sections on External Integration (§6) and Constraints as needed.

---

## Audit

| Timestamp   | Persona       | Action     | Adapter |
|------------|----------------|------------|---------|
| 2025-02-01 | @system.arch   | create-sad | crewai  |

SAD generated from prd.md, mrd.md, Usecase.txt, and .cursor/templates/sad-template.md. No code fences around machine-parsed sections.
