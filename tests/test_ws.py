import asyncio
import websockets

import requests

async def test_connection():
    # Test HTTP first
    try:
        r = requests.get("http://127.0.0.1:8000/stats")
        print(f"HTTP /stats status: {r.status_code}")
    except Exception as e:
        print(f"HTTP failed: {e}")

    uri = "ws://127.0.0.1:8000/ws/neural-link"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to WebSocket!")
            await websocket.send("Hello")
            print("Sent message")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
