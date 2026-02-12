import { NextRequest, NextResponse } from "next/server";
import { getUserBySessionToken } from "@/lib/auth";
import { query } from "@/lib/db";

// Use Node.js runtime to support crypto and pg modules
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * PATCH /api/users/[id]/toggle-active - Toggle user active status
 */
export async function PATCH(
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

    // Only admin can toggle user status
    if (currentUser.role !== "admin") {
      return NextResponse.json(
        { error: "Unauthorized. Admin access required." },
        { status: 403 }
      );
    }

    const userId = params.id;
    const body = await request.json().catch(() => ({}));
    const isActive = body.isActive !== undefined ? Boolean(body.isActive) : null;

    if (isActive === null) {
      return NextResponse.json(
        { error: "isActive is required" },
        { status: 400 }
      );
    }

    // Prevent deactivating yourself
    if (userId === currentUser.id && !isActive) {
      return NextResponse.json(
        { error: "You cannot deactivate your own account" },
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

    // Update user status
    await query(
      "UPDATE users SET is_active = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
      [isActive, userId]
    );

    return NextResponse.json({ success: true, isActive });
  } catch (err) {
    console.error("Toggle user active error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to update user status" },
      { status: 500 }
    );
  }
}
