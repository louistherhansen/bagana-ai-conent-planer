import { NextRequest, NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";
import { query } from "@/lib/db";

loadEnv({ path: path.resolve(process.cwd(), ".env") });

// Use Node.js runtime to support pg module
export const runtime = 'nodejs';

/**
 * Market Trends API (results from trend_researcher CrewAI agent)
 *
 * GET /api/trends - List all (optional ?brand_name= for filter)
 * GET /api/trends?id=<id> - Get one by id
 * POST /api/trends - Create (brandName, fullOutput, conversationId?)
 */

export interface TrendRecord {
  id: string;
  brandName: string;
  fullOutput: string;
  conversationId?: string;
  createdAt: number;
}

function generateId(): string {
  return `trend_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

const TRENDS_TABLE_SQL = `
  CREATE TABLE IF NOT EXISTS market_trends (
    id VARCHAR(255) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255),
    key_market_trends JSONB,
    summary_bar_chart_data JSONB,
    trend_line_chart_data JSONB,
    creator_economy_insights TEXT,
    competitive_landscape TEXT,
    content_format_trends TEXT,
    timing_seasonality TEXT,
    implications_strategy TEXT,
    recommendations TEXT,
    sources TEXT,
    audit TEXT,
    full_output TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX IF NOT EXISTS idx_market_trends_brand_name ON market_trends(brand_name);
  CREATE INDEX IF NOT EXISTS idx_market_trends_created_at ON market_trends(created_at DESC);
  CREATE INDEX IF NOT EXISTS idx_market_trends_conversation_id ON market_trends(conversation_id);
  CREATE INDEX IF NOT EXISTS idx_market_trends_summary_bar ON market_trends USING GIN (summary_bar_chart_data);
  CREATE INDEX IF NOT EXISTS idx_market_trends_trend_lines ON market_trends USING GIN (trend_line_chart_data);
`;

/** Ensure market_trends table exists (idempotent). */
async function ensureTrendsTable(): Promise<void> {
  const statements = TRENDS_TABLE_SQL.split(";").map((s) => s.trim()).filter(Boolean);
  for (const stmt of statements) {
    await query(stmt).catch(() => {});
  }
}

/**
 * Parse CrewAI output into structured data
 */
function parseTrendOutput(fullOutput: string): {
  keyMarketTrends: any[] | null;
  summaryBarChartData: any[] | null;
  trendLineChartData: any[] | null;
  creatorEconomyInsights: string | null;
  competitiveLandscape: string | null;
  contentFormatTrends: string | null;
  timingSeasonality: string | null;
  implicationsStrategy: string | null;
  recommendations: string | null;
  sources: string | null;
  audit: string | null;
} {
  const text = fullOutput || "";
  
  // Parse Key Market Trends
  const keyTrendsMatch = text.match(/##?\s*Key\s+Market\s+Trends[\s\S]*?(?=##|$)/i);
  const keyMarketTrends: any[] = [];
  if (keyTrendsMatch) {
    const section = keyTrendsMatch[0];
    const lines = section.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      // Match format: "1. **Trend Name**: Description"
      const match = trimmed.match(/^\d+\.\s+\*\*(.+?)\*\*:\s*(.+)$/);
      if (match) {
        keyMarketTrends.push({ name: match[1].trim(), description: match[2].trim() });
      }
    }
  }
  
  // Parse Summary Bar Chart Data
  const summaryBars: any[] = [];
  const summaryMatch = text.match(/##?\s*Summary\s+Bar\s+Chart\s+Data[\s\S]*?(?=##|$)/i);
  if (summaryMatch) {
    const section = summaryMatch[0];
    const lines = section.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const match = trimmed.match(/^(.+?)\s*\|\s*(\d+(?:\.\d+)?)$/);
      if (match) {
        summaryBars.push({ 
          name: match[1].trim(), 
          value: Math.min(100, Math.max(0, parseFloat(match[2]) || 0)) 
        });
      }
    }
  }
  
  // Parse Trend Line Chart Data
  const trendLines: any[] = [];
  const trendLineMatch = text.match(/##?\s*Trend\s+Line\s+Chart\s+Data[\s\S]*?(?=##|$)/i);
  if (trendLineMatch) {
    const section = trendLineMatch[0];
    const lines = section.split(/\r?\n/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const match = trimmed.match(/^(.+?)\s*\|\s*(.+)$/);
      if (match) {
        const trendName = match[1].trim();
        const dataStr = match[2].trim();
        const dataPoints: any[] = [];
        const pairs = dataStr.split(",");
        for (const pair of pairs) {
          const pairMatch = pair.trim().match(/^(.+?):\s*(\d+(?:\.\d+)?)$/);
          if (pairMatch) {
            dataPoints.push({
              period: pairMatch[1].trim(),
              value: Math.min(100, Math.max(0, parseFloat(pairMatch[2]) || 0))
            });
          }
        }
        if (dataPoints.length > 0) {
          trendLines.push({ name: trendName, data: dataPoints });
        }
      }
    }
  }
  
  // Parse text sections
  const extractSection = (sectionName: string): string | null => {
    // Try multiple patterns to match section headers
    const patterns = [
      new RegExp(`##?\\s*${sectionName.replace(/\s+/g, "\\s+")}[\\s\\S]*?(?=##|$)`, "i"),
      new RegExp(`##?\\s*${sectionName.replace(/\s+/g, "[\\s-]+")}[\\s\\S]*?(?=##|$)`, "i"),
      new RegExp(`#\\s+${sectionName.replace(/\s+/g, "\\s+")}[\\s\\S]*?(?=#|$)`, "i"),
    ];
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        const section = match[0];
        // Remove header line(s) and return content
        const content = section.replace(/^##?\s*[^\n]+\n?/i, "").trim();
        return content || null;
      }
    }
    return null;
  };
  
  return {
    keyMarketTrends: keyMarketTrends.length > 0 ? keyMarketTrends : null,
    summaryBarChartData: summaryBars.length > 0 ? summaryBars : null,
    trendLineChartData: trendLines.length > 0 ? trendLines : null,
    creatorEconomyInsights: extractSection("Creator Economy Insights"),
    competitiveLandscape: extractSection("Competitive Landscape"),
    contentFormatTrends: extractSection("Content Format Trends"),
    timingSeasonality: extractSection("Timing and Seasonality"),
    implicationsStrategy: extractSection("Implications for Strategy"),
    recommendations: extractSection("Recommendations"),
    sources: extractSection("Sources"),
    audit: extractSection("Audit"),
  };
}

export async function GET(request: NextRequest) {
  try {
    await ensureTrendsTable();
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");
    const brandName = searchParams.get("brand_name");

    if (id) {
      const result = await query<{
        id: string;
        brand_name: string;
        full_output: string | null;
        conversation_id: string | null;
        created_at: Date;
      }>(
        "SELECT id, brand_name, full_output, conversation_id, created_at FROM market_trends WHERE id = $1",
        [id]
      );
      if (result.rows.length === 0) {
        return NextResponse.json({ error: "Trend analysis not found" }, { status: 404 });
      }
      const row = result.rows[0];
      const record: TrendRecord = {
        id: row.id,
        brandName: row.brand_name,
        fullOutput: row.full_output ?? "",
        conversationId: row.conversation_id ?? undefined,
        createdAt: row.created_at.getTime(),
      };
      return NextResponse.json(record);
    }

    // List: optional filter by brand_name
    let sql =
      "SELECT id, brand_name, full_output, conversation_id, created_at FROM market_trends";
    const params: (string | number)[] = [];
    if (brandName && brandName.trim()) {
      sql += " WHERE brand_name = $1";
      params.push(brandName.trim());
    }
    sql += " ORDER BY created_at DESC";

    const result = await query<{
      id: string;
      brand_name: string;
      full_output: string | null;
      conversation_id: string | null;
      created_at: Date;
    }>(sql, params.length ? params : undefined);

    const list: TrendRecord[] = result.rows.map((row) => ({
      id: row.id,
      brandName: row.brand_name,
      fullOutput: row.full_output ?? "",
      conversationId: row.conversation_id ?? undefined,
      createdAt: row.created_at.getTime(),
    }));

    return NextResponse.json(list);
  } catch (err) {
    console.error("Trends GET error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to fetch trends" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    await ensureTrendsTable();
    const body = await request.json().catch(() => ({}));
    const brandName = (body.brandName ?? body.brand_name ?? "").toString().trim();
    if (!brandName) {
      return NextResponse.json(
        { error: "brandName is required" },
        { status: 400 }
      );
    }

    const fullOutput = (body.fullOutput ?? body.full_output ?? "").toString();
    const conversationId = (body.conversationId ?? body.conversation_id ?? null) as string | null;

    // Parse fullOutput into structured data
    const parsed = parseTrendOutput(fullOutput);

    const id = generateId();

    await query(
      `INSERT INTO market_trends (
        id, brand_name, conversation_id,
        key_market_trends, summary_bar_chart_data, trend_line_chart_data,
        creator_economy_insights, competitive_landscape, content_format_trends,
        timing_seasonality, implications_strategy, recommendations,
        sources, audit, full_output
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
      )`,
      [
        id,
        brandName,
        conversationId ?? null,
        parsed.keyMarketTrends ? JSON.stringify(parsed.keyMarketTrends) : null,
        parsed.summaryBarChartData ? JSON.stringify(parsed.summaryBarChartData) : null,
        parsed.trendLineChartData ? JSON.stringify(parsed.trendLineChartData) : null,
        parsed.creatorEconomyInsights,
        parsed.competitiveLandscape,
        parsed.contentFormatTrends,
        parsed.timingSeasonality,
        parsed.implicationsStrategy,
        parsed.recommendations,
        parsed.sources,
        parsed.audit,
        fullOutput,
      ]
    );

    const record: TrendRecord = {
      id,
      brandName,
      fullOutput,
      conversationId: conversationId ?? undefined,
      createdAt: Date.now(),
    };

    return NextResponse.json(record);
  } catch (err) {
    console.error("Trends POST error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to save trend analysis" },
      { status: 500 }
    );
  }
}
