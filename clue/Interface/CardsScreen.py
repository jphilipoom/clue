import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class CardsScreen(QWidget):

    def __init__(self, websocket_thread, main_window):
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread
        super().__init__()
        self.initUI(weapon="hi", suspect="someone", location="somewhere")

    def initUI(self, weapon, suspect, location):
        # Create labels and text boxes
        self.label1 = QLabel("Weapon: " + str(weapon))
        # self.textbox1 = QLineEdit()
        self.label2 = QLabel("Suspect: " + str(suspect))
        # self.textbox2 = QLineEdit()
        self.label3 = QLabel("Location: " + str(location))
        # self.textbox3 = QLineEdit()

        # Create button
        self.button = QPushButton("Ready")
        self.button.clicked.connect(self.on_click)

        # Create layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label1)
        # vbox.addWidget(self.textbox1)
        vbox.addWidget(self.label2)
        # vbox.addWidget(self.textbox2)
        vbox.addWidget(self.label3)
        # vbox.addWidget(self.textbox3)
        vbox.addWidget(self.button)

        self.setLayout(vbox)
        # self.show()

    def on_click(self):
        print("LCICKED")
        # text1 = self.textbox1.text()
        # text2 = self.textbox2.text()
        # text3 = self.textbox3.text()
        # print(f"Text Box 1: {text1}, Text Box 2: {text2}, Text Box 3: {text3}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     widget = CardsScreen()
#     sys.exit(app.exec_())
