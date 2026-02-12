import { NextRequest, NextResponse } from "next/server";
import { getUserBySessionToken, createUser } from "@/lib/auth";
import { query } from "@/lib/db";

// Use Node.js runtime to support crypto and pg modules
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/users - List all users
 */
export async function GET(request: NextRequest) {
  try {
    const token = request.cookies.get("auth_token")?.value;

    if (!token) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    const currentUser = await getUserBySessionToken(token);

    if (!currentUser) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    // Only admin can view all users
    if (currentUser.role !== "admin") {
      return NextResponse.json(
        { error: "Unauthorized. Admin access required." },
        { status: 403 }
      );
    }

    const result = await query<{
      id: string;
      email: string;
      username: string;
      full_name: string | null;
      role: string;
      is_active: boolean;
      created_at: Date;
      last_login: Date | null;
    }>(
      `SELECT id, email, username, full_name, role, is_active, created_at, last_login 
       FROM users 
       ORDER BY created_at DESC`
    );

    const users = result.rows.map((row) => ({
      id: row.id,
      email: row.email,
      username: row.username,
      fullName: row.full_name || undefined,
      role: row.role,
      isActive: row.is_active,
      createdAt: row.created_at.toISOString(),
      lastLogin: row.last_login ? row.last_login.toISOString() : undefined,
    }));

    return NextResponse.json({ users });
  } catch (err) {
    console.error("Get users error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to get users" },
      { status: 500 }
    );
  }
}

/**
 * POST /api/users - Create new user
 */
export async function POST(request: NextRequest) {
  try {
    const token = request.cookies.get("auth_token")?.value;

    if (!token) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    const currentUser = await getUserBySessionToken(token);

    if (!currentUser) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    // Only admin can create users
    if (currentUser.role !== "admin") {
      return NextResponse.json(
        { error: "Unauthorized. Admin access required." },
        { status: 403 }
      );
    }

    const body = await request.json().catch(() => ({}));
    const email = (body.email || "").toString().trim();
    const username = (body.username || "").toString().trim();
    const password = (body.password || "").toString();
    const fullName = (body.fullName || "").toString().trim() || undefined;
    const role = (body.role || "user").toString().trim();

    if (!email || !username || !password) {
      return NextResponse.json(
        { error: "Email, username, and password are required" },
        { status: 400 }
      );
    }

    if (password.length < 6) {
      return NextResponse.json(
        { error: "Password must be at least 6 characters long" },
        { status: 400 }
      );
    }

    // Validate role
    const validRoles = ["user", "admin", "moderator"];
    if (!validRoles.includes(role)) {
      return NextResponse.json(
        { error: "Invalid role. Must be one of: user, admin, moderator" },
        { status: 400 }
      );
    }

    // Check if email or username already exists
    const existingEmail = await query<{ id: string }>(
      "SELECT id FROM users WHERE email = $1",
      [email]
    );
    if (existingEmail.rows.length > 0) {
      return NextResponse.json(
        { error: "Email already exists" },
        { status: 400 }
      );
    }

    const existingUsername = await query<{ id: string }>(
      "SELECT id FROM users WHERE username = $1",
      [username]
    );
    if (existingUsername.rows.length > 0) {
      return NextResponse.json(
        { error: "Username already exists" },
        { status: 400 }
      );
    }

    // Create user
    const newUser = await createUser({
      email,
      username,
      password,
      fullName,
      role,
    });

    if (!newUser) {
      return NextResponse.json(
        { error: "Failed to create user" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      user: {
        id: newUser.id,
        email: newUser.email,
        username: newUser.username,
        fullName: newUser.fullName,
        role: newUser.role,
        isActive: newUser.isActive,
      },
    });
  } catch (err) {
    console.error("Create user error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to create user" },
      { status: 500 }
    );
  }
}
