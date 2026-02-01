"""
BAGANA AI — Stub code for future/backlog agent logic.
PRD P1/P2; SAD §2, §6. Per backend-eng *stub-nonmvp: no implementation, placeholders only.
Do not call real APIs or persist data.
"""

from __future__ import annotations

from typing import Any


# --- P1: report_summarizer agent (PRD §3, F6) ---

def build_report_summarizer_agent_stub() -> dict[str, Any]:
    """Stub: Return config for report_summarizer agent. P1. Wire in agents.yaml when implemented."""
    return {
        "role": "Report and summary producer",
        "goal": "Produce human-readable summaries and reports from plan + sentiment + trend outputs",
        "backstory": "Communicates clearly to agency stakeholders. 5+ years in agency reporting.",
        "llm": "openai",
        "allow_delegation": False,
        "verbose": False,
        "max_iter": 8,
        "max_execution_time": 60,
        "max_retry_limit": 2,
        "tools": [],  # report_template_renderer when implemented
    }


def build_report_summarize_task_stub() -> dict[str, Any]:
    """Stub: Return config for report_summarize task. P1. Context: plan + sentiment + trend outputs."""
    return {
        "name": "report_summarize",
        "agent": "report_summarizer",
        "description": "Produce human-readable report from plan, sentiment, and trend outputs.",
        "expected_output": "Report at project-context/2.build/artifacts/report.md",
        "output_file": "project-context/2.build/artifacts/report.md",
        "context_from": ["plan_content", "analyze_sentiment", "research_trends"],
    }


# --- P1: External API clients (PRD F2, F3; SAD §6) ---


class SentimentAPIClient:
    """Stub: Sentiment analysis API client. P1. Use SENTIMENT_API_KEY from env when implemented."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key
        self._base_url = base_url or "https://api.sentiment.example.com"

    def analyze(self, content: str, language: str = "en") -> dict[str, Any]:
        """Stub: Analyze content sentiment. Returns placeholder."""
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "risks": [],
            "opportunities": [],
            "_stub": True,
        }


class TrendAPIClient:
    """Stub: Trend/data source API client. P1. Use TREND_API_KEY from env when implemented."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = api_key
        self._base_url = base_url or "https://api.trends.example.com"

    def fetch_trends(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Stub: Fetch trend insights. Returns placeholder."""
        return [{"query": query, "trend": "placeholder", "_stub": True}]


# --- P1: Messaging optimization (PRD F5) ---


class MessagingOptimizer:
    """Stub: Suggest messaging optimizations from sentiment and trend data. P1."""

    def optimize(
        self,
        plan: dict[str, Any],
        sentiment: dict[str, Any],
        trends: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Stub: Return optimization suggestions. Placeholder only."""
        return [{"suggestion": "Implement in P1", "_stub": True}]


# --- P1: Reporting (PRD F6) ---


class ReportTemplateRenderer:
    """Stub: Render plan + sentiment + trends into report template. P1."""

    def render(
        self,
        plan: str,
        sentiment: str,
        trends: str,
        template_name: str = "default",
    ) -> str:
        """Stub: Return rendered report. Placeholder only."""
        return f"# Report (Stub)\n\nPlan: {len(plan)} chars. Sentiment: {len(sentiment)} chars. Trends: {len(trends)} chars."


# --- P1: Calendars and briefs (PRD F7) ---


class CalendarBriefLoader:
    """Stub: Load calendars and briefs from external systems. P1."""

    def import_calendar(self, source: str, format: str = "ical") -> dict[str, Any]:
        """Stub: Import calendar. Placeholder only."""
        return {"events": [], "source": source, "_stub": True}

    def export_brief(self, brief: dict[str, Any], format: str = "json") -> str:
        """Stub: Export brief. Placeholder only."""
        return '{"_stub": true}'


# --- P2: Advanced analytics (PRD F8) ---


class AnalyticsEngine:
    """Stub: Deeper performance and attribution analytics. P2."""

    def analyze_performance(
        self, campaign_id: str, metrics: list[str] | None = None
    ) -> dict[str, Any]:
        """Stub: Return performance analytics. Placeholder only."""
        return {"campaign_id": campaign_id, "_stub": True}


# --- P2: Custom models and rules (PRD F10) ---


class CustomRulesEvaluator:
    """Stub: Configurable sentiment/trend rules and optional custom models. P2."""

    def evaluate(self, content: str, rules: list[dict[str, Any]]) -> dict[str, Any]:
        """Stub: Evaluate content against custom rules. Placeholder only."""
        return {"matched_rules": [], "content_length": len(content), "_stub": True}
