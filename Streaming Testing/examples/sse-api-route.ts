// app/api/crew/stream/route.ts
import { NextRequest } from "next/server";
import { spawn } from "child_process";
import { getPythonCommand, buildCrewEnv } from "@/lib/crew-utils";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        const body = await request.json();
        const { message, language } = body;
        
        const projectRoot = process.cwd();
        const pythonCmd = getPythonCommand();
        const env = buildCrewEnv();
        
        const proc = spawn(pythonCmd, ["-m", "crew.run", "--stdin"], {
          cwd: projectRoot,
          env,
          stdio: ["pipe", "pipe", "pipe"],
        });
        
        // Send initial connection message
        controller.enqueue(
          encoder.encode("data: {"type":"connected"}\n\n")
        );
        
        // Handle stderr (progress updates)
        proc.stderr?.on("data", (chunk: Buffer) => {
          const lines = chunk.toString().split("\n");
          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("{") && trimmed.includes('"type":"progress"')) {
              try {
                const progress = JSON.parse(trimmed);
                // Send as SSE message
                const sse = `data: ${JSON.stringify(progress)}\n\n`;
                controller.enqueue(encoder.encode(sse));
              } catch {
                // Ignore parse errors
              }
            }
          }
        });
        
        // Handle stdout (final result)
        let stdoutChunks: Buffer[] = [];
        proc.stdout?.on("data", (chunk: Buffer) => {
          stdoutChunks.push(chunk);
        });
        
        // Handle completion
        proc.on("close", (code) => {
          const rawStdout = Buffer.concat(stdoutChunks).toString("utf-8");
          const stdout = rawStdout.replace(/\x1b\[[0-9;]*m/g, "").trim();
          
          try {
            const result = JSON.parse(stdout || "{}");
            
            // Send final result
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ type: "result", ...result })}\n\n`)
            );
            
            // Send completion marker
            controller.enqueue(encoder.encode("data: [DONE]\n\n"));
            controller.close();
          } catch {
            controller.enqueue(
              encoder.encode(`data: {"type":"error","error":"Invalid output"}\n\n`)
            );
            controller.close();
          }
        });
        
        // Handle errors
        proc.on("error", (err) => {
          controller.enqueue(
            encoder.encode(`data: {"type":"error","error":"${err.message}"}\n\n`)
          );
          controller.close();
        });
        
        // Write input to stdin
        const payload = JSON.stringify({
          user_input: message || "No message provided.",
          message,
          output_language: language || "English",
        });
        
        proc.stdin?.write(payload, "utf-8", (err) => {
          if (err) {
            controller.enqueue(
              encoder.encode(`data: {"type":"error","error":"${err.message}"}\n\n`)
            );
            controller.close();
          } else {
            proc.stdin?.end();
          }
        });
        
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unknown error";
        controller.enqueue(
          encoder.encode(`data: {"type":"error","error":"${message}"}\n\n`)
        );
        controller.close();
      }
    },
  });
  
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no", // Disable nginx buffering
    },
  });
}
