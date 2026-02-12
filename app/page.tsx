import { redirect } from "next/navigation";

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  // Root path redirect is handled in middleware.ts
  // This is just a fallback - middleware will redirect based on session
  redirect("/login");
}
