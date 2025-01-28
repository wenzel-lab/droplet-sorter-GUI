import json
import asyncio
from websockets.asyncio.client import connect
import threading


# Dirección del servidor WebSocket (Red Pitaya)
RP_IP = "192.168.31.29"
WS_PORT = 8000
HTTP_URL = f"http://{RP_IP}:{WS_PORT}"


class WebSocketClient():

    def __init__(self):
        self.uri = f"ws://{RP_IP}:{WS_PORT}/ws"
        self.data_received = None
        self._running = False
        self._loop = asyncio.new_event_loop()

        #asyncio.run(self._connect())

    async def _connect(self):
        try:
            async with connect(self.uri) as websocket:
                print("Conectado al servidor WebSocket")
                while True:
                    # Espera mensajes del servidor
                    data = await websocket.recv()
                    self.data_received = json.loads(data)  # Decodificar JSON
        except Exception as e:
            print(f"Error: {e}")

    def start(self):
        """
        Inicia el cliente WebSocket en un hilo.
        """
        self._running = True
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        """
        Inicia el bucle de eventos asincrónico en un hilo.
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect())

    def stop(self):
        """
        Detiene el cliente WebSocket.
        """
        self._running = False
        self._loop.stop()


if __name__ == "__main__":
    websocket_client = WebSocketClient()
    asyncio.run(websocket_client._connect())


