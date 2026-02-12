import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getUserBySessionToken } from "@/lib/auth";

// Routes that don't require authentication
const publicRoutes = ["/login", "/api/auth/login", "/api/auth/register"];

// Routes that require authentication
const protectedRoutes = [
  "/dashboard",
  "/chat",
  "/plans",
  "/sentiment",
  "/trends",
  "/reports",
  "/settings",
  "/calendar",
  "/review",
  "/optimization",
  "/subscription",
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth_token")?.value;

  // Handle root path - redirect based on token and session validation
  if (pathname === "/") {
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
    // Validate session in database
    const user = await getUserBySessionToken(token);
    if (!user) {
      // Invalid session - clear cookie and redirect to login
      const response = NextResponse.redirect(new URL("/login", request.url));
      response.cookies.delete("auth_token");
      return response;
    }
    // Valid session - redirect to dashboard
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Allow public routes
  if (publicRoutes.some((route) => pathname.startsWith(route))) {
    // If user has token and tries to access login page, validate session first
    if (pathname === "/login" && token) {
      const user = await getUserBySessionToken(token);
      if (user) {
        // Valid session - redirect to dashboard
        return NextResponse.redirect(new URL("/dashboard", request.url));
      }
      // Invalid session - clear cookie and allow access to login
      const response = NextResponse.next();
      response.cookies.delete("auth_token");
      return response;
    }
    return NextResponse.next();
  }

  // Protect routes that require authentication
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Validate session in database
    const user = await getUserBySessionToken(token);
    if (!user) {
      // Invalid or expired session - clear cookie and redirect to login
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete("auth_token");
      return response;
    }

    // Valid session - allow access
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
