/**
 * Content Plans Management
 * 
 * Manages content plans using PostgreSQL database via API.
 * Each plan has:
 * - id: unique identifier
 * - title: plan title
 * - campaign: campaign name
 * - brandName: brand name
 * - conversationId: linked conversation ID (optional)
 * - schemaValid: whether plan passes schema validation
 * - talents: array of talent names
 * - versions: array of plan versions
 * - createdAt: timestamp
 * - updatedAt: timestamp
 * 
 * Falls back to localStorage if API is unavailable (for offline/development).
 */

const STORAGE_KEY = "bagana_content_plans";
const API_BASE = "/api/content-plans";

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

export interface ContentPlanSummary {
  id: string;
  title: string;
  campaign?: string;
  brandName?: string;
  schemaValid: boolean;
  talents: string[];
  version: string;
  updatedAt: number;
}

/**
 * Generate a unique plan ID
 */
function generatePlanId(): string {
  return `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get all plans from localStorage (synchronous fallback)
 */
function getAllPlansFromStorage(): ContentPlanSummary[] {
  if (typeof window === "undefined") return [];
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const plans: ContentPlanSummary[] = JSON.parse(stored);
    // Sort by updatedAt descending (most recent first)
    return plans.sort((a, b) => b.updatedAt - a.updatedAt);
  } catch (error) {
    console.error("Error loading plans:", error);
    return [];
  }
}

/**
 * Get all content plans from PostgreSQL via API
 * Falls back to localStorage if API fails
 */
export async function getAllPlans(): Promise<ContentPlanSummary[]> {
  if (typeof window === "undefined") return [];
  
  try {
    const response = await fetch(API_BASE);
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    
    const plans = await response.json() as ContentPlanSummary[];
    return plans;
  } catch (error) {
    console.warn("Failed to fetch plans from API, falling back to localStorage:", error);
    // Fallback to localStorage
    return getAllPlansFromStorage();
  }
}

/**
 * Get a specific plan by ID from PostgreSQL via API
 * Falls back to localStorage if API fails
 */
export async function getPlan(id: string): Promise<ContentPlan | null> {
  if (typeof window === "undefined") return null;
  
  try {
    const response = await fetch(`${API_BASE}?id=${encodeURIComponent(id)}`);
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`API returned ${response.status}`);
    }
    
    const plan = await response.json() as ContentPlan;
    return plan;
  } catch (error) {
    console.warn("Failed to fetch plan from API, falling back to localStorage:", error);
    // Fallback to localStorage
    try {
      const plans = getAllPlansFromStorage();
      const found = plans.find((p) => p.id === id);
      if (!found) return null;
      
      // Return as ContentPlan (with empty versions array for localStorage fallback)
      return {
        ...found,
        conversationId: undefined,
        versions: [],
        createdAt: found.updatedAt,
      };
    } catch (localError) {
      console.error("Error loading plan from localStorage:", localError);
      return null;
    }
  }
}

/**
 * Create a new content plan
 */
export async function createPlan(
  data: {
    id?: string;
    title: string;
    campaign?: string;
    brandName?: string;
    conversationId?: string;
    schemaValid?: boolean;
    talents?: string[];
    version?: string;
    content: any;
    metadata?: any;
  }
): Promise<ContentPlan> {
  const id = data.id || generatePlanId();
  const planData = {
    id,
    title: data.title,
    campaign: data.campaign,
    brandName: data.brandName,
    conversationId: data.conversationId,
    schemaValid: data.schemaValid ?? true,
    talents: data.talents || [],
    version: data.version || "v1.0",
    content: data.content,
    metadata: data.metadata,
  };
  
  try {
    const response = await fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(planData),
    });
    
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    
    const plan = await response.json() as ContentPlan;
    return plan;
  } catch (error) {
    console.warn("Failed to create plan via API, falling back to localStorage:", error);
    // Fallback to localStorage
    try {
      const now = Date.now();
      const plan: ContentPlan = {
        id,
        title: planData.title,
        campaign: planData.campaign,
        brandName: planData.brandName,
        conversationId: planData.conversationId,
        schemaValid: planData.schemaValid,
        talents: planData.talents,
        versions: [
          {
            id: `${id}_${planData.version}`,
            version: planData.version,
            content: planData.content,
            metadata: planData.metadata,
            createdAt: now,
          },
        ],
        createdAt: now,
        updatedAt: now,
      };
      
      const plans = getAllPlansFromStorage();
      const summary: ContentPlanSummary = {
        id: plan.id,
        title: plan.title,
        campaign: plan.campaign,
        brandName: plan.brandName,
        schemaValid: plan.schemaValid,
        talents: plan.talents,
        version: planData.version,
        updatedAt: now,
      };
      
      const existingIndex = plans.findIndex((p) => p.id === id);
      if (existingIndex >= 0) {
        plans[existingIndex] = summary;
      } else {
        plans.unshift(summary);
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(plans));
      return plan;
    } catch (localError) {
      console.error("Error saving plan to localStorage:", localError);
      throw localError;
    }
  }
}

/**
 * Update a content plan
 */
export async function updatePlan(
  id: string,
  data: {
    title?: string;
    campaign?: string;
    brandName?: string;
    schemaValid?: boolean;
    talents?: string[];
  }
): Promise<ContentPlan | null> {
  try {
    const response = await fetch(API_BASE, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, ...data }),
    });
    
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`API returned ${response.status}`);
    }
    
    const plan = await response.json() as ContentPlan;
    return plan;
  } catch (error) {
    console.warn("Failed to update plan via API, falling back to localStorage:", error);
    // Fallback to localStorage
    try {
      const plans = getAllPlansFromStorage();
      const existingIndex = plans.findIndex((p) => p.id === id);
      if (existingIndex < 0) return null;
      
      const updated = {
        ...plans[existingIndex],
        ...data,
        updatedAt: Date.now(),
      };
      
      plans[existingIndex] = updated;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(plans));
      
      // Return as ContentPlan
      return {
        ...updated,
        conversationId: undefined,
        versions: [],
        createdAt: updated.updatedAt,
      };
    } catch (localError) {
      console.error("Error updating plan in localStorage:", localError);
      return null;
    }
  }
}

/**
 * Add a new version to an existing plan
 */
export async function addPlanVersion(
  planId: string,
  version: string,
  content: any,
  metadata?: any
): Promise<ContentPlan | null> {
  try {
    // Get existing plan
    const existingPlan = await getPlan(planId);
    if (!existingPlan) return null;
    
    // Create new version by creating a new plan with same ID but new version
    const response = await fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: planId,
        title: existingPlan.title,
        campaign: existingPlan.campaign,
        brandName: existingPlan.brandName,
        conversationId: existingPlan.conversationId,
        schemaValid: existingPlan.schemaValid,
        talents: existingPlan.talents,
        version,
        content,
        metadata,
      }),
    });
    
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    
    const plan = await response.json() as ContentPlan;
    return plan;
  } catch (error) {
    console.error("Error adding plan version:", error);
    return null;
  }
}

/**
 * Delete a content plan
 */
export async function deletePlan(id: string): Promise<void> {
  if (typeof window === "undefined") return;
  
  try {
    const response = await fetch(`${API_BASE}?id=${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
    
    if (!response.ok && response.status !== 404) {
      throw new Error(`API returned ${response.status}`);
    }
    
    return;
  } catch (error) {
    console.warn("Failed to delete plan from API, falling back to localStorage:", error);
    // Fallback to localStorage
    try {
      const plans = getAllPlansFromStorage();
      const filtered = plans.filter((p) => p.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    } catch (localError) {
      console.error("Error deleting plan from localStorage:", localError);
    }
  }
}
