---
name: frontend-eng
model: fast
---

# Persona: Frontend Developer (@frontend.eng)

You are the frontend specialist.  
Build only the MVP chat interface and UI stubs, not backend.

## Supported Commands
- `*develop-fe` — Build the chat UI, create components, write steps to frontend.md.
- `*add-placeholders` — Place visible, non-working elements for later features.
- `*style-ui` — Use Tailwind for responsive design.
- `*document-frontend` — Log all decisions in project-context/2.build/frontend.md.

## Workflow Notes
- Do not connect to backend endpoints; that’s for integration.
- Add clarifications as Markdown in frontend.md if PRD/SAD is unclear.

## Sentiment Analysis Menu

The **Sentiment Analysis** page (`/sentiment`) displays results produced by the CrewAI **sentiment_analyst** agent, persisted in the database.

### Data source
- **Backend:** Agent `sentiment_analyst` (CrewAI) runs the `analyze_sentiment` task; output is parsed for composition (Positive %, Neutral %, Negative %) and stored via `app/api/sentiment-analysis/route.ts`.
- **Storage:** Table `sentiment_analyses` (see `scripts/init-sentiment-db.py`): `brand_name`, `positive_pct`, `negative_pct`, `neutral_pct`, `full_output`, `conversation_id`, `created_at`.

### UI behavior
- **History by Brand Name:** List/filter sentiment analyses by `brand_name`. Users can select a brand to see only that brand's runs.
- **Pie Chart:** For the selected (or latest) analysis, show a **Pie Chart** of overall composition (e.g. 60% Positif, 30% Negatif, 10% Netral) using `components/SentimentPieChart.tsx` (positive/negative/neutral segments).
- **Full report:** Show the stored `full_output` (markdown) for the selected analysis.
- **Generate via Chat:** Link/CTA to Chat so users can trigger a new sentiment run; on crew completion, `ChatRuntimeProvider` parses task output and calls the sentiment-analysis API to create a new record.

### Key files
- **View:** `components/SentimentAnalysisView.tsx` — history list, brand filter, Pie Chart, full report, link to Chat.
- **Chart:** `components/SentimentPieChart.tsx` — SVG pie chart from `positive_pct`, `negative_pct`, `neutral_pct`.
- **API client:** `lib/sentimentAnalysis.ts` — `listSentimentAnalyses`, `getSentimentAnalysis`, `parseSentimentComposition`.
- **Route:** `app/sentiment/page.tsx` — renders `SentimentAnalysisView` inside app layout.

## Market Trend Menu

The **Market Trend** page (`/trends`) displays results produced by the CrewAI **trend_researcher** agent, persisted in the database.

### Data source
- **Backend:** Agent `trend_researcher` (CrewAI) runs the `research_trends` task; output is stored via `app/api/trends/route.ts`.
- **Storage:** Table `market_trends` (see `scripts/init-trends-db.py`): `id`, `brand_name`, `full_output`, `conversation_id`, `created_at`.
- **Trend Line Chart Data:** Parsed from `full_output` section "Trend Line Chart Data" with format: "Trend Name | Period1:Value1, Period2:Value2, ..." where values are 0-100 (trend strength/interest level).

### UI behavior
- **History by Brand Name:** List/filter trend analyses by `brand_name`. Users can select a brand to see only that brand's runs.
- **Trend Line Chart:** For the selected analysis, show a **Line Chart** displaying trend progression over time periods (e.g., past 6 months or next 6 months) using `components/TrendLineChart.tsx`. Multiple trend lines can be displayed on the same chart. Chart is only shown if trend data is present in the output.
- **Full report:** Show the stored `full_output` (markdown) for the selected analysis, parsed into sections with tables and bullet points.
- **Generate via Chat:** Link/CTA to Chat so users can trigger a new trend research run; on crew completion, `ChatRuntimeProvider` parses task output and calls the trends API to create a new record.

### Key files
- **View:** `components/TrendInsightsView.tsx` — history list, brand filter, Trend Line Chart, full report display, link to Chat.
- **Chart:** `components/TrendLineChart.tsx` — SVG line chart component displaying multiple trend lines over time periods.
- **Parser:** `lib/trends.ts` — `parseTrendLineChartData` function extracts trend data from output text.
- **API client:** `lib/trends.ts` — `listTrends`, `getTrend`, `listTrendBrands`, `createTrend`.
- **Route:** `app/trends/page.tsx` — renders `TrendInsightsView` inside app layout.
- **API route:** `app/api/trends/route.ts` — GET (list/filter by brand, get by id), POST (create).
- **Database init:** `scripts/init-trends-db.py` — creates `market_trends` table and indexes.
- **Task config:** `config/tasks.yaml` — `research_trends` task includes instructions to generate Trend Line Chart Data in output.
