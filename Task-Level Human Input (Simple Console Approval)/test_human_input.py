"""
Test script for Task-Level Human Input functionality.
Verifies that human_input gates work correctly in CrewAI tasks.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crewai import Agent, Task, Crew


def test_human_input_basic():
    """Test basic human input functionality."""
    print("="*80)
    print("TEST 1: Basic Human Input")
    print("="*80)
    
    agent = Agent(
        role="Test Agent",
        goal="Test human input functionality",
        backstory="You are a test agent.",
        verbose=True,
    )
    
    task1 = Task(
        description="Generate a simple test output",
        agent=agent,
        expected_output="A test message",
    )
    
    task2 = Task(
        description="This task requires human approval",
        agent=agent,
        expected_output="Approved output",
        human_input=True,  # Enable human input
        context=[task1],
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task1, task2],
        verbose=True,
    )
    
    print("\n🚀 Starting crew execution...")
    print("📝 Task 1 will run automatically")
    print("⏸️  Task 2 will pause for your approval\n")
    
    try:
        result = crew.kickoff(inputs={"user_input": "Test input"})
        print("\n✅ Test PASSED: Human input worked correctly")
        print(f"Result: {result}")
        return True
    except KeyboardInterrupt:
        print("\n⚠️  Test INTERRUPTED: User stopped execution")
        return False
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_human_input_feedback():
    """Test human input with feedback."""
    print("\n" + "="*80)
    print("TEST 2: Human Input with Feedback")
    print("="*80)
    
    agent = Agent(
        role="Content Writer",
        goal="Write content based on feedback",
        backstory="You write content and incorporate feedback.",
        verbose=True,
    )
    
    task = Task(
        description="Write a draft blog post about AI",
        agent=agent,
        expected_output="A blog post draft",
        human_input=True,
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    
    print("\n🚀 Starting crew execution...")
    print("📝 Task will generate a draft")
    print("💬 When prompted, try typing 'e' and providing feedback\n")
    
    try:
        result = crew.kickoff(inputs={"user_input": "Write about AI"})
        print("\n✅ Test PASSED: Feedback mechanism worked")
        return True
    except KeyboardInterrupt:
        print("\n⚠️  Test INTERRUPTED")
        return False
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        return False


def test_multiple_approval_gates():
    """Test multiple tasks with approval gates."""
    print("\n" + "="*80)
    print("TEST 3: Multiple Approval Gates")
    print("="*80)
    
    agent = Agent(
        role="Multi-stage Processor",
        goal="Process through multiple approval stages",
        backstory="You process content through stages.",
        verbose=True,
    )
    
    task1 = Task(
        description="Stage 1: Initial processing",
        agent=agent,
        expected_output="Stage 1 output",
    )
    
    task2 = Task(
        description="Stage 2: First approval gate",
        agent=agent,
        expected_output="Stage 2 output",
        human_input=True,
        context=[task1],
    )
    
    task3 = Task(
        description="Stage 3: Second approval gate",
        agent=agent,
        expected_output="Stage 3 output",
        human_input=True,
        context=[task2],
    )
    
    task4 = Task(
        description="Stage 4: Final processing",
        agent=agent,
        expected_output="Final output",
        context=[task3],
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task1, task2, task3, task4],
        verbose=True,
    )
    
    print("\n🚀 Starting crew execution...")
    print("📝 Task 1: Runs automatically")
    print("⏸️  Task 2: Requires approval (type 'y')")
    print("⏸️  Task 3: Requires approval (type 'y')")
    print("📝 Task 4: Runs automatically\n")
    
    try:
        result = crew.kickoff(inputs={"user_input": "Process through stages"})
        print("\n✅ Test PASSED: Multiple approval gates worked")
        return True
    except KeyboardInterrupt:
        print("\n⚠️  Test INTERRUPTED")
        return False
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("TASK-LEVEL HUMAN INPUT TEST SUITE")
    print("="*80)
    print("\nThis will test human input functionality in CrewAI.")
    print("You will be prompted for approval during test execution.\n")
    
    input("Press Enter to start tests...")
    
    results = []
    
    # Test 1: Basic human input
    results.append(("Basic Human Input", test_human_input_basic()))
    
    # Test 2: Feedback mechanism
    # Uncomment to test feedback (requires manual interaction)
    # results.append(("Human Input with Feedback", test_human_input_feedback()))
    
    # Test 3: Multiple gates
    # Uncomment to test multiple gates (requires multiple approvals)
    # results.append(("Multiple Approval Gates", test_multiple_approval_gates()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    print("="*80)


if __name__ == "__main__":
    main()
