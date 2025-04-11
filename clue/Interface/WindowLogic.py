import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QComboBox,
)

from Websocket import WebSocketThread

# import StartScreen, LobbyScreen, PlayerSelectScreen
from StartScreen import StartScreen
from LobbyScreen import LobbyScreen
from PlayerSelectScreen import PlayerSelectScreen
from Player import Player

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
import sys
from PyQt5.QtCore import QThread, pyqtSignal


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.player_name = None

        # Create layout to manage screens
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize WebSocket thread
        # Initialize WebSocket thread and pass the WebSocket URL
        self.websocket_thread = WebSocketThread()
        self.websocket_thread.start()  # Start the WebSocket thread

        # Create screens
        self.start_screen = StartScreen(self)
        self.player_select_screen = PlayerSelectScreen(self.websocket_thread, self)
        self.lobby_screen = LobbyScreen()

        self.player_select_screen.character_selected.connect(self.on_character_selected)

        # Initially show the start screen
        self.layout.addWidget(self.start_screen)

    def show_player_select_screen(self):
        # Remove the current screen and show the player select screen
        self.clear_layout()
        self.layout.addWidget(self.player_select_screen)

        # Simulate receiving the player list from the server
        simulated_players = [
            Player("Dumb"),
            Player("Two"),
            Player("Three"),
        ]

        # Emit the signal to update the player list AFTER the PlayerSelectScreen is shown
        self.player_select_screen.update_players_signal.emit(simulated_players)

    def on_character_selected(self, name):
        self.player_name = name
        self.setWindowTitle(f"Clue - {name}")

        self.lobby_screen = LobbyScreen(player_name=name)

    def show_lobby_screen(self):
        # Remove the current screen and show the lobby screen
        self.clear_layout()
        self.layout.addWidget(self.lobby_screen)

    def clear_layout(self):
        # Remove all widgets from the layout to clear it for the new screen
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Clue")
    window.setGeometry(100, 100, 400, 300)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
