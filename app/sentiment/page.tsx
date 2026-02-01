import { PageLayout } from "@/components/PageLayout";
import { IconHeart } from "@/components/icons";
import Link from "next/link";

export default function SentimentPage() {
  return (
    <PageLayout currentPath="/sentiment">
      <div className="flex flex-col items-center justify-center px-4 py-16 min-h-[60vh]">
        <div className="max-w-md text-center">
          <div className="mb-6 inline-flex items-center justify-center w-16 h-16 rounded-full bg-bagana-muted/50 text-bagana-primary">
            {IconHeart}
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            Sentiment Analysis
          </h2>
          <p className="text-slate-600 mb-6">
            Analyze content or briefs for sentiment and tone. Surface risks and
            opportunities. Configurable inputs; outputs usable by planning and
            reporting. (F2 — P0)
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
