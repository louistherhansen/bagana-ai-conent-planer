import { NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";
import { query } from "@/lib/db";

loadEnv({ path: path.resolve(process.cwd(), ".env") });

// Use Node.js runtime to support pg module
export const runtime = 'nodejs';

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
`;

async function ensureSentimentTable(): Promise<void> {
  const statements = SENTIMENT_TABLE_SQL.split(";").map((s) => s.trim()).filter(Boolean);
  for (const stmt of statements) {
    await query(stmt).catch(() => {});
  }
}

/**
 * GET /api/sentiment-analysis/brands
 * Returns distinct brand_name for Filter by Brand dropdown.
 */
export async function GET() {
  try {
    await ensureSentimentTable();
    const result = await query<{ brand_name: string }>(
      "SELECT DISTINCT brand_name FROM sentiment_analyses ORDER BY brand_name"
    );
    const brands = result.rows.map((r) => r.brand_name).filter(Boolean);
    return NextResponse.json({ brands });
  } catch (err) {
    console.error("Sentiment analysis brands GET error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to fetch brands" },
      { status: 500 }
    );
  }
}
