"use client";

import { useRef, useMemo, useState, createContext, useContext, useCallback, useEffect, useTransition } from "react";
import {
  useLocalRuntime,
  AssistantRuntimeProvider,
  useAuiState,
  type ChatModelAdapter,
  type ChatModelRunOptions,
  type ChatModelRunResult,
} from "@assistant-ui/react";
import {
  getConversation,
  saveConversation,
  createConversation,
  updateConversationMessages,
  type ChatMessage,
  type Conversation,
} from "@/lib/chatHistory";
import { createPlan, type ContentPlan } from "@/lib/contentPlans";
import { createSentimentAnalysis, parseSentimentComposition } from "@/lib/sentimentAnalysis";
import { createTrend } from "@/lib/trends";

/** Context for output language preference (multi-language chat). */
export const OutputLanguageContext = createContext<{
  language: string;
  setLanguage: (value: string) => void;
  options: { value: string; label: string }[];
}>({ language: "", setLanguage: () => {}, options: [] });

export function useOutputLanguage() {
  return useContext(OutputLanguageContext);
}


/** Context for agent progress tracking. */
export interface AgentResult {
  agent: string;
  task: string;
  output?: string;
  timestamp: string;
  startTime?: number; // Unix timestamp in milliseconds
  endTime?: number; // Unix timestamp in milliseconds
  duration?: number; // Duration in milliseconds
}

export const AgentProgressContext = createContext<{
  currentAgent: string | null;
  completedAgents: string[];
  agentResults: AgentResult[];
  setProgress: (agent: string | null) => void;
  addAgentResult: (result: AgentResult) => void;
  resetProgress: () => void;
}>({
  currentAgent: null,
  completedAgents: [],
  agentResults: [],
  setProgress: () => {},
  addAgentResult: () => {},
  resetProgress: () => {},
});

export function useAgentProgress() {
  return useContext(AgentProgressContext);
}

/** Convert markdown formatting: ## menjadi angka berurutan, ** menjadi - */
function stripMarkdownHeadersAndBold(text: string): string {
  if (!text || typeof text !== "string") return text;
  
  let result = text;
  let sectionNumber = 1;
  
  // Replace ## (level 2 heading) dengan angka berurutan (1., 2., 3., dst)
  result = result.replace(/^##\s+(.+)$/gm, (match, content) => {
    const numbered = `${sectionNumber}. ${content}`;
    sectionNumber++;
    return numbered;
  });
  
  // Replace ### (level 3 heading) - hapus saja atau biarkan sebagai sub-section
  result = result.replace(/^###\s+(.+)$/gm, "$1");
  
  // Replace # (level 1 heading) - hapus saja
  result = result.replace(/^#\s+(.+)$/gm, "$1");
  
  // Replace ** dengan - (bold menjadi bullet)
  result = result.replace(/\*\*([^*]+)\*\*/g, "- $1");
  
  return result;
}

/**
 * Extract content plan from crew output and save to database
 */
async function extractAndSaveContentPlan(
  crewData: {
    task_outputs?: Array<{ task?: string; output?: string }>;
    output?: string;
  },
  conversationId: string | null
): Promise<void> {
  try {
    // Find content plan task output (MVP: create_content_plan)
    // Also check for legacy task names for backward compatibility
    const contentPlanTask = crewData.task_outputs?.find(
      (t) => t.task === "create_content_plan" || 
             t.task === "create_content_strategy" ||
             t.task?.includes("content_plan") || 
             t.task?.includes("content_strategy")
    );
    
    if (!contentPlanTask?.output) {
      console.log("No content plan output found, skipping plan extraction");
      return;
    }

    // Extract brand name from user input (from conversation)
    let brandName: string | undefined;
    let campaign: string | undefined;
    let talents: string[] = [];

    if (conversationId) {
      try {
        const conv = await getConversation(conversationId);
        if (conv) {
          // Extract brand name from first user message
          const firstUserMessage = conv.messages.find((m) => m.role === "user");
          if (firstUserMessage) {
            const text = firstUserMessage.content.find((c) => c.type === "text")?.text || "";
            
            // Extract brand name
            const brandMatch = text.match(/-?\s*Brand\s+Name:\s*([^\n\r]+)/i);
            if (brandMatch && brandMatch[1]) {
              brandName = brandMatch[1].trim().split(/[,\-–—]/)[0].trim();
            }
            
            // Extract campaign
            const campaignMatch = text.match(/-?\s*Campaign\s+Type:\s*([^\n\r]+)/i);
            if (campaignMatch && campaignMatch[1]) {
              campaign = campaignMatch[1].trim();
            }
          }
        }
      } catch (err) {
        console.error("Error loading conversation for plan extraction:", err);
      }
    }

    // Extract talents from content plan output
    // Look for patterns like "Talent 1", "Creator 1", etc.
    const talentPatterns = [
      /(?:Talent|Creator|Influencer|KOL)\s+(\d+):\s*([^\n]+)/gi,
      /-?\s*(?:Talent|Creator|Influencer|KOL):\s*([^\n]+)/gi,
    ];
    
    const foundTalents = new Set<string>();
    for (const pattern of talentPatterns) {
      const matches = Array.from(contentPlanTask.output.matchAll(pattern));
      for (const match of matches) {
        const talentName = match[2] || match[1];
        if (talentName) {
          foundTalents.add(talentName.trim());
        }
      }
    }
    talents = Array.from(foundTalents);

    // Generate plan ID
    const planId = `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Extract title from content plan (first heading or first line)
    const titleMatch = contentPlanTask.output.match(/^#+\s*(.+)$/m) || 
                      contentPlanTask.output.match(/^(.+)$/m);
    const title = titleMatch ? titleMatch[1].trim().substring(0, 100) : 
                  (brandName ? `${brandName} Content Plan` : "Content Plan");

    // Create plan
    await createPlan({
      id: planId,
      title,
      campaign,
      brandName,
      conversationId: conversationId || undefined,
      schemaValid: true,
      talents: talents.length > 0 ? talents : [],
      version: "v1.0",
      content: {
        raw: contentPlanTask.output,
        formatted: stripMarkdownHeadersAndBold(contentPlanTask.output),
      },
      metadata: {
        extractedAt: new Date().toISOString(),
        source: "crew_output",
        taskOutputs: crewData.task_outputs?.map((t) => ({
          task: t.task,
          hasOutput: !!t.output,
        })),
      },
    });

    console.log("Content plan saved:", planId);
  } catch (error) {
    console.error("Error extracting and saving content plan:", error);
    // Don't throw - this is a background operation
  }
}

/**
 * Derive a short brand label from the last user message (e.g. first line or "Brand: X").
 */
function deriveBrandFromMessage(message: string | undefined): string | undefined {
  if (!message || typeof message !== "string") return undefined;
  const trimmed = message.trim();
  if (!trimmed) return undefined;
  // Prefer "Brand Name: X" or "Brand: X"
  const m = trimmed.match(/(?:Brand\s+Name|Brand)\s*[:\-]\s*([^\n\r,]+)/i);
  if (m?.[1]?.trim()) return m[1].trim().slice(0, 100);
  // Else use first line or first 50 chars
  const firstLine = trimmed.split(/[\n\r]/)[0]?.trim();
  if (firstLine) return firstLine.slice(0, 80);
  return trimmed.slice(0, 80) || undefined;
}

/**
 * Extract sentiment analysis from crew output (analyze_sentiment task) and save to database.
 * Parses "Sentiment Composition (Pie Chart): Positive X%, Neutral Y%, Negative Z%" for Pie Chart.
 */
async function extractAndSaveSentimentAnalysis(
  crewData: {
    task_outputs?: Array<{ task?: string; output?: string }>;
  },
  conversationId: string | null,
  getBrandNameFromConversation: (convId: string | null) => Promise<string | undefined>,
  lastUserMessage?: string
): Promise<void> {
  try {
    console.log("Extracting sentiment analysis from task_outputs:", crewData.task_outputs?.map(t => ({ task: t.task, hasOutput: !!t.output })));
    
    // Try multiple matching strategies for robustness
    const sentimentTask = crewData.task_outputs?.find(
      (t) => {
        const taskName = (t.task || "").toLowerCase();
        return (
          taskName === "analyze_sentiment" ||
          taskName === "analyze sentiment" ||
          taskName.includes("sentiment") ||
          taskName.includes("analyze_sentiment")
        );
      }
    );
    
    if (!sentimentTask) {
      console.warn("Sentiment task not found. Available tasks:", crewData.task_outputs?.map(t => t.task));
      return;
    }
    
    if (!sentimentTask.output || !sentimentTask.output.trim()) {
      console.warn("Sentiment task found but output is empty:", sentimentTask.task);
      return;
    }

    console.log("Found sentiment task:", sentimentTask.task, "Output length:", sentimentTask.output.length);

    const composition = parseSentimentComposition(sentimentTask.output);
    if (!composition) {
      console.warn("Failed to parse sentiment composition from output. Output preview:", sentimentTask.output.substring(0, 200));
    }
    
    const positivePct = composition?.positivePct ?? 0;
    const neutralPct = composition?.neutralPct ?? 0;
    const negativePct = composition?.negativePct ?? 0;

    let brandName = await getBrandNameFromConversation(conversationId);
    if (!brandName || !brandName.trim()) {
      brandName = deriveBrandFromMessage(lastUserMessage) ?? "Unknown Brand";
    }

    console.log("Saving sentiment analysis for brand:", brandName, { positivePct, neutralPct, negativePct });

    await createSentimentAnalysis({
      brandName: brandName.trim(),
      positivePct,
      negativePct,
      neutralPct,
      fullOutput: sentimentTask.output,
      conversationId: conversationId ?? undefined,
    });
    console.log("✓ Sentiment analysis saved successfully for brand:", brandName);
  } catch (error) {
    console.error("Error extracting and saving sentiment analysis:", error);
    // Re-throw to help with debugging
    throw error;
  }
}

/**
 * Extract trend research from crew output (research_trends task) and save to database.
 */
async function extractAndSaveTrends(
  crewData: {
    task_outputs?: Array<{ task?: string; output?: string }>;
  },
  conversationId: string | null,
  getBrandNameFromConversation: (convId: string | null) => Promise<string | undefined>,
  lastUserMessage?: string
): Promise<void> {
  try {
    console.log("Extracting trends from task_outputs:", crewData.task_outputs?.map(t => ({ task: t.task, hasOutput: !!t.output })));
    
    // Try multiple matching strategies for robustness
    const trendTask = crewData.task_outputs?.find(
      (t) => {
        const taskName = (t.task || "").toLowerCase();
        return (
          taskName === "research_trends" ||
          taskName === "research trends" ||
          taskName.includes("trend") ||
          taskName.includes("research_trends")
        );
      }
    );
    
    if (!trendTask) {
      console.warn("Trend task not found. Available tasks:", crewData.task_outputs?.map(t => t.task));
      return;
    }
    
    if (!trendTask.output || !trendTask.output.trim()) {
      console.warn("Trend task found but output is empty:", trendTask.task);
      return;
    }

    console.log("Found trend task:", trendTask.task, "Output length:", trendTask.output.length);

    let brandName = await getBrandNameFromConversation(conversationId);
    if (!brandName || !brandName.trim()) {
      brandName = deriveBrandFromMessage(lastUserMessage) ?? "Unknown Brand";
    }

    console.log("Saving trend analysis for brand:", brandName);

    await createTrend({
      brandName: brandName.trim(),
      fullOutput: trendTask.output,
      conversationId: conversationId ?? undefined,
    });
    console.log("✓ Trend analysis saved successfully for brand:", brandName);
  } catch (error) {
    console.error("Error extracting and saving trend analysis:", error);
    // Re-throw to help with debugging
    throw error;
  }
}

// MVP: 3 core agents per PRD §3 and SAD §2
const AGENT_ORDER = [
  "Content Planner",
  "Sentiment Analyst",
  "Trend Researcher",
];

/** Resolve brand name from conversation (first user message). */
async function getBrandNameFromConversation(conversationId: string | null): Promise<string | undefined> {
  if (!conversationId) return undefined;
  try {
    const conv = await getConversation(conversationId);
    const firstUser = conv?.messages?.find((m) => m.role === "user");
    const text = firstUser?.content?.find((c: { type: string }) => c.type === "text")?.text ?? "";
    const m = text.match(/-?\s*Brand\s+Name:\s*([^\n\r]+)/i);
    return m?.[1]?.trim()?.split(/[,\-–—]/)[0]?.trim();
  } catch {
    return undefined;
  }
}

/** Chat model adapter: wires assistant-ui chat to backend CrewAI API (POST /api/crew). */
function createCrewAdapter(
  getLanguage: () => string,
  setCurrentAgent: (agent: string | null) => void,
  setCompletedAgents: (agents: string[] | ((prev: string[]) => string[])) => void,
  addAgentResult: (result: AgentResult) => void,
  setAgentStartTime: (agent: string) => void,
  getAgentStartTime: (agent: string) => number | undefined,
  getConversationId: () => string | null
): ChatModelAdapter {
  return {
    async run(options: ChatModelRunOptions): Promise<ChatModelRunResult> {
      const { messages, abortSignal } = options;
      const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
      const text = lastUserMessage?.content?.find((c) => c.type === "text");
      const message = typeof text === "object" && text && "text" in text ? String(text.text) : "";

      if (abortSignal.aborted) {
        setCurrentAgent(null);
        setCompletedAgents([]);
        return { content: [], status: { type: "incomplete" as const, reason: "cancelled" as const } };
      }

      // Reset progress for new run
      setCompletedAgents([]);
      // Set first agent as current (Content Planner)
      const firstAgent = AGENT_ORDER[0] || null;
      setCurrentAgent(firstAgent);
      if (firstAgent) {
        setAgentStartTime(firstAgent);
      }
      // Note: agentResults are kept to show final results
      console.log('Starting crew run, first agent:', firstAgent);

      // Validate message before sending
      if (!message || message.trim().length === 0) {
        setCurrentAgent(null);
        setCompletedAgents([]);
        return {
          content: [{ type: "text" as const, text: "Error: Message cannot be empty. Please enter a message." }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }

      const language = getLanguage();
      const body: Record<string, string> = { message: message.trim() };
      if (language) body.language = language;

      try {
      const res = await fetch("/api/crew", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: abortSignal,
      });
      
      // Parse response data
      let data: Record<string, unknown>;
      try {
        data = await res.json();
      } catch (parseError) {
        // If JSON parsing fails, try to get text response
        const text = await res.text();
        setCurrentAgent(null);
        setCompletedAgents([]);
        return {
          content: [{ type: "text" as const, text: `Error: Failed to parse response. ${res.statusText || text.slice(0, 200)}` }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }
      
      console.log('Crew API response:', {
        status: data.status,
        hasProgress: Array.isArray(data.progress),
        progressCount: Array.isArray(data.progress) ? data.progress.length : 0,
        hasTaskOutputs: Array.isArray(data.task_outputs),
        taskOutputsCount: Array.isArray(data.task_outputs) ? data.task_outputs.length : 0,
      });
      
      // Handle HTTP errors
      if (!res.ok) {
        setCurrentAgent(null);
        setCompletedAgents([]);
        const errorMessage = (data.error as string) || (data.message as string) || res.statusText || `HTTP ${res.status}`;
        return {
          content: [{ type: "text" as const, text: `Error: ${errorMessage}` }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }

      // Handle crew execution errors
      if (data.status === "error") {
        setCurrentAgent(null);
        setCompletedAgents([]);
        const errorMessage = (data.error as string) || "Unknown error occurred";
        return {
          content: [{ type: "text" as const, text: `Crew error: ${errorMessage}` }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }

      // Update progress based on response
      // Progress updates come from step_callback in run.py via stderr JSON lines
      if (Array.isArray(data.progress) && data.progress.length > 0) {
        const progressArray = data.progress as Array<{ agent: string; task: string; timestamp: string; output?: string }>;
        
        // Debug: log all progress updates
        console.log('Progress updates received:', progressArray);
        console.log('Unique agents from progress:', Array.from(new Set(progressArray.map((p) => p.agent))));
        
        // Process each progress update individually to track each agent
        progressArray.forEach((p) => {
          const agentName = p.agent;
          
          // Track when agent starts (if not already tracked)
          if (!getAgentStartTime(agentName)) {
            setAgentStartTime(agentName);
          }
          
          // Add agent result - mark as completed when progress is received
          const startTime = getAgentStartTime(agentName);
          const endTime = Date.now();
          
          // Format output dengan nomor urut untuk setiap agent (reset nomor untuk setiap agent)
          const agentOutput = p.output || "";
          const formattedOutput = stripMarkdownHeadersAndBold(agentOutput);
          
          addAgentResult({
            agent: agentName,
            task: p.task,
            output: formattedOutput,
            timestamp: p.timestamp,
            startTime: startTime,
            endTime: endTime,
            duration: startTime ? endTime - startTime : undefined,
          });
        });
        
        // Update completed agents list - get unique agents from progress array
        const uniqueAgents = Array.from(new Set(progressArray.map((p) => p.agent)));
        
        // Update completed agents and determine current agent
        setCompletedAgents((prevCompleted) => {
          const merged = Array.from(new Set([...prevCompleted, ...uniqueAgents]));
          
          // Find the highest index agent that has completed
          let maxCompletedIndex = -1;
          merged.forEach((agent) => {
            const index = AGENT_ORDER.indexOf(agent);
            if (index > maxCompletedIndex) {
              maxCompletedIndex = index;
            }
          });
          
          // Set current agent to the next one after the last completed
          // Use setTimeout to avoid state update during render
          setTimeout(() => {
            if (maxCompletedIndex >= 0 && maxCompletedIndex < AGENT_ORDER.length - 1) {
              const nextAgent = AGENT_ORDER[maxCompletedIndex + 1];
              setCurrentAgent(nextAgent);
              if (!getAgentStartTime(nextAgent)) {
                setAgentStartTime(nextAgent);
              }
            } else if (maxCompletedIndex === AGENT_ORDER.length - 1) {
              // All agents completed
              setCurrentAgent(null);
            }
          }, 0);
          
          return merged;
        });
      } else {
        // If no progress array, try to infer from task_outputs
        // This handles cases where progress updates are not sent but task_outputs are available
        console.log('No progress array, checking task_outputs...');
      }
      
      // Also check task_outputs for agent results
      // Map task names to agent names based on MVP task configuration (3 tasks)
      const taskToAgentMap: Record<string, string> = {
        "create_content_plan": "Content Planner",
        "analyze_sentiment": "Sentiment Analyst",
        "research_trends": "Trend Researcher",
      };
      
      // Process task_outputs to ensure all agents are tracked (fallback if progress array is empty)
      if (Array.isArray(data.task_outputs) && data.task_outputs.length > 0) {
        const agentsFromTasks: string[] = [];
        
        console.log('Processing task_outputs:', data.task_outputs);
        
        data.task_outputs.forEach((taskOutput: { task?: string; agent?: string; output?: string }) => {
          const taskName = taskOutput.task || "";
          const agentName = taskOutput.agent || taskToAgentMap[taskName] || "";
          
          console.log(`Task: ${taskName}, Mapped Agent: ${agentName}`);
          
          if (agentName && AGENT_ORDER.includes(agentName)) {
            agentsFromTasks.push(agentName);
            
            // Track start time if not already tracked
            if (!getAgentStartTime(agentName)) {
              setAgentStartTime(agentName);
            }
            
            // Mark agent as completed if we have output
            setCompletedAgents((prev) => {
              if (!prev.includes(agentName)) {
                console.log(`Marking ${agentName} as completed from task_outputs`);
                return [...prev, agentName];
              }
              return prev;
            });
            
            const startTime = getAgentStartTime(agentName);
            const endTime = Date.now();
            
            // Format output dengan nomor urut untuk setiap agent (reset nomor untuk setiap agent)
            const agentOutput = typeof taskOutput.output === 'string' ? taskOutput.output : JSON.stringify(taskOutput.output);
            const formattedOutput = stripMarkdownHeadersAndBold(agentOutput);
            
            addAgentResult({
              agent: agentName,
              task: taskName,
              output: formattedOutput,
              timestamp: new Date().toISOString(),
              startTime: startTime,
              endTime: endTime,
              duration: startTime ? endTime - startTime : undefined,
            });
          }
        });
        
        console.log('Agents from tasks:', agentsFromTasks);
        
        // Update current agent based on task outputs
        if (agentsFromTasks.length > 0) {
          let maxCompletedIndex = -1;
          agentsFromTasks.forEach((agent) => {
            const index = AGENT_ORDER.indexOf(agent);
            if (index > maxCompletedIndex) {
              maxCompletedIndex = index;
            }
          });
          
          console.log('Max completed index from tasks:', maxCompletedIndex);
          
          setTimeout(() => {
            if (maxCompletedIndex >= 0 && maxCompletedIndex < AGENT_ORDER.length - 1) {
              const nextAgent = AGENT_ORDER[maxCompletedIndex + 1];
              console.log('Setting next agent from tasks:', nextAgent);
              setCurrentAgent(nextAgent);
              if (!getAgentStartTime(nextAgent)) {
                setAgentStartTime(nextAgent);
              }
            } else if (maxCompletedIndex === AGENT_ORDER.length - 1) {
              console.log('All agents completed from tasks');
              setCurrentAgent(null);
            }
          }, 0);
        }
      }

      // Error handling already done above, continue with output processing

      // Ensure we always show something: main output or task_outputs fallback
      let outText: string;
      const output = data.output;
      if (output != null && String(output).trim() !== "") {
        outText = typeof output === "string" ? output : JSON.stringify(output, null, 2);
      } else if (Array.isArray(data.task_outputs) && data.task_outputs.length > 0) {
        // Format setiap task output dengan nomor urut terpisah untuk setiap task
        outText = data.task_outputs
          .map((t: { task?: string; output?: string }) => {
            const taskOutput = t.output ?? "";
            // Format output dengan nomor urut untuk setiap task (reset nomor untuk setiap task)
            const formattedTaskOutput = stripMarkdownHeadersAndBold(taskOutput);
            return `**${t.task ?? "Task"}**\n${formattedTaskOutput}`;
          })
          .join("\n\n---\n\n");
      } else {
        outText = "Crew finished with no text output. Check .env (OPENROUTER_API_KEY or OPENAI_API_KEY) and logs at project-context/2.build/logs/trace.log.";
      }
      // Format output utama juga dengan nomor urut
      outText = stripMarkdownHeadersAndBold(outText);
      
      // Save content plan, sentiment analysis, and trends to database when crew completes
      const convId = getConversationId();
      if (data.status === "complete" && Array.isArray(data.task_outputs) && data.task_outputs.length > 0) {
        console.log("Crew completed. Saving results to database. Task outputs:", data.task_outputs.map(t => ({ task: t.task, outputLength: t.output?.length || 0 })));
        
        // Save all three types of results with better error handling
        Promise.allSettled([
          extractAndSaveContentPlan(data, convId),
          extractAndSaveSentimentAnalysis(data, convId, getBrandNameFromConversation, message),
          extractAndSaveTrends(data, convId, getBrandNameFromConversation, message),
        ]).then((results) => {
          results.forEach((result, index) => {
            const taskNames = ["content plan", "sentiment analysis", "trends"];
            if (result.status === "rejected") {
              console.error(`Failed to save ${taskNames[index]}:`, result.reason);
            } else {
              console.log(`✓ Successfully saved ${taskNames[index]}`);
            }
          });
        });
      } else {
        console.warn("Crew completed but no task_outputs found or status not complete:", { status: data.status, hasTaskOutputs: Array.isArray(data.task_outputs) && data.task_outputs.length > 0 });
      }
      
      // Reset progress on completion (but keep results)
      // Mark all agents as completed when crew finishes
      setCompletedAgents((prev) => {
        // Merge with all agents to ensure all are marked as completed
        const allAgents = Array.from(new Set([...prev, ...AGENT_ORDER]));
        return allAgents;
      });
      setCurrentAgent(null);
      
      return {
        content: [{ type: "text" as const, text: outText }],
        status: { type: "complete" as const, reason: "stop" as const },
      };
    } catch (err) {
      // Check if error is due to abort signal
      if (err instanceof Error && err.name === "AbortError") {
        console.log("Request aborted by user");
        setCurrentAgent(null);
        setCompletedAgents([]);
        return { content: [], status: { type: "incomplete" as const, reason: "cancelled" as const } };
      }
      
      // Handle network errors
      if (err instanceof TypeError && err.message.includes("fetch")) {
        setCurrentAgent(null);
        setCompletedAgents([]);
        return {
          content: [{ type: "text" as const, text: "Error: Network error. Please check your internet connection and try again." }],
          status: { type: "complete" as const, reason: "stop" as const },
        };
      }
      
      // Handle other errors
      const msg = err instanceof Error ? err.message : "Request failed";
      console.error("Chat error:", err);
      setCurrentAgent(null);
      setCompletedAgents([]);
      return {
        content: [{ type: "text" as const, text: `Error: ${msg}` }],
        status: { type: "complete" as const, reason: "stop" as const },
      };
    }
  },
  };
}

const OUTPUT_LANGUAGE_OPTIONS = [
  { value: "", label: "Same as message" },
  { value: "Bahasa Indonesia", label: "Bahasa Indonesia" },
  { value: "English", label: "English" },
  { value: "日本語", label: "日本語" },
  { value: "中文", label: "中文" },
  { value: "Español", label: "Español" },
  { value: "Français", label: "Français" },
];

export function ChatRuntimeProvider({ children }: { children: React.ReactNode }) {
  const [outputLanguage, setOutputLanguage] = useState("English");
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [completedAgents, setCompletedAgents] = useState<string[]>([]);
  const [agentResults, setAgentResults] = useState<AgentResult[]>([]);
  const agentStartTimes = useRef<Map<string, number>>(new Map());
  const languageRef = useRef(outputLanguage);
  const conversationIdRef = useRef<string | null>(null);

  languageRef.current = outputLanguage;

  const getAgentStartTime = useCallback((agent: string): number | undefined => {
    return agentStartTimes.current.get(agent);
  }, []);

  const addAgentResult = useCallback((result: AgentResult) => {
    setAgentResults((prev) => {
      // Update existing result or add new one
      const existingIndex = prev.findIndex(
        (r) => r.agent === result.agent && r.task === result.task
      );
      
      // Calculate duration if start time exists
      let finalResult = { ...result };
      if (result.startTime && result.endTime) {
        finalResult.duration = result.endTime - result.startTime;
      } else {
        const startTime = agentStartTimes.current.get(result.agent);
        if (startTime) {
          const endTime = Date.now();
          finalResult.startTime = startTime;
          finalResult.endTime = endTime;
          finalResult.duration = endTime - startTime;
          // Don't delete - keep for reference
        }
      }
      
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = finalResult;
        return updated;
      }
      return [...prev, finalResult];
    });
  }, []);
  
  const setAgentStartTime = useCallback((agent: string) => {
    agentStartTimes.current.set(agent, Date.now());
  }, []);

  const crewAdapter = useMemo(
    () => createCrewAdapter(
      () => languageRef.current, 
      setCurrentAgent, 
      setCompletedAgents,
      addAgentResult,
      setAgentStartTime,
      getAgentStartTime,
      () => conversationIdRef.current
    ),
    [addAgentResult, setAgentStartTime, getAgentStartTime]
  );

  const initialMessages = useMemo(() => [
    {
      id: "welcome",
      role: "assistant" as const,
      content: [
        {
          type: "text" as const,
          text: "Welcome to BAGANA AI. I'll help you create multi-talent content plans with sentiment analysis and trend insights. Share your campaign context or a brief to get started.",
        },
      ],
    },
  ], []);

  const runtime = useLocalRuntime(crewAdapter, {
    initialMessages,
  });

  const languageContextValue = useMemo(
    () => ({
      language: outputLanguage,
      setLanguage: setOutputLanguage,
      options: OUTPUT_LANGUAGE_OPTIONS,
    }),
    [outputLanguage]
  );

  const progressContextValue = useMemo(
    () => ({
      currentAgent,
      completedAgents,
      agentResults,
      setProgress: setCurrentAgent,
      addAgentResult,
      resetProgress: () => {
        setCurrentAgent(null);
        setCompletedAgents([]);
        setAgentResults([]);
      },
    }),
    [currentAgent, completedAgents, agentResults, addAgentResult]
  );

  return (
    <OutputLanguageContext.Provider value={languageContextValue}>
      <AgentProgressContext.Provider value={progressContextValue}>
        <AssistantRuntimeProvider runtime={runtime}>
          {children}
        </AssistantRuntimeProvider>
      </AgentProgressContext.Provider>
    </OutputLanguageContext.Provider>
  );
}
