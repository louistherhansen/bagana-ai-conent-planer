import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { getUserBySessionToken } from "@/lib/auth";

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    redirect("/login");
  }

  // Verify session
  const user = await getUserBySessionToken(token);
  if (!user) {
    redirect("/login");
  }

  // Redirect authenticated users to dashboard
  redirect("/dashboard");
}
