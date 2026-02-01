# BAGANA AI — Frontend Artifact

**Document version:** 1.0  
**Persona:** @frontend.eng  
**Invocation:** *develop-fe, *add-placeholders, *style-ui  
**Sources:** PRD (prd.md), MRD (mrd.md), SAD (sad.md), Usecase.txt, setup.md  
**Output:** project-context/2.build/frontend.md (this file)

---

## Context

This document records all frontend development decisions, component status, responsive design choices, and deferred work. The frontend implements the MVP chat interface and UI stubs per SAD §3; no backend integration is wired (Integration epic).

**Use case (anchor):**  
BAGANA AI is an AI-powered platform designed for KOL, influencer, and content creator agencies to manage content strategy at scale through integrated content planning, sentiment analysis, and market trend insights.

---

## 1. Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.0 | App Router, RSC, API routes |
| React | 18.3.x | UI framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.4.x | Utility-first styling |
| assistant-ui | 0.12.x | Chat interface (Thread, Composer, Message primitives) |

**Rationale:** Aligns with SAD §3 (Next.js 14+ App Router, assistant-ui, Tailwind). No shadcn/ui added; custom components suffice for MVP.

---

## 2. Architecture Decisions

### 2.1 Layout and Navigation

- **PageLayout:** Shared layout with header and nav; used by all pages.
- **AppNav:** Client component with responsive behavior:
  - **lg+:** Horizontal nav with flex-wrap.
  - **&lt;lg:** Hamburger menu opening slide-out sheet from right; overlay dismisses.
- **Rationale:** 8 nav items overflow on mobile; hamburger keeps header clean.

### 2.2 Chat Interface

- **assistant-ui** with `useLocalRuntime` and mock `ChatModelAdapter`.
- **ChatRuntimeProvider:** Wraps chat page; provides runtime with initial welcome message.
- **ChatInterface:** Uses `ThreadPrimitive`, `ComposerPrimitive`, `MessagePrimitive`.
- **No backend wiring:** Mock adapter returns placeholder response. Integration epic wires API.

### 2.3 Feature Stubs

- **FeatureStub:** Reusable card (icon, title, description, phase badge, optional link).
- **Phase badges:** P0 (emerald), P1 (amber), P2 (slate).
- **Dashboard:** Central hub listing all PRD features F1–F10 with PRD refs.

---

## 3. Responsive Design Decisions

### 3.1 Breakpoints (Tailwind)

| Breakpoint | Width | Usage |
|------------|-------|-------|
| (default) | &lt;640px | Mobile: stacked composer, hamburger nav |
| sm | ≥640px | Increased padding, 2-col feature grid |
| md | ≥768px | Dashboard 2-col grid |
| lg | ≥1024px | Desktop nav visible, dashboard 3-col, composer inline |
| xl | ≥1280px | Wider nav gaps |

### 3.2 Touch Targets

- **Minimum 44×44px** for interactive elements (WCAG 2.5.5).
- Applied to: nav links, hamburger, Send button, primary CTA.
- Utility: `.touch-target` in globals.css.

### 3.3 Safe Area

- CSS vars `--safe-area-inset-top`, `--safe-area-inset-bottom` for notched devices.
- `safe-area-padding` on body.
- Viewport meta: `width=device-width`, `initial-scale=1`, `maximumScale=5`, `themeColor`.

### 3.4 Typography

- Headings: `text-xl sm:text-2xl`, `text-2xl sm:text-3xl` for fluid scaling.
- Body: `text-sm`, `text-base sm:text-lg` where appropriate.
- `line-clamp-3` on FeatureStub descriptions to cap height.

### 3.5 Chat Responsiveness

- **Viewport padding:** `px-3 sm:px-4`, `py-4 sm:py-6`.
- **Message width:** `max-w-[85%]` on mobile, `sm:max-w-[75%]` on larger screens.
- **Composer:** Stacks vertically on mobile (`flex-col sm:flex-row`); inline on sm+.
- **Input:** `min-h-[44px]` for touch; Send uses `touch-target`.

---

## 4. Styling Decisions

### 4.1 Color Palette (BAGANA)

| Token | Hex | Usage |
|-------|-----|-------|
| bagana-primary | #0f766e | Primary actions, active nav |
| bagana-secondary | #0d9488 | Hover states |
| bagana-accent | #14b8a6 | Highlights |
| bagana-muted | #99f6e4 | Icon backgrounds, subtle fills |
| bagana-dark | #134e4a | Logo, headings |

Defined in `tailwind.config.js` and `globals.css` (`:root`).

### 4.2 Components

- **FeatureStub:** `rounded-xl`, `border-slate-200`, `shadow-sm`, `hover:shadow-md`.
- **Messages:** User = `bg-bagana-primary`; Assistant = `border`, `bg-white`, `shadow-sm`.
- **Phase badges:** P0 emerald, P1 amber, P2 slate.
- **Focus:** `focus:ring-2 focus:ring-bagana-primary/20` on inputs and buttons.

---

## 5. Component Inventory

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| PageLayout | components/PageLayout.tsx | Done | Shared header + main |
| AppNav | components/AppNav.tsx | Done | Responsive, hamburger on mobile |
| FeatureStub | components/FeatureStub.tsx | Done | Phase-aware cards |
| ChatRuntimeProvider | components/ChatRuntimeProvider.tsx | Done | Mock adapter, initial message |
| ChatInterface | components/ChatInterface.tsx | Done | assistant-ui Thread/Composer |
| icons | components/icons.tsx | Done | SVG icons for features |

---

## 6. Route and Page Status

| Route | Page | Status | PRD Ref |
|-------|------|--------|---------|
| / | Home | Done | — |
| /chat | Chat | Done (stub backend) | F4 |
| /dashboard | Features overview | Done | F1–F10 |
| /plans | Content Plans | Stub | F1 |
| /reports | Reports & Dashboards | Stub | F6 |
| /sentiment | Sentiment Analysis | Stub | F2 |
| /trends | Trend Insights | Stub | F3 |
| /settings | Custom Models & Rules | Stub | F10 |
| /api/crew | Crew API | Stub (empty) | — |

---

## 7. Deferred Work

| Item | Owner | Notes |
|------|-------|-------|
| Backend wiring | Integration epic | Wire /api/crew to CrewAI; streaming |
| assistant-ui → API | Integration epic | Replace mock adapter with useChat/API |
| shadcn/ui | Optional | SAD mentions it; not required for MVP |
| WCAG audit | QA epic | Basic focus/touch in place; full audit TBD |
| E2E tests | QA epic | Playwright or equivalent |

---

## 8. File Structure

```
app/
├─ layout.tsx          # Root layout, viewport, metadata
├─ page.tsx            # Home (hero + feature grid)
├─ globals.css         # Tailwind, CSS vars, safe-area, touch-target
├─ chat/page.tsx       # Chat (ChatRuntimeProvider + ChatInterface)
├─ dashboard/page.tsx  # Features roadmap
├─ plans/page.tsx      # F1 stub
├─ reports/page.tsx    # F6 stub
├─ sentiment/page.tsx  # F2 stub
├─ trends/page.tsx     # F3 stub
├─ settings/page.tsx   # F10 stub
└─ api/crew/route.ts   # Stub (Integration epic)

components/
├─ AppNav.tsx          # Responsive nav (hamburger)
├─ PageLayout.tsx      # Shared layout
├─ FeatureStub.tsx     # Feature card
├─ ChatRuntimeProvider.tsx
├─ ChatInterface.tsx   # assistant-ui integration
└─ icons.tsx           # SVG icon set
```

---

## 9. Clarifications and Assumptions

- **No backend connection:** All stub pages and chat use mock/placeholder data. Integration epic wires CrewAI.
- **assistant-ui LocalRuntime:** Chosen for mock/no-backend MVP; swap to AI SDK or custom runtime when API ready.
- **Mobile-first:** Breakpoints and touch targets designed for mobile; desktop inherits.
- **No auth:** Out of scope for MVP; SAD §8 defers to org policy.

---

## Sources

- **project-context/1.define/prd.md** — F1–F10, UX requirements (§6).
- **project-context/1.define/sad.md** — Frontend spec (§3), Next.js, assistant-ui, Tailwind.
- **project-context/1.define/mrd.md** — UX and workflow context.
- **Usecase.txt** — Product anchor.
- **project-context/2.build/setup.md** — Setup skeleton, deferred frontend.
- **.cursor/agents/frontend-eng.md** — Persona, actions, prohibited actions.

---

## Audit

| Timestamp   | Persona       | Action            |
|------------|----------------|-------------------|
| 2025-02-01 | @frontend.eng  | *develop-fe       |
| 2025-02-01 | @frontend.eng  | *add-placeholders |
| 2025-02-01 | @frontend.eng  | *style-ui         |
| 2025-02-01 | @frontend.eng  | *document-frontend|

Frontend artifact created. Responsive styling applied. No code fences around machine-parsed sections.
