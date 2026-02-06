"""
Example implementation of streaming API route for CrewAI.
This demonstrates how to implement SSE streaming in Next.js API routes.
"""
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_nextjs_sse_route():
    """Generate example Next.js SSE API route code."""
    
    code = '''// app/api/crew/stream/route.ts
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
          encoder.encode("data: {"type":"connected"}\\n\\n")
        );
        
        // Handle stderr (progress updates)
        proc.stderr?.on("data", (chunk: Buffer) => {
          const lines = chunk.toString().split("\\n");
          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith("{") && trimmed.includes('"type":"progress"')) {
              try {
                const progress = JSON.parse(trimmed);
                // Send as SSE message
                const sse = `data: ${JSON.stringify(progress)}\\n\\n`;
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
          const stdout = rawStdout.replace(/\\x1b\\[[0-9;]*m/g, "").trim();
          
          try {
            const result = JSON.parse(stdout || "{}");
            
            // Send final result
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ type: "result", ...result })}\\n\\n`)
            );
            
            // Send completion marker
            controller.enqueue(encoder.encode("data: [DONE]\\n\\n"));
            controller.close();
          } catch {
            controller.enqueue(
              encoder.encode(`data: {"type":"error","error":"Invalid output"}\\n\\n`)
            );
            controller.close();
          }
        });
        
        // Handle errors
        proc.on("error", (err) => {
          controller.enqueue(
            encoder.encode(`data: {"type":"error","error":"${err.message}"}\\n\\n`)
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
              encoder.encode(`data: {"type":"error","error":"${err.message}"}\\n\\n`)
            );
            controller.close();
          } else {
            proc.stdin?.end();
          }
        });
        
      } catch (error) {
        const message = error instanceof Error ? error.message : "Unknown error";
        controller.enqueue(
          encoder.encode(`data: {"type":"error","error":"${message}"}\\n\\n`)
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
'''
    
    return code


def generate_frontend_streaming_adapter():
    """Generate example frontend streaming adapter code."""
    
    code = '''// components/StreamingCrewAdapter.tsx
import { ChatModelAdapter, ChatModelRunOptions, ChatModelRunResult } from "@assistant-ui/react";

export function createStreamingCrewAdapter(): ChatModelAdapter {
  return {
    async run(options: ChatModelRunOptions): Promise<ChatModelRunResult> {
      const { messages, abortSignal } = options;
      const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
      const text = lastUserMessage?.content?.find((c) => c.type === "text");
      const message = typeof text === "object" && text && "text" in text ? String(text.text) : "";

      if (!message || message.trim().length === 0) {
        return {
          content: [{ type: "text", text: "Error: Message cannot be empty." }],
          status: { type: "complete", reason: "stop" },
        };
      }

      const language = getLanguage(); // Your language getter
      const body = { message, ...(language ? { language } : {}) };

      try {
        const response = await fetch("/api/crew/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: abortSignal,
        });

        if (!response.ok) {
          return {
            content: [{ type: "text", text: `Error: HTTP ${response.status}` }],
            status: { type: "complete", reason: "stop" },
          };
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let fullOutput = "";

        if (!reader) {
          return {
            content: [{ type: "text", text: "Error: No response stream" }],
            status: { type: "complete", reason: "stop" },
          };
        }

        // Stream processing
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              
              if (data === "[DONE]") {
                return {
                  content: [{ type: "text", text: fullOutput }],
                  status: { type: "complete", reason: "stop" },
                };
              }

              try {
                const parsed = JSON.parse(data);
                
                if (parsed.type === "progress") {
                  // Handle progress update
                  console.log("Progress:", parsed.agent, parsed.task);
                  // Update UI with progress
                } else if (parsed.type === "result") {
                  // Handle final result
                  fullOutput = parsed.output || "";
                } else if (parsed.type === "error") {
                  return {
                    content: [{ type: "text", text: `Error: ${parsed.error}` }],
                    status: { type: "complete", reason: "stop" },
                  };
                }
              } catch {
                // Ignore parse errors
              }
            }
          }
        }

        return {
          content: [{ type: "text", text: fullOutput || "No output received" }],
          status: { type: "complete", reason: "stop" },
        };

      } catch (error) {
        const message = error instanceof Error ? error.message : "Unknown error";
        return {
          content: [{ type: "text", text: `Error: ${message}` }],
          status: { type: "complete", reason: "stop" },
        };
      }
    },
  };
}
'''
    
    return code


def main():
    """Generate example code files."""
    print("=" * 60)
    print("CrewAI Real-Time Streaming - Example Code Generator")
    print("=" * 60)
    
    print("\n[1/2] Generating Next.js SSE API route...")
    sse_route = generate_nextjs_sse_route()
    print("[OK] SSE route code generated")
    
    print("\n[2/2] Generating frontend streaming adapter...")
    frontend_adapter = generate_frontend_streaming_adapter()
    print("[OK] Frontend adapter code generated")
    
    # Save to files
    output_dir = Path(__file__).parent / "examples"
    output_dir.mkdir(exist_ok=True)
    
    (output_dir / "sse-api-route.ts").write_text(sse_route)
    (output_dir / "streaming-adapter.tsx").write_text(frontend_adapter)
    
    print(f"\n[OK] Example code saved to: {output_dir}")
    print("\nFiles created:")
    print("  - examples/sse-api-route.ts")
    print("  - examples/streaming-adapter.tsx")
    
    print("\n" + "=" * 60)
    print("Usage:")
    print("=" * 60)
    print("1. Copy sse-api-route.ts to app/api/crew/stream/route.ts")
    print("2. Copy streaming-adapter.tsx to components/StreamingCrewAdapter.tsx")
    print("3. Update ChatRuntimeProvider to use streaming adapter")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
