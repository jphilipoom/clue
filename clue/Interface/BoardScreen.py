from PyQt5.QtWidgets import QPushButton
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

from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from asyncio import run_coroutine_threadsafe

from server_side_util import (
    # Player,
    SUSPECTS,
    ROOMS,
    WEAPONS,
    LOCATIONS,
)

from msgs.messages import Suggestion, Accusation


class BoardTile(QPushButton):
    def __init__(self, name, is_room=True, orientation=None):
        super().__init__()
        self.name = name
        self.is_room = is_room
        self.players = []

        if is_room:
            self.setFixedSize(100, 100)
        elif orientation == "H":
            self.setFixedSize(100, 70)
        elif orientation == "V":
            self.setFixedSize(70, 100)
        else:
            self.setFixedSize(60, 60)  # fallback/default

        self.update_text()
        self.set_active(False)

    def update_text(self):
        players_text = "\n".join(self.players)
        self.setText(f"{self.name}\n{players_text}")

    def add_player(self, player_name):
        if player_name not in self.players:
            self.players.append(player_name)
            self.update_text()

    def remove_player(self, player_name):
        if player_name in self.players:
            self.players.remove(player_name)
            self.update_text()

    def set_active(self, active):
        self.setEnabled(active)
        if active:
            self.setStyleSheet("background-color: lightgreen; font-size: 10px;")
        else:
            self.setStyleSheet("background-color: lightgray; font-size: 10px;")


class BoardScreen(QWidget):
    tile_clicked = pyqtSignal(str)  # Emits the name of the tile clicked
    update_board_signal = pyqtSignal(dict)  # Signal to send selected character name
    player_turn_signal = pyqtSignal(dict)  # Signal to send selected character name

    player_accusation_signal = pyqtSignal(dict)
    player_suggestion_signal = pyqtSignal(dict)

    will_move = pyqtSignal(bool)
    will_accuse = pyqtSignal(bool)
    will_suggest = pyqtSignal(bool)

    board_dict = {}
    player_accusation_dict = {}
    player_suggestion_dict = {}

    player_name = None

    turn_phase = None
    current_loc = None

    def update_name(self, name):
        player_name = name

    # def __init__(self):
    def __init__(self, websocket_thread, main_window):
        self.main_window = main_window  # Store reference to main window
        self.websocket_thread = websocket_thread
        super().__init__()

        self.tiles = {}  # Dictionary: tile name -> BoardTile

        # Create the layout for the notification bar at the top
        self.notification_label = QLabel("Welcome to the game!")
        self.notification_label.setStyleSheet(
            "background-color: #333; color: white; padding: 5px; font-size: 14px;"
        )

        self.move_button = QPushButton("Move")
        self.move_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "move"),
                self.update_button_vis(),
                self.will_move.emit(True),
            ),
        )
        self.dont_move_button = QPushButton("Don't")
        self.dont_move_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "after_move"),
                self.update_button_vis(),
                self.will_move.emit(False),
            ),
        )

        self.suggestion_button = QPushButton("Suggestion")
        self.suggestion_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "suggest"),
                self.update_button_vis(),
                self.will_suggest.emit(True),
            ),
        )

        self.suggestion_suspect_box = QComboBox()
        self.suggestion_suspect_box.addItems(SUSPECTS)

        self.suggestion_weapons_box = QComboBox()
        self.suggestion_weapons_box.addItems(WEAPONS)

        self.dont_suggestion_button = QPushButton("Don't")
        self.dont_suggestion_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "after_suggest"),
                self.update_button_vis(),
                self.will_suggest.emit(False),
            ),
        )

        self.submit_suggestion_button = QPushButton("Submit Suggestion")
        self.submit_suggestion_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "after_suggest"),
                self.update_button_vis(),
                self.sendSuggestion(),
            ),
        )

        self.accusation_button = QPushButton("Accusation")
        self.accusation_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "accuse"),
                self.update_button_vis(),
                self.will_accuse.emit(True),
            ),
        )

        self.accusation_location_box = QComboBox()
        self.accusation_location_box.addItems(LOCATIONS)

        self.dont_accusation_button = QPushButton("Don't")
        self.dont_accusation_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "after_accusation"),
                self.update_button_vis(),
                self.will_accuse.emit(False),
            ),
        )

        self.submit_accusation_button = QPushButton("Submit Accusation")
        self.submit_accusation_button.clicked.connect(
            lambda: (
                setattr(self, "turn_phase", "after_accusation"),
                self.update_button_vis(),
                self.sendAccusation(),
            ),
        )

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)  # No spacing between cells
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # No outer padding

        self.build_board()

        # Now use a main vertical layout to add the notification bar and board
        self.main_layout = QVBoxLayout(self)  # Use a vertical layout for everything

        # Add the notification bar at the top
        self.main_layout.addWidget(self.notification_label)

        self.buttons = [
            self.move_button,
            self.dont_move_button,
            self.suggestion_button,
            self.dont_suggestion_button,
            self.submit_suggestion_button,
            self.accusation_button,
            self.dont_accusation_button,
            self.submit_accusation_button,
        ]

        [self.main_layout.addWidget(button) for button in self.buttons]
        [button.setVisible(False) for button in self.buttons]

        [
            self.main_layout.addWidget(dropdown)
            for dropdown in [
                self.accusation_location_box,
                self.suggestion_suspect_box,
                self.suggestion_weapons_box,
            ]
        ]
        [
            dropdown.setVisible(False)
            for dropdown in [
                self.accusation_location_box,
                self.suggestion_suspect_box,
                self.suggestion_weapons_box,
            ]
        ]

        self.tile_clicked.connect(
            lambda name: (
                # print("Clicked tile:", name),
                setattr(self, "current_loc", name),
                setattr(self, "turn_phase", "after_move"),
                self.update_button_vis(),
            )
        )

        # Add the board screen (which is your QGridLayout content)
        self.main_layout.addLayout(self.grid_layout)

        self.setLayout(self.main_layout)

        self.websocket_thread.update_board_signal.connect(self.update_board_dict)
        self.websocket_thread.player_turn_signal.connect(self.player_turn_dict)

    def update_board_dict(self, dictionary):
        """Slot to update the player list based on the server's message."""
        self.board_dict = dictionary

        for key in dictionary.keys():
            self.update_player_position(key, None, dictionary[key])

    def player_turn_dict(self, dictionary):
        """Slot to update the player list based on the server's message."""
        self.turn_dict = dictionary

        self.current_loc = dictionary["location"]

        if self.turn_dict["current_turn"]:
            self.notification_label.setText("Your turn!")
            self.turn_phase = "start"
            self.update_button_vis()
        else:
            self.notification_label.setText("It is somebody else's turn")

            self.highlight_valid_moves([])
            print("NOT")

    def update_button_vis(self):

        [button.setVisible(False) for button in self.buttons]

        if self.turn_phase == "start":
            self.move_button.setVisible(True)
            self.dont_move_button.setVisible(True)
        if self.turn_phase == "move":
            self.highlight_valid_moves(self.turn_dict["valid_moves"])
        if self.turn_phase == "after_move":
            self.highlight_valid_moves([])

            # Check in valid room to be making a suggestion
            if not (
                self.current_loc.startswith("H") and self.current_loc[1:].isdigit()
            ):
                self.suggestion_button.setVisible(True)
                self.dont_suggestion_button.setVisible(True)
            else:
                self.turn_phase = "after_suggest"
                self.update_button_vis()
        if self.turn_phase == "suggest":
            [
                dropdown.setVisible(True)
                for dropdown in [
                    self.suggestion_suspect_box,
                    self.suggestion_weapons_box,
                ]
            ]

            self.submit_suggestion_button.setVisible(True)

            # TODO: make dropdowns for all suggestion options, then a submit button
        if self.turn_phase == "after_suggest":
            self.accusation_button.setVisible(True)
            self.dont_accusation_button.setVisible(True)
        if self.turn_phase == "accuse":
            [
                dropdown.setVisible(True)
                for dropdown in [
                    self.accusation_location_box,
                    self.suggestion_suspect_box,
                    self.suggestion_weapons_box,
                ]
            ]
            self.submit_accusation_button.setVisible(True)

        if self.turn_phase == "after_accusation":
            [
                dropdown.setVisible(False)
                for dropdown in [
                    self.accusation_location_box,
                    self.suggestion_suspect_box,
                    self.suggestion_weapons_box,
                ]
            ]

            self.turn_phase = "done"

    def build_board(self):
        # Define board layout (None = empty cell)
        board_layout = [
            ["Study", "H1", "Hall", "H2", "Lounge"],
            ["H3", None, "H4", None, "H5"],
            ["Library", "H6", "Billiard Room", "H7", "Dining Room"],
            ["H8", None, "H9", None, "H10"],
            ["Conservatory", "H11", "Ballroom", "H12", "Kitchen"],
        ]

        for row_idx, row in enumerate(board_layout):
            for col_idx, name in enumerate(row):
                if name:
                    is_room = not (name.startswith("H") and name[1:].isdigit())
                    orientation = None
                    if not is_room:
                        number = int(name[1:])
                        if number in [1, 2, 6, 7, 11, 12]:
                            orientation = "H"
                        else:
                            orientation = "V"
                    tile = BoardTile(
                        name=name, is_room=is_room, orientation=orientation
                    )
                    tile.clicked.connect(lambda _, n=name: self.tile_clicked.emit(n))

                    self.tiles[name] = tile
                    self.grid_layout.addWidget(tile, row_idx, col_idx)

    def update_player_position(self, player_name, from_tile, to_tile):
        if from_tile in self.tiles:
            self.tiles[from_tile].remove_player(player_name)
        if to_tile in self.tiles:
            self.tiles[to_tile].add_player(player_name)

    def highlight_valid_moves(self, valid_tile_names):
        for name, tile in self.tiles.items():
            tile.set_active(name in valid_tile_names)

    def sendAccusation(self):
        suspect = self.suggestion_suspect_box.currentText()
        weapon = self.suggestion_weapons_box.currentText()
        location = self.accusation_location_box.currentText()

        accusation = Accusation(
            self.player_name, location, weapon, suspect=suspect, correct=False
        )
        msg = {"type": "ACCUSATION", "data": accusation.to_dict()}

        self.player_accusation_signal.emit(msg)

    def sendSuggestion(self):
        suspect = self.suggestion_suspect_box.currentText()
        weapon = self.suggestion_weapons_box.currentText()

        suggestion = Suggestion(
            self.player_name, self.current_loc, weapon, suspect=suspect
        )

        msg = {"type": "SUGGESTION", "data": suggestion.to_dict()}

        self.player_suggestion_signal.emit(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    board = BoardScreen()
    board.resize(600, 600)
    board.show()

    # Example test moves
    board.update_player_position("Miss Scarlet", None, "Study")
    board.update_player_position("Colonel Mustard", None, "H1")
    board.highlight_valid_moves(["H3", "H6", "H8"])

    # Print clicked tile name
    # board.tile_clicked.connect(lambda name: print("Clicked tile:", name))

    sys.exit(app.exec_())
