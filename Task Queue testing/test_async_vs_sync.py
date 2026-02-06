"""
Performance comparison between synchronous and asynchronous crew execution.
"""
import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


def run_sync(crew_id: str, user_input: str):
    """Run crew synchronously."""
    print(f"[{crew_id}] Starting sync execution...")
    start_time = time.time()
    
    crew = build_crew()
    inputs = {
        "user_input": user_input,
        "output_language": "English"
    }
    
    try:
        result = crew.kickoff(inputs=inputs)
        duration = time.time() - start_time
        print(f"[{crew_id}] ✓ Sync completed in {duration:.2f} seconds")
        return {"crew_id": crew_id, "duration": duration, "status": "success"}
    except Exception as e:
        duration = time.time() - start_time
        print(f"[{crew_id}] ✗ Sync failed after {duration:.2f} seconds: {e}")
        return {"crew_id": crew_id, "duration": duration, "status": "error", "error": str(e)}


async def run_async(crew_id: str, user_input: str):
    """Run crew asynchronously."""
    print(f"[{crew_id}] Starting async execution...")
    start_time = time.time()
    
    crew = build_crew()
    inputs = {
        "user_input": user_input,
        "output_language": "English"
    }
    
    try:
        if hasattr(crew, 'kickoff_async'):
            result = await crew.kickoff_async(inputs=inputs)
        else:
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        duration = time.time() - start_time
        print(f"[{crew_id}] ✓ Async completed in {duration:.2f} seconds")
        return {"crew_id": crew_id, "duration": duration, "status": "success"}
    except Exception as e:
        duration = time.time() - start_time
        print(f"[{crew_id}] ✗ Async failed after {duration:.2f} seconds: {e}")
        return {"crew_id": crew_id, "duration": duration, "status": "error", "error": str(e)}


def test_sync_execution():
    """Test synchronous execution of multiple crews."""
    print("=" * 60)
    print("Test: Synchronous Execution (Sequential)")
    print("=" * 60)
    
    crew_configs = [
        ("sync-1", "Create a content plan for summer campaign."),
        ("sync-2", "Plan a winter holiday campaign."),
        ("sync-3", "Design a spring product launch campaign."),
    ]
    
    print(f"\nRunning {len(crew_configs)} crews sequentially...")
    overall_start = time.time()
    
    results = []
    for crew_id, user_input in crew_configs:
        result = run_sync(crew_id, user_input)
        results.append(result)
    
    overall_duration = time.time() - overall_start
    
    print(f"\n✓ Sequential execution completed in {overall_duration:.2f} seconds")
    return results, overall_duration


async def test_async_execution():
    """Test asynchronous execution of multiple crews."""
    print("\n" + "=" * 60)
    print("Test: Asynchronous Execution (Concurrent)")
    print("=" * 60)
    
    crew_configs = [
        ("async-1", "Create a content plan for summer campaign."),
        ("async-2", "Plan a winter holiday campaign."),
        ("async-3", "Design a spring product launch campaign."),
    ]
    
    print(f"\nRunning {len(crew_configs)} crews concurrently...")
    overall_start = time.time()
    
    tasks = [
        run_async(crew_id, user_input)
        for crew_id, user_input in crew_configs
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    overall_duration = time.time() - overall_start
    
    print(f"\n✓ Concurrent execution completed in {overall_duration:.2f} seconds")
    return results, overall_duration


async def main():
    """Run performance comparison tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async vs Sync Performance Comparison")
    print("=" * 60)
    
    # Test 1: Synchronous execution
    sync_results, sync_duration = test_sync_execution()
    
    # Wait a bit between tests
    print("\nWaiting 2 seconds before async test...")
    await asyncio.sleep(2)
    
    # Test 2: Asynchronous execution
    async_results, async_duration = await test_async_execution()
    
    # Compare results
    print("\n" + "=" * 60)
    print("Performance Comparison Summary")
    print("=" * 60)
    
    sync_total = sum(r.get("duration", 0) for r in sync_results if isinstance(r, dict))
    async_total = sum(r.get("duration", 0) for r in async_results if isinstance(r, dict))
    
    print(f"\nSynchronous (Sequential):")
    print(f"  Total time: {sync_duration:.2f} seconds")
    print(f"  Sum of individual durations: {sync_total:.2f} seconds")
    
    print(f"\nAsynchronous (Concurrent):")
    print(f"  Total time: {async_duration:.2f} seconds")
    print(f"  Sum of individual durations: {async_total:.2f} seconds")
    
    if sync_duration > 0:
        speedup = ((sync_duration - async_duration) / sync_duration) * 100
        print(f"\nSpeedup: {speedup:.1f}% faster with async")
        print(f"Time saved: {sync_duration - async_duration:.2f} seconds")
    
    # Individual crew comparison
    print("\nIndividual Crew Durations:")
    print(f"{'Crew ID':<15} {'Sync (s)':<12} {'Async (s)':<12}")
    print("-" * 40)
    
    sync_dict = {r.get("crew_id"): r.get("duration", 0) for r in sync_results if isinstance(r, dict)}
    async_dict = {r.get("crew_id"): r.get("duration", 0) for r in async_results if isinstance(r, dict)}
    
    all_crews = set(sync_dict.keys()) | set(async_dict.keys())
    for crew_id in sorted(all_crews):
        sync_time = sync_dict.get(crew_id, 0)
        async_time = async_dict.get(crew_id, 0)
        print(f"{crew_id:<15} {sync_time:<12.2f} {async_time:<12.2f}")
    
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
