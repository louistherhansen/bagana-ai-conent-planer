import Link from "next/link";
import { AppNav, MAIN_NAV_ITEMS } from "./AppNav";

type PageLayoutProps = {
  children: React.ReactNode;
  currentPath?: string;
};

export function PageLayout({ children, currentPath }: PageLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur shrink-0">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link
            href="/"
            className="text-lg font-semibold text-bagana-dark hover:text-bagana-primary transition-colors shrink-0"
          >
            BAGANA AI
          </Link>
          <AppNav items={MAIN_NAV_ITEMS} currentPath={currentPath} />
        </div>
      </header>
      <main className="flex-1 flex flex-col min-h-0">{children}</main>
    </div>
  );
}
