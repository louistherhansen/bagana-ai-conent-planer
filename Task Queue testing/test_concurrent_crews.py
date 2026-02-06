"""
Test concurrent execution of multiple crews using async task queues.
Demonstrates running multiple crews in parallel.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


async def run_crew_async(crew_id: str, user_input: str) -> Dict[str, Any]:
    """Run a single crew asynchronously."""
    print(f"\n[{crew_id}] Starting crew execution...")
    start_time = datetime.now()
    
    crew = build_crew()
    inputs = {
        "user_input": user_input,
        "output_language": "English"
    }
    
    try:
        if hasattr(crew, 'kickoff_async'):
            result = await crew.kickoff_async(inputs=inputs)
        else:
            # Fallback to thread pool executor
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"[{crew_id}] ✓ Completed in {duration:.2f} seconds")
        
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
        print(f"[{crew_id}] ✗ Failed after {duration:.2f} seconds: {e}")
        
        return {
            "crew_id": crew_id,
            "status": "error",
            "duration": duration,
            "error": str(e),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }


async def test_concurrent_crews():
    """Test running multiple crews concurrently."""
    print("=" * 60)
    print("Test: Concurrent Crew Execution")
    print("=" * 60)
    
    # Define multiple crew runs with different inputs
    crew_configs = [
        ("crew-1", "Create a content plan for a summer beach campaign with 2 talents."),
        ("crew-2", "Plan a winter holiday campaign focusing on family activities with 3 talents."),
        ("crew-3", "Design a spring product launch campaign with influencer partnerships."),
    ]
    
    print(f"\nStarting {len(crew_configs)} crews concurrently...")
    overall_start = datetime.now()
    
    # Create async tasks for all crews
    tasks = [
        run_crew_async(crew_id, user_input)
        for crew_id, user_input in crew_configs
    ]
    
    # Execute all crews concurrently
    print("\n→ All crews started, waiting for completion...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    overall_end = datetime.now()
    total_duration = (overall_end - overall_start).total_seconds()
    
    # Process results
    successful = []
    failed = []
    
    for result in results:
        if isinstance(result, Exception):
            failed.append({"error": str(result)})
        elif result.get("status") == "success":
            successful.append(result)
        else:
            failed.append(result)
    
    # Display summary
    print("\n" + "=" * 60)
    print("Concurrent Execution Summary")
    print("=" * 60)
    print(f"Total crews: {len(crew_configs)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total duration: {total_duration:.2f} seconds")
    
    if successful:
        print("\nSuccessful executions:")
        for r in successful:
            print(f"  - {r['crew_id']}: {r['duration']:.2f}s")
    
    if failed:
        print("\nFailed executions:")
        for r in failed:
            error_msg = r.get("error", "Unknown error")
            print(f"  - {r.get('crew_id', 'unknown')}: {error_msg}")
    
    # Calculate efficiency (sequential vs concurrent)
    if successful:
        sequential_time = sum(r['duration'] for r in successful)
        efficiency = ((sequential_time - total_duration) / sequential_time * 100) if sequential_time > 0 else 0
        print(f"\nEfficiency gain: {efficiency:.1f}% (sequential would take {sequential_time:.2f}s)")
    
    return results


async def test_limited_concurrency():
    """Test concurrent execution with limited concurrency (semaphore pattern)."""
    print("\n" + "=" * 60)
    print("Test: Limited Concurrency (Semaphore)")
    print("=" * 60)
    
    # Limit to 2 concurrent crews
    semaphore = asyncio.Semaphore(2)
    
    async def run_with_limit(crew_id: str, user_input: str):
        async with semaphore:
            return await run_crew_async(crew_id, user_input)
    
    crew_configs = [
        ("limited-1", "Create a content plan for Q1 campaign."),
        ("limited-2", "Plan a product launch campaign."),
        ("limited-3", "Design a brand awareness campaign."),
        ("limited-4", "Create a seasonal campaign plan."),
    ]
    
    print(f"\nStarting {len(crew_configs)} crews with max 2 concurrent...")
    overall_start = datetime.now()
    
    tasks = [
        run_with_limit(crew_id, user_input)
        for crew_id, user_input in crew_configs
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    overall_end = datetime.now()
    total_duration = (overall_end - overall_start).total_seconds()
    
    print(f"\n✓ All crews completed in {total_duration:.2f} seconds")
    print(f"  (Limited to 2 concurrent executions)")
    
    return results


async def main():
    """Run all concurrent crew tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Concurrent Crew Tests")
    print("=" * 60)
    
    # Test 1: Full concurrency
    results1 = await test_concurrent_crews()
    
    # Test 2: Limited concurrency
    results2 = await test_limited_concurrency()
    
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
