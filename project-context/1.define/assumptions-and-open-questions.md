# BAGANA AI — Assumptions & Open Questions (Downstream Resolution)

**Document version:** 1.0  
**Purpose:** Single register of assumptions and open questions from Define-phase artifacts for downstream resolution by SAD, setup, build, and project planning.  
**Sources:** PRD (prd.md), MRD (mrd.md), validation-completeness.md  
**Persona:** @product-mgr (maintain); @system-arch, @project-mgr, build agents (resolve)

---

## How to Use This Artifact

- **Downstream owners:** When you resolve an item, check it off below and record where it was resolved (e.g., "Resolved in SAD §Integration" or "Resolved in setup.md").
- **Do not remove** assumptions or open questions; add a **Resolved** line with artifact reference and date.
- **New items:** Add assumptions or open questions discovered in Build/Deliver here with source artifact and assign downstream owner.

---

## Assumptions (Register)

| ID | Assumption | Source | Downstream owner | Resolved |
|----|------------|--------|------------------|----------|
| A1 | Target users are agency/content strategists and campaign managers; market size and persona details are inferred (no deep research report). | PRD, MRD | Product / MRD update (optional) | — |
| A2 | CrewAI is the execution framework; agent list and tools will be finalized in SAD and adapter config. | PRD, MRD | SAD, adapter config | — |
| A3 | MVP can start with CLI or minimal UI; full web/mobile UX is P1/P2. | PRD | Frontend, SAD | — |
| A4 | Sentiment and trend data sources will be chosen in SAD with security and cost constraints. | PRD, MRD | SAD, Backend/Integration | — |
| A5 | One primary crew (plan + sentiment + trends) is sufficient for MVP; optional reporting crew is P1. | PRD | SAD | — |
| A6 | MVP success criteria: core crew stable, P0 complete, NFRs met; beta feedback will refine priorities. | MRD | QA, project plan | — |

---

## Open Questions (Register)

| ID | Open question | Source | Downstream owner | Resolved |
|----|----------------|--------|------------------|----------|
| Q1 | Exact sentiment and trend APIs/sources and their rate limits and cost. | PRD, MRD | SAD, Backend/Integration, budgeting | — |
| Q2 | Preferred calendar/brief formats and systems for F7 (P1). | PRD, MRD | SAD, Integration | — |
| Q3 | Geographic and language scope for v1. | PRD, MRD | Product / SAD | — |
| Q4 | Formal ROI model and baseline metrics for “efficiency” and “manual workload.” | PRD, MRD | Product / project plan, sales | — |
| Q5 | Timeline and milestones. | MRD | Project plan | — |

---

## Resolution Log (Downstream)

When an item is resolved, add a row below. Keep the table above as the register; use this log for traceability.

| Date | Item (ID) | Resolved in | Note |
|------|-----------|-------------|------|
| — | — | — | — |

---

## Cross-Reference: Where to Resolve

| Downstream artifact / phase | Items to resolve |
|-----------------------------|-------------------|
| **SAD (sad.md)** | A2, A4, A5; Q1, Q2, Q3 (technical/scope) |
| **Setup (setup.md)** | Env, dependencies implied by A2, A4 |
| **Backend / Integration** | Q1 (APIs, rate limits, cost); Q2 (calendar/brief formats) |
| **Project plan** | Q4 (ROI, baselines); Q5 (timeline, milestones); A6 (success criteria) |
| **Product / MRD update** | A1 (primary research); Q3 (geo/language); Q4 (ROI) |

---

## Audit

| Timestamp   | Persona      | Action                          |
|------------|---------------|----------------------------------|
| 2025-02-01 | @product-mgr  | create assumptions-open-questions register |

Consolidated from prd.md and mrd.md for downstream resolution. No code fences around machine-parsed sections.
