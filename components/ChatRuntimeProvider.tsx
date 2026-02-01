"use client";

import {
  useLocalRuntime,
  AssistantRuntimeProvider,
  type ChatModelAdapter,
  type ChatModelRunOptions,
  type ChatModelRunResult,
} from "@assistant-ui/react";

/** Chat model adapter: wires assistant-ui chat to backend CrewAI API (POST /api/crew). */
const crewAdapter: ChatModelAdapter = {
  async run(options: ChatModelRunOptions): Promise<ChatModelRunResult> {
    const { messages, abortSignal } = options;
    const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
    const text = lastUserMessage?.content?.find((c) => c.type === "text");
    const message = typeof text === "object" && text && "text" in text ? String(text.text) : "";

    if (abortSignal.aborted) {
      return { content: [], status: { type: "incomplete" as const, reason: "cancelled" as const } };
    }

    try {
      const res = await fetch("/api/crew", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
        signal: abortSignal,
      });
      const data = await res.json();

      if (!res.ok) {
        return {
          content: [{ type: "text" as const, text: `Error: ${data.error ?? res.statusText}` }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }

      if (data.status === "error") {
        return {
          content: [{ type: "text" as const, text: `Crew error: ${data.error ?? "Unknown"}` }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }

      const output = data.output ?? "";
      return {
        content: [{ type: "text" as const, text: output }],
        status: { type: "complete" as const, reason: "stop" as const },
      };
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Request failed";
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        status: { type: "complete" as const, reason: "stop" as const },
      };
    }
  },
};

export function ChatRuntimeProvider({ children }: { children: React.ReactNode }) {
  const runtime = useLocalRuntime(crewAdapter, {
    initialMessages: [
      {
        id: "welcome",
        role: "assistant",
        content: [
          {
            type: "text",
            text: "Welcome to BAGANA AI. I'll help you create multi-talent content plans with sentiment analysis and trend insights. Share your campaign context or a brief to get started.",
          },
        ],
      },
    ],
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
