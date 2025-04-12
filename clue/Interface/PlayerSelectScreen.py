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
from PyQt5.QtCore import QThread, pyqtSignal
from Interface.LobbyScreen import LobbyScreen


class PlayerSelectScreen(QWidget):
    update_players_signal = pyqtSignal(list)  # Signal to update players list
    character_selected_signal = pyqtSignal(
        dict
    )  # Signal to send selected character name

    choose_players_dict = {"start": False}
    startable = False

    def __init__(self, websocket_thread, main_window):
        super().__init__()
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread

        self.layout = QVBoxLayout()
        self.character_dropdown = QComboBox()

        # Initially add a label and a dropdown to the layout
        label = QLabel("Select your character:")
        self.layout.addWidget(label)
        self.layout.addWidget(self.character_dropdown)

        # Add a button to proceed to the lobby
        button = QPushButton("Enter Lobby")
        button.clicked.connect(self.on_enter_lobby)
        self.layout.addWidget(button)

        self.setLayout(self.layout)

        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.on_start_game)
        # Connect signal to slot
        self.websocket_thread.player_list_signal.connect(self.update_player_list)
        self.websocket_thread.choose_player_signal.connect(self.choose_player_update)

    def set_characters(self, characters):
        """Set the list of characters in the dropdown."""
        self.character_dropdown.clear()  # Clear any existing options
        self.character_dropdown.addItems(
            [str(character) for character in characters]
        )  # Add new options

    def update_player_list(self, players):
        """Slot to update the player list based on the server's message."""
        self.set_characters(players)

    def on_enter_lobby(self):
        # Switch to the lobby screen after entering lobby
        selected = self.character_dropdown.currentText()
        self.character_selected_signal.emit(
            {"selected_player": selected, "start": False}
        )
        self.main_window.show_lobby_screen()

    def on_start_game(self):
        # Switch to the lobby screen after entering lobby
        selected = self.character_dropdown.currentText()
        self.character_selected_signal.emit(
            {"selected_player": selected, "start": True}
        )
        self.main_window.show_board_screen()

    def choose_player_update(self, choose_players_dict):
        """Slot to update the player list based on the server's message."""

        self.choose_players_dict = choose_players_dict

        self.startable = len(self.choose_players_dict["players"]) <= 4

        if self.startable:
            # Add a button to proceed to the lobby
            print("GAME IS STARTABLE")
            self.layout.addWidget(self.start_button)
