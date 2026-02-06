"""
Run all async task queue tests.
This script executes all test files in sequence.
"""
import asyncio
import sys
import subprocess
from pathlib import Path


def run_test(test_file: str) -> bool:
    """Run a single test file and return success status."""
    print(f"\n{'=' * 60}")
    print(f"Running: {test_file}")
    print('=' * 60)
    
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=False,
            text=True,
            timeout=600  # 10 minute timeout per test
        )
        
        if result.returncode == 0:
            print(f"\n✓ {test_file} completed successfully")
            return True
        else:
            print(f"\n✗ {test_file} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n✗ {test_file} timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"\n✗ {test_file} failed with error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("CrewAI Async Task Queue - Test Suite")
    print("=" * 60)
    
    # List of test files to run
    test_files = [
        "example_simple_async.py",
        "test_basic_async.py",
        "test_concurrent_crews.py",
        "test_async_vs_sync.py",
        "test_async_task_queue.py",
        "test_async_with_callbacks.py",
    ]
    
    results = {}
    
    for test_file in test_files:
        success = run_test(test_file)
        results[test_file] = success
        
        # Small delay between tests
        import time
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Suite Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed results:")
    for test_file, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {test_file}")
    
    print("=" * 60)
    
    # Exit with error code if any test failed
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
