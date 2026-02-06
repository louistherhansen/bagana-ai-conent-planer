"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import dynamic from "next/dynamic";

function LoadingWithTimeout({ onRetry }: { onRetry: () => void }) {
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setTimedOut(true), 10000);
    return () => clearTimeout(t);
  }, []);

  if (timedOut) {
    return (
      <div className="flex-1 flex flex-col min-h-0 items-center justify-center px-4 py-12 text-center">
        <p className="text-slate-600 text-sm mb-3">Memuat terlalu lama.</p>
        <p className="text-slate-500 text-sm mb-4">Periksa koneksi lalu coba lagi.</p>
        <button
          type="button"
          onClick={onRetry}
          className="rounded-xl bg-bagana-primary px-5 py-2.5 text-sm font-medium text-white hover:bg-bagana-secondary transition-colors"
        >
          Coba lagi
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 items-center justify-center px-4 py-12 text-slate-500 text-sm">
      Loading chat…
    </div>
  );
}

export function ChatPageClient() {
  const [key, setKey] = useState(0);
  const setKeyRef = useRef(setKey);
  setKeyRef.current = setKey;

  const DynamicChat = useMemo(
    () =>
      dynamic(() => import("@/components/ChatContent"), {
        ssr: false,
        loading: () => (
          <LoadingWithTimeout
            onRetry={() => {
              setKeyRef.current((k: number) => k + 1);
            }}
          />
        ),
      }),
    []
  );

  return <DynamicChat key={key} />;
}
