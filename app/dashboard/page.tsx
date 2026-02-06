import { PageLayout } from "@/components/PageLayout";
import { FeatureStub } from "@/components/FeatureStub";
import {
  IconChat,
  IconClipboard,
  IconChart,
  IconHeart,
  IconTrending,
  IconCalendar,
  IconCog,
  IconSparkles,
  IconGlobe,
} from "@/components/icons";

export default function DashboardPage() {
  return (
    <PageLayout currentPath="/dashboard">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-800 mb-2">
          Planned Features
        </h1>
        <p className="text-slate-600 mb-6 sm:mb-8 text-sm sm:text-base">
          Roadmap of BAGANA AI features. P0 = MVP, P1 = Enhanced, P2 = Future.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <FeatureStub
            title="Chat"
            description="Plan and optimize workflow with AI crew. Content planning, sentiment, and trend insights in one conversation."
            phase="P0"
            prdRef="F4"
            href="/chat"
            icon={IconChat}
          />
          <FeatureStub
            title="Content Plans"
            description="Multi-talent content plans, calendars, and briefs. Schema-valid, versioned, traceable to campaign."
            phase="P0"
            prdRef="F1"
            href="/plans"
            icon={IconClipboard}
          />
          <FeatureStub
            title="Sentiment Analysis"
            description="Analyze content and briefs for sentiment and tone. Surface risks and opportunities."
            phase="P0"
            prdRef="F2"
            href="/sentiment"
            icon={IconHeart}
          />
          <FeatureStub
            title="Trend Insights"
            description="Market and trend research for content strategy. Ingest and summarize insights."
            phase="P0"
            prdRef="F3"
            href="/trends"
            icon={IconTrending}
          />
          <FeatureStub
            title="Reports & Dashboards"
            description="Summaries and reports from plan + sentiment + trend outputs for stakeholders."
            phase="P1"
            prdRef="F6"
            href="/reports"
            icon={IconChart}
          />
          <FeatureStub
            title="Messaging Optimization"
            description="Suggestions to optimize messaging and engagement based on sentiment and trend data."
            phase="P1"
            prdRef="F5"
            href="/optimization"
            icon={IconSparkles}
          />
          <FeatureStub
            title="Calendars & Briefs"
            description="Optional integration with calendar/brief systems for import/export."
            phase="P1"
            prdRef="F7"
            href="/calendar"
            icon={IconCalendar}
          />
          <FeatureStub
            title="Advanced Analytics"
            description="Deeper performance and attribution analytics."
            phase="P2"
            prdRef="F8"
            icon={IconChart}
          />
          <FeatureStub
            title="Platforms & Regions"
            description="Additional social platforms, languages, and data sources."
            phase="P2"
            prdRef="F9"
            icon={IconGlobe}
          />
          <FeatureStub
            title="Custom Models & Rules"
            description="Configurable sentiment/trend rules and optional custom models."
            phase="P2"
            prdRef="F10"
            href="/settings"
            icon={IconCog}
          />
        </div>
      </div>
    </PageLayout>
  );
}
