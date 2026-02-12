import { NextRequest, NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";
import { query } from "@/lib/db";

loadEnv({ path: path.resolve(process.cwd(), ".env") });

// Use Node.js runtime to support pg module
export const runtime = 'nodejs';

/**
 * Sentiment Analysis API (results from sentiment_analyst CrewAI agent)
 *
 * GET /api/sentiment-analysis - List all (optional ?brand_name= for filter)
 * GET /api/sentiment-analysis?id=<id> - Get one by id
 * POST /api/sentiment-analysis - Create (brandName, positivePct, negativePct, neutralPct, fullOutput, conversationId?)
 */

export interface SentimentAnalysisRecord {
  id: string;
  brandName: string;
  positivePct: number;
  negativePct: number;
  neutralPct: number;
  fullOutput: string;
  conversationId?: string;
  createdAt: number;
}

function generateId(): string {
  return `sent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

const SENTIMENT_TABLE_SQL = `
  CREATE TABLE IF NOT EXISTS sentiment_analyses (
    id VARCHAR(255) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    positive_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    negative_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    neutral_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    full_output TEXT,
    conversation_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_brand_name ON sentiment_analyses(brand_name);
  CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_created_at ON sentiment_analyses(created_at DESC);
  CREATE INDEX IF NOT EXISTS idx_sentiment_analyses_conversation_id ON sentiment_analyses(conversation_id);
`;

/** Ensure sentiment_analyses table exists (idempotent). */
async function ensureSentimentTable(): Promise<void> {
  const statements = SENTIMENT_TABLE_SQL.split(";").map((s) => s.trim()).filter(Boolean);
  for (const stmt of statements) {
    await query(stmt).catch(() => {});
  }
}

export async function GET(request: NextRequest) {
  try {
    await ensureSentimentTable();
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");
    const brandName = searchParams.get("brand_name");

    if (id) {
      const result = await query<{
        id: string;
        brand_name: string;
        positive_pct: number;
        negative_pct: number;
        neutral_pct: number;
        full_output: string | null;
        conversation_id: string | null;
        created_at: Date;
      }>(
        "SELECT id, brand_name, positive_pct, negative_pct, neutral_pct, full_output, conversation_id, created_at FROM sentiment_analyses WHERE id = $1",
        [id]
      );
      if (result.rows.length === 0) {
        return NextResponse.json({ error: "Sentiment analysis not found" }, { status: 404 });
      }
      const row = result.rows[0];
      const record: SentimentAnalysisRecord = {
        id: row.id,
        brandName: row.brand_name,
        positivePct: Number(row.positive_pct),
        negativePct: Number(row.negative_pct),
        neutralPct: Number(row.neutral_pct),
        fullOutput: row.full_output ?? "",
        conversationId: row.conversation_id ?? undefined,
        createdAt: row.created_at.getTime(),
      };
      return NextResponse.json(record);
    }

    // List: optional filter by brand_name
    let sql =
      "SELECT id, brand_name, positive_pct, negative_pct, neutral_pct, full_output, conversation_id, created_at FROM sentiment_analyses";
    const params: (string | number)[] = [];
    if (brandName && brandName.trim()) {
      sql += " WHERE brand_name = $1";
      params.push(brandName.trim());
    }
    sql += " ORDER BY created_at DESC";

    const result = await query<{
      id: string;
      brand_name: string;
      positive_pct: number;
      negative_pct: number;
      neutral_pct: number;
      full_output: string | null;
      conversation_id: string | null;
      created_at: Date;
    }>(sql, params.length ? params : undefined);

    const list: SentimentAnalysisRecord[] = result.rows.map((row) => ({
      id: row.id,
      brandName: row.brand_name,
      positivePct: Number(row.positive_pct),
      negativePct: Number(row.negative_pct),
      neutralPct: Number(row.neutral_pct),
      fullOutput: row.full_output ?? "",
      conversationId: row.conversation_id ?? undefined,
      createdAt: row.created_at.getTime(),
    }));

    return NextResponse.json(list);
  } catch (err) {
    console.error("Sentiment analysis GET error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to fetch sentiment analyses" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    await ensureSentimentTable();
    const body = await request.json().catch(() => ({}));
    const brandName = (body.brandName ?? body.brand_name ?? "").toString().trim();
    if (!brandName) {
      return NextResponse.json(
        { error: "brandName is required" },
        { status: 400 }
      );
    }

    const positivePct = Math.min(100, Math.max(0, Number(body.positivePct ?? body.positive_pct ?? 0)));
    const negativePct = Math.min(100, Math.max(0, Number(body.negativePct ?? body.negative_pct ?? 0)));
    const neutralPct = Math.min(100, Math.max(0, Number(body.neutralPct ?? body.neutral_pct ?? 0)));
    const fullOutput = (body.fullOutput ?? body.full_output ?? "").toString();
    const conversationId = (body.conversationId ?? body.conversation_id ?? null) as string | null;

    const id = generateId();

    await query(
      `INSERT INTO sentiment_analyses (id, brand_name, positive_pct, negative_pct, neutral_pct, full_output, conversation_id)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [id, brandName, positivePct, negativePct, neutralPct, fullOutput, conversationId ?? null]
    );

    const record: SentimentAnalysisRecord = {
      id,
      brandName,
      positivePct,
      negativePct,
      neutralPct,
      fullOutput,
      conversationId: conversationId ?? undefined,
      createdAt: Date.now(),
    };

    return NextResponse.json(record);
  } catch (err) {
    console.error("Sentiment analysis POST error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to save sentiment analysis" },
      { status: 500 }
    );
  }
}
