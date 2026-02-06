"""
Example: Flow-Level Human Feedback Decorator Usage
Demonstrates how to use @human_feedback decorator with CrewAI crews.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import Agent, Task, Crew
from human_feedback_decorator import human_feedback, FeedbackAction


def build_example_crew():
    """Build a simple example crew."""
    agent = Agent(
        role="Content Planner",
        goal="Create content plans",
        backstory="You are an expert content strategist.",
        verbose=True,
    )
    
    task1 = Task(
        description="Create a content plan for a summer campaign",
        agent=agent,
        expected_output="A content plan document",
    )
    
    task2 = Task(
        description="Refine the content plan based on feedback",
        agent=agent,
        expected_output="Refined content plan",
        context=[task1],
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task1, task2],
        verbose=True,
    )
    
    return crew


# Example 1: Single checkpoint after planning phase
@human_feedback(
    checkpoint="after_planning",
    description="Review the content plan before proceeding to refinement"
)
def execute_planning_phase(inputs: dict):
    """Execute planning phase with feedback checkpoint."""
    crew = build_example_crew()
    # Simulate planning phase (first task only)
    # In real usage, you'd execute specific tasks or phases
    result = crew.kickoff(inputs=inputs)
    return result


# Example 2: Checkpoint with condition
def should_review_plan(context: dict) -> bool:
    """Condition: only review if plan is complex."""
    # Example condition logic
    user_input = context.get("user_input", "")
    return len(user_input) > 100  # Review if input is long/complex


@human_feedback(
    checkpoint="conditional_review",
    description="Review complex plans",
    condition=should_review_plan
)
def execute_conditional_flow(inputs: dict):
    """Execute flow with conditional checkpoint."""
    crew = build_example_crew()
    result = crew.kickoff(inputs=inputs)
    return result


# Example 3: Checkpoint with custom context extraction
def extract_plan_context(result) -> dict:
    """Extract relevant context from crew result."""
    context = {}
    if isinstance(result, dict):
        context["status"] = result.get("status", "unknown")
        context["output_length"] = len(str(result.get("output", "")))
    elif hasattr(result, "raw"):
        context["output_preview"] = str(result.raw)[:300]
    return context


@human_feedback(
    checkpoint="before_finalization",
    description="Final review before completing the workflow",
    context_extractor=extract_plan_context
)
def execute_with_context_extraction(inputs: dict):
    """Execute flow with custom context extraction."""
    crew = build_example_crew()
    result = crew.kickoff(inputs=inputs)
    return result


# Example 4: Multi-stage flow with multiple checkpoints
def stage1_planning(inputs: dict):
    """Stage 1: Planning."""
    crew = build_example_crew()
    # Execute only planning tasks
    result = crew.kickoff(inputs=inputs)
    return result


@human_feedback(checkpoint="after_stage1", description="Review planning results")
def execute_stage1(inputs: dict):
    """Execute stage 1 with checkpoint."""
    return stage1_planning(inputs)


def stage2_refinement(inputs: dict, plan_result: dict):
    """Stage 2: Refinement based on plan."""
    crew = build_example_crew()
    # In real usage, you'd pass plan_result as context
    result = crew.kickoff(inputs=inputs)
    return result


@human_feedback(checkpoint="after_stage2", description="Review refinement results")
def execute_stage2(inputs: dict, plan_result: dict):
    """Execute stage 2 with checkpoint."""
    return stage2_refinement(inputs, plan_result)


def execute_multi_stage_flow(inputs: dict):
    """Execute multi-stage flow with checkpoints."""
    # Stage 1
    stage1_result = execute_stage1(inputs)
    
    # Check if stopped
    if isinstance(stage1_result, dict) and stage1_result.get("_stopped"):
        return stage1_result
    
    # Stage 2
    stage2_result = execute_stage2(inputs, stage1_result)
    
    return {
        "stage1": stage1_result,
        "stage2": stage2_result,
        "status": "complete"
    }


def main():
    """Run examples."""
    print("="*80)
    print("Flow-Level Human Feedback Decorator Examples")
    print("="*80)
    
    inputs = {
        "user_input": "Create a content plan for a summer campaign promoting eco-friendly products",
        "output_language": "English"
    }
    
    print("\n1. Single Checkpoint Example")
    print("-"*80)
    try:
        result = execute_planning_phase(inputs)
        print(f"\nResult: {result}")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n\n2. Conditional Checkpoint Example")
    print("-"*80)
    print("(Skipping - requires user interaction)")
    
    print("\n\n3. Multi-Stage Flow Example")
    print("-"*80)
    print("(Skipping - requires multiple user interactions)")
    
    print("\n" + "="*80)
    print("Examples complete!")
    print("="*80)


if __name__ == "__main__":
    main()
