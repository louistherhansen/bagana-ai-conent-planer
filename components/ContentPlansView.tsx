"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { IconClipboard, IconCalendar, IconDocument, IconCheck } from "@/components/icons";
import { getAllPlans, type ContentPlanSummary } from "@/lib/contentPlans";

/** Plan card item - matches ContentPlanSummary from API */
type PlanCard = ContentPlanSummary & {
  updatedAtFormatted: string;
};

function PlanCardRow({ plan }: { plan: PlanCard }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-slate-800 truncate">{plan.title}</h3>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm">
            {plan.campaign && (
              <span className="rounded-md bg-slate-100 px-2 py-0.5 text-slate-600" title="Campaign">
                {plan.campaign}
              </span>
            )}
            {plan.brandName && (
              <span className="rounded-md bg-blue-100 px-2 py-0.5 text-blue-700" title="Brand">
                {plan.brandName}
              </span>
            )}
            {plan.talents.slice(0, 3).map((t) => (
              <span
                key={t}
                className="rounded-md bg-bagana-muted/60 px-2 py-0.5 text-bagana-dark"
                title="Talent"
              >
                {t}
              </span>
            ))}
            {plan.talents.length > 3 && (
              <span className="rounded-md bg-slate-100 px-2 py-0.5 text-slate-600">
                +{plan.talents.length - 3} more
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
            {plan.version}
          </span>
          {plan.schemaValid ? (
            <span className="inline-flex items-center gap-1 rounded-md bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800">
              {IconCheck}
              Schema valid
            </span>
          ) : (
            <span className="rounded-md bg-amber-100 px-2 py-1 text-xs font-medium text-amber-800">
              Schema invalid
            </span>
          )}
        </div>
      </div>
      <p className="mt-2 text-xs text-slate-400">Updated {plan.updatedAtFormatted}</p>
    </div>
  );
}

function PlansSection() {
  const [plans, setPlans] = useState<PlanCard[]>([]);
  const [loading, setLoading] = useState(true);

  const loadPlans = useCallback(async () => {
    try {
      setLoading(true);
      const fetchedPlans = await getAllPlans();
      
      // Format plans with formatted date
      const formattedPlans: PlanCard[] = fetchedPlans.map((plan) => ({
        ...plan,
        updatedAtFormatted: formatDate(plan.updatedAt),
      }));
      
      setPlans(formattedPlans);
    } catch (error) {
      console.error("Error loading plans:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPlans();
  }, [loadPlans]);

  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <p className="text-sm text-slate-600">
          Multi-talent content plans. Schema-valid, versioned, traceable to campaign/talent (F1).
        </p>
        <Link
          href="/chat"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-bagana-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors shrink-0"
        >
          {IconClipboard}
          Create plan via Chat
        </Link>
      </div>
      {loading ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
            {IconClipboard}
          </div>
          <p className="text-sm text-slate-600">Loading content plans...</p>
        </div>
      ) : plans.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
            {IconClipboard}
          </div>
          <h3 className="font-semibold text-slate-800 mb-1">No content plans yet</h3>
          <p className="text-sm text-slate-600 mb-4 max-w-sm mx-auto">
            Generate a plan from Chat: describe your campaign and talents, then the crew will produce a structured plan.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-bagana-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary"
          >
            Go to Chat
          </Link>
        </div>
      ) : (
        <ul className="space-y-3">
          {plans.map((plan) => (
            <li key={plan.id}>
              <PlanCardRow plan={plan} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CalendarStub() {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
        {IconCalendar}
      </div>
      <h3 className="font-semibold text-slate-800 mb-1">Calendar view</h3>
      <p className="text-sm text-slate-600 max-w-sm mx-auto">
        Content calendar by week/month — linked to plans and briefs. (Placeholder; integration epic.)
      </p>
    </div>
  );
}

function BriefsStub() {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
        {IconDocument}
      </div>
      <h3 className="font-semibold text-slate-800 mb-1">Briefs</h3>
      <p className="text-sm text-slate-600 max-w-sm mx-auto">
        Campaign and talent briefs — traceable to plans. (Placeholder; integration epic.)
      </p>
    </div>
  );
}

const TABS = [
  { id: "plans", label: "Plans", content: <PlansSection /> },
  { id: "calendar", label: "Calendar", content: <CalendarStub /> },
  { id: "briefs", label: "Briefs", content: <BriefsStub /> },
] as const;

export function ContentPlansView() {
  const [activeTab, setActiveTab] = useState<"plans" | "calendar" | "briefs">("plans");

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-slate-200 bg-white/80">
        <nav className="flex gap-1 px-1" aria-label="Content plans sections">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? "bg-white text-bagana-primary border border-b-0 border-slate-200 -mb-px"
                  : "text-slate-600 hover:text-slate-800 hover:bg-slate-50"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      <div className="flex-1 overflow-auto bg-slate-50/50 p-4 sm:p-6">
        {TABS.find((t) => t.id === activeTab)?.content}
      </div>
    </div>
  );
}
