"""
Integration Guide: Adding Flow-Level Human Feedback to Existing Crew
Shows how to integrate @human_feedback decorator into crew/run.py and API routes.
"""

# ============================================================================
# STEP 1: Import the decorator in crew/run.py
# ============================================================================

"""
# At the top of crew/run.py, add:

from pathlib import Path
import sys

# Add decorator module to path if needed
DECORATOR_PATH = Path(__file__).parent.parent / "Flow-Level @human_feedback Decorator"
if str(DECORATOR_PATH) not in sys.path:
    sys.path.insert(0, str(DECORATOR_PATH))

from human_feedback_decorator import human_feedback
"""

# ============================================================================
# STEP 2: Wrap kickoff() function with flow-level checkpoints
# ============================================================================

"""
# In crew/run.py, modify the kickoff() function:

@human_feedback(
    checkpoint="before_crew_execution",
    description="Review inputs before starting crew execution"
)
def kickoff(inputs: dict | None = None) -> dict:
    '''
    Run crew.kickoff(inputs). Returns structured result for API/Integration epic.
    Now includes flow-level human feedback checkpoint.
    '''
    inputs = inputs or {}
    if "user_input" not in inputs:
        inputs["user_input"] = inputs.get("message", inputs.get("campaign_context", "No context provided."))
    
    # ... rest of existing kickoff() code ...
    
    crew = build_crew()
    if crew.step_callback is None:
        crew.step_callback = _step_callback

    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        # ... error handling ...
        pass
    
    # ... return result ...
"""

# ============================================================================
# STEP 3: Add checkpoints at specific flow stages
# ============================================================================

"""
# Option A: Wrap specific phases

def execute_planning_phase(inputs: dict) -> dict:
    '''Execute planning tasks only.'''
    crew = build_crew()
    # Filter to planning tasks only
    planning_tasks = [t for t in crew.tasks if "plan" in t.name.lower()]
    planning_crew = Crew(
        agents=crew.agents,
        tasks=planning_tasks,
        verbose=crew.verbose
    )
    return planning_crew.kickoff(inputs=inputs)


@human_feedback(
    checkpoint="after_planning",
    description="Review content plan before proceeding to analysis"
)
def execute_analysis_phase(inputs: dict, plan_result: dict) -> dict:
    '''Execute analysis tasks with plan context.'''
    crew = build_crew()
    # Filter to analysis tasks
    analysis_tasks = [t for t in crew.tasks if "sentiment" in t.name.lower() or "trend" in t.name.lower()]
    analysis_crew = Crew(
        agents=crew.agents,
        tasks=analysis_tasks,
        verbose=crew.verbose
    )
    # Add plan result to inputs
    inputs["plan_context"] = plan_result
    return analysis_crew.kickoff(inputs=inputs)


# Option B: Add checkpoint after specific task completion using step_callback

def _step_callback_with_feedback(step: object) -> None:
    '''Enhanced step callback with optional feedback checkpoint.'''
    # Existing step logging...
    _step_callback(step)
    
    # Check if this step should trigger feedback
    if hasattr(step, "task") and step.task:
        task_name = getattr(step.task, "name", "")
        if task_name == "create_content_plan":
            # Trigger feedback checkpoint
            from human_feedback_decorator import HumanFeedbackHandler
            handler = HumanFeedbackHandler("after_content_plan", "Review content plan")
            context = {"task": task_name, "step": str(step)}
            feedback = handler.prompt_feedback(context)
            
            if feedback["action"].value == "stop":
                # Signal to stop execution
                raise KeyboardInterrupt("Stopped by user feedback")
"""

# ============================================================================
# STEP 4: Integrate with API route (app/api/crew/route.ts)
# ============================================================================

"""
# For API integration, you have two options:

# Option A: Console feedback (works when Python runs directly)
# The decorator will prompt via stdin/stderr

# Option B: Webhook-based feedback (for web UI)
# Modify route.ts to handle feedback requests:

// In app/api/crew/route.ts, add feedback endpoint:

export async function POST(request: NextRequest) {
  // ... existing code ...
  
  // Check if this is a feedback request
  const body = await request.json();
  if (body.feedback_checkpoint) {
    // Store feedback request and return checkpoint info
    return NextResponse.json({
      status: "checkpoint",
      checkpoint: body.feedback_checkpoint,
      message: "Awaiting human feedback"
    });
  }
  
  // ... rest of existing POST handler ...
}

// Add feedback submission endpoint:
export async function PUT(request: NextRequest) {
  const body = await request.json();
  const { checkpoint_id, action, feedback } = body;
  
  // Process feedback and continue/resume execution
  // This requires state management (Redis, DB, or in-memory store)
  
  return NextResponse.json({ status: "feedback_received" });
}
"""

# ============================================================================
# STEP 5: Add to YAML config for declarative checkpoints
# ============================================================================

"""
# Create config/flow_checkpoints.yaml:

flow_checkpoints:
  - checkpoint: "after_planning"
    description: "Review content plan before analysis"
    condition: "always"  # or "complex_plans", "first_run", etc.
    task_filter: ["create_content_plan"]
    
  - checkpoint: "after_analysis"
    description: "Review sentiment and trend analysis"
    condition: "always"
    task_filter: ["analyze_sentiment", "research_trends"]
    
  - checkpoint: "before_finalization"
    description: "Final review before content strategy"
    condition: "always"
    task_filter: ["create_content_strategy"]

# Then load and apply in crew/run.py:

def load_flow_checkpoints() -> list:
    '''Load flow checkpoint config from YAML.'''
    import yaml
    checkpoints_path = Path(__file__).parent.parent / "config" / "flow_checkpoints.yaml"
    with open(checkpoints_path) as f:
        config = yaml.safe_load(f)
    return config.get("flow_checkpoints", [])

def apply_checkpoints_to_kickoff():
    '''Dynamically apply checkpoints based on YAML config.'''
    checkpoints = load_flow_checkpoints()
    # Apply decorators programmatically
    # (Advanced: requires dynamic decoration)
"""

# ============================================================================
# NOTES AND BEST PRACTICES
# ============================================================================

"""
1. **Checkpoint Placement**:
   - Place checkpoints after major phases (planning, analysis, finalization)
   - Avoid too many checkpoints (slows execution)
   - Use conditions to skip checkpoints when not needed

2. **Context Extraction**:
   - Extract relevant context for human review
   - Keep context concise (humans need quick decisions)
   - Include key metrics, summaries, not full outputs

3. **Feedback Handling**:
   - CONTINUE: Proceed normally
   - STOP: Halt execution, return current state
   - REVISE: Add feedback to context for revision
   - SKIP: Continue without checkpoint (for conditional checkpoints)

4. **API Integration**:
   - Console mode: Works directly with decorator
   - Web mode: Requires webhook/state management
   - Consider async execution for web-based feedback

5. **Performance**:
   - Checkpoints add latency (human response time)
   - Use conditions to minimize unnecessary checkpoints
   - Consider async/background execution for long-running flows

6. **Error Handling**:
   - Handle KeyboardInterrupt for STOP action
   - Preserve state on STOP for resumption
   - Log feedback history for audit trail
"""
