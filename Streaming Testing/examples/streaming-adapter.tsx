// components/StreamingCrewAdapter.tsx
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
          const lines = buffer.split("\n");
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
