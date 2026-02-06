"""
Test WebSocket control messages (pause, cancel, modify).
Demonstrates bidirectional communication for controlling crew execution.
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from enum import Enum

# Try to import websockets
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


class CrewStatus(Enum):
    """Crew execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ERROR = "error"


class ControllableCrewServer:
    """WebSocket server with crew execution control."""
    
    def __init__(self, host: str = "localhost", port: int = 8768):
        self.host = host
        self.port = port
        self.clients: dict = {}
        self.crews: dict = {}  # crew_id -> status
    
    async def handle_control_message(self, websocket, message: dict):
        """Handle control messages."""
        msg_type = message.get("type")
        crew_id = message.get("crew_id")
        
        if msg_type == "pause_crew":
            if crew_id in self.crews and self.crews[crew_id] == CrewStatus.RUNNING:
                self.crews[crew_id] = CrewStatus.PAUSED
                await websocket.send(json.dumps({
                    "type": "crew_paused",
                    "crew_id": crew_id,
                    "timestamp": datetime.now().isoformat()
                }))
                return True
        
        elif msg_type == "resume_crew":
            if crew_id in self.crews and self.crews[crew_id] == CrewStatus.PAUSED:
                self.crews[crew_id] = CrewStatus.RUNNING
                await websocket.send(json.dumps({
                    "type": "crew_resumed",
                    "crew_id": crew_id,
                    "timestamp": datetime.now().isoformat()
                }))
                return True
        
        elif msg_type == "cancel_crew":
            if crew_id in self.crews:
                self.crews[crew_id] = CrewStatus.CANCELLED
                await websocket.send(json.dumps({
                    "type": "crew_cancelled",
                    "crew_id": crew_id,
                    "timestamp": datetime.now().isoformat()
                }))
                return True
        
        elif msg_type == "get_status":
            status = self.crews.get(crew_id, CrewStatus.PENDING)
            await websocket.send(json.dumps({
                "type": "crew_status",
                "crew_id": crew_id,
                "status": status.value,
                "timestamp": datetime.now().isoformat()
            }))
            return True
        
        return False
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connection."""
        client_id = f"client_{datetime.now().timestamp()}"
        self.clients[client_id] = websocket
        
        await websocket.send(json.dumps({
            "type": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    # Handle control messages
                    if msg_type in ["pause_crew", "resume_crew", "cancel_crew", "get_status"]:
                        handled = await self.handle_control_message(websocket, data)
                        if not handled:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"Failed to handle {msg_type}",
                                "crew_id": data.get("crew_id")
                            }))
                    
                    elif msg_type == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
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
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def start(self):
        """Start the server."""
        if not WEBSOCKETS_AVAILABLE:
            return
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[Server] Control server running on ws://{self.host}:{self.port}")
            await asyncio.Future()


async def test_control_messages():
    """Test control message handling."""
    print("=" * 60)
    print("Test: WebSocket Control Messages")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("⚠ websockets library not available")
        return False
    
    server = ControllableCrewServer(host="localhost", port=8768)
    
    # Initialize a test crew
    server.crews["test_crew_1"] = CrewStatus.RUNNING
    
    print("\n[1/4] Starting control server...")
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    
    print("\n[2/4] Testing pause/resume...")
    try:
        async with websockets.connect("ws://localhost:8768") as ws:
            # Receive connection message
            await ws.recv()
            
            # Test pause
            await ws.send(json.dumps({
                "type": "pause_crew",
                "crew_id": "test_crew_1"
            }))
            response = await ws.recv()
            data = json.loads(response)
            print(f"  -> {data.get('type')}: {data.get('crew_id')}")
            
            # Test resume
            await ws.send(json.dumps({
                "type": "resume_crew",
                "crew_id": "test_crew_1"
            }))
            response = await ws.recv()
            data = json.loads(response)
            print(f"  -> {data.get('type')}: {data.get('crew_id')}")
    
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    
    print("\n[3/4] Testing cancel...")
    server.crews["test_crew_2"] = CrewStatus.RUNNING
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    
    try:
        async with websockets.connect("ws://localhost:8768") as ws:
            await ws.recv()
            
            await ws.send(json.dumps({
                "type": "cancel_crew",
                "crew_id": "test_crew_2"
            }))
            response = await ws.recv()
            data = json.loads(response)
            print(f"  -> {data.get('type')}: {data.get('crew_id')}")
    
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    
    print("\n[4/4] Testing status query...")
    server.crews["test_crew_3"] = CrewStatus.RUNNING
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)
    
    try:
        async with websockets.connect("ws://localhost:8768") as ws:
            await ws.recv()
            
            await ws.send(json.dumps({
                "type": "get_status",
                "crew_id": "test_crew_3"
            }))
            response = await ws.recv()
            data = json.loads(response)
            print(f"  -> Status: {data.get('status')}")
    
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
    
    print("\n[OK] Control message tests completed")
    return True


async def main():
    """Run control message tests."""
    print("\n" + "=" * 60)
    print("CrewAI WebSocket Testing - Control Messages")
    print("=" * 60)
    
    result = await test_control_messages()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Control Messages: {'[OK] Passed' if result else '[FAIL] Failed'}")
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
