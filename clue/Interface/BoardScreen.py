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


class BoardTile(QPushButton):
    def __init__(self, name, is_room=True, orientation=None):
        super().__init__()
        self.name = name
        self.is_room = is_room
        self.players = []

        if is_room:
            self.setFixedSize(100, 100)
        elif orientation == "H":
            self.setFixedSize(100, 40)
        elif orientation == "V":
            self.setFixedSize(40, 100)
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

    def __init__(self):
        super().__init__()

        self.tiles = {}  # Dictionary: tile name -> BoardTile
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.grid_layout.setSpacing(0)  # No spacing between cells
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # No outer padding

        self.build_board()

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
    board.tile_clicked.connect(lambda name: print("Clicked tile:", name))

    sys.exit(app.exec_())


# if __name__ == "__main__":
#     main()
