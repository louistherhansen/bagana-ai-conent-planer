"""
Example WebSocket client for testing CrewAI WebSocket server.
Demonstrates how to connect and interact with the WebSocket server.
"""
import asyncio
import json
import sys
from datetime import datetime

# Try to import websockets
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets library not installed. Install with: pip install websockets")


async def test_websocket_client():
    """Test WebSocket client connection."""
    print("=" * 60)
    print("CrewAI WebSocket Client Example")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("\n⚠ websockets library not available")
        print("Install with: pip install websockets")
        return
    
    uri = "ws://localhost:8769"
    
    print(f"\n[1/4] Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            # Receive connection message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"  -> {data.get('type')}: {data.get('message')}")
            
            print("\n[2/4] Sending crew execution request...")
            
            # Send execution request
            request = {
                "type": "execute_crew",
                "crew_id": "example_crew_1",
                "user_input": "Create a content plan for a summer campaign.",
                "output_language": "English"
            }
            
            await websocket.send(json.dumps(request))
            print(f"  -> Sent: {request['type']}")
            
            print("\n[3/4] Receiving progress updates...")
            
            # Receive updates
            progress_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=180.0)
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "crew_started":
                        print(f"  -> Crew started: {data.get('crew_id')}")
                    
                    elif msg_type == "progress":
                        progress = data.get("data", {})
                        progress_count += 1
                        agent = progress.get("agent", "?")
                        task = progress.get("task", "?")
                        print(f"  -> Progress {progress_count}: {agent} | {task[:50]}")
                    
                    elif msg_type == "crew_completed":
                        result = data.get("result", {})
                        print(f"\n[4/4] Crew completed!")
                        print(f"  -> Progress updates: {data.get('progress_count')}")
                        print(f"  -> Status: {result.get('status', 'unknown')}")
                        break
                    
                    elif msg_type == "crew_error":
                        print(f"  -> Error: {data.get('error')}")
                        break
                
                except asyncio.TimeoutError:
                    print("  -> Timeout waiting for completion")
                    break
            
            print(f"\n[OK] Received {progress_count} progress updates")
    
    except websockets.exceptions.InvalidURI:
        print(f"  [FAIL] Invalid URI: {uri}")
    except websockets.exceptions.ConnectionClosed:
        print("  [FAIL] Connection closed by server")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")


async def test_ping_pong():
    """Test ping/pong heartbeat."""
    print("\n" + "=" * 60)
    print("Test: Ping/Pong Heartbeat")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        return
    
    uri = "ws://localhost:8769"
    
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.recv()  # Connection message
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Receive pong
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("type") == "pong":
                print("  [OK] Ping/pong working")
            else:
                print(f"  [FAIL] Unexpected response: {data.get('type')}")
    
    except Exception as e:
        print(f"  [FAIL] Error: {e}")


async def main():
    """Run client tests."""
    print("\n" + "=" * 60)
    print("CrewAI WebSocket Client Testing")
    print("=" * 60)
    
    # Test 1: Basic client
    await test_websocket_client()
    
    # Test 2: Ping/pong
    await test_ping_pong()
    
    print("\n" + "=" * 60)
    print("Client Tests Completed")
    print("=" * 60)
    print("\nNote: Make sure the WebSocket server is running")
    print("Start server with: python 'WebSocket Testing/example_websocket_server.py'")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nClient interrupted by user")
    except Exception as e:
        print(f"\n\nClient error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
