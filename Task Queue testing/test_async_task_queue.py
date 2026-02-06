"""
Test async task queue pattern for managing multiple crew executions.
Implements a queue-based approach for processing crew tasks asynchronously.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


class AsyncTaskQueue:
    """Async task queue for managing crew executions."""
    
    def __init__(self, max_concurrent: int = 3):
        """Initialize task queue with max concurrent executions."""
        self.max_concurrent = max_concurrent
        self.queue: deque = deque()
        self.running: Dict[str, asyncio.Task] = {}
        self.completed: List[Dict[str, Any]] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def add_task(self, task_id: str, user_input: str) -> str:
        """Add a task to the queue."""
        self.queue.append({
            "task_id": task_id,
            "user_input": user_input,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        })
        print(f"[Queue] Task '{task_id}' added to queue (queue size: {len(self.queue)})")
        return task_id
    
    async def process_queue(self):
        """Process tasks from the queue."""
        while True:
            if not self.queue and not self.running:
                # Queue empty and no running tasks
                break
            
            if self.queue and len(self.running) < self.max_concurrent:
                # Process next task
                task_data = self.queue.popleft()
                task_id = task_data["task_id"]
                
                # Create async task
                task = asyncio.create_task(
                    self._execute_crew(task_id, task_data["user_input"])
                )
                self.running[task_id] = task
                print(f"[Queue] Task '{task_id}' started (running: {len(self.running)})")
            
            # Wait for at least one task to complete
            if self.running:
                done, pending = await asyncio.wait(
                    self.running.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for task in done:
                    result = await task
                    task_id = result.get("task_id")
                    if task_id in self.running:
                        del self.running[task_id]
                    self.completed.append(result)
                    print(f"[Queue] Task '{task_id}' completed (running: {len(self.running)}, completed: {len(self.completed)})")
            else:
                # No running tasks, wait a bit
                await asyncio.sleep(0.1)
    
    async def _execute_crew(self, task_id: str, user_input: str) -> Dict[str, Any]:
        """Execute a single crew task."""
        async with self.semaphore:
            start_time = datetime.now()
            
            try:
                crew = build_crew()
                inputs = {
                    "user_input": user_input,
                    "output_language": "English"
                }
                
                if hasattr(crew, 'kickoff_async'):
                    result = await crew.kickoff_async(inputs=inputs)
                else:
                    result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return {
                    "task_id": task_id,
                    "status": "success",
                    "duration": duration,
                    "result": result,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return {
                    "task_id": task_id,
                    "status": "error",
                    "duration": duration,
                    "error": str(e),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "queued": len(self.queue),
            "running": len(self.running),
            "completed": len(self.completed),
            "max_concurrent": self.max_concurrent
        }


async def test_basic_queue():
    """Test basic async task queue."""
    print("=" * 60)
    print("Test: Basic Async Task Queue")
    print("=" * 60)
    
    queue = AsyncTaskQueue(max_concurrent=2)
    
    # Add tasks to queue
    tasks = [
        ("task-1", "Create a content plan for summer campaign."),
        ("task-2", "Plan a winter holiday campaign."),
        ("task-3", "Design a spring product launch campaign."),
        ("task-4", "Create a brand awareness campaign."),
    ]
    
    print(f"\nAdding {len(tasks)} tasks to queue...")
    for task_id, user_input in tasks:
        await queue.add_task(task_id, user_input)
    
    print(f"\nQueue status: {queue.get_status()}")
    
    # Process queue
    print("\nProcessing queue...")
    start_time = datetime.now()
    await queue.process_queue()
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    # Display results
    print("\n" + "=" * 60)
    print("Queue Processing Results")
    print("=" * 60)
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"Completed tasks: {len(queue.completed)}")
    
    successful = [r for r in queue.completed if r.get("status") == "success"]
    failed = [r for r in queue.completed if r.get("status") == "error"]
    
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print("\nSuccessful tasks:")
        for r in successful:
            print(f"  - {r['task_id']}: {r['duration']:.2f}s")
    
    if failed:
        print("\nFailed tasks:")
        for r in failed:
            print(f"  - {r['task_id']}: {r.get('error', 'Unknown error')}")
    
    return queue


async def test_dynamic_queue():
    """Test dynamic task queue with tasks added during processing."""
    print("\n" + "=" * 60)
    print("Test: Dynamic Task Queue")
    print("=" * 60)
    
    queue = AsyncTaskQueue(max_concurrent=2)
    
    # Initial tasks
    initial_tasks = [
        ("dynamic-1", "Create a content plan for Q1."),
        ("dynamic-2", "Plan a product launch."),
    ]
    
    print(f"\nAdding initial {len(initial_tasks)} tasks...")
    for task_id, user_input in initial_tasks:
        await queue.add_task(task_id, user_input)
    
    # Start processing
    process_task = asyncio.create_task(queue.process_queue())
    
    # Add more tasks after a delay
    await asyncio.sleep(1)
    
    additional_tasks = [
        ("dynamic-3", "Design a brand campaign."),
        ("dynamic-4", "Create a seasonal plan."),
    ]
    
    print(f"\nAdding {len(additional_tasks)} more tasks during processing...")
    for task_id, user_input in additional_tasks:
        await queue.add_task(task_id, user_input)
    
    # Wait for all tasks to complete
    await process_task
    
    print(f"\n✓ All tasks completed: {len(queue.completed)}")
    return queue


async def main():
    """Run all async task queue tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Queue Pattern Tests")
    print("=" * 60)
    
    # Test 1: Basic queue
    queue1 = await test_basic_queue()
    
    # Test 2: Dynamic queue
    queue2 = await test_dynamic_queue()
    
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
