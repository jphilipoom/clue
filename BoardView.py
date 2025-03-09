import arcade
from arcade.gui import (
    NinePatchTexture,
    UIAnchorLayout,
    UIBoxLayout,
    UIButtonRow,
    UIDropdown,
    UIDummy,
    UIFlatButton,
    UIImage,
    UIInputText,
    UILabel,
    UIManager,
    UIMessageBox,
    UIOnActionEvent,
    UIOnChangeEvent,
    UISlider,
    UISpace,
    UISpriteWidget,
    UITextArea,
    UITextureButton,
    UITextureSlider,
    UITextureToggle,
    UIView,
)

BOARD_SIZE = 800 # Board width/height
FRAME_OFFSET = 15
ROOM_SIZE = BOARD_SIZE/4
HALLWAY_WIDTH = ROOM_SIZE/4
HALLWAY_LENGTH = (BOARD_SIZE/8) - FRAME_OFFSET
ROOM_NAMES = ['Conservatory', 'Ballroom', 'Kitchen', 'Library',
              'Billiard Room', 'Dining Room', 'Study', 'Hall', 'Lounge']

def draw_room(room_num):
    if room_num % 3 == 0:
        left_pos = FRAME_OFFSET
    elif room_num % 3 == 1:
        left_pos = (BOARD_SIZE/2) - (ROOM_SIZE/2)
    else:
        left_pos = BOARD_SIZE - (ROOM_SIZE + FRAME_OFFSET)

    if room_num < 3:
        bottom_pos = FRAME_OFFSET
    elif room_num < 6:
        bottom_pos = (BOARD_SIZE/2) - (ROOM_SIZE/2)
    else:
        bottom_pos = BOARD_SIZE - (ROOM_SIZE + FRAME_OFFSET)
    arcade.draw_lbwh_rectangle_filled(left_pos, bottom_pos, ROOM_SIZE, ROOM_SIZE,(214, 214, 214))
    arcade.draw_text(ROOM_NAMES[room_num], left_pos + (ROOM_SIZE/2),
                     bottom_pos + (ROOM_SIZE/2), (0, 0, 0),
                     anchor_x='center', anchor_y='center')
    return

def draw_hallway(hallway_num):
    lb_pos1 = ROOM_SIZE + FRAME_OFFSET
    lb_pos2 = (BOARD_SIZE/2) + (ROOM_SIZE/2)
    if hallway_num % 3 == 0:
        bl_pos = (3/8)*ROOM_SIZE + FRAME_OFFSET
    elif hallway_num % 3 == 1:
        bl_pos = (BOARD_SIZE/2) - (HALLWAY_WIDTH/2)
    else:
        bl_pos = BOARD_SIZE - ((5/8)*ROOM_SIZE) - FRAME_OFFSET
    if hallway_num < 3:
        arcade.draw_lbwh_rectangle_filled(lb_pos1, bl_pos, HALLWAY_LENGTH, HALLWAY_WIDTH,
                                          (150, 150, 150))
        arcade.draw_lbwh_rectangle_filled(lb_pos2, bl_pos, HALLWAY_LENGTH, HALLWAY_WIDTH,
                                          (150, 150, 150))
    else:
        arcade.draw_lbwh_rectangle_filled(bl_pos, lb_pos1, HALLWAY_WIDTH, HALLWAY_LENGTH,
                                          (150, 150, 150))
        arcade.draw_lbwh_rectangle_filled(bl_pos, lb_pos2, HALLWAY_WIDTH, HALLWAY_LENGTH,
                                          (150, 150, 150))

class BoardView(UIView):

    def __init__(self):
        super().__init__()

        arcade.start_render()
        for room_num in range(9):
            draw_room(room_num)
            if room_num < 6:
                draw_hallway(room_num)
        arcade.finish_render()
        arcade.run()

def main():
    window = arcade.Window(title="Clue-less")
    window.show_view(BoardView())
    window.run()


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()