"""
Test basic CrewAI streaming execution.
Demonstrates using CrewAI's native streaming capabilities.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


def test_basic_streaming():
    """Test basic streaming with step callback."""
    print("=" * 60)
    print("Test: Basic CrewAI Streaming")
    print("=" * 60)
    
    # Build crew
    print("\n[1/3] Building crew...")
    crew = build_crew()
    print(f"✓ Crew built with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
    
    # Check if step_callback is set
    if hasattr(crew, 'step_callback') and crew.step_callback:
        print("✓ Step callback is configured")
    else:
        print("⚠ Step callback not configured")
    
    # Prepare inputs
    inputs = {
        "user_input": "Create a simple content plan for a product launch.",
        "output_language": "English"
    }
    
    print("\n[2/3] Starting streaming execution...")
    print("→ Progress updates will be shown in real-time via step_callback")
    print("→ Check stderr for JSON progress lines")
    
    start_time = datetime.now()
    
    # Collect progress updates
    progress_updates = []
    
    # Custom step callback to collect progress
    def collect_progress(step):
        """Collect progress updates."""
        from crew.run import _step_callback
        
        # Call original callback
        _step_callback(step)
        
        # Extract info for display
        info = getattr(step, "__dict__", {}) if hasattr(step, "__dict__") else {}
        agent_obj = info.get("agent") or getattr(step, "agent", None)
        task_obj = info.get("task") or getattr(step, "task", None)
        
        agent_name = getattr(agent_obj, "role", "?") if agent_obj else "?"
        task_name = getattr(task_obj, "name", "?") if task_obj else "?"
        
        progress_updates.append({
            "agent": agent_name,
            "task": task_name,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"  → Step: {agent_name[:30]} | {task_name[:50]}")
    
    # Set custom callback
    crew.step_callback = collect_progress
    
    try:
        result = crew.kickoff(inputs=inputs)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[3/3] Execution completed in {duration:.2f} seconds")
        print(f"✓ Total progress updates: {len(progress_updates)}")
        
        # Display progress summary
        if progress_updates:
            print("\nProgress Summary:")
            for i, update in enumerate(progress_updates, 1):
                print(f"  {i}. {update['agent'][:30]:<30} | {update['task'][:40]}")
        
        return result, progress_updates
        
    except Exception as e:
        print(f"\n✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return None, []


def test_streaming_generator():
    """Test streaming using generator pattern."""
    print("\n" + "=" * 60)
    print("Test: Streaming Generator Pattern")
    print("=" * 60)
    
    crew = build_crew()
    inputs = {
        "user_input": "Create a content plan for summer campaign.",
        "output_language": "English"
    }
    
    print("\n→ Testing generator-based streaming...")
    
    # Note: CrewAI may not have direct generator support
    # This is a conceptual test for streaming patterns
    print("⚠ CrewAI streaming via generators may require custom implementation")
    print("  Current approach: Use step_callback for progress updates")
    
    return None


def main():
    """Run all basic streaming tests."""
    print("\n" + "=" * 60)
    print("CrewAI Real-Time Streaming - Basic Tests")
    print("=" * 60)
    
    # Test 1: Basic streaming
    result, progress = test_basic_streaming()
    
    # Test 2: Generator pattern
    test_streaming_generator()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Basic Streaming: {'✓ Passed' if result else '✗ Failed'}")
    print(f"Progress Updates Collected: {len(progress)}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
