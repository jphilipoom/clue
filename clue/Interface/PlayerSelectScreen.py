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
from LobbyScreen import LobbyScreen


class PlayerSelectScreen(QWidget):
    update_players_signal = pyqtSignal(list)  # Signal to update players list
    character_selected = pyqtSignal(str)  # Signal to send selected character name

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

        # Connect signal to slot
        self.websocket_thread.player_list_signal.connect(self.update_player_list)

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
        self.character_selected.emit(selected)
        self.main_window.show_lobby_screen()
