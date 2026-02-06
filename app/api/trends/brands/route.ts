import { NextRequest, NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";
import { query } from "@/lib/db";

loadEnv({ path: path.resolve(process.cwd(), ".env") });

const TRENDS_TABLE_SQL = `
  CREATE TABLE IF NOT EXISTS market_trends (
    id VARCHAR(255) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    full_output TEXT,
    conversation_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX IF NOT EXISTS idx_market_trends_brand_name ON market_trends(brand_name);
`;

async function ensureTrendsTable(): Promise<void> {
  const statements = TRENDS_TABLE_SQL.split(";").map((s) => s.trim()).filter(Boolean);
  for (const stmt of statements) {
    await query(stmt).catch(() => {});
  }
}

/** GET /api/trends/brands — distinct brand names for Filter by Brand dropdown. */
export async function GET(request: NextRequest) {
  try {
    await ensureTrendsTable();
    const result = await query<{ brand_name: string }>(
      "SELECT DISTINCT brand_name FROM market_trends ORDER BY brand_name"
    );
    const brands = result.rows.map((row) => row.brand_name);
    return NextResponse.json({ brands });
  } catch (err) {
    console.error("Trends brands GET error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to fetch trend brands" },
      { status: 500 }
    );
  }
}
