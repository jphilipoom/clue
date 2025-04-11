import asyncio
import websockets
import json
from PyQt5.QtCore import QThread, pyqtSignal

from Player import Player


# WebSocket Thread to handle async communication
class WebSocketThread(QThread):
    player_list_signal = pyqtSignal(list)  # Signal to pass updated player list to GUI
    start_game_signal = pyqtSignal(bool)  # Signal to notify when game can start

    def __init__(self):
        super().__init__()
        self.uri = "ws://localhost:8180"  # WebSocket URL
        self.players = []

    def run(self):
        # WebSocket connection and event loop
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            while True:
                data = await websocket.recv()
                message = json.loads(data)

                message_type = message["type"]

                info = message["data"]

                if message_type == "CHOOSE_PLAYER":
                    print(message)
                    # Update player list from the server message
                    self.players = [Player(x) for x in info["players"]]
                    self.player_list_signal.emit(
                        self.players
                    )  # Emit signal with updated list
