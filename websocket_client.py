import json
import asyncio
from websockets.asyncio.client import connect
import threading


# IP address of websocket server (Red Pitaya)
RP_IP = "192.168.100.45"
WS_PORT = 8000
HTTP_URL = f"http://{RP_IP}:{WS_PORT}"


class WebSocketClient():
    """
    Handles asynchronous communication with a WebSocket server (e.g., Red Pitaya).
    Continuously listens for incoming messages in a background thread and decodes JSON data.
    """

    def __init__(self):
        """Initializes the client with WebSocket URI and local async event loop"""
        self.uri = f"ws://{RP_IP}:{WS_PORT}/ws"
        self.data_received = None
        self._running = False
        self._loop = asyncio.new_event_loop()

        #asyncio.run(self._connect())

    async def _connect(self):
        """
        Asynchronously connects to the WebSocket server and listens for incoming data.
        Stores the most recent JSON-decoded message in self.data_received.
        """
        try:
            async with connect(self.uri) as websocket:
                print("Connected to WebSocket Server")
                while True:
                    # Waits the server message
                    data = await websocket.recv()
                    self.data_received = json.loads(data)  # JSON decoding
        except Exception as e:
            print(f"Error: {e}")

    def start(self):
        """
        Starts the WebSocket client in a background thread by running the event loop.
        """
        self._running = True
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        """
        Runs the asyncio event loop in a dedicated thread for non-blocking WebSocket communication.
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect())

    def stop(self):
        """
        Stops the WebSocket client by stopping the event loop.
        """
        self._running = False
        self._loop.stop()


if __name__ == "__main__":
    # For standalone testing of the WebSocket client
    websocket_client = WebSocketClient()
    asyncio.run(websocket_client._connect())
