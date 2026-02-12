import { NextRequest, NextResponse } from "next/server";
import { getUserBySessionToken, hashPassword } from "@/lib/auth";
import { query } from "@/lib/db";

// Use Node.js runtime to support crypto and pg modules
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * PUT /api/users/[id] - Update user
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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

    // Only admin can update users
    if (currentUser.role !== "admin") {
      return NextResponse.json(
        { error: "Unauthorized. Admin access required." },
        { status: 403 }
      );
    }

    const userId = params.id;
    const body = await request.json().catch(() => ({}));
    const email = (body.email || "").toString().trim();
    const username = (body.username || "").toString().trim();
    const fullName = (body.fullName || "").toString().trim() || null;
    const role = (body.role || "").toString().trim();
    const password = body.password && body.password.toString().trim() ? body.password.toString().trim() : null;

    if (!email || !username || !role) {
      return NextResponse.json(
        { error: "Email, username, and role are required" },
        { status: 400 }
      );
    }

    if (password !== null && password.length < 6) {
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

    // Check if user exists
    const userCheck = await query<{ id: string }>(
      "SELECT id FROM users WHERE id = $1",
      [userId]
    );
    if (userCheck.rows.length === 0) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }

    // Check if email or username already exists (excluding current user)
    const existingEmail = await query<{ id: string }>(
      "SELECT id FROM users WHERE email = $1 AND id != $2",
      [email, userId]
    );
    if (existingEmail.rows.length > 0) {
      return NextResponse.json(
        { error: "Email already exists" },
        { status: 400 }
      );
    }

    const existingUsername = await query<{ id: string }>(
      "SELECT id FROM users WHERE username = $1 AND id != $2",
      [username, userId]
    );
    if (existingUsername.rows.length > 0) {
      return NextResponse.json(
        { error: "Username already exists" },
        { status: 400 }
      );
    }

    // Update user
    if (password) {
      const passwordHash = await hashPassword(password);
      await query(
        `UPDATE users 
         SET email = $1, username = $2, full_name = $3, role = $4, password_hash = $5, updated_at = CURRENT_TIMESTAMP
         WHERE id = $6`,
        [email, username, fullName, role, passwordHash, userId]
      );
    } else {
      await query(
        `UPDATE users 
         SET email = $1, username = $2, full_name = $3, role = $4, updated_at = CURRENT_TIMESTAMP
         WHERE id = $5`,
        [email, username, fullName, role, userId]
      );
    }

    // Get updated user
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
      "SELECT id, email, username, full_name, role, is_active, created_at, last_login FROM users WHERE id = $1",
      [userId]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }

    const user = result.rows[0];
    return NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        fullName: user.full_name || undefined,
        role: user.role,
        isActive: user.is_active,
        createdAt: user.created_at.toISOString(),
        lastLogin: user.last_login ? user.last_login.toISOString() : undefined,
      },
    });
  } catch (err) {
    console.error("Update user error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to update user" },
      { status: 500 }
    );
  }
}
