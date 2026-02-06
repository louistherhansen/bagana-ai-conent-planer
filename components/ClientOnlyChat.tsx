"use client";

import { useState, useEffect } from "react";
import { ChatRuntimeProvider } from "@/components/ChatRuntimeProvider";
import { ChatInterface } from "@/components/ChatInterface";

/**
 * Renders chat only after client mount so assistant-ui does not run during SSR.
 */
export function ClientOnlyChat() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <div className="flex-1 flex flex-col min-h-0 items-center justify-center px-4 py-12 text-slate-500 text-sm">
        Loading chat…
      </div>
    );
  }

  return (
    <ChatRuntimeProvider>
      <ChatInterface />
    </ChatRuntimeProvider>
  );
}
