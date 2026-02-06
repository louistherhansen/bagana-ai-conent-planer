"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { IconHeart, IconCheck, IconDocument } from "@/components/icons";
import { SentimentPieChart } from "@/components/SentimentPieChart";
import {
  listSentimentAnalyses,
  listSentimentBrands,
  removeHeadingSymbols,
  type SentimentAnalysisRecord,
} from "@/lib/sentimentAnalysis";

/** Parsed section: numbered header + rows (label: content). */
type FullReportSection = {
  number: number;
  header: string;
  rows: { label: string; content: string }[];
  rawLines: string[];
  bulletPoints: string[];
};

/**
 * Parse Full Report: #, ##, or "1. " as section headers, "- Key: value" as table rows.
 * Returns sections for table display.
 */
function parseFullReportToSections(text: string): FullReportSection[] {
  if (!text || typeof text !== "string") return [];
  
  // Remove ### heading symbols first (using lib function)
  let out = removeHeadingSymbols(text);
  out = out.replace(/\*\*/g, "");
  
  // Convert # (single) and ## (double) to "1. ", "2. ", ...
  let n = 1;
  // First handle ## (level 2 headings)
  out = out.replace(/^##\s+(.+)$/gm, (_, content) => {
    const line = `${n}. ${content.trim()}`;
    n += 1;
    return line;
  });
  // Then handle # (level 1 headings) - only if not already converted
  out = out.replace(/^#\s+(.+)$/gm, (match, content) => {
    // Check if this line was already processed (starts with number)
    if (/^\d+\.\s+/.test(match)) return match;
    const line = `${n}. ${content.trim()}`;
    n += 1;
    return line;
  });
  
  // Split by numbered lines (1. Header, 2. Next, ...)
  const numberedLineRe = /^(\d+)\.\s+(.+)$/gm;
  const sections: FullReportSection[] = [];
  let num = 0;
  let header = "";
  let lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = numberedLineRe.exec(out)) !== null) {
    if (num > 0) {
      const body = out.slice(lastIndex, m.index).trim();
      const { rows, rawLines, bulletPoints } = parseSectionBody(body);
      sections.push({ number: num, header, rows, rawLines, bulletPoints });
    }
    num = parseInt(m[1], 10);
    header = m[2].trim();
    lastIndex = numberedLineRe.lastIndex;
  }
  if (num > 0) {
    const body = out.slice(lastIndex).trim();
    const { rows, rawLines, bulletPoints } = parseSectionBody(body);
    sections.push({ number: num, header, rows, rawLines, bulletPoints });
  }
  return sections;
}

/** Parse section body into rows (Label: content) and raw lines. Split only on first ": ". */
function parseSectionBody(body: string): {
  rows: { label: string; content: string }[];
  rawLines: string[];
  bulletPoints: string[];
} {
  const rows: { label: string; content: string }[] = [];
  const rawLines: string[] = [];
  const bulletPoints: string[] = [];
  const lines = body.split(/\r?\n/);
  
  for (const line of lines) {
    let trimmed = line.trim();
    if (!trimmed) continue;
    
    // Remove ### symbols from line
    trimmed = trimmed.replace(/^###\s*/g, "");
    
    // Check if it's a bullet point
    if (/^[-*]\s+/.test(trimmed)) {
      const bullet = trimmed.replace(/^[-*]\s+/, "");
      const colonIdx = bullet.indexOf(": ");
      
      // If it has ":", treat as key-value pair
      if (colonIdx > 0 && colonIdx < bullet.length - 2) {
        const label = bullet.slice(0, colonIdx).trim();
        const content = bullet.slice(colonIdx + 2).trim();
        // Only add as row if label is not too long (likely a proper key-value)
        if (label.length < 100) {
          rows.push({ label, content });
        } else {
          // If label too long, treat as bullet point
          bulletPoints.push(bullet);
        }
      } else {
        // No colon or colon at end, treat as bullet point
        bulletPoints.push(bullet);
      }
    } else {
      // Not a bullet point, add as raw line
      rawLines.push(trimmed);
    }
  }
  
  return { rows, rawLines, bulletPoints };
}

/** Platform + risk level for Brand Safety section (e.g. "YouTube (Medium)"). */
export type BrandSafetyItem = { platform: string; level: "Low" | "Medium" | "High" };

const BRAND_SAFETY_LEVELS: ("Low" | "Medium" | "High")[] = ["Low", "Medium", "High"];

/** Extract "Platform (Low|Medium|High)" from section text. */
function parseBrandSafetyData(sec: FullReportSection): BrandSafetyItem[] {
  const text = [
    ...sec.rows.map((r) => `${r.label}: ${r.content}`),
    ...sec.rawLines,
  ].join("\n");
  const re = /([A-Za-z0-9_]+)\s*\(\s*(Low|Medium|High)\s*\)/gi;
  const seen = new Set<string>();
  const items: BrandSafetyItem[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    const platform = m[1].trim();
    const level = m[2].charAt(0).toUpperCase() + m[2].slice(1).toLowerCase() as "Low" | "Medium" | "High";
    if (level !== "Low" && level !== "Medium" && level !== "High") continue;
    const key = `${platform}-${level}`;
    if (seen.has(key)) continue;
    seen.add(key);
    items.push({ platform, level });
  }
  return items;
}

/** Diverging Stacked Bar Chart: one row per platform, segments Low | Medium | High; filled segment by level. */
function DivergingStackedBarChart({ data }: { data: BrandSafetyItem[] }) {
  if (data.length === 0) return null;
  const barHeight = 28;
  const barWidth = 180;
  const segmentWidth = barWidth / 3;
  const colors = { Low: "rgb(34, 197, 94)", Medium: "rgb(234, 179, 8)", High: "rgb(239, 68, 68)" };
  const labelWidth = 88;

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-4">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-600">Risk level by platform</span>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-4 rounded bg-emerald-500" /> Low
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-4 rounded bg-amber-500" /> Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-4 rounded bg-red-500" /> High
          </span>
        </div>
      </div>
      <div className="space-y-2">
        {data.map(({ platform, level }, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-[88px] shrink-0 text-xs font-medium text-slate-700">{platform}</div>
            <div
              className="flex h-7 shrink-0 overflow-hidden rounded border border-slate-200 bg-white"
              style={{ width: barWidth }}
            >
              {BRAND_SAFETY_LEVELS.map((l) => (
                <div
                  key={l}
                  className="h-full border-r border-slate-200 last:border-r-0"
                  style={{
                    width: segmentWidth,
                    backgroundColor: l === level ? colors[l] : "rgb(241, 245, 249)",
                  }}
                  title={`${platform}: ${level}`}
                />
              ))}
            </div>
            <span className="text-xs text-slate-600">{level}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/** Default Brand Safety data when section 2 is "Brand Safety Concerns" and no items parsed. */
const DEFAULT_BRAND_SAFETY: BrandSafetyItem[] = [
  { platform: "YouTube", level: "Medium" },
  { platform: "Instagram", level: "Low" },
  { platform: "TikTok", level: "Medium" },
  { platform: "X", level: "High" },
  { platform: "LinkedIn", level: "Low" },
];

/** Full Report as attractive table(s): section headers + rows; section 2 Brand Safety gets Diverging Stacked Bar Chart. */
function FullReportTable({ text }: { text: string }) {
  const sections = parseFullReportToSections(text);
  if (sections.length === 0) {
    // Remove ### symbols and ** bold markers from fallback display
    let fallback = removeHeadingSymbols(text);
    fallback = fallback.replace(/\*\*/g, "").trim();
    return (
      <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans bg-slate-50 p-4 rounded-lg border border-slate-200">
        {fallback || "—"}
      </pre>
    );
  }

  // Determine section type for special styling
  const getSectionType = (header: string): "sentiment" | "recommendations" | "risks" | "sources" | "default" => {
    const lower = header.toLowerCase();
    if (/sentiment|positive|negative|neutral/i.test(lower)) return "sentiment";
    if (/recommendation|suggestion|action|mitigation/i.test(lower)) return "recommendations";
    if (/risk|safety|concern|warning/i.test(lower)) return "risks";
    if (/source|reference/i.test(lower)) return "sources";
    return "default";
  };

  return (
    <div className="space-y-5">
      {sections.map((sec) => {
        const sectionType = getSectionType(sec.header);
        const isBrandSafety =
          sec.number === 2 && /brand\s*safety/i.test(sec.header);
        const isMitigationActions = /recommended\s*mitigation\s*actions/i.test(sec.header);
        const parsed = parseBrandSafetyData(sec);
        const brandSafetyData =
          parsed.length > 0 ? parsed : isBrandSafety ? DEFAULT_BRAND_SAFETY : [];
        
        // Use bulletPoints from parsed section, or extract from rawLines as fallback
        const bulletPoints = sec.bulletPoints.length > 0 
          ? sec.bulletPoints 
          : isMitigationActions
            ? sec.rawLines
                .map((line) => {
                  const trimmed = line.trim();
                  if (/^[-*]\s+/.test(trimmed)) {
                    return trimmed.replace(/^[-*]\s+/, "").trim();
                  }
                  return null;
                })
                .filter((point): point is string => Boolean(point))
            : [];

        // Section header colors based on type
        const headerColors = {
          sentiment: "bg-blue-50 border-blue-200 text-blue-900",
          recommendations: "bg-emerald-50 border-emerald-200 text-emerald-900",
          risks: "bg-red-50 border-red-200 text-red-900",
          sources: "bg-slate-50 border-slate-200 text-slate-700",
          default: "bg-gradient-to-r from-slate-50 to-slate-100 border-slate-200 text-slate-800",
        };

        return (
          <div
            key={sec.number}
            className="overflow-hidden rounded-xl border-2 bg-white shadow-md hover:shadow-lg transition-shadow"
          >
            {/* Enhanced Section Header */}
            <div className={`border-b-2 px-5 py-3.5 ${headerColors[sectionType]}`}>
              <div className="flex items-center gap-2.5">
                <span className="flex items-center justify-center w-7 h-7 rounded-full bg-white/80 text-xs font-bold text-slate-700 shadow-sm">
                  {sec.number}
                </span>
                <h5 className="text-base font-bold">
                  {sec.header}
                </h5>
              </div>
            </div>

            {/* Content Area */}
            <div className="overflow-x-auto bg-white">
              {isBrandSafety && brandSafetyData.length > 0 ? (
                <div className="p-4">
                  <DivergingStackedBarChart data={brandSafetyData} />
                </div>
              ) : (bulletPoints.length > 0 || sec.rows.length > 0) ? (
                <div className="p-0">
                  <table className="w-full text-sm border-collapse">
                    <thead>
                      <tr className="bg-slate-100 border-b-2 border-slate-300">
                        <th className="w-64 min-w-[200px] px-5 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                          Item
                        </th>
                        <th className="px-5 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">
                          Description
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* Render bullet points as table rows */}
                      {bulletPoints.map((point, i) => {
                        const colonIdx = point.indexOf(": ");
                        const hasKeyValue = colonIdx > 0 && colonIdx < point.length - 2;
                        
                        if (hasKeyValue) {
                          const label = point.slice(0, colonIdx).trim();
                          const content = point.slice(colonIdx + 2).trim();
                          return (
                            <tr
                              key={`bullet-${i}`}
                              className={`border-b border-slate-200 last:border-0 transition-all hover:bg-blue-50/50 ${
                                i % 2 === 0 ? "bg-white" : "bg-slate-50/30"
                              }`}
                            >
                              <td className="w-64 min-w-[200px] px-5 py-4 align-top">
                                <div className="flex items-start gap-2.5">
                                  <span
                                    className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                                      sectionType === "recommendations"
                                        ? "bg-emerald-500"
                                        : sectionType === "risks"
                                        ? "bg-red-500"
                                        : sectionType === "sentiment"
                                        ? "bg-blue-500"
                                        : "bg-bagana-primary"
                                    }`}
                                  />
                                  <span className="font-bold text-slate-900 text-sm leading-tight">
                                    {label.replace(/^###\s*/g, "").trim()}
                                  </span>
                                </div>
                              </td>
                              <td className="px-5 py-4 align-top">
                                <span className="text-sm text-slate-700 leading-relaxed">
                                  {content.replace(/^###\s*/g, "").trim()}
                                </span>
                              </td>
                            </tr>
                          );
                        } else {
                          // Regular bullet point - span full width
                          return (
                            <tr
                              key={`bullet-${i}`}
                              className={`border-b border-slate-200 last:border-0 transition-all hover:bg-blue-50/50 ${
                                i % 2 === 0 ? "bg-white" : "bg-slate-50/30"
                              }`}
                            >
                              <td colSpan={2} className="px-5 py-4">
                                <div className="flex items-start gap-3">
                                  <span
                                    className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                                      sectionType === "recommendations"
                                        ? "bg-emerald-500"
                                        : sectionType === "risks"
                                        ? "bg-red-500"
                                        : sectionType === "sentiment"
                                        ? "bg-blue-500"
                                        : "bg-bagana-primary"
                                    }`}
                                  />
                                  <span className="flex-1 leading-relaxed text-sm text-slate-700 font-medium">
                                    {point.replace(/^###\s*/g, "").trim()}
                                  </span>
                                </div>
                              </td>
                            </tr>
                          );
                        }
                      })}
                      
                      {/* Render regular rows */}
                      {sec.rows.map((row, i) => {
                        // Clean ### symbols from label and content
                        const cleanLabel = row.label.replace(/^###\s*/g, "").trim();
                        const cleanContent = row.content.replace(/^###\s*/g, "").trim();
                        return (
                          <tr
                            key={`row-${i}`}
                            className={`border-b border-slate-200 last:border-0 transition-all hover:bg-blue-50/50 ${
                              (bulletPoints.length + i) % 2 === 0 ? "bg-white" : "bg-slate-50/30"
                            }`}
                          >
                            <td className="w-64 min-w-[200px] px-5 py-4 align-top">
                              <div className="flex items-start gap-2.5">
                                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-bagana-primary" />
                                <span className="font-bold text-slate-900 text-sm leading-tight">
                                  {cleanLabel}
                                </span>
                              </div>
                            </td>
                            <td className="px-5 py-4 align-top">
                              <span className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                                {cleanContent}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      
                      {/* Render raw lines */}
                      {sec.rawLines.map((raw, i) => {
                        // Clean ### symbols from raw lines
                        const cleanRaw = raw.replace(/^###\s*/g, "").trim();
                        return (
                          <tr
                            key={`raw-${i}`}
                            className={`border-b border-slate-200 last:border-0 transition-all hover:bg-blue-50/50 ${
                              (bulletPoints.length + sec.rows.length + i) % 2 === 0 ? "bg-white" : "bg-slate-50/30"
                            }`}
                          >
                            <td colSpan={2} className="px-5 py-4">
                              <span className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                                {cleanRaw}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-5 text-center">
                  <p className="text-sm text-slate-400 italic">—</p>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function SentimentAnalysisView() {
  const [history, setHistory] = useState<SentimentAnalysisRecord[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [selected, setSelected] = useState<SentimentAnalysisRecord | null>(null);
  const [filterBrand, setFilterBrand] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [brandsLoading, setBrandsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadBrands = useCallback(async () => {
    setBrandsLoading(true);
    try {
      const list = await listSentimentBrands();
      setBrands(list);
    } catch (e) {
      console.error("Failed to load brands:", e);
      setBrands([]);
    } finally {
      setBrandsLoading(false);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await listSentimentAnalyses(filterBrand.trim() || undefined);
      setHistory(list);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Gagal memuat history";
      setError(msg);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }, [filterBrand]);

  useEffect(() => {
    loadBrands();
  }, [loadBrands]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleRefresh = useCallback(() => {
    setError(null);
    loadBrands();
    loadHistory();
  }, [loadBrands, loadHistory]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-end gap-3">
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleRefresh}
            disabled={loading || brandsLoading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Refresh
          </button>
          <Link
            href="/chat"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-bagana-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors"
          >
            {IconHeart}
            Generate via Chat
          </Link>
        </div>
      </div>

      {/* History by Brand Name */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
        <h3 className="font-semibold text-slate-800 mb-4">History Sentiment Analysis (by Brand Name)</h3>
        <div className="mb-4">
          <label htmlFor="filter-brand" className="block text-sm font-medium text-slate-700 mb-1">
            Filter by Brand
          </label>
          <select
            id="filter-brand"
            value={filterBrand}
            onChange={(e) => setFilterBrand(e.target.value)}
            disabled={brandsLoading}
            className="w-full max-w-xs rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white focus:border-bagana-primary focus:outline-none focus:ring-1 focus:ring-bagana-primary/20 disabled:opacity-60"
          >
            <option value="">All brands</option>
            {brands.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
          {brands.length === 0 && !brandsLoading && !error && (
            <p className="mt-1 text-xs text-slate-500">Belum ada data. Jalankan crew di Chat lalu klik Refresh.</p>
          )}
        </div>
        {loading && (
          <div className="py-8 text-center text-slate-500 text-sm">Loading history…</div>
        )}
        {error && (
          <div className="py-4 rounded-lg bg-red-50 text-red-700 text-sm px-4">
            {error}
            <p className="mt-2 text-xs">Pastikan database berjalan dan tabel sentiment_analyses ada (script: scripts/init-sentiment-db.py).</p>
          </div>
        )}
        {!loading && !error && history.length === 0 && (
          <div className="py-8 text-center text-slate-500 text-sm">
            Belum ada hasil sentiment. Generate dari Chat (crew akan menyimpan otomatis).
          </div>
        )}
        {!loading && !error && history.length > 0 && (
          <ul className="space-y-2">
            {history.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => setSelected(selected?.id === item.id ? null : item)}
                  className={`w-full text-left rounded-lg border px-4 py-3 transition-colors ${
                    selected?.id === item.id
                      ? "border-bagana-primary bg-bagana-primary/5"
                      : "border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium text-slate-800">{item.brandName}</span>
                    <span className="text-xs text-slate-500">
                      {new Date(item.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-1 flex gap-4 text-xs text-slate-600">
                    <span className="text-emerald-600">Positive {item.positivePct}%</span>
                    <span className="text-slate-500">Neutral {item.neutralPct}%</span>
                    <span className="text-red-600">Negative {item.negativePct}%</span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Selected: Pie Chart + full output */}
      {selected && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Sentiment Composition — {selected.brandName}</h3>
            <button
              type="button"
              onClick={() => setSelected(null)}
              className="text-sm text-slate-500 hover:text-slate-700"
            >
              Tutup
            </button>
          </div>
          <div className="flex justify-center">
            <SentimentPieChart
              positivePct={selected.positivePct}
              neutralPct={selected.neutralPct}
              negativePct={selected.negativePct}
              size={220}
            />
          </div>
          <div className="border-t border-slate-200 pt-4">
            <h4 className="text-sm font-medium text-slate-700 mb-2">Full Report (sentiment_analyst)</h4>
            <div className="max-h-[28rem] overflow-y-auto">
              <FullReportTable text={selected.fullOutput || ""} />
            </div>
          </div>
        </div>
      )}

      {!selected && history.length === 0 && !loading && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50/50 p-8 sm:p-12 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-bagana-muted/50 text-bagana-primary mb-4">
            {IconHeart}
          </div>
          <h3 className="font-semibold text-slate-800 mb-1">Belum ada analisis</h3>
          <p className="text-sm text-slate-600 mb-4 max-w-sm mx-auto">
            Hasil dari agent sentiment_analyst (CrewAI) akan tersimpan otomatis setelah Anda menjalankan crew dari Chat. Buka Chat, kirim brief kampanye, lalu kembali ke halaman ini untuk melihat history dan Pie Chart.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-bagana-primary px-4 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors"
          >
            {IconHeart}
            Buka Chat
          </Link>
        </div>
      )}
    </div>
  );
}
