# CrewAI WebSocket Testing

This folder contains test scripts and examples for testing WebSocket-based real-time communication with CrewAI. WebSocket provides bidirectional communication, allowing both server-to-client streaming and client-to-server control messages.

## Overview

WebSocket offers several advantages over SSE for CrewAI integration:
- **Bidirectional Communication**: Client can send control messages (pause, cancel, modify) during execution
- **Lower Overhead**: More efficient than HTTP polling or SSE for frequent updates
- **Real-time Feedback**: Instant two-way communication between frontend and backend
- **Connection Management**: Persistent connection with automatic reconnection support

## Current Status

Per `project-context/2.build/integration.md`:
- **Streaming**: Not implemented (P1 priority)
- **WebSocket**: Not implemented
- **Progress Updates**: Partially implemented (via stderr JSON, collected but not streamed)
- **Step Callback**: Implemented in `crew/run.py` (`_step_callback`)

## Test Files

1. **test_basic_websocket.py** - Basic WebSocket server implementation
2. **test_websocket_client.py** - WebSocket client for testing
3. **test_websocket_crew_integration.py** - CrewAI integration with WebSocket
4. **test_websocket_control_messages.py** - Control message handling (pause, cancel, etc.)
5. **test_websocket_reconnection.py** - Connection management and reconnection
6. **example_websocket_server.py** - Complete WebSocket server example
7. **example_websocket_client.py** - Complete WebSocket client example

## Prerequisites

- Python 3.8+
- CrewAI installed (`pip install crewai`)
- WebSocket library: `pip install websockets` or `pip install fastapi[websockets]`
- Environment variables configured (OPENAI_API_KEY or OPENROUTER_API_KEY)
- Access to the main crew configuration (config/agents.yaml, config/tasks.yaml)

## Running Tests

```bash
# Test basic WebSocket server
python "WebSocket Testing/test_basic_websocket.py"

# Test WebSocket client
python "WebSocket Testing/test_websocket_client.py"

# Test CrewAI integration
python "WebSocket Testing/test_websocket_crew_integration.py"

# Test control messages
python "WebSocket Testing/test_websocket_control_messages.py"

# Test reconnection
python "WebSocket Testing/test_websocket_reconnection.py"
```

## WebSocket Architecture

### Server-Side (Python)
- WebSocket server receives crew execution requests
- Spawns crew process and captures progress updates
- Streams progress updates to connected clients
- Handles control messages (pause, cancel, modify)

### Client-Side (TypeScript/JavaScript)
- Connects to WebSocket server
- Sends crew execution requests
- Receives real-time progress updates
- Can send control messages during execution

## Integration Points

- **Backend**: `crew/run.py` - `_step_callback` writes progress to stderr
- **WebSocket Server**: New server to handle WebSocket connections
- **API**: Can be integrated with Next.js via WebSocket route or separate server
- **Frontend**: `components/ChatRuntimeProvider.tsx` - Ready for WebSocket adapter

## WebSocket vs SSE

| Feature | WebSocket | SSE |
|---------|-----------|-----|
| **Bidirectional** | ✅ Yes | ❌ No (server → client only) |
| **Overhead** | Lower | Higher (HTTP headers) |
| **Reconnection** | Manual | Automatic (browser) |
| **Control Messages** | ✅ Yes | ❌ No |
| **Complexity** | Higher | Lower |
| **Next.js Support** | Requires custom server | Native API routes |

## Notes

- WebSocket requires a persistent connection
- Consider connection limits and scaling
- Implement proper error handling and reconnection logic
- Monitor connection health and cleanup
- Use WebSocket for interactive features, SSE for simple streaming
