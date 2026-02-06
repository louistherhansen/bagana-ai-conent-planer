import { PageLayout } from "@/components/PageLayout";
import { IconCog, IconSparkles } from "@/components/icons";
import Link from "next/link";

/**
 * Settings & Custom Rules (F10 — P2): Configurable sentiment and trend rules.
 * Optional custom models. Integrations and API keys.
 * PRD F10; SAD P2; frontend only — no backend wiring (P2 epic).
 */
export default function SettingsPage() {
  return (
    <PageLayout currentPath="/settings">
      <div className="flex flex-col flex-1 min-h-0 max-w-4xl mx-auto w-full px-4 sm:px-6 py-6">
        <header className="mb-6 shrink-0">
          <div className="flex items-center gap-3 mb-2">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-bagana-muted/50 text-bagana-primary">
              {IconCog}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">Settings & Custom Rules</h1>
              <p className="text-sm text-slate-500">F10 — P2</p>
            </div>
          </div>
          <p className="text-slate-600 text-sm sm:text-base">
            Configurable sentiment and trend rules. Optional custom models. Integrations and API keys.
          </p>
        </header>

        <section className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Subscription & Billing</h2>
            <p className="text-sm text-slate-600 mb-4">
              Manage your subscription, view billing history, and update payment methods.
            </p>
            <Link
              href="/subscription"
              className="inline-flex items-center gap-2 rounded-xl bg-bagana-primary px-5 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors"
            >
              {IconSparkles}
              View Plans & Pricing
            </Link>
          </div>

          <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
              {IconCog}
            </div>
            <h3 className="font-semibold text-slate-800 mb-1">Custom Rules & Models</h3>
            <p className="text-sm text-slate-600 mb-4 max-w-sm mx-auto">
              Configurable sentiment and trend rules, custom models, and API integrations. (P2 feature)
            </p>
            <span className="inline-block rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600">
              Coming in P2
            </span>
          </div>
        </section>
      </div>
    </PageLayout>
  );
}
