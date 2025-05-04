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


class LobbyScreen(QWidget):
    def __init__(self, websocket_thread, main_window, player_name="Unknown??"):
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread

        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Welcome {player_name}, waiting for others..."))

        self.setLayout(layout)
        self.setWindowTitle(f"Clue - {player_name}")

        self.websocket_thread.send_board_signal.connect(self.show_board_dict_rename)

    def show_board_dict_rename(self, dictionary):
        """Make sure all players at board screen when dict is sent"""

        self.main_window.show_board_screen()
        # set to board screen
