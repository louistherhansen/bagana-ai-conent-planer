"""
Basic async execution test for CrewAI.
Demonstrates using kickoff_async() for non-blocking crew execution.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew, kickoff


async def test_basic_async():
    """Test basic async execution using kickoff_async()."""
    print("=" * 60)
    print("Test: Basic Async Execution")
    print("=" * 60)
    
    # Build crew
    print("\n[1/3] Building crew...")
    crew = build_crew()
    print(f"✓ Crew built with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
    
    # Prepare inputs
    inputs = {
        "user_input": "Create a content plan for a summer campaign with 2 talents focusing on beach activities.",
        "output_language": "English"
    }
    
    print("\n[2/3] Starting async execution...")
    start_time = datetime.now()
    
    # Use kickoff_async() for non-blocking execution
    try:
        # Note: CrewAI's kickoff_async() may return a coroutine or future
        # Check if crew has kickoff_async method
        if hasattr(crew, 'kickoff_async'):
            print("✓ Using crew.kickoff_async()")
            # For async execution, we need to await it
            result = await crew.kickoff_async(inputs=inputs)
        else:
            # Fallback: use asyncio.to_thread for async wrapper
            print("⚠ kickoff_async() not available, using asyncio.to_thread wrapper")
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n[3/3] Execution completed in {duration:.2f} seconds")
        print(f"✓ Status: {result.status if hasattr(result, 'status') else 'complete'}")
        
        # Display output summary
        if hasattr(result, 'raw'):
            output_preview = str(result.raw)[:200] + "..." if len(str(result.raw)) > 200 else str(result.raw)
            print(f"\nOutput preview:\n{output_preview}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error during async execution: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_async_with_await():
    """Test async execution with proper await pattern."""
    print("\n" + "=" * 60)
    print("Test: Async Execution with Await Pattern")
    print("=" * 60)
    
    crew = build_crew()
    inputs = {
        "user_input": "Test async execution with await pattern.",
        "output_language": "English"
    }
    
    print("\nStarting async execution (non-blocking)...")
    start_time = datetime.now()
    
    # Create task for async execution
    if hasattr(crew, 'kickoff_async'):
        task = crew.kickoff_async(inputs=inputs)
        print("✓ Async task created, execution started in background")
        
        # Do other work while crew executes
        print("  → Simulating other work...")
        await asyncio.sleep(1)
        print("  → Other work completed")
        
        # Now await the result
        print("\nAwaiting crew result...")
        result = await task
    else:
        # Use thread pool executor for async wrapper
        print("⚠ Using thread pool executor wrapper")
        result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n✓ Crew execution completed in {duration:.2f} seconds")
    return result


async def main():
    """Run all basic async tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Basic Tests")
    print("=" * 60)
    
    # Test 1: Basic async
    result1 = await test_basic_async()
    
    # Test 2: Async with await pattern
    result2 = await test_async_with_await()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Test 1 (Basic Async): {'✓ Passed' if result1 else '✗ Failed'}")
    print(f"Test 2 (Await Pattern): {'✓ Passed' if result2 else '✗ Failed'}")
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
