import { NextRequest, NextResponse } from "next/server";
import { config as loadEnv } from "dotenv";
import path from "path";
import { query } from "@/lib/db";

// Load environment variables
loadEnv({ path: path.resolve(process.cwd(), ".env") });

/**
 * Content Plans API Endpoints
 * 
 * GET /api/content-plans - Get all content plans
 * GET /api/content-plans?id=<plan_id> - Get specific plan with versions
 * POST /api/content-plans - Create new content plan
 * PUT /api/content-plans - Update content plan
 * DELETE /api/content-plans?id=<plan_id> - Delete content plan
 */

export interface PlanTalent {
  name: string;
}

export interface PlanVersion {
  id: string;
  version: string;
  content: any;
  metadata?: any;
  createdAt: number;
}

export interface ContentPlan {
  id: string;
  title: string;
  campaign?: string;
  brandName?: string;
  conversationId?: string;
  schemaValid: boolean;
  talents: string[];
  versions: PlanVersion[];
  createdAt: number;
  updatedAt: number;
}

/**
 * GET /api/content-plans
 * Get all content plans or a specific plan by ID
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const planId = searchParams.get("id");

    if (planId) {
      // Get specific plan with versions and talents
      const planResult = await query<{
        id: string;
        title: string;
        campaign: string | null;
        brand_name: string | null;
        conversation_id: string | null;
        schema_valid: boolean;
        created_at: Date;
        updated_at: Date;
      }>(
        "SELECT id, title, campaign, brand_name, conversation_id, schema_valid, created_at, updated_at FROM content_plans WHERE id = $1",
        [planId]
      );

      if (planResult.rows.length === 0) {
        return NextResponse.json(
          { error: "Content plan not found" },
          { status: 404 }
        );
      }

      const plan = planResult.rows[0];

      // Get versions for this plan
      const versionsResult = await query<{
        id: string;
        version: string;
        content: any;
        metadata: any;
        created_at: Date;
      }>(
        "SELECT id, version, content, metadata, created_at FROM plan_versions WHERE plan_id = $1 ORDER BY created_at DESC",
        [planId]
      );

      // Get talents for this plan
      const talentsResult = await query<{
        talent_name: string;
      }>(
        "SELECT talent_name FROM plan_talents WHERE plan_id = $1 ORDER BY talent_name",
        [planId]
      );

      const contentPlan: ContentPlan = {
        id: plan.id,
        title: plan.title,
        campaign: plan.campaign || undefined,
        brandName: plan.brand_name || undefined,
        conversationId: plan.conversation_id || undefined,
        schemaValid: plan.schema_valid,
        talents: talentsResult.rows.map((row) => row.talent_name),
        versions: versionsResult.rows.map((row) => ({
          id: row.id,
          version: row.version,
          content: row.content,
          metadata: row.metadata || undefined,
          createdAt: row.created_at.getTime(),
        })),
        createdAt: plan.created_at.getTime(),
        updatedAt: plan.updated_at.getTime(),
      };

      return NextResponse.json(contentPlan);
    } else {
      // Get all content plans (without versions for performance)
      const result = await query<{
        id: string;
        title: string;
        campaign: string | null;
        brand_name: string | null;
        schema_valid: boolean;
        updated_at: Date;
      }>(
        "SELECT id, title, campaign, brand_name, schema_valid, updated_at FROM content_plans ORDER BY updated_at DESC LIMIT 100"
      );

      // Get talents for each plan
      const plansWithTalents = await Promise.all(
        result.rows.map(async (row) => {
          const talentsResult = await query<{
            talent_name: string;
          }>(
            "SELECT talent_name FROM plan_talents WHERE plan_id = $1 ORDER BY talent_name",
            [row.id]
          );

          // Get latest version for version number
          const latestVersionResult = await query<{
            version: string;
          }>(
            "SELECT version FROM plan_versions WHERE plan_id = $1 ORDER BY created_at DESC LIMIT 1",
            [row.id]
          );

          return {
            id: row.id,
            title: row.title,
            campaign: row.campaign || undefined,
            brandName: row.brand_name || undefined,
            schemaValid: row.schema_valid,
            talents: talentsResult.rows.map((t) => t.talent_name),
            version: latestVersionResult.rows[0]?.version || "v1.0",
            updatedAt: row.updated_at.getTime(),
          };
        })
      );

      return NextResponse.json(plansWithTalents);
    }
  } catch (error) {
    console.error("Error fetching content plans:", error);
    return NextResponse.json(
      {
        error: "Failed to fetch content plans",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/content-plans
 * Create a new content plan
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      id,
      title,
      campaign,
      brandName,
      conversationId,
      schemaValid = true,
      talents = [],
      version = "v1.0",
      content,
      metadata,
    } = body as {
      id: string;
      title: string;
      campaign?: string;
      brandName?: string;
      conversationId?: string;
      schemaValid?: boolean;
      talents?: string[];
      version?: string;
      content: any;
      metadata?: any;
    };

    if (!id || !title || !content) {
      return NextResponse.json(
        { error: "Plan ID, title, and content are required" },
        { status: 400 }
      );
    }

    // Insert content plan
    await query(
      "INSERT INTO content_plans (id, title, campaign, brand_name, conversation_id, schema_valid) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (id) DO UPDATE SET title = $2, campaign = $3, brand_name = $4, conversation_id = $5, schema_valid = $6, updated_at = CURRENT_TIMESTAMP",
      [id, title, campaign || null, brandName || null, conversationId || null, schemaValid]
    );

    // Insert talents
    if (talents.length > 0) {
      // Delete existing talents
      await query("DELETE FROM plan_talents WHERE plan_id = $1", [id]);
      
      // Insert new talents
      for (const talent of talents) {
        await query(
          "INSERT INTO plan_talents (plan_id, talent_name) VALUES ($1, $2) ON CONFLICT (plan_id, talent_name) DO NOTHING",
          [id, talent]
        );
      }
    }

    // Insert version
    const versionId = `${id}_${version}`;
    await query(
      "INSERT INTO plan_versions (id, plan_id, version, content, metadata) VALUES ($1, $2, $3, $4::jsonb, $5::jsonb) ON CONFLICT (id) DO UPDATE SET content = $4::jsonb, metadata = $5::jsonb",
      [versionId, id, version, JSON.stringify(content), metadata ? JSON.stringify(metadata) : null]
    );

    // Fetch created plan
    const planResult = await query<{
      id: string;
      title: string;
      campaign: string | null;
      brand_name: string | null;
      conversation_id: string | null;
      schema_valid: boolean;
      created_at: Date;
      updated_at: Date;
    }>(
      "SELECT id, title, campaign, brand_name, conversation_id, schema_valid, created_at, updated_at FROM content_plans WHERE id = $1",
      [id]
    );

    const plan = planResult.rows[0];

    // Get talents
    const talentsResult = await query<{
      talent_name: string;
    }>(
      "SELECT talent_name FROM plan_talents WHERE plan_id = $1 ORDER BY talent_name",
      [id]
    );

    // Get versions
    const versionsResult = await query<{
      id: string;
      version: string;
      content: any;
      metadata: any;
      created_at: Date;
    }>(
      "SELECT id, version, content, metadata, created_at FROM plan_versions WHERE plan_id = $1 ORDER BY created_at DESC",
      [id]
    );

    const contentPlan: ContentPlan = {
      id: plan.id,
      title: plan.title,
      campaign: plan.campaign || undefined,
      brandName: plan.brand_name || undefined,
      conversationId: plan.conversation_id || undefined,
      schemaValid: plan.schema_valid,
      talents: talentsResult.rows.map((row) => row.talent_name),
      versions: versionsResult.rows.map((row) => ({
        id: row.id,
        version: row.version,
        content: row.content,
        metadata: row.metadata || undefined,
        createdAt: row.created_at.getTime(),
      })),
      createdAt: plan.created_at.getTime(),
      updatedAt: plan.updated_at.getTime(),
    };

    return NextResponse.json(contentPlan, { status: 201 });
  } catch (error) {
    console.error("Error creating content plan:", error);
    return NextResponse.json(
      {
        error: "Failed to create content plan",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/content-plans
 * Update content plan (title, campaign, brandName, schemaValid, talents)
 * To add a new version, use POST with same plan ID
 */
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      id,
      title,
      campaign,
      brandName,
      schemaValid,
      talents,
    } = body as {
      id: string;
      title?: string;
      campaign?: string;
      brandName?: string;
      schemaValid?: boolean;
      talents?: string[];
    };

    if (!id) {
      return NextResponse.json(
        { error: "Plan ID is required" },
        { status: 400 }
      );
    }

    // Update plan fields
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (title !== undefined) {
      updates.push(`title = $${paramIndex++}`);
      values.push(title);
    }
    if (campaign !== undefined) {
      updates.push(`campaign = $${paramIndex++}`);
      values.push(campaign || null);
    }
    if (brandName !== undefined) {
      updates.push(`brand_name = $${paramIndex++}`);
      values.push(brandName || null);
    }
    if (schemaValid !== undefined) {
      updates.push(`schema_valid = $${paramIndex++}`);
      values.push(schemaValid);
    }

    if (updates.length > 0) {
      values.push(id);
      await query(
        `UPDATE content_plans SET ${updates.join(", ")}, updated_at = CURRENT_TIMESTAMP WHERE id = $${paramIndex}`,
        values
      );
    }

    // Update talents if provided
    if (talents !== undefined) {
      // Delete existing talents
      await query("DELETE FROM plan_talents WHERE plan_id = $1", [id]);
      
      // Insert new talents
      for (const talent of talents) {
        await query(
          "INSERT INTO plan_talents (plan_id, talent_name) VALUES ($1, $2) ON CONFLICT (plan_id, talent_name) DO NOTHING",
          [id, talent]
        );
      }
    }

    // Fetch updated plan
    const planResult = await query<{
      id: string;
      title: string;
      campaign: string | null;
      brand_name: string | null;
      conversation_id: string | null;
      schema_valid: boolean;
      created_at: Date;
      updated_at: Date;
    }>(
      "SELECT id, title, campaign, brand_name, conversation_id, schema_valid, created_at, updated_at FROM content_plans WHERE id = $1",
      [id]
    );

    if (planResult.rows.length === 0) {
      return NextResponse.json(
        { error: "Content plan not found" },
        { status: 404 }
      );
    }

    const plan = planResult.rows[0];

    // Get talents
    const talentsResult = await query<{
      talent_name: string;
    }>(
      "SELECT talent_name FROM plan_talents WHERE plan_id = $1 ORDER BY talent_name",
      [id]
    );

    // Get versions
    const versionsResult = await query<{
      id: string;
      version: string;
      content: any;
      metadata: any;
      created_at: Date;
    }>(
      "SELECT id, version, content, metadata, created_at FROM plan_versions WHERE plan_id = $1 ORDER BY created_at DESC",
      [id]
    );

    const contentPlan: ContentPlan = {
      id: plan.id,
      title: plan.title,
      campaign: plan.campaign || undefined,
      brandName: plan.brand_name || undefined,
      conversationId: plan.conversation_id || undefined,
      schemaValid: plan.schema_valid,
      talents: talentsResult.rows.map((row) => row.talent_name),
      versions: versionsResult.rows.map((row) => ({
        id: row.id,
        version: row.version,
        content: row.content,
        metadata: row.metadata || undefined,
        createdAt: row.created_at.getTime(),
      })),
      createdAt: plan.created_at.getTime(),
      updatedAt: plan.updated_at.getTime(),
    };

    return NextResponse.json(contentPlan);
  } catch (error) {
    console.error("Error updating content plan:", error);
    return NextResponse.json(
      {
        error: "Failed to update content plan",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/content-plans?id=<plan_id>
 * Delete a content plan and all its versions and talents
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const planId = searchParams.get("id");

    if (!planId) {
      return NextResponse.json(
        { error: "Plan ID is required" },
        { status: 400 }
      );
    }

    // Delete plan (versions and talents will be deleted automatically due to CASCADE)
    const result = await query(
      "DELETE FROM content_plans WHERE id = $1 RETURNING id",
      [planId]
    );

    if (result.rows.length === 0) {
      return NextResponse.json(
        { error: "Content plan not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true, id: planId });
  } catch (error) {
    console.error("Error deleting content plan:", error);
    return NextResponse.json(
      {
        error: "Failed to delete content plan",
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
