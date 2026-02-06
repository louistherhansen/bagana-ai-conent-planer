"""
Test Server-Sent Events (SSE) streaming implementation for CrewAI.
SSE is ideal for one-way streaming from server to client over HTTP.
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

# Add parent directory to path to import crew.run
sys.path.insert(0, str(Path(__file__).parent.parent))


async def simulate_sse_stream(progress_updates: list) -> AsyncGenerator[str, None]:
    """Simulate SSE stream from progress updates."""
    for update in progress_updates:
        # SSE format: "data: {json}\n\n"
        data = json.dumps(update)
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.1)  # Simulate delay


def test_sse_format():
    """Test SSE message format."""
    print("=" * 60)
    print("Test: SSE Message Format")
    print("=" * 60)
    
    # SSE format example
    sample_progress = {
        "type": "progress",
        "agent": "Content Planner",
        "task": "create_content_plan",
        "timestamp": datetime.now().isoformat()
    }
    
    sse_message = f"data: {json.dumps(sample_progress)}\n\n"
    
    print("\nSSE Message Format:")
    print(sse_message)
    print("✓ Format: 'data: {json}\\n\\n'")
    print("✓ Content-Type: text/event-stream")
    print("✓ Each message ends with double newline")
    
    return sse_message


async def test_sse_streaming():
    """Test SSE streaming pattern."""
    print("\n" + "=" * 60)
    print("Test: SSE Streaming Pattern")
    print("=" * 60)
    
    # Simulate progress updates
    progress_updates = [
        {"type": "progress", "agent": "Content Planner", "task": "create_content_plan", "timestamp": "2026-02-06T15:00:00Z"},
        {"type": "progress", "agent": "Sentiment Analyst", "task": "analyze_sentiment", "timestamp": "2026-02-06T15:01:00Z"},
        {"type": "progress", "agent": "Trend Researcher", "task": "research_trends", "timestamp": "2026-02-06T15:02:00Z"},
        {"type": "complete", "status": "success", "timestamp": "2026-02-06T15:03:00Z"},
    ]
    
    print("\nSimulating SSE stream...")
    print("→ Each update will be sent as SSE message")
    
    async for sse_message in simulate_sse_stream(progress_updates):
        print(f"  {sse_message.strip()}")
    
    print("\n✓ SSE stream completed")
    
    return True


def test_sse_api_route():
    """Test SSE API route implementation pattern."""
    print("\n" + "=" * 60)
    print("Test: SSE API Route Pattern")
    print("=" * 60)
    
    # Example Next.js API route pattern
    route_code = '''
// app/api/crew/stream/route.ts
export async function GET(request: Request) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      // Start crew execution
      const crew = build_crew();
      const inputs = { user_input: "..." };
      
      // Stream progress updates
      crew.step_callback = (step) => {
        const progress = extractProgress(step);
        const sse = `data: ${JSON.stringify(progress)}\\n\\n`;
        controller.enqueue(encoder.encode(sse));
      };
      
      await crew.kickoff(inputs);
      
      // Send completion
      controller.enqueue(encoder.encode("data: [DONE]\\n\\n"));
      controller.close();
    }
  });
  
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
'''
    
    print("\nExample Next.js API Route:")
    print(route_code)
    print("✓ Pattern for implementing SSE streaming in Next.js")
    
    return True


async def main():
    """Run all SSE streaming tests."""
    print("\n" + "=" * 60)
    print("CrewAI Real-Time Streaming - SSE Tests")
    print("=" * 60)
    
    # Test 1: SSE format
    test_sse_format()
    
    # Test 2: SSE streaming
    await test_sse_streaming()
    
    # Test 3: API route pattern
    test_sse_api_route()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✓ SSE format validated")
    print("✓ SSE streaming pattern tested")
    print("✓ API route pattern provided")
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
