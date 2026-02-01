import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";

/**
 * Chat API endpoint for CrewAI crew.
 * SAD §4: Next.js API routes call Python CrewAI service layer.
 * POST body: { message?: string, user_input?: string, campaign_context?: string }
 * Response: { status, output?, task_outputs?, error? }
 */

const CREW_TIMEOUT_MS = 120_000; // 2 min for full crew run

async function runCrew(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const projectRoot = process.cwd();
  const pythonCmd = process.platform === "win32" ? "python" : "python3";

  return new Promise((resolve, reject) => {
    const proc = spawn(pythonCmd, ["-m", "crew.run", "--stdin"], {
      cwd: projectRoot,
      env: { ...process.env, PYTHONUNBUFFERED: "1" },
      stdio: ["pipe", "pipe", "pipe"],
    });

    const chunks: Buffer[] = [];
    let stderr = "";

    proc.stdout?.on("data", (chunk: Buffer) => chunks.push(chunk));
    proc.stderr?.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    proc.on("error", (err) => {
      reject(new Error(`Failed to start crew: ${err.message}`));
    });

    proc.on("close", (code, signal) => {
      const stdout = Buffer.concat(chunks).toString("utf-8").trim();
      if (code !== 0 && !stdout) {
        reject(new Error(`Crew exited ${code ?? signal}: ${stderr || "No output"}`));
        return;
      }
      try {
        const result = JSON.parse(stdout || "{}") as Record<string, unknown>;
        resolve(result);
      } catch {
        reject(new Error(`Invalid crew output: ${stdout.slice(0, 200)}`));
      }
    });

    const timeout = setTimeout(() => {
      proc.kill("SIGTERM");
      reject(new Error(`Crew timed out after ${CREW_TIMEOUT_MS / 1000}s`));
    }, CREW_TIMEOUT_MS);

    proc.on("close", () => clearTimeout(timeout));

    const input = JSON.stringify(payload);
    proc.stdin?.write(input, "utf-8", (err) => {
      if (err) reject(err);
      else proc.stdin?.end();
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const message =
      (body.message as string) ??
      (body.user_input as string) ??
      (body.campaign_context as string) ??
      "";
    const payload = {
      user_input: message || "No message provided.",
      message: body.message,
      campaign_context: body.campaign_context,
    };

    const result = await runCrew(payload);

    if ((result.status as string) === "error") {
      return NextResponse.json(
        { error: result.error ?? "Crew execution failed", status: "error" },
        { status: 500 }
      );
    }

    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { error: message, status: "error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: "ok",
    message: "CrewAI chat API. POST with { message: string } to run the content planning crew.",
  });
}
