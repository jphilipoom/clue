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


class LobbyScreen(QWidget):
    def __init__(self, websocket_thread, main_window, player_name="Unknown??"):

        super().__init__()
        layout = QVBoxLayout()

        button = QPushButton("Start Game")

        # TODO: update based on whether enough players entered - need signal for this
        button.setEnabled(False)  # Initially disabled
        layout.addWidget(QLabel(f"Welcome {player_name}, waiting for others..."))

        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle(f"Clue - {player_name}")
