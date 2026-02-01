"use client";

import Link from "next/link";
import { useState } from "react";

type NavItem = {
  href: string;
  label: string;
  active?: boolean;
};

export function AppNav({
  items,
  currentPath,
}: {
  items: NavItem[];
  currentPath?: string;
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = (
    <>
      {items.map((item) => {
        const isActive = currentPath === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setMobileOpen(false)}
            className={`text-sm font-medium transition-colors touch-target flex items-center ${
              isActive
                ? "text-bagana-primary border-b-2 border-bagana-primary pb-0.5"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </>
  );

  return (
    <>
      {/* Desktop nav */}
      <nav className="hidden lg:flex flex-wrap gap-4 xl:gap-6 items-center">
        {navLinks}
      </nav>

      {/* Mobile: hamburger + overlay */}
      <div className="lg:hidden relative">
        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          className="touch-target flex items-center justify-center rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-800"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
        >
          {mobileOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>

        {mobileOpen && (
          <>
            <div
              className="fixed inset-0 bg-slate-900/20 z-40 lg:hidden"
              onClick={() => setMobileOpen(false)}
              aria-hidden
            />
            <nav
              className="fixed right-0 top-0 bottom-0 w-64 max-w-[85vw] bg-white border-l border-slate-200 shadow-xl z-50 flex flex-col gap-1 p-4 pt-16"
              aria-label="Mobile navigation"
            >
              {navLinks}
            </nav>
          </>
        )}
      </div>
    </>
  );
}

export const MAIN_NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Home" },
  { href: "/chat", label: "Chat" },
  { href: "/dashboard", label: "Features" },
  { href: "/plans", label: "Plans" },
  { href: "/reports", label: "Reports" },
  { href: "/sentiment", label: "Sentiment" },
  { href: "/trends", label: "Trends" },
  { href: "/settings", label: "Settings" },
];
