import { PageLayout } from "@/components/PageLayout";
import { IconChart } from "@/components/icons";

export default function AiChartsPage() {
  return (
    <PageLayout currentPath="/ai-charts">
      <div className="flex flex-col flex-1 min-h-0 max-w-4xl mx-auto w-full px-4 sm:px-6 py-6">
        <header className="mb-6 shrink-0">
          <div className="flex items-center gap-3 mb-2">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-bagana-muted/50 text-bagana-primary">
              {IconChart}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">
                AI Chart Services
              </h1>
              <p className="text-sm text-slate-500">AI-powered insight visuals</p>
            </div>
          </div>
          <p className="text-slate-600 text-sm sm:text-base">
            Explore BAGANA AI&apos;s chart-based insight products that turn sentiment
            and trend research into clear, stakeholder-ready visuals.
          </p>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <article className="rounded-xl border border-slate-200 bg-white shadow-sm p-4 sm:p-5 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-1">
              Sentiment Composition Pie Charts
            </h2>
            <p className="text-xs text-slate-500 mb-3">
              Powered by Sentiment Analysis (F2)
            </p>
            <p className="text-sm text-slate-600 mb-3">
              Visualize the balance of Positive, Neutral, and Negative sentiment for
              each content plan or campaign. Ideal for stakeholder updates,
              approvals, and risk reviews.
            </p>
            <ul className="mt-auto space-y-1 text-sm text-slate-600 list-disc list-inside">
              <li>Automatic % breakdown from sentiment reports</li>
              <li>Side‑by‑side comparison across brands or campaigns</li>
              <li>Ready to embed in decks and executive summaries</li>
            </ul>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white shadow-sm p-4 sm:p-5 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-1">
              Market Trend Line Charts
            </h2>
            <p className="text-xs text-slate-500 mb-3">
              Powered by Trend Insights (F3)
            </p>
            <p className="text-sm text-slate-600 mb-3">
              Track how key creator and audience trends evolve over time with
              multi-line charts extracted from research outputs.
            </p>
            <ul className="mt-auto space-y-1 text-sm text-slate-600 list-disc list-inside">
              <li>Time‑series view of trend strength (0–100)</li>
              <li>Compare multiple trends on a single chart</li>
              <li>Highlight inflection points and seasonality</li>
            </ul>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white shadow-sm p-4 sm:p-5 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-1">
              Summary Bar Charts
            </h2>
            <p className="text-xs text-slate-500 mb-3">
              Powered by Trend &amp; Performance Summaries
            </p>
            <p className="text-sm text-slate-600 mb-3">
              Turn ranked trend or performance metrics into clear bar charts that
              make prioritization obvious for marketing and content teams.
            </p>
            <ul className="mt-auto space-y-1 text-sm text-slate-600 list-disc list-inside">
              <li>Ranked views of top trends and opportunities</li>
              <li>Consistent 0–100 scoring for easy comparison</li>
              <li>Configurable slices for brands, platforms, or segments</li>
            </ul>
          </article>

          <article className="rounded-xl border border-slate-200 bg-white shadow-sm p-4 sm:p-5 flex flex-col">
            <h2 className="text-lg font-semibold text-slate-800 mb-1">
              Custom AI Chart Products
            </h2>
            <p className="text-xs text-slate-500 mb-3">
              Tailored to your data, markets, and workflows
            </p>
            <p className="text-sm text-slate-600 mb-3">
              Collaborate with BAGANA AI to design bespoke chart experiences built
              on your first‑party data, from channel performance to creator
              benchmarking.
            </p>
            <ul className="mt-auto space-y-1 text-sm text-slate-600 list-disc list-inside">
              <li>Custom schemas and chart types (funnel, cohort, more)</li>
              <li>White‑label visual layers for agencies and partners</li>
              <li>Roadmap for future predictive and simulation views</li>
            </ul>
          </article>
        </section>
      </div>
    </PageLayout>
  );
}

