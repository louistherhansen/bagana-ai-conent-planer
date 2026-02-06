"""
Simple example demonstrating async task queue execution in CrewAI.
This is a minimal example to get started with async execution.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))

from crew.run import build_crew


async def simple_async_example():
    """Simple example of async crew execution."""
    print("=" * 60)
    print("Simple Async Crew Execution Example")
    print("=" * 60)
    
    # Build crew
    print("\n1. Building crew...")
    crew = build_crew()
    print(f"   ✓ Crew ready with {len(crew.agents)} agents")
    
    # Prepare inputs
    inputs = {
        "user_input": "Create a simple content plan for a product launch campaign.",
        "output_language": "English"
    }
    
    # Execute asynchronously
    print("\n2. Starting async execution...")
    print("   → This will run in the background")
    
    try:
        # Check if kickoff_async is available
        if hasattr(crew, 'kickoff_async'):
            # Use native async method
            result = await crew.kickoff_async(inputs=inputs)
        else:
            # Fallback: wrap sync kickoff in async thread
            print("   → Using thread pool executor (kickoff_async not available)")
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        print("\n3. Execution completed!")
        print(f"   ✓ Status: {result.status if hasattr(result, 'status') else 'complete'}")
        
        # Show output preview
        if hasattr(result, 'raw'):
            output = str(result.raw)
            preview = output[:300] + "..." if len(output) > 300 else output
            print(f"\n4. Output preview:\n{preview}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def multiple_async_example():
    """Example of running multiple crews concurrently."""
    print("\n" + "=" * 60)
    print("Multiple Concurrent Crews Example")
    print("=" * 60)
    
    # Define multiple tasks
    tasks = [
        "Create a content plan for summer campaign.",
        "Plan a winter holiday campaign.",
        "Design a spring product launch campaign.",
    ]
    
    print(f"\nRunning {len(tasks)} crews concurrently...")
    
    async def run_single_crew(index: int, user_input: str):
        """Run a single crew."""
        crew = build_crew()
        inputs = {
            "user_input": user_input,
            "output_language": "English"
        }
        
        print(f"  → Starting crew {index + 1}...")
        
        if hasattr(crew, 'kickoff_async'):
            result = await crew.kickoff_async(inputs=inputs)
        else:
            result = await asyncio.to_thread(crew.kickoff, inputs=inputs)
        
        print(f"  ✓ Crew {index + 1} completed")
        return result
    
    # Create tasks for all crews
    crew_tasks = [
        run_single_crew(i, task_input)
        for i, task_input in enumerate(tasks)
    ]
    
    # Execute all concurrently
    results = await asyncio.gather(*crew_tasks, return_exceptions=True)
    
    print(f"\n✓ All {len(results)} crews completed")
    
    # Count successes
    successful = sum(1 for r in results if not isinstance(r, Exception))
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(results) - successful}")
    
    return results


async def main():
    """Run examples."""
    print("\n" + "=" * 60)
    print("CrewAI Async Task Queue - Simple Examples")
    print("=" * 60)
    
    # Example 1: Single async execution
    result = await simple_async_example()
    
    # Example 2: Multiple concurrent executions
    results = await multiple_async_example()
    
    print("\n" + "=" * 60)
    print("Examples Completed")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
    except Exception as e:
        print(f"\n\nExample failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
