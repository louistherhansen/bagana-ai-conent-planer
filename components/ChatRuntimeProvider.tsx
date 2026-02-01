"use client";

import {
  useLocalRuntime,
  AssistantRuntimeProvider,
  type ChatModelAdapter,
  type ChatModelRunOptions,
  type ChatModelRunResult,
} from "@assistant-ui/react";

const MOCK_RESPONSE =
  "Backend integration is pending (Integration epic). Your message will be processed by the CrewAI content planning crew once the API is wired. For now, this is a visual stub.";

const mockAdapter: ChatModelAdapter = {
  async run(options: ChatModelRunOptions): Promise<ChatModelRunResult> {
    const { abortSignal } = options;
    await new Promise((r) => setTimeout(r, 600));

    if (abortSignal.aborted) {
      return { content: [], status: { type: "incomplete" as const, reason: "cancelled" as const } };
    }

    return {
      content: [{ type: "text" as const, text: MOCK_RESPONSE }],
      status: { type: "complete" as const, reason: "stop" as const },
    };
  },
};

export function ChatRuntimeProvider({ children }: { children: React.ReactNode }) {
  const runtime = useLocalRuntime(mockAdapter, {
    initialMessages: [
      {
        id: "welcome",
        role: "assistant",
        content: [
          {
            type: "text",
            text: "Welcome to BAGANA AI. I'll help you create multi-talent content plans with sentiment analysis and trend insights. Share your campaign context or a brief to get started. _(Backend not yet connected — Integration epic will wire CrewAI.)_",
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
