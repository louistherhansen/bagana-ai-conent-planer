"use client";

import {
  ThreadPrimitive,
  ComposerPrimitive,
  MessagePrimitive,
} from "@assistant-ui/react";

function UserMessage() {
  return (
    <MessagePrimitive.Root className="flex justify-end">
      <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl bg-bagana-primary px-4 py-3 text-white">
        <MessagePrimitive.Parts
          components={{
            Text: ({ text }) => (
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>
            ),
          }}
        />
      </div>
    </MessagePrimitive.Root>
  );
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="flex justify-start">
      <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
        <MessagePrimitive.Parts
          components={{
            Text: ({ text }) => (
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-slate-800">
                {text}
              </p>
            ),
          }}
        />
      </div>
    </MessagePrimitive.Root>
  );
}

export function ChatInterface() {
  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      <ThreadPrimitive.Root className="flex-1 flex flex-col min-h-0">
        <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-3 sm:px-4 py-4 sm:py-6">
          <div className="space-y-6">
            <ThreadPrimitive.Messages
              components={{
                UserMessage,
                AssistantMessage,
              }}
            />
          </div>
        </ThreadPrimitive.Viewport>

        <div className="shrink-0 border-t border-slate-200 bg-white p-3 sm:p-4">
          <ComposerPrimitive.Root className="max-w-4xl mx-auto">
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
              <ComposerPrimitive.Input
                placeholder="Describe your campaign, share a brief, or ask for a content plan..."
                className="flex-1 min-h-[44px] rounded-xl border border-slate-300 px-4 py-3 text-sm placeholder:text-slate-400 focus:border-bagana-primary focus:outline-none focus:ring-2 focus:ring-bagana-primary/20"
              />
              <ComposerPrimitive.Send className="rounded-xl bg-bagana-primary px-5 py-3 text-sm font-medium text-white hover:bg-bagana-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors touch-target shrink-0">
                Send
              </ComposerPrimitive.Send>
            </div>
          </ComposerPrimitive.Root>
        </div>
      </ThreadPrimitive.Root>
    </div>
  );
}
