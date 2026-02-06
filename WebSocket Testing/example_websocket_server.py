"""
Complete WebSocket server example for CrewAI integration.
This can be used as a reference for implementing WebSocket support.
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
    print("Warning: websockets library not installed. Install with: pip install websockets")


class CrewAIWebSocketServer:
    """Complete WebSocket server for CrewAI integration."""
    
    def __init__(self, host: str = "localhost", port: int = 8769):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.active_crews: dict = {}  # crew_id -> process
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client."""
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            "type": "connected",
            "message": "Connected to CrewAI WebSocket server",
            "server_time": datetime.now().isoformat()
        }))
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client."""
        self.clients.discard(websocket)
    
    async def execute_crew(self, websocket: WebSocketServerProtocol, request: dict):
        """Execute crew and stream progress."""
        crew_id = request.get("crew_id", f"crew_{datetime.now().timestamp()}")
        user_input = request.get("user_input", "No input provided")
        output_language = request.get("output_language", "English")
        
        # Send start notification
        await websocket.send(json.dumps({
            "type": "crew_started",
            "crew_id": crew_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Prepare payload
        payload = {
            "user_input": user_input,
            "output_language": output_language
        }
        
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
            
            self.active_crews[crew_id] = proc
            
            # Write input
            proc.stdin.write(json.dumps(payload))
            proc.stdin.close()
            
            # Stream progress updates
            progress_count = 0
            for line in proc.stderr:
                if not line.strip():
                    continue
                
                # Check for progress updates
                if line.strip().startswith("{") and '"type":"progress"' in line:
                    try:
                        progress = json.loads(line.strip())
                        progress_count += 1
                        
                        await websocket.send(json.dumps({
                            "type": "progress",
                            "crew_id": crew_id,
                            "data": progress,
                            "count": progress_count,
                            "timestamp": datetime.now().isoformat()
                        }))
                    except json.JSONDecodeError:
                        pass
            
            # Wait for completion
            proc.wait()
            
            # Read result
            stdout = proc.stdout.read()
            try:
                result = json.loads(stdout)
                
                await websocket.send(json.dumps({
                    "type": "crew_completed",
                    "crew_id": crew_id,
                    "result": result,
                    "progress_count": progress_count,
                    "timestamp": datetime.now().isoformat()
                }))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "crew_error",
                    "crew_id": crew_id,
                    "error": "Failed to parse result",
                    "timestamp": datetime.now().isoformat()
                }))
        
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "crew_error",
                "crew_id": crew_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }))
        
        finally:
            if crew_id in self.active_crews:
                del self.active_crews[crew_id]
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connection."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "execute_crew":
                        asyncio.create_task(self.execute_crew(websocket, data))
                    
                    elif msg_type == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    elif msg_type == "list_crews":
                        await websocket.send(json.dumps({
                            "type": "crews_list",
                            "active_crews": list(self.active_crews.keys()),
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Unknown message type: {msg_type}"
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
            print("Install with: pip install websockets")
            return
        
        print(f"[Server] Starting CrewAI WebSocket server...")
        print(f"[Server] Listening on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[Server] Server running. Ready for connections.")
            await asyncio.Future()


def main():
    """Run the WebSocket server."""
    print("=" * 60)
    print("CrewAI WebSocket Server")
    print("=" * 60)
    
    server = CrewAIWebSocketServer(host="localhost", port=8769)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    except Exception as e:
        print(f"\n[Server] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
