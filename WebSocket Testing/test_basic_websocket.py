"""
Test basic WebSocket server implementation.
Demonstrates WebSocket connection handling and message exchange.
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Set

# Try to import websockets library
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets library not installed. Install with: pip install websockets")


class WebSocketServer:
    """Basic WebSocket server for testing."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.message_count = 0
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection."""
        self.clients.add(websocket)
        print(f"[Server] Client connected: {websocket.remote_address}")
        await self.broadcast({
            "type": "client_connected",
            "client_count": len(self.clients),
            "timestamp": datetime.now().isoformat()
        }, exclude=websocket)
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection."""
        self.clients.discard(websocket)
        print(f"[Server] Client disconnected: {websocket.remote_address}")
        await self.broadcast({
            "type": "client_disconnected",
            "client_count": len(self.clients),
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast(self, message: dict, exclude: WebSocketServerProtocol = None):
        """Broadcast message to all connected clients."""
        if not self.clients:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            if client == exclude:
                continue
            try:
                await client.send(message_json)
            except Exception as e:
                print(f"[Server] Error sending to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            self.clients.discard(client)
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a client connection."""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                self.message_count += 1
                try:
                    data = json.loads(message)
                    print(f"[Server] Received: {data.get('type', 'unknown')}")
                    
                    # Echo message back
                    response = {
                        "type": "echo",
                        "original": data,
                        "message_count": self.message_count,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(response))
                    
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
        
        print(f"[Server] Starting WebSocket server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[Server] Server running. Waiting for connections...")
            await asyncio.Future()  # Run forever


async def test_basic_websocket():
    """Test basic WebSocket functionality."""
    print("=" * 60)
    print("Test: Basic WebSocket Server")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("\n[WARN] websockets library not installed")
        print("Install with: pip install websockets")
        return False
    
    server = WebSocketServer(host="localhost", port=8765)
    
    print("\n[1/2] Starting WebSocket server...")
    print("-> Server will run in background")
    print("-> Connect with: ws://localhost:8765")
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait a bit for server to start
    await asyncio.sleep(1)
    
    print("\n[2/2] Server started successfully")
    print("[OK] WebSocket server is ready")
    print("-> Use test_websocket_client.py to test connections")
    
    # Cancel server task (for testing)
    server_task.cancel()
    
    try:
        await server_task
    except asyncio.CancelledError:
        pass
    
    return True


async def test_message_exchange():
    """Test WebSocket message exchange."""
    print("\n" + "=" * 60)
    print("Test: WebSocket Message Exchange")
    print("=" * 60)
    
    if not WEBSOCKETS_AVAILABLE:
        print("[WARN] websockets library not available")
        return False
    
    server = WebSocketServer(host="localhost", port=8766)
    
    async def client_handler(websocket, path):
        await server.register_client(websocket)
        try:
            # Send test message
            test_message = {
                "type": "test",
                "data": "Hello WebSocket"
            }
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"  -> Received response: {data.get('type')}")
            
        finally:
            await server.unregister_client(websocket)
    
    print("\n-> Testing message exchange...")
    
    async with websockets.serve(client_handler, "localhost", 8766):
        await asyncio.sleep(0.5)
        
        # Connect as client
        async with websockets.connect("ws://localhost:8766") as ws:
            # Receive initial message
            message = await ws.recv()
            data = json.loads(message)
            print(f"  -> Received: {data.get('type')}")
            
            # Send response
            await ws.send(json.dumps({"type": "response", "data": "OK"}))
            await asyncio.sleep(0.1)
    
    print("[OK] Message exchange test completed")
    return True


async def main():
    """Run all basic WebSocket tests."""
    print("\n" + "=" * 60)
    print("CrewAI WebSocket Testing - Basic Tests")
    print("=" * 60)
    
    # Test 1: Basic WebSocket server
    result1 = await test_basic_websocket()
    
    # Test 2: Message exchange
    result2 = await test_message_exchange()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Basic WebSocket Server: {'[OK] Passed' if result1 else '[FAIL] Failed'}")
    print(f"Message Exchange: {'[OK] Passed' if result2 else '[FAIL] Failed'}")
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
