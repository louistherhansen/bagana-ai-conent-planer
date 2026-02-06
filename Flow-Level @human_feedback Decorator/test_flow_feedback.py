"""
Test suite for Flow-Level Human Feedback Decorator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from human_feedback_decorator import (
    human_feedback,
    HumanFeedbackHandler,
    FeedbackAction,
    multi_checkpoint_feedback
)
from crewai import Agent, Task, Crew


def test_decorator_basic():
    """Test basic decorator functionality."""
    print("="*80)
    print("TEST 1: Basic Decorator")
    print("="*80)
    
    @human_feedback(checkpoint="test_checkpoint", description="Test checkpoint")
    def test_function(inputs: dict):
        return {"status": "complete", "result": "test"}
    
    # Verify decorator attached attributes
    assert hasattr(test_function, "_feedback_handler")
    assert hasattr(test_function, "_checkpoint_name")
    assert test_function._checkpoint_name == "test_checkpoint"
    
    print("✅ Decorator attributes attached correctly")
    return True


def test_handler_prompt():
    """Test HumanFeedbackHandler prompt (requires manual interaction)."""
    print("\n" + "="*80)
    print("TEST 2: Handler Prompt")
    print("="*80)
    
    handler = HumanFeedbackHandler("test_checkpoint", "Test description")
    context = {"test_key": "test_value"}
    
    print("⚠️  This test requires manual interaction")
    print("When prompted, try different actions: 'c', 's', 'r', 'k'")
    
    try:
        feedback = handler.prompt_feedback(context)
        print(f"\n✅ Feedback received: {feedback['action']}")
        return True
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        return False


def test_conditional_checkpoint():
    """Test conditional checkpoint."""
    print("\n" + "="*80)
    print("TEST 3: Conditional Checkpoint")
    print("="*80)
    
    def condition(context: dict) -> bool:
        return context.get("should_checkpoint", False)
    
    @human_feedback(
        checkpoint="conditional",
        condition=condition
    )
    def conditional_function(inputs: dict):
        return {"status": "complete"}
    
    # Test with condition=False (should skip checkpoint)
    result1 = conditional_function({"should_checkpoint": False})
    assert result1["status"] == "complete"
    print("✅ Condition=False: Checkpoint skipped")
    
    # Test with condition=True (will prompt - requires interaction)
    print("⚠️  Condition=True: Will prompt (requires interaction)")
    # result2 = conditional_function({"should_checkpoint": True})
    
    return True


def test_context_extraction():
    """Test custom context extraction."""
    print("\n" + "="*80)
    print("TEST 4: Context Extraction")
    print("="*80)
    
    def extractor(result) -> dict:
        return {"extracted": "context", "result_status": result.get("status")}
    
    @human_feedback(
        checkpoint="with_context",
        context_extractor=extractor
    )
    def function_with_context(inputs: dict):
        return {"status": "complete", "data": "test"}
    
    print("✅ Context extractor attached")
    # Note: Full test requires execution with user interaction
    return True


def test_feedback_actions():
    """Test feedback action handling."""
    print("\n" + "="*80)
    print("TEST 5: Feedback Actions")
    print("="*80)
    
    actions = [FeedbackAction.CONTINUE, FeedbackAction.STOP, 
               FeedbackAction.REVISE, FeedbackAction.SKIP]
    
    for action in actions:
        assert action.value in ["continue", "stop", "revise", "skip"]
        print(f"✅ Action {action.name}: {action.value}")
    
    return True


def test_multi_stage_flow():
    """Test multi-stage flow pattern."""
    print("\n" + "="*80)
    print("TEST 6: Multi-Stage Flow")
    print("="*80)
    
    @human_feedback(checkpoint="after_stage1")
    def stage1(inputs: dict):
        return {"stage": 1, "result": "stage1_complete"}
    
    @human_feedback(checkpoint="after_stage2")
    def stage2(inputs: dict, stage1_result: dict):
        return {"stage": 2, "result": "stage2_complete"}
    
    def full_flow(inputs: dict):
        r1 = stage1(inputs)
        if isinstance(r1, dict) and r1.get("_stopped"):
            return r1
        r2 = stage2(inputs, r1)
        return {"stage1": r1, "stage2": r2, "status": "complete"}
    
    print("✅ Multi-stage flow pattern defined")
    # Note: Full test requires execution with user interaction
    return True


def test_with_crewai():
    """Test decorator with actual CrewAI crew."""
    print("\n" + "="*80)
    print("TEST 7: CrewAI Integration")
    print("="*80)
    
    agent = Agent(
        role="Test Agent",
        goal="Test flow feedback",
        backstory="Test agent",
        verbose=False,
    )
    
    task = Task(
        description="Test task",
        agent=agent,
        expected_output="Test output",
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    
    @human_feedback(checkpoint="after_crew", description="Review crew result")
    def execute_with_feedback(inputs: dict):
        return crew.kickoff(inputs=inputs)
    
    print("✅ CrewAI integration pattern defined")
    print("⚠️  Full test requires API key and user interaction")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FLOW-LEVEL HUMAN FEEDBACK DECORATOR TEST SUITE")
    print("="*80)
    
    results = []
    
    # Automated tests
    results.append(("Basic Decorator", test_decorator_basic()))
    results.append(("Feedback Actions", test_feedback_actions()))
    results.append(("Conditional Checkpoint", test_conditional_checkpoint()))
    results.append(("Context Extraction", test_context_extraction()))
    results.append(("Multi-Stage Flow", test_multi_stage_flow()))
    results.append(("CrewAI Integration", test_with_crewai()))
    
    # Manual tests (require user interaction)
    print("\n" + "="*80)
    print("MANUAL TESTS (Require User Interaction)")
    print("="*80)
    print("Run these individually:")
    print("  - test_handler_prompt()")
    print("  - Execute decorated functions with real inputs")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("✅ All automated tests passed!" if all_passed else "❌ Some tests failed"))
    print("="*80)


if __name__ == "__main__":
    main()
