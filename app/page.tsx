import Link from "next/link";
import { PageLayout } from "@/components/PageLayout";
import { FeatureStub } from "@/components/FeatureStub";
import { IconChat, IconClipboard, IconHeart, IconTrending } from "@/components/icons";

export default function HomePage() {
  return (
    <PageLayout currentPath="/">
      <div className="flex flex-col items-center px-4 sm:px-6 py-12 sm:py-16">
        <div className="max-w-2xl text-center mb-10 sm:mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-4">
            Content Strategy at Scale
          </h2>
          <p className="text-slate-600 mb-8 leading-relaxed text-base sm:text-lg">
            BAGANA AI helps KOL, influencer, and content creator agencies manage
            content strategy through integrated planning, sentiment analysis, and
            market trend insights.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-lg bg-bagana-primary px-6 py-3 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors touch-target min-h-[44px] items-center justify-center"
          >
            Open Chat
            <span aria-hidden>→</span>
          </Link>
        </div>

        <div className="w-full max-w-4xl">
          <h3 className="text-base sm:text-lg font-semibold text-slate-700 mb-4">Key features</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
            <FeatureStub
              title="Chat"
              description="AI-powered planning workflow"
              phase="P0"
              href="/chat"
              icon={IconChat}
            />
            <FeatureStub
              title="Plans"
              description="Multi-talent content plans"
              phase="P0"
              href="/plans"
              icon={IconClipboard}
            />
            <FeatureStub
              title="Sentiment"
              description="Tone and sentiment analysis"
              phase="P0"
              href="/sentiment"
              icon={IconHeart}
            />
            <FeatureStub
              title="Trends"
              description="Market trend insights"
              phase="P0"
              href="/trends"
              icon={IconTrending}
            />
          </div>
          <div className="mt-6 text-center">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-bagana-primary hover:text-bagana-accent"
            >
              View full roadmap →
            </Link>
          </div>
        </div>
      </div>
      <footer className="border-t border-slate-200 py-4 text-center text-sm text-slate-500 mt-auto">
        BAGANA AI — MVP • Backend integration in Development
      </footer>
    </PageLayout>
  );
}
