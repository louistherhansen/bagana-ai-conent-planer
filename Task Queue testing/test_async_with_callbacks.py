"""
Test async execution with progress callbacks and event handling.
Demonstrates monitoring async crew execution with callbacks.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Callable

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


class AsyncProgressTracker:
    """Track progress of async crew executions."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable):
        """Add a progress callback function."""
        self.callbacks.append(callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a progress event."""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data
        }
        self.events.append(event)
        
        # Call all registered callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Warning: Callback error: {e}")
    
    def get_events(self, event_type: str = None) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e.get("type") == event_type]
        return self.events


async def run_with_progress_tracking(
    crew_id: str,
    user_input: str,
    tracker: AsyncProgressTracker
) -> Dict[str, Any]:
    """Run crew with progress tracking."""
    tracker.emit_event("start", {"crew_id": crew_id, "user_input": user_input})
    
    start_time = datetime.now()
    
    try:
        crew = build_crew()
        inputs = {
            "user_input": user_input,
            "output_language": "English"
        }
        
        tracker.emit_event("crew_built", {"crew_id": crew_id})
        
        # Note: CrewAI's step_callback is synchronous, so we'll track start/end
        tracker.emit_event("execution_started", {"crew_id": crew_id})
        
        if hasattr(crew, 'kickoff_async'):
            result = await crew.kickoff_async(inputs=inputs)
        else:
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        tracker.emit_event("execution_completed", {
            "crew_id": crew_id,
            "duration": duration,
            "status": "success"
        })
        
        return {
            "crew_id": crew_id,
            "status": "success",
            "duration": duration,
            "result": result,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        tracker.emit_event("execution_failed", {
            "crew_id": crew_id,
            "duration": duration,
            "error": str(e)
        })
        
        return {
            "crew_id": crew_id,
            "status": "error",
            "duration": duration,
            "error": str(e),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }


def print_progress_callback(event: Dict[str, Any]):
    """Example progress callback that prints events."""
    event_type = event.get("type")
    crew_id = event.get("crew_id", "unknown")
    timestamp = event.get("timestamp", "")
    
    if event_type == "start":
        print(f"[{timestamp}] → Starting crew: {crew_id}")
    elif event_type == "crew_built":
        print(f"[{timestamp}]   ✓ Crew built: {crew_id}")
    elif event_type == "execution_started":
        print(f"[{timestamp}]   → Execution started: {crew_id}")
    elif event_type == "execution_completed":
        duration = event.get("duration", 0)
        print(f"[{timestamp}]   ✓ Completed: {crew_id} ({duration:.2f}s)")
    elif event_type == "execution_failed":
        error = event.get("error", "Unknown error")
        print(f"[{timestamp}]   ✗ Failed: {crew_id} - {error}")


async def test_async_with_callbacks():
    """Test async execution with progress callbacks."""
    print("=" * 60)
    print("Test: Async Execution with Progress Callbacks")
    print("=" * 60)
    
    tracker = AsyncProgressTracker()
    tracker.add_callback(print_progress_callback)
    
    crew_configs = [
        ("callback-1", "Create a content plan for summer campaign."),
        ("callback-2", "Plan a winter holiday campaign."),
        ("callback-3", "Design a spring product launch campaign."),
    ]
    
    print(f"\nRunning {len(crew_configs)} crews with progress tracking...")
    
    # Create async tasks
    tasks = [
        run_with_progress_tracking(crew_id, user_input, tracker)
        for crew_id, user_input in crew_configs
    ]
    
    # Execute concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display event summary
    print("\n" + "=" * 60)
    print("Event Summary")
    print("=" * 60)
    
    event_types = {}
    for event in tracker.get_events():
        event_type = event.get("type")
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # Display results
    successful = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
    failed = [r for r in results if isinstance(r, dict) and r.get("status") == "error"]
    
    print(f"\nResults: {len(successful)} successful, {len(failed)} failed")
    
    return tracker, results


async def test_custom_callbacks():
    """Test with custom callback implementations."""
    print("\n" + "=" * 60)
    print("Test: Custom Callback Implementations")
    print("=" * 60)
    
    tracker = AsyncProgressTracker()
    
    # Custom callback: collect statistics
    stats = {
        "start_times": {},
        "durations": {},
        "errors": []
    }
    
    def stats_callback(event: Dict[str, Any]):
        event_type = event.get("type")
        crew_id = event.get("crew_id")
        
        if event_type == "start":
            stats["start_times"][crew_id] = event.get("timestamp")
        elif event_type == "execution_completed":
            stats["durations"][crew_id] = event.get("duration", 0)
        elif event_type == "execution_failed":
            stats["errors"].append({
                "crew_id": crew_id,
                "error": event.get("error")
            })
    
    tracker.add_callback(stats_callback)
    tracker.add_callback(print_progress_callback)
    
    crew_configs = [
        ("stats-1", "Create a content plan for Q1."),
        ("stats-2", "Plan a product launch."),
    ]
    
    tasks = [
        run_with_progress_tracking(crew_id, user_input, tracker)
        for crew_id, user_input in crew_configs
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display statistics
    print("\n" + "=" * 60)
    print("Statistics Summary")
    print("=" * 60)
    
    if stats["durations"]:
        avg_duration = sum(stats["durations"].values()) / len(stats["durations"])
        print(f"Average duration: {avg_duration:.2f} seconds")
        print(f"Total crews: {len(stats["durations"])}")
    
    if stats["errors"]:
        print(f"Errors: {len(stats["errors"])}")
        for err in stats["errors"]:
            print(f"  - {err['crew_id']}: {err['error']}")
    
    return tracker, results


async def main():
    """Run all callback tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Callback Tests")
    print("=" * 60)
    
    # Test 1: Basic callbacks
    tracker1, results1 = await test_async_with_callbacks()
    
    # Test 2: Custom callbacks
    tracker2, results2 = await test_custom_callbacks()
    
    print("\n" + "=" * 60)
    print("All Tests Completed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
