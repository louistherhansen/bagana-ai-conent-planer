import { NextRequest, NextResponse } from "next/server";
import { getUserBySessionToken, verifyPassword, updateUserPassword } from "@/lib/auth";

// Use Node.js runtime to support crypto and pg modules
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const token = request.cookies.get("auth_token")?.value;

    if (!token) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    const user = await getUserBySessionToken(token);

    if (!user) {
      return NextResponse.json(
        { error: "Invalid session" },
        { status: 401 }
      );
    }

    const body = await request.json().catch(() => ({}));
    const currentPassword = (body.currentPassword || "").toString();
    const newPassword = (body.newPassword || "").toString();

    if (!currentPassword || !newPassword) {
      return NextResponse.json(
        { error: "Current password and new password are required" },
        { status: 400 }
      );
    }

    if (newPassword.length < 6) {
      return NextResponse.json(
        { error: "New password must be at least 6 characters long" },
        { status: 400 }
      );
    }

    // Get current password hash
    const { query } = await import("@/lib/db");
    const result = await query<{ password_hash: string }>(
      "SELECT password_hash FROM users WHERE id = $1",
      [user.id]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }

    // Verify current password
    const isValid = await verifyPassword(currentPassword, result.rows[0].password_hash);
    if (!isValid) {
      return NextResponse.json(
        { error: "Current password is incorrect" },
        { status: 401 }
      );
    }

    // Update password
    const success = await updateUserPassword(user.id, newPassword);
    if (!success) {
      return NextResponse.json(
        { error: "Failed to update password" },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("Change password error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to change password" },
      { status: 500 }
    );
  }
}
