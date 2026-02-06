"""
Example: Task-Level Human Input with Simple Console Approval
Demonstrates how to add human approval gates to CrewAI tasks.

This example shows:
1. How to configure tasks with human_input=True
2. How to handle console-based approval prompts
3. How to integrate with existing crew structure
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import crew modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import Agent, Task, Crew
from crewai.tasks import TaskOutput


def create_human_input_handler():
    """
    Create a simple console-based human input handler.
    This function will be called when a task with human_input=True completes.
    """
    def handler(task_output: TaskOutput) -> str:
        """
        Handle human input for task approval.
        
        Args:
            task_output: The TaskOutput object containing task results
            
        Returns:
            "CONTINUE" to proceed, "STOP" to halt, or custom feedback string
        """
        print("\n" + "="*80)
        print(f"🔍 TASK REQUIRES HUMAN APPROVAL: {task_output.task.description[:60]}...")
        print("="*80)
        
        # Display task output summary
        if hasattr(task_output, 'raw') and task_output.raw:
            output_preview = str(task_output.raw)[:500]
            print(f"\n📋 Task Output Preview:\n{output_preview}...")
        
        if hasattr(task_output, 'output') and task_output.output:
            output_preview = str(task_output.output)[:500]
            print(f"\n📄 Task Result:\n{output_preview}...")
        
        print("\n" + "-"*80)
        print("Options:")
        print("  [y/yes] - Approve and continue")
        print("  [n/no]  - Reject and stop")
        print("  [e/edit] - Provide feedback (crew will revise)")
        print("-"*80)
        
        while True:
            response = input("\n👉 Your decision: ").strip().lower()
            
            if response in ['y', 'yes']:
                print("✅ Approved! Continuing to next task...\n")
                return "CONTINUE"
            elif response in ['n', 'no']:
                print("❌ Rejected! Stopping crew execution...\n")
                return "STOP"
            elif response in ['e', 'edit']:
                feedback = input("📝 Enter your feedback: ").strip()
                if feedback:
                    print(f"📝 Feedback received: {feedback}\n")
                    return feedback
                else:
                    print("⚠️  Empty feedback. Please try again.")
            else:
                print("⚠️  Invalid input. Please enter 'y', 'n', or 'e'.")


def build_example_crew_with_human_input():
    """
    Build a crew with tasks that require human approval.
    This demonstrates the pattern for adding human_input gates.
    """
    # Example agent
    reviewer_agent = Agent(
        role="Content Reviewer",
        goal="Review and validate content plans before finalization",
        backstory="You are an experienced content strategist who ensures all plans meet quality standards.",
        verbose=True,
        allow_delegation=False,
    )
    
    # Task WITHOUT human input (runs automatically)
    draft_task = Task(
        description="Create a draft content plan for a summer campaign",
        agent=reviewer_agent,
        expected_output="A draft content plan document",
    )
    
    # Task WITH human input (requires approval)
    review_task = Task(
        description="Review the draft content plan and prepare it for approval",
        agent=reviewer_agent,
        expected_output="A reviewed content plan ready for human approval",
        human_input=True,  # This enables the approval gate
        context=[draft_task],  # Uses output from draft_task
    )
    
    # Task that runs AFTER approval
    finalize_task = Task(
        description="Finalize the approved content plan",
        agent=reviewer_agent,
        expected_output="Final content plan document",
        context=[review_task],  # Uses output from review_task
    )
    
    # Create crew
    crew = Crew(
        agents=[reviewer_agent],
        tasks=[draft_task, review_task, finalize_task],
        verbose=True,
    )
    
    return crew


def run_example():
    """Run the example crew with human input."""
    print("🚀 Starting CrewAI with Human Input Example")
    print("="*80)
    
    crew = build_example_crew_with_human_input()
    
    inputs = {
        "user_input": "Create a content plan for a summer campaign promoting eco-friendly products",
        "output_language": "English"
    }
    
    try:
        result = crew.kickoff(inputs=inputs)
        print("\n" + "="*80)
        print("✅ Crew execution completed!")
        print("="*80)
        print(f"\nFinal output:\n{result}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_example()
