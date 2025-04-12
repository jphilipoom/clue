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
    choose_players_dict = {"start": False}
    startable = False

    def __init__(self, websocket_thread, main_window, player_name="Unknown??"):
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread

        super().__init__()
        layout = QVBoxLayout()

        self.button = QPushButton("Start Game")

        self.startable = False
        # TODO: update based on whether enough players entered - need signal for this
        self.button.setEnabled(
            self.startable
        )  # self.choose_players_dict["start"])  # Initially disabled
        self.button.clicked.connect(self.on_join_game)

        layout.addWidget(QLabel(f"Welcome {player_name}, waiting for others..."))

        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle(f"Clue - {player_name}")

        self.websocket_thread.choose_player_signal.connect(self.choose_player_update)

    def on_join_game(self):
        # Switch to the next screen when the button is clicked
        if self.startable:
            print("ON JOIN???")
            self.main_window.show_cards_screen()
        else:
            print("DISABLED")

    def choose_player_update(self, choose_players_dict):
        """Slot to update the player list based on the server's message."""

        self.choose_players_dict = choose_players_dict
        # print(self.choose_players_dict["start"])
        # self.button.setEnabled(
        #     len(self.choose_players_dict["players"]) < 5
        # )  # Initially disabled
        self.startable = self.choose_players_dict[
            "start"
        ]  # len(self.choose_players_dict["players"]) <= 4
        self.button.setEnabled(self.startable)  # Initially disabled
        print("enabled? " + str(self.startable))
        self.button.repaint()
        self.repaint()
        # self.set_characters(players)
