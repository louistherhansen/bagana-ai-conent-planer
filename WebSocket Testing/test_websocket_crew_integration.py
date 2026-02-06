"""
Test WebSocket integration with CrewAI crew execution.
Demonstrates streaming crew progress updates via WebSocket.
"""
import asyncio
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Set, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import websockets
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


class CrewWebSocketServer:
    """WebSocket server integrated with CrewAI."""
    
    def __init__(self, host: str = "localhost", port: int = 8767):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.running_crews: dict = {}
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client."""
        self.clients.add(websocket)
        print(f"[Server] Client connected: {websocket.remote_address}")
        await websocket.send(json.dumps({
            "type": "connected",
            "message": "WebSocket connected to CrewAI server",
            "timestamp": datetime.now().isoformat()
        }))
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client."""
        self.clients.discard(websocket)
        print(f"[Server] Client disconnected: {websocket.remote_address}")
    
    async def execute_crew(self, websocket: WebSocketServerProtocol, payload: dict):
        """Execute crew and stream progress updates."""
        crew_id = payload.get("crew_id", f"crew_{datetime.now().timestamp()}")
        
        print(f"[Server] Starting crew execution: {crew_id}")
        
        # Send start message
        await websocket.send(json.dumps({
            "type": "crew_started",
            "crew_id": crew_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Prepare input
        input_json = json.dumps({
            "user_input": payload.get("user_input", "Test crew execution"),
            "output_language": payload.get("output_language", "English")
        })
        
        # Get Python command
        import sys as sys_module
        python_cmd = sys_module.executable
        
        try:
            # Spawn crew process
            proc = subprocess.Popen(
                [python_cmd, "-m", "crew.run", "--stdin"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            # Write input
            proc.stdin.write(input_json)
            proc.stdin.close()
            
            # Stream progress from stderr
            progress_count = 0
            for line in proc.stderr:
                line = line.strip()
                if line.startswith("{") and '"type":"progress"' in line:
                    try:
                        progress = json.loads(line)
                        progress_count += 1
                        
                        # Send progress update via WebSocket
                        await websocket.send(json.dumps({
                            "type": "progress",
                            "crew_id": crew_id,
                            "progress": progress,
                            "progress_count": progress_count,
                            "timestamp": datetime.now().isoformat()
                        }))
                        
                        print(f"  -> Progress {progress_count}: {progress.get('agent', '?')} | {progress.get('task', '?')[:50]}")
                    except json.JSONDecodeError:
                        pass
            
            # Wait for completion
            proc.wait()
            
            # Read final result
            stdout = proc.stdout.read()
            try:
                result = json.loads(stdout)
                
                # Send completion
                await websocket.send(json.dumps({
                    "type": "crew_completed",
                    "crew_id": crew_id,
                    "result": result,
                    "progress_updates": progress_count,
                    "timestamp": datetime.now().isoformat()
                }))
                
                print(f"[Server] Crew {crew_id} completed with {progress_count} progress updates")
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "crew_error",
                    "crew_id": crew_id,
                    "error": "Failed to parse crew output",
                    "timestamp": datetime.now().isoformat()
                }))
        
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "crew_error",
                "crew_id": crew_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }))
            print(f"[Server] Error executing crew {crew_id}: {e}")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connection and messages."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "execute_crew":
                        # Execute crew in background
                        asyncio.create_task(self.execute_crew(websocket, data))
                    
                    elif message_type == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Unknown message type: {message_type}"
                        }))
                
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            print("Error: websockets library not available")
            return
        
        print(f"[Server] Starting CrewAI WebSocket server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[Server] Server running. Waiting for connections...")
            await asyncio.Future()


async def test_crew_integration():
    """Test CrewAI integration with WebSocket."""
    print("=" * 60)
    print("Test: CrewAI WebSocket Integration")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("\n⚠ websockets library not installed")
        print("Install with: pip install websockets")
        return False
    
    server = CrewWebSocketServer(host="localhost", port=8767)
    
    print("\n[1/3] Starting WebSocket server...")
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)
    
    print("\n[2/3] Connecting client and executing crew...")
    
    try:
        async with websockets.connect("ws://localhost:8767") as ws:
            # Receive connection message
            message = await ws.recv()
            data = json.loads(message)
            print(f"  -> {data.get('type')}: {data.get('message')}")
            
            # Send crew execution request
            execution_request = {
                "type": "execute_crew",
                "crew_id": "test_crew_1",
                "user_input": "Create a simple content plan for a product launch.",
                "output_language": "English"
            }
            
            await ws.send(json.dumps(execution_request))
            print("  -> Sent crew execution request")
            
            # Receive updates
            progress_updates = []
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=180.0)
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "crew_started":
                        print(f"  -> Crew started: {data.get('crew_id')}")
                    
                    elif msg_type == "progress":
                        progress = data.get("progress", {})
                        progress_updates.append(progress)
                        print(f"  -> Progress: {progress.get('agent', '?')} | {progress.get('task', '?')[:40]}")
                    
                    elif msg_type == "crew_completed":
                        print(f"  -> Crew completed: {data.get('progress_updates')} progress updates")
                        break
                    
                    elif msg_type == "crew_error":
                        print(f"  -> Error: {data.get('error')}")
                        break
                
                except asyncio.TimeoutError:
                    print("  -> Timeout waiting for crew completion")
                    break
            
            print(f"\n[3/3] Received {len(progress_updates)} progress updates")
    
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    
    return True


async def main():
    """Run all CrewAI WebSocket integration tests."""
    print("\n" + "=" * 60)
    print("CrewAI WebSocket Testing - Crew Integration")
    print("=" * 60)
    
    result = await test_crew_integration()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"CrewAI Integration: {'[OK] Passed' if result else '[FAIL] Failed'}")
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
