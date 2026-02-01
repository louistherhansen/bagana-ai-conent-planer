import { PageLayout } from "@/components/PageLayout";
import { IconTrending } from "@/components/icons";
import Link from "next/link";

export default function TrendsPage() {
  return (
    <PageLayout currentPath="/trends">
      <div className="flex flex-col items-center justify-center px-4 py-16 min-h-[60vh]">
        <div className="max-w-md text-center">
          <div className="mb-6 inline-flex items-center justify-center w-16 h-16 rounded-full bg-bagana-muted/50 text-bagana-primary">
            {IconTrending}
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            Market Trend Insights
          </h2>
          <p className="text-slate-600 mb-6">
            Ingest and summarize relevant trend and market insights for content
            strategy. Defined sources and rate limits; outputs linked to plans or
            briefs. (F3 — P0)
          </p>
          <span className="inline-block rounded-lg bg-amber-100 px-4 py-2 text-sm font-medium text-amber-800 mb-6">
            Placeholder — Backend epic
          </span>
          <Link
            href="/dashboard"
            className="text-sm font-medium text-bagana-primary hover:text-bagana-accent"
          >
            View all features →
          </Link>
        </div>
      </div>
    </PageLayout>
  );
}
