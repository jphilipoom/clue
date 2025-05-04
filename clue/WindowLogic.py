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

from Interface.Websocket import WebSocketThread

# import StartScreen, LobbyScreen, PlayerSelectScreen
from Interface.StartScreen import StartScreen
from Interface.LobbyScreen import LobbyScreen
from Interface.PlayerSelectScreen import PlayerSelectScreen
from Interface.Player import DumbPlayer
from Interface.CardsScreen import CardsScreen
from Interface.BoardScreen import BoardScreen

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
import sys
from PyQt5.QtCore import QThread, pyqtSignal


class MainWindow(QWidget):
    character_selected_signal = pyqtSignal(
        dict
    )  # Signal to get selected character name

    def __init__(self):
        super().__init__()
        self.player_name = None

        # Create layout to manage screens
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Initialize WebSocket thread
        self.websocket_thread = WebSocketThread()
        self.websocket_thread.start()  # Start the WebSocket thread

        # Create screens
        self.start_screen = StartScreen(self.websocket_thread, self)
        self.player_select_screen = PlayerSelectScreen(self.websocket_thread, self)
        self.lobby_screen = LobbyScreen(self.websocket_thread, self)
        self.cards_screen = CardsScreen(self.websocket_thread, self)
        self.board_screen = BoardScreen(self.websocket_thread, self)

        # send data from player select screen to websocket to send update data to server
        self.player_select_screen.character_selected_signal.connect(
            self.websocket_thread.on_character_selected
        )
        # send data from player select screen to here to update window title with player name
        self.player_select_screen.character_selected_signal.connect(
            self.on_character_selected
        )

        self.board_screen.tile_clicked.connect(self.websocket_thread.on_character_moved)
        self.board_screen.set_will_accuse.connect(self.websocket_thread.set_will_accuse)
        self.board_screen.set_will_suggest.connect(
            self.websocket_thread.set_will_suggest
        )
        self.board_screen.set_will_move.connect(self.websocket_thread.set_will_move)

        self.board_screen.player_accusation_signal.connect(
            self.websocket_thread.handle_accusation
        )

        self.board_screen.player_suggestion_signal.connect(
            self.websocket_thread.handle_suggestion
        )

        self.board_screen.player_response_suggestion_signal.connect(
            self.websocket_thread.handle_suggestion_response
        )

        # Initially show the start screen
        self.layout.addWidget(self.start_screen)

    def show_player_select_screen(self):
        # Remove the current screen and show the player select screen
        self.clear_layout()
        self.layout.addWidget(self.player_select_screen)

    def on_character_selected(self, character_selected_dict):
        character_name = character_selected_dict["selected_player"]
        self.player_name = character_name
        self.setWindowTitle(f"Clue - {character_name}")

        self.lobby_screen = LobbyScreen(
            self.websocket_thread, self, player_name=character_name
        )

    def show_lobby_screen(self):
        # Remove the current screen and show the lobby screen
        self.clear_layout()
        self.layout.addWidget(self.lobby_screen)

    def show_cards_screen(self):
        # Remove the current screen and show the lobby screen
        self.clear_layout()
        self.layout.addWidget(self.cards_screen)

    def show_board_screen(self):
        # Remove the current screen and show the lobby screen
        self.clear_layout()
        self.board_screen.update_name(self.player_name)
        self.layout.addWidget(self.board_screen)

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
