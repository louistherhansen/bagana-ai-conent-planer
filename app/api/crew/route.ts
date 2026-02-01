import { NextRequest, NextResponse } from "next/server";

/**
 * API route stub for CrewAI proxy.
 * SAD §4: Next.js API routes call Python CrewAI service layer.
 *
 * Integration epic will wire this to:
 * - CrewAI layer (crew.kickoff)
 * - Streaming support
 * - Request/response validation (Zod)
 *
 * No backend connection in Frontend epic per agent rules.
 */
export async function POST(request: NextRequest) {
  return NextResponse.json(
    {
      error: "Not implemented",
      message:
        "CrewAI backend integration pending. Integration epic will wire this route to the Python crew layer.",
    },
    { status: 501 }
  );
}

export async function GET() {
  return NextResponse.json(
    {
      status: "stub",
      message: "CrewAI API route. Use POST with campaign/brief payload when Integration epic wires backend.",
    },
    { status: 200 }
  );
}
