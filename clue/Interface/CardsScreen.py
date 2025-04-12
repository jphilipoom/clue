import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


# TODO: this isn't actually showing yet - need to add it as a part of the board screen or determine what to do with it
class CardsScreen(QWidget):

    def __init__(self, websocket_thread, main_window):
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread
        super().__init__()
        self.initUI(weapon="hi", suspect="someone", location="somewhere")

    def initUI(self, weapon, suspect, location):
        # Create labels and text boxes
        self.label1 = QLabel("Weapon: " + str(weapon))
        self.label2 = QLabel("Suspect: " + str(suspect))
        self.label3 = QLabel("Location: " + str(location))

        # Create button
        self.button = QPushButton("Ready")
        self.button.clicked.connect(self.on_click)

        # Create layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label1)
        vbox.addWidget(self.label2)
        vbox.addWidget(self.label3)
        vbox.addWidget(self.button)

        self.setLayout(vbox)

    def on_click(self):
        print("CLICKED")
        self.main_window.show_board_screen()
