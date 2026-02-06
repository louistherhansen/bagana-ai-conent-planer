import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { config as loadEnv } from "dotenv";

// Pastikan .env terbaca (path relatif ke project root = folder package.json / next.config)
loadEnv({ path: path.resolve(process.cwd(), ".env") });

/**
 * Chat API endpoint for CrewAI crew.
 * SAD §4: Next.js API routes call Python CrewAI service layer.
 * POST body: { message?: string, user_input?: string, campaign_context?: string, language?: string }
 * Response: { status, output?, task_outputs?, error? }
 */

const CREW_TIMEOUT_MS = 300_000; // 5 menit untuk 5 agent
const CREW_CLOUD_POLL_MS = 3_000;
const CREW_CLOUD_POLL_MAX = 100; // ~5 menit

/** Konfigurasi CrewAI Cloud (app.crewai): URL + Bearer token + webhook opsional. */
function getCrewCloudConfig(): {
  baseUrl: string;
  token: string;
  taskWebhookUrl?: string;
  stepWebhookUrl?: string;
  crewWebhookUrl?: string;
} | null {
  const url = (process.env.CREWAI_CLOUD_URL ?? "").trim().replace(/\/$/, "");
  const token = cleanApiKey(process.env.CREWAI_BEARER_TOKEN ?? process.env.CREWAI_CLOUD_TOKEN ?? "");
  const useCloud = process.env.CREWAI_CLOUD_MODE === "1" || process.env.CREWAI_CLOUD_MODE === "true";
  if ((useCloud || token) && url && token.length > 10) {
    const taskWebhookUrl = (process.env.CREWAI_WEBHOOK_TASK_URL ?? "").trim() || undefined;
    const stepWebhookUrl = (process.env.CREWAI_WEBHOOK_STEP_URL ?? "").trim() || undefined;
    const crewWebhookUrl = (process.env.CREWAI_WEBHOOK_CREW_URL ?? "").trim() || undefined;
    return {
      baseUrl: url,
      token,
      ...(taskWebhookUrl && { taskWebhookUrl }),
      ...(stepWebhookUrl && { stepWebhookUrl }),
      ...(crewWebhookUrl && { crewWebhookUrl }),
    };
  }
  return null;
}

function getPythonCommand(): string {
  if (process.platform !== "win32") return "python3";
  // Windows: try "python" first; "py -3" is common when Python Launcher is installed
  return "python";
}

const BOM = "\uFEFF";

/** Bersihkan key dari BOM, spasi, newline, tanda kutip (sering bikin 401). */
function cleanApiKey(raw: string): string {
  if (typeof raw !== "string") return "";
  return raw.replace(/\s/g, "").replace(/^["']|["']$/g, "").replace(BOM, "").trim();
}

function getEnvKey(name: string): string {
  const raw = process.env[name] ?? process.env[BOM + name] ?? "";
  return cleanApiKey(raw);
}

function buildCrewEnv(): NodeJS.ProcessEnv {
  const openRouter = getEnvKey("OPENROUTER_API_KEY");
  const openAi = getEnvKey("OPENAI_API_KEY");
  const apiKey = openAi || openRouter;
  const baseUrl = process.env.OPENAI_BASE_URL || process.env.OPENAI_API_BASE || "https://openrouter.ai/api/v1";
  const model = process.env.OPENAI_MODEL || process.env.OPENAI_MODEL_NAME || "openai/gpt-4o-mini";
  return {
    ...process.env,
    PYTHONUNBUFFERED: "1",
    OPENAI_API_KEY: apiKey,
    OPENROUTER_API_KEY: openRouter || apiKey,
    OPENAI_BASE_URL: baseUrl,
    OPENAI_API_BASE: baseUrl,
    OPENAI_MODEL: model,
    OPENAI_MODEL_NAME: model,
  };
}

async function runCrew(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const projectRoot = process.cwd();
  const pythonCmd = getPythonCommand();
  const env = buildCrewEnv();

  return new Promise((resolve, reject) => {
    const proc = spawn(pythonCmd, ["-m", "crew.run", "--stdin"], {
      cwd: projectRoot,
      env,
      stdio: ["pipe", "pipe", "pipe"],
    });

    const chunks: Buffer[] = [];
    let stderr = "";
    const progressUpdates: Array<{ agent: string; task: string; timestamp: string }> = [];
    let settled = false;

    proc.stdout?.on("data", (chunk: Buffer) => chunks.push(chunk));
    proc.stderr?.on("data", (chunk: Buffer) => {
      const stderrChunk = chunk.toString();
      stderr += stderrChunk;
      
      // Parse progress updates from stderr (JSON lines)
      const lines = stderrChunk.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("{") && trimmed.includes('"type":"progress"')) {
          try {
            const progress = JSON.parse(trimmed) as { type: string; agent: string; task: string; timestamp: string };
            if (progress.type === "progress") {
              progressUpdates.push({
                agent: progress.agent,
                task: progress.task,
                timestamp: progress.timestamp,
              });
            }
          } catch {
            // Ignore JSON parse errors
          }
        }
      }
    });

    proc.on("error", (err) => {
      if (!settled) {
        settled = true;
        reject(new Error(`Failed to start crew (${pythonCmd}): ${err.message}. Pastikan Python terpasang dan ada di PATH.`));
      }
    });

    const timeout = setTimeout(() => {
      if (!settled) {
        settled = true;
        proc.kill("SIGTERM");
        reject(new Error(`Crew timed out after ${CREW_TIMEOUT_MS / 1000}s`));
      }
    }, CREW_TIMEOUT_MS);

    proc.on("close", (code, signal) => {
      clearTimeout(timeout);
      if (settled) return;
      settled = true;

      const rawStdout = Buffer.concat(chunks).toString("utf-8");
      const stdout = rawStdout.replace(/\x1b\[[0-9;]*m/g, "").trim();
      const combined = `${stdout}\n${stderr}`;
      if (code !== 0 && !stdout) {
        reject(new Error(`Crew exited ${code ?? signal}: ${stderr || "No output"}`));
        return;
      }
      try {
        const result = JSON.parse(stdout || "{}") as Record<string, unknown>;
        // Add progress updates to result
        if (progressUpdates.length > 0) {
          result.progress = progressUpdates;
        }
        resolve(result);
      } catch {
        if (/401|Incorrect API key|Invalid API key/i.test(combined)) {
          reject(new Error("OpenRouter menolak API key (401). 1) Jalankan: npm run validate-key — jika gagal, buat key baru di https://openrouter.ai/settings/keys. 2) Di .env: OPENROUTER_API_KEY=sk-or-v1-... (copy utuh, tanpa spasi/kutip). 3) Restart: npm run dev"));
        } else {
          reject(new Error(`Invalid crew output: ${stdout.slice(0, 200)}`));
        }
      }
    });

    const input = JSON.stringify(payload);
    proc.stdin?.write(input, "utf-8", (err) => {
      if (err && !settled) {
        settled = true;
        clearTimeout(timeout);
        reject(err);
      } else {
        proc.stdin?.end();
      }
    });
  });
}

/**
 * Jalankan crew via CrewAI Cloud API (app.crewai / AMP).
 * POST /kickoff dengan inputs; opsional taskWebhookUrl, stepWebhookUrl, crewWebhookUrl.
 * Lalu poll GET /status/{kickoff_id} sampai selesai (kecuali pakai webhook saja).
 */
async function runCrewCloud(
  payload: Record<string, unknown>,
  config: {
    baseUrl: string;
    token: string;
    taskWebhookUrl?: string;
    stepWebhookUrl?: string;
    crewWebhookUrl?: string;
  }
): Promise<Record<string, unknown>> {
  const { baseUrl, token, taskWebhookUrl, stepWebhookUrl, crewWebhookUrl } = config;
  const kickoffBody: Record<string, unknown> = { inputs: payload };
  if (taskWebhookUrl) kickoffBody.taskWebhookUrl = taskWebhookUrl;
  if (stepWebhookUrl) kickoffBody.stepWebhookUrl = stepWebhookUrl;
  if (crewWebhookUrl) kickoffBody.crewWebhookUrl = crewWebhookUrl;

  const kickoffRes = await fetch(`${baseUrl}/kickoff`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(kickoffBody),
  });

  if (!kickoffRes.ok) {
    const errText = await kickoffRes.text();
    throw new Error(`CrewAI Cloud kickoff failed (${kickoffRes.status}): ${errText.slice(0, 300)}`);
  }

  const kickoffData = (await kickoffRes.json()) as Record<string, unknown>;
  const kickoffId =
    (kickoffData.kickoff_id as string) ??
    (kickoffData.id as string) ??
    (kickoffData.task_id as string);
  if (!kickoffId) {
    throw new Error("CrewAI Cloud did not return kickoff_id/id. Response: " + JSON.stringify(kickoffData).slice(0, 200));
  }

  for (let i = 0; i < CREW_CLOUD_POLL_MAX; i++) {
    await new Promise((r) => setTimeout(r, CREW_CLOUD_POLL_MS));
    const statusRes = await fetch(`${baseUrl}/status/${kickoffId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!statusRes.ok) {
      throw new Error(`CrewAI Cloud status failed (${statusRes.status})`);
    }
    const statusData = (await statusRes.json()) as Record<string, unknown>;
    const status = (statusData.status as string) ?? (statusData.state as string);
    if (status === "completed" || status === "complete" || status === "COMPLETED") {
      const raw = (statusData.result ?? statusData.output ?? statusData.raw ?? statusData) as Record<string, unknown>;
      const output = (raw.output as string) ?? (raw.raw as string) ?? (statusData.result as string) ?? "";
      const taskOutputs = (raw.task_outputs as unknown[]) ?? (raw.tasks_output as unknown[]) ?? [];
      return {
        status: "complete",
        output: typeof output === "string" ? output : JSON.stringify(output),
        task_outputs: Array.isArray(taskOutputs) ? taskOutputs : [],
      };
    }
    if (status === "failed" || status === "error") {
      const err = (statusData.error as string) ?? (statusData.message as string) ?? "Crew failed";
      return { status: "error", error: err };
    }
  }

  throw new Error(`CrewAI Cloud timed out after ${(CREW_CLOUD_POLL_MS * CREW_CLOUD_POLL_MAX) / 1000}s`);
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const message =
      (body.message as string) ??
      (body.user_input as string) ??
      (body.campaign_context as string) ??
      "";

    // Ping: return immediately without running Python (untuk uji koneksi UI ↔ API)
    if (body.ping === true || (typeof message === "string" && message.trim().toLowerCase() === "ping")) {
      return NextResponse.json({
        status: "complete",
        output: "Pong. API dan Chat berjalan. Kirim pesan lain (mis. brief kampanye) untuk menjalankan crew (bisa 1–2 menit).",
        task_outputs: [],
      });
    }

    const cloudConfig = getCrewCloudConfig();
    if (!cloudConfig) {
      // Mode lokal: butuh OpenRouter/OpenAI key untuk Python crew
      const openRouterKey = getEnvKey("OPENROUTER_API_KEY");
      const openAiKey = getEnvKey("OPENAI_API_KEY");
      const isPlaceholder = (k: string) =>
        !k || k === "your-openrouter-api-key-here" || k.startsWith("sk-or-v1-xxx") || k === "sk-...";
      const hasValidKey = (!isPlaceholder(openRouterKey) && openRouterKey.length > 20) || (!isPlaceholder(openAiKey) && openAiKey.length > 20);
      if (!hasValidKey) {
        return NextResponse.json(
          {
            status: "error",
            error:
              "API key belum diisi atau masih placeholder. Buat file .env di root project, isi OPENROUTER_API_KEY dengan key dari https://openrouter.ai/settings/keys lalu restart npm run dev.",
          },
          { status: 400 }
        );
      }
    }

    const language =
      (body.language as string)?.trim() ||
      (body.locale as string)?.trim() ||
      (body.output_language as string)?.trim() ||
      "";

    const payload = {
      user_input: message || "No message provided.",
      message: body.message,
      campaign_context: body.campaign_context,
      ...(language ? { language, output_language: language } : {}),
    };

    // Webhook opsional: dari body (override) atau dari config
    const webhookFromBody = {
      taskWebhookUrl: (body.taskWebhookUrl as string)?.trim() || undefined,
      stepWebhookUrl: (body.stepWebhookUrl as string)?.trim() || undefined,
      crewWebhookUrl: (body.crewWebhookUrl as string)?.trim() || undefined,
    };
    const cloudConfigWithWebhooks =
      cloudConfig && cloudConfig.baseUrl
        ? {
            ...cloudConfig,
            taskWebhookUrl: webhookFromBody.taskWebhookUrl ?? cloudConfig.taskWebhookUrl,
            stepWebhookUrl: webhookFromBody.stepWebhookUrl ?? cloudConfig.stepWebhookUrl,
            crewWebhookUrl: webhookFromBody.crewWebhookUrl ?? cloudConfig.crewWebhookUrl,
          }
        : cloudConfig;

    const result = cloudConfigWithWebhooks
      ? await runCrewCloud(payload, cloudConfigWithWebhooks)
      : await runCrew(payload);

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

/** Cek validitas OpenRouter API key tanpa jalankan crew. */
async function validateOpenRouterKey(): Promise<{ valid: boolean; error?: string }> {
  const key = getEnvKey("OPENROUTER_API_KEY") || getEnvKey("OPENAI_API_KEY");
  if (!key || key === "your-openrouter-api-key-here") {
    return { valid: false, error: "OPENROUTER_API_KEY tidak di-set di .env. Copy env.example ke .env lalu isi key dari https://openrouter.ai/settings/keys" };
  }
  try {
    const res = await fetch("https://openrouter.ai/api/v1/models", {
      method: "GET",
      headers: { Authorization: `Bearer ${key}` },
    });
    if (res.status === 401) {
      return { valid: false, error: "Key ditolak (401). Buat key baru di https://openrouter.ai/settings/keys → Create Key → paste di .env sebagai OPENROUTER_API_KEY=sk-or-v1-... lalu restart: npm run dev" };
    }
    if (!res.ok) {
      return { valid: false, error: `OpenRouter mengembalikan ${res.status}. Coba lagi atau ganti key.` };
    }
    return { valid: true };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { valid: false, error: `Gagal cek key: ${msg}` };
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  if (searchParams.get("validate") === "1" || searchParams.get("check") === "key") {
    const result = await validateOpenRouterKey();
    return NextResponse.json(result.valid ? { valid: true, message: "API key valid. Chat siap dipakai." } : { valid: false, error: result.error });
  }
  // Cek apakah .env terbaca oleh API (tanpa menampilkan key)
  if (searchParams.get("env") === "1") {
    const key = getEnvKey("OPENROUTER_API_KEY") || getEnvKey("OPENAI_API_KEY");
    const hasKey = key.length > 20 && key !== "your-openrouter-api-key-here";
    return NextResponse.json({
      envLoaded: true,
      hasKey,
      hint: hasKey ? "Key terbaca. Jika masih 401, ganti key baru di .env lalu restart." : "Key belum terbaca. Pastikan .env di root project (satu folder dengan package.json) dan restart: npm run dev",
    });
  }
  return NextResponse.json({
    status: "ok",
    message:
      "CrewAI chat API. POST untuk jalankan crew. GET ?validate=1 cek key, GET ?env=1 cek .env terbaca. Jika CREWAI_CLOUD_URL + CREWAI_BEARER_TOKEN di-set, crew dijalankan via CrewAI Cloud (app.crewai).",
    crewMode: getCrewCloudConfig() ? "cloud" : "local",
  });
}
