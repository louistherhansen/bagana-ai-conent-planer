"""
Integration Guide: Adding Human Input to Existing Crew
Shows how to modify crew/run.py to support human_input from YAML config.
"""

# This file shows the code changes needed in crew/run.py

# ============================================================================
# STEP 1: Update _build_task function to read human_input from YAML
# ============================================================================

# In crew/run.py, modify _build_task function:

"""
def _build_task(
    task_id: str,
    config: dict,
    agents: dict[str, Agent],
    task_refs: dict[str, Task],
) -> Task:
    # ... existing code ...
    
    params = {k: v for k, v in config.items() if k in TASK_PARAMS}
    params["agent"] = agent
    params.pop("context_from", None)
    
    # ADD THIS: Handle human_input from YAML config
    human_input = config.get("human_input", False)
    if isinstance(human_input, str):
        # Handle string "true"/"false" from YAML
        human_input = human_input.lower() in ("true", "yes", "1")
    params["human_input"] = bool(human_input)
    
    # ... rest of existing code ...
    
    return Task(**params)
"""

# ============================================================================
# STEP 2: Update TASK_PARAMS to include human_input
# ============================================================================

# In crew/run.py, update the TASK_PARAMS list:

"""
TASK_PARAMS = [
    "description",
    "expected_output",
    "agent",
    "context",
    "tools",
    "async_execution",
    "output_file",
    "output_json",
    "output_pydantic",
    "human_input",  # ADD THIS
    # ... other params ...
]
"""

# ============================================================================
# STEP 3: Create Human Input Handler Function
# ============================================================================

"""
def handle_human_input(task_output: TaskOutput, task_id: str) -> str:
    '''
    Handle human input for task approval.
    Called automatically by CrewAI when a task with human_input=True completes.
    
    Args:
        task_output: The TaskOutput object containing task results
        task_id: The ID of the task requiring approval
        
    Returns:
        "CONTINUE" to proceed, "STOP" to halt, or custom feedback string
    '''
    import sys
    
    print("\n" + "="*80, file=sys.stderr)
    print(f"🔍 TASK REQUIRES HUMAN APPROVAL: {task_id}", file=sys.stderr)
    print("="*80, file=sys.stderr)
    
    # Display task output summary
    if hasattr(task_output, 'raw') and task_output.raw:
        output_preview = str(task_output.raw)[:500]
        print(f"\n📋 Task Output Preview:\n{output_preview}...", file=sys.stderr)
    
    if hasattr(task_output, 'output') and task_output.output:
        output_preview = str(task_output.output)[:500]
        print(f"\n📄 Task Result:\n{output_preview}...", file=sys.stderr)
    
    print("\n" + "-"*80, file=sys.stderr)
    print("Options:", file=sys.stderr)
    print("  [y/yes] - Approve and continue", file=sys.stderr)
    print("  [n/no]  - Reject and stop", file=sys.stderr)
    print("  [e/edit] - Provide feedback (crew will revise)", file=sys.stderr)
    print("-"*80, file=sys.stderr)
    
    while True:
        response = input("\n👉 Your decision: ").strip().lower()
        
        if response in ['y', 'yes']:
            print("✅ Approved! Continuing to next task...\n", file=sys.stderr)
            return "CONTINUE"
        elif response in ['n', 'no']:
            print("❌ Rejected! Stopping crew execution...\n", file=sys.stderr)
            return "STOP"
        elif response in ['e', 'edit']:
            feedback = input("📝 Enter your feedback: ").strip()
            if feedback:
                print(f"📝 Feedback received: {feedback}\n", file=sys.stderr)
                return feedback
            else:
                print("⚠️  Empty feedback. Please try again.", file=sys.stderr)
        else:
            print("⚠️  Invalid input. Please enter 'y', 'n', or 'e'.", file=sys.stderr)
"""

# ============================================================================
# STEP 4: Register Handler with Crew (if using custom handler)
# ============================================================================

# CrewAI automatically calls human_input handler when human_input=True
# The handler function signature should match what CrewAI expects
# For custom handlers, you may need to set it on the Task:

"""
task = Task(
    ...,
    human_input=True,
    # CrewAI will automatically prompt for input
    # Custom handlers can be registered via crew configuration
)
"""

# ============================================================================
# NOTES:
# ============================================================================
# 1. CrewAI's built-in human_input=True automatically prompts via stdin
# 2. The default behavior is to pause and wait for user input
# 3. User can type feedback which becomes part of the task context
# 4. To stop execution, user can send interrupt signal (Ctrl+C)
# 5. For production, consider webhook-based approval instead of console
