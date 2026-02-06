"""
Test step callback streaming patterns for CrewAI.
Demonstrates different ways to use step_callbacks for streaming.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


class StreamingCallback:
    """Callback class for streaming progress updates."""
    
    def __init__(self):
        self.updates: List[Dict[str, Any]] = []
        self.on_update = None  # Callback function
    
    def __call__(self, step):
        """Handle step callback."""
        info = getattr(step, "__dict__", {}) if hasattr(step, "__dict__") else {}
        agent_obj = info.get("agent") or getattr(step, "agent", None)
        task_obj = info.get("task") or getattr(step, "task", None)
        
        agent_name = getattr(agent_obj, "role", "?") if agent_obj else "?"
        task_name = getattr(task_obj, "name", "?") if task_obj else "?"
        
        update = {
            "type": "progress",
            "agent": agent_name,
            "task": task_name,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        
        self.updates.append(update)
        
        # Call custom callback if set
        if self.on_update:
            self.on_update(update)
        
        # Also write to stderr (for API capture)
        try:
            import sys as sys_module
            progress_json = json.dumps(update) + "\n"
            sys_module.stderr.write(progress_json)
            sys_module.stderr.flush()
        except Exception:
            pass


def test_callback_class():
    """Test using callback class for streaming."""
    print("=" * 60)
    print("Test: Callback Class Pattern")
    print("=" * 60)
    
    crew = build_crew()
    
    # Create streaming callback
    stream_callback = StreamingCallback()
    
    # Set custom update handler
    def handle_update(update):
        print(f"  → Stream: {update['agent'][:30]} | {update['task'][:50]}")
    
    stream_callback.on_update = handle_update
    
    # Set callback
    crew.step_callback = stream_callback
    
    inputs = {
        "user_input": "Create a simple content plan.",
        "output_language": "English"
    }
    
    print("\nStarting execution with streaming callback...")
    
    try:
        result = crew.kickoff(inputs=inputs)
        print(f"\n✓ Execution completed")
        print(f"✓ Total updates: {len(stream_callback.updates)}")
        return stream_callback.updates
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return []


def test_callback_function():
    """Test using callback function for streaming."""
    print("\n" + "=" * 60)
    print("Test: Callback Function Pattern")
    print("=" * 60)
    
    crew = build_crew()
    updates = []
    
    def streaming_callback(step):
        """Simple callback function."""
        info = getattr(step, "__dict__", {}) if hasattr(step, "__dict__") else {}
        agent_obj = info.get("agent") or getattr(step, "agent", None)
        task_obj = info.get("task") or getattr(step, "task", None)
        
        agent_name = getattr(agent_obj, "role", "?")[:30] if agent_obj else "?"
        task_name = getattr(task_obj, "name", "?")[:50] if task_obj else "?"
        
        update = {
            "agent": agent_name,
            "task": task_name,
            "timestamp": datetime.now().isoformat()
        }
        updates.append(update)
        print(f"  → Callback: {agent_name} | {task_name}")
    
    crew.step_callback = streaming_callback
    
    inputs = {
        "user_input": "Test callback function pattern.",
        "output_language": "English"
    }
    
    print("\nStarting execution with function callback...")
    
    try:
        result = crew.kickoff(inputs=inputs)
        print(f"\n✓ Execution completed")
        print(f"✓ Total updates: {len(updates)}")
        return updates
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return []


def test_callback_with_queue():
    """Test callback with queue for async processing."""
    print("\n" + "=" * 60)
    print("Test: Callback with Queue Pattern")
    print("=" * 60)
    
    import queue
    
    # Create queue for progress updates
    progress_queue = queue.Queue()
    
    def queued_callback(step):
        """Callback that puts updates in queue."""
        info = getattr(step, "__dict__", {}) if hasattr(step, "__dict__") else {}
        agent_obj = info.get("agent") or getattr(step, "agent", None)
        task_obj = info.get("task") or getattr(step, "task", None)
        
        agent_name = getattr(agent_obj, "role", "?") if agent_obj else "?"
        task_name = getattr(task_obj, "name", "?") if task_obj else "?"
        
        update = {
            "type": "progress",
            "agent": agent_name,
            "task": task_name,
            "timestamp": datetime.now().isoformat()
        }
        
        progress_queue.put(update)
        print(f"  → Queued: {agent_name[:30]} | {task_name[:50]}")
    
    crew = build_crew()
    crew.step_callback = queued_callback
    
    inputs = {
        "user_input": "Test queue pattern.",
        "output_language": "English"
    }
    
    print("\nStarting execution with queue callback...")
    
    try:
        result = crew.kickoff(inputs=inputs)
        
        # Process queue
        queued_updates = []
        while not progress_queue.empty():
            queued_updates.append(progress_queue.get())
        
        print(f"\n✓ Execution completed")
        print(f"✓ Updates in queue: {len(queued_updates)}")
        return queued_updates
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return []


def main():
    """Run all step callback streaming tests."""
    print("\n" + "=" * 60)
    print("CrewAI Real-Time Streaming - Step Callback Tests")
    print("=" * 60)
    
    # Test 1: Callback class
    updates1 = test_callback_class()
    
    # Test 2: Callback function
    updates2 = test_callback_function()
    
    # Test 3: Callback with queue
    updates3 = test_callback_with_queue()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Callback Class Updates: {len(updates1)}")
    print(f"Callback Function Updates: {len(updates2)}")
    print(f"Queue Pattern Updates: {len(updates3)}")
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
