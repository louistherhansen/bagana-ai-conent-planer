"""
Quick test to verify async task queue setup without full crew execution.
Tests the async infrastructure and imports.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_imports():
    """Test that all imports work correctly."""
    print("=" * 60)
    print("Test: Import Verification")
    print("=" * 60)
    
    try:
        from crew.run import build_crew
        print("✓ Successfully imported build_crew")
        
        crew = build_crew()
        print(f"✓ Successfully built crew with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        
        # Check if kickoff_async is available
        if hasattr(crew, 'kickoff_async'):
            print("✓ Crew has kickoff_async() method available")
        else:
            print("⚠ Crew does not have kickoff_async(), will use asyncio.to_thread wrapper")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_basic():
    """Test basic async functionality."""
    print("\n" + "=" * 60)
    print("Test: Basic Async Functionality")
    print("=" * 60)
    
    async def simple_task(name: str, delay: float):
        """Simple async task."""
        print(f"  → Starting {name}...")
        await asyncio.sleep(delay)
        print(f"  ✓ Completed {name}")
        return f"Result from {name}"
    
    print("\nRunning 3 async tasks concurrently...")
    start = datetime.now()
    
    results = await asyncio.gather(
        simple_task("Task 1", 0.5),
        simple_task("Task 2", 0.3),
        simple_task("Task 3", 0.4)
    )
    
    duration = (datetime.now() - start).total_seconds()
    
    print(f"\n✓ All tasks completed in {duration:.2f} seconds")
    print(f"  (Sequential would take ~1.2s, concurrent took {duration:.2f}s)")
    print(f"  Results: {results}")
    
    return True


async def test_crew_async_wrapper():
    """Test async wrapper for crew execution (without actually running)."""
    print("\n" + "=" * 60)
    print("Test: Crew Async Wrapper Setup")
    print("=" * 60)
    
    try:
        from crew.run import build_crew
        
        crew = build_crew()
        print("✓ Crew built successfully")
        
        # Test that we can create an async wrapper
        async def async_kickoff_wrapper(inputs):
            """Wrapper to test async pattern."""
            return await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        print("✓ Async wrapper function created")
        print("  → This pattern can be used for async crew execution")
        
        # Test that inputs can be prepared
        test_inputs = {
            "user_input": "Test input",
            "output_language": "English"
        }
        print(f"✓ Test inputs prepared: {list(test_inputs.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all quick tests."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Quick Verification Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", await test_imports()))
    
    # Test 2: Basic async
    results.append(("Basic Async", await test_async_basic()))
    
    # Test 3: Crew async wrapper
    results.append(("Crew Async Wrapper", await test_crew_async_wrapper()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    print(f"\nOverall: {'✓ All tests passed' if all_passed else '✗ Some tests failed'}")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
