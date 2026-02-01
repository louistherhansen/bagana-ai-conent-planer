import { PageLayout } from "@/components/PageLayout";
import { IconCog } from "@/components/icons";
import Link from "next/link";

export default function SettingsPage() {
  return (
    <PageLayout currentPath="/settings">
      <div className="flex flex-col items-center justify-center px-4 py-16 min-h-[60vh]">
        <div className="max-w-md text-center">
          <div className="mb-6 inline-flex items-center justify-center w-16 h-16 rounded-full bg-bagana-muted/50 text-bagana-primary">
            {IconCog}
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">
            Settings & Custom Rules
          </h2>
          <p className="text-slate-600 mb-6">
            Configurable sentiment and trend rules. Optional custom models.
            Integrations and API keys. (F10 — P2)
          </p>
          <span className="inline-block rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-600 mb-6">
            Placeholder — Future
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
