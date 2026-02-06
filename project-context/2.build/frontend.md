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

- **assistant-ui** with `useLocalRuntime` and `ChatModelAdapter` wired to CrewAI API.
- **ChatRuntimeProvider:** Wraps chat page; provides runtime with initial welcome message. Handles conversation persistence to PostgreSQL via API.
- **ChatInterface:** Uses `ThreadPrimitive`, `ComposerPrimitive`, `MessagePrimitive`. Includes campaign template form.
- **ChatHistorySidebar:** Sidebar component for browsing and managing chat history from PostgreSQL database.
- **Backend wiring:** Chat adapter calls `/api/crew`; conversation history saved to `/api/chat-history` (PostgreSQL).

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
- **Chat History Sidebar:**
  - **Desktop (sm+):** Always visible, fixed width 320px (`w-80`), left side.
  - **Mobile:** Hidden by default; toggle button in header opens overlay sidebar with backdrop.
  - **Sidebar content:** Scrollable conversation list, "New Chat" button, delete actions on hover.

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
| ChatRuntimeProvider | components/ChatRuntimeProvider.tsx | Done | CrewAI adapter, auto-save to PostgreSQL |
| ChatInterface | components/ChatInterface.tsx | Done | assistant-ui Thread/Composer |
| ChatHistorySidebar | components/ChatHistorySidebar.tsx | Done | Conversation list, create/delete |
| ChatContent | components/ChatContent.tsx | Done | Orchestrates sidebar + interface |
| ReportsDashboardView | components/ReportsDashboardView.tsx | Enhanced (P1) | Reports dashboard with stats and filters |
| MessagingOptimizationView | components/MessagingOptimizationView.tsx | Enhanced (P1) | F5: Messaging optimization suggestions |
| CalendarBriefsView | components/CalendarBriefsView.tsx | Enhanced (P1) | F7: Calendar/brief integrations |
| ContentPlansView | components/ContentPlansView.tsx | Done | Content plans list with PostgreSQL |
| ReviewDashboardView | components/ReviewDashboardView.tsx | Done | Review and approval interface |
| icons | components/icons.tsx | Done | SVG icons for features |

---

## 6. Route and Page Status

| Route | Page | Status | PRD Ref |
|-------|------|--------|---------|
| / | Home | Done | — |
| /chat | Chat | Done (PostgreSQL history) | F4 |
| /dashboard | Features overview | Done | F1–F10 |
| /plans | Content Plans | Done (PostgreSQL) | F1 |
| /reports | Reports & Dashboards | Enhanced (P1) | F6 |
| /optimization | Messaging Optimization | Enhanced (P1) | F5 |
| /calendar | Calendar & Briefs | Enhanced (P1) | F7 |
| /sentiment | Sentiment Analysis | Stub | F2 |
| /trends | Trend Insights | Stub | F3 |
| /review | Review & Approval | Done | — |
| /settings | Custom Models & Rules | Stub | F10 |
| /api/crew | Crew API | Done (CrewAI integration) | — |
| /api/chat-history | Chat History API | Done (PostgreSQL) | — |
| /api/content-plans | Content Plans API | Done (PostgreSQL) | F1 |

---

## 7. Chat History with PostgreSQL

### 7.1 Architecture

- **Database:** PostgreSQL tables `conversations` and `messages` (schema via `scripts/init-chat-history-db.py`).
- **API:** `/api/chat-history` endpoints (GET, POST, PUT, DELETE) for CRUD operations.
- **Frontend Library:** `lib/chatHistory.ts` provides async functions with automatic fallback to localStorage if API unavailable.
- **Auto-save:** `ChatRuntimeProvider` includes `AutoSaveHandler` component that monitors messages via `useAuiState` and saves to database with 2-second debounce.
- **Conversation Loading:** When `conversationId` prop changes, `ChatRuntimeProvider` loads conversation from database and updates `initialMessages`.

### 7.2 UI Components

- **ChatHistorySidebar:** 
  - Displays list of conversations sorted by `updatedAt` (most recent first).
  - Shows conversation title, relative timestamp (e.g., "2h ago", "Just now").
  - "New Chat" button creates new conversation.
  - Delete button (trash icon) appears on hover; confirms before deletion.
  - Active conversation highlighted with primary color border.
  - Responsive: always visible on desktop, overlay on mobile.

- **ChatContent:**
  - Manages sidebar open/close state (mobile only).
  - Tracks current conversation ID in state and localStorage.
  - Passes `conversationId` and `onConversationChange` to `ChatRuntimeProvider`.

### 7.3 User Flow

1. User opens `/chat` → `ChatContent` loads current conversation ID from localStorage (if any).
2. User sends first message → `AutoSaveHandler` detects real messages, creates conversation if none exists, saves to database.
3. User clicks conversation in sidebar → `ChatContent` updates `conversationId`, `ChatRuntimeProvider` loads messages from database.
4. User sends more messages → Auto-saved every 2 seconds after last change.
5. User clicks "New Chat" → Creates new conversation, clears current messages, shows welcome message.

### 7.4 Data Flow

```
User Action → ChatInterface → assistant-ui runtime → AutoSaveHandler → 
lib/chatHistory.ts → /api/chat-history → lib/db.ts → PostgreSQL
```

Fallback path (if API fails):
```
lib/chatHistory.ts → localStorage (synchronous)
```

## 8. Enhanced Features P1 (F5-F7)

### 8.1 F5 — Messaging Optimization

**Route:** `/optimization`  
**Component:** `MessagingOptimizationView`  
**Status:** UI complete; backend integration deferred to P1 epic

**Features:**
- Summary stats dashboard (total suggestions, high priority, sentiment-based, trend-based)
- Filterable suggestions list by type (sentiment, trend, engagement) and priority
- Expandable suggestion cards with:
  - Current vs. suggested messaging comparison
  - Rationale based on sentiment/trend analysis
  - Expected impact metrics
  - Links to related plans, sentiment, and trend insights
- "Apply Suggestion" button (disabled, requires backend)
- "Generate Suggestions" button (disabled, requires backend)
- Link to Chat for optimization via conversation

**UI Design:**
- Color-coded suggestion types: sentiment (red), trend (blue), engagement (purple)
- Priority badges: high (red), medium (amber), low (slate)
- Responsive grid layout for stats cards
- Empty state with CTAs

### 8.2 F6 — Reports & Dashboards (Enhanced)

**Route:** `/reports`  
**Component:** `ReportsDashboardView` (enhanced)  
**Status:** UI enhanced; backend integration deferred to P1 epic

**Enhancements:**
- Summary stats dashboard (total reports, this month, with plans, with sentiment, with trends)
- Chart placeholder for report trends visualization
- Enhanced filters (campaign, date range)
- Report cards with plan, sentiment, and trend summaries
- Export functionality (disabled, requires backend)
- Generate report button (disabled, requires backend)

**UI Design:**
- 5-column stats grid (responsive: 1 col mobile, 2 col tablet, 5 col desktop)
- Chart placeholder with icon and description
- Filter section with dropdowns
- Report cards with color-coded sections (plan: slate, sentiment: red, trend: blue)

### 8.3 F7 — Calendar & Briefs Integration

**Route:** `/calendar`  
**Component:** `CalendarBriefsView`  
**Status:** UI complete; backend integration deferred to P1 epic

**Features:**

**Calendar Integrations:**
- Integration cards for Google Calendar, Outlook, iCal feeds
- Connection status badges (connected, disconnected, error)
- "Connect Calendar" button (disabled, requires OAuth backend)
- Sync status and event counts display
- Disconnect functionality (disabled, requires backend)

**Brief Export Formats:**
- Format cards: PDF, DOCX, Markdown, JSON
- Format descriptions and support status
- "Export Sample" button (disabled, requires backend)
- Link to Plans page for export

**Brief Import:**
- Upload brief file section
- File upload button (disabled, requires backend)
- Support for various brief formats

**UI Design:**
- 2-column grid for calendar integrations and brief formats
- Status badges with icons
- Empty states with CTAs
- Responsive layout

---

## 9. Deferred Work

| Item | Owner | Notes |
|------|-------|-------|
| ~~Backend wiring~~ | ~~Integration epic~~ | ✅ Done: CrewAI API wired |
| ~~assistant-ui → API~~ | ~~Integration epic~~ | ✅ Done: Chat adapter calls /api/crew |
| F5 backend integration | Integration epic | Messaging optimization agent, sentiment/trend analysis |
| F6 backend integration | Integration epic | Report summarizer agent, report template renderer |
| F7 backend integration | Integration epic | Calendar sync APIs (OAuth), brief import/export parsers |
| Conversation search/filter | Future | Add search bar in sidebar |
| Conversation export | Future | Export to JSON/Markdown |
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
├─ ChatRuntimeProvider.tsx  # CrewAI adapter, auto-save
├─ ChatInterface.tsx   # assistant-ui integration
├─ ChatHistorySidebar.tsx  # Conversation list sidebar
├─ ChatContent.tsx     # Chat page orchestrator
└─ icons.tsx           # SVG icon set

lib/
├─ chatHistory.ts      # PostgreSQL chat history API client
└─ db.ts               # PostgreSQL connection pool utility
```

---

## 9. Clarifications and Assumptions

- **Backend connection:** Chat interface wired to CrewAI API (`/api/crew`). Chat history persisted to PostgreSQL via `/api/chat-history`.
- **assistant-ui LocalRuntime:** Used with custom `ChatModelAdapter` that calls CrewAI API. Runtime manages message state; auto-save handler persists to database.
- **Mobile-first:** Breakpoints and touch targets designed for mobile; desktop inherits.
- **No auth:** Out of scope for MVP; SAD §8 defers to org policy. All conversations stored without user association (future: add user_id column).
- **Conversation persistence:** Auto-save debounced to 2 seconds to avoid excessive API calls. Falls back to localStorage if PostgreSQL unavailable.

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
| 2025-02-04 | @frontend.eng  | Chat history UI with PostgreSQL |
| 2025-02-04 | @frontend.eng  | Enhanced Features P1 (F5-F7) UI |

Frontend artifact created. Responsive styling applied. Chat history sidebar integrated with PostgreSQL database. Auto-save functionality implemented. Enhanced Features P1 (F5-F7) UI components created: Messaging Optimization (F5), Reports & Dashboards enhancement (F6), Calendar & Briefs Integration (F7). All P1 features have complete UI with mock data; backend integration deferred to P1 epic. Navigation updated to include new routes. No code fences around machine-parsed sections.
