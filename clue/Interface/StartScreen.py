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


class StartScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # Store reference to main window

        layout = QVBoxLayout()
        button = QPushButton("Join Game")
        button.clicked.connect(self.on_join_game)
        layout.addWidget(button)
        self.setLayout(layout)

    def on_join_game(self):
        # Switch to the next screen when the button is clicked
        self.main_window.show_player_select_screen()
