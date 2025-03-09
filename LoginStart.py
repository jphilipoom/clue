"""An overview of all included widgets.

See the other GUI examples for more indepth information about specific widgets.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.2_widgets
"""

from __future__ import annotations

import textwrap
from copy import deepcopy
import players
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
from arcade.gui import UIInputText, UIOnClickEvent, UIView
from arcade.gui.widgets.layout import UIGridLayout, UIAnchorLayout

import BoardView
import UserSelectView
# Load system fonts

DEFAULT_FONT = ("arial", "arial")
DETAILS_FONT = ("arial", "arial Narrow")

# Preload textures, because they are mostly used multiple times, so they are not
# loaded multiple times
TEX_SCROLL_DOWN = arcade.load_texture(":resources:gui_basic_assets/scroll/indicator_down.png")
TEX_SCROLL_UP = arcade.load_texture(":resources:gui_basic_assets/scroll/indicator_up.png")

TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")
TEX_RED_BUTTON_DISABLE = arcade.load_texture(":resources:gui_basic_assets/button/red_disabled.png")

TEX_TOGGLE_RED = arcade.load_texture(":resources:gui_basic_assets/toggle/red.png")
TEX_TOGGLE_GREEN = arcade.load_texture(":resources:gui_basic_assets/toggle/green.png")

TEX_CHECKBOX_CHECKED = arcade.load_texture(":resources:gui_basic_assets/checkbox/blue_check.png")
TEX_CHECKBOX_UNCHECKED = arcade.load_texture(":resources:gui_basic_assets/checkbox/empty.png")

TEX_SLIDER_THUMB_BLUE = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_blue.png")
TEX_SLIDER_TRACK_BLUE = arcade.load_texture(":resources:gui_basic_assets/slider/track_blue.png")
TEX_SLIDER_THUMB_RED = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_red.png")
TEX_SLIDER_TRACK_RED = arcade.load_texture(":resources:gui_basic_assets/slider/track_red.png")
TEX_SLIDER_THUMB_GREEN = arcade.load_texture(":resources:gui_basic_assets/slider/thumb_green.png")
TEX_SLIDER_TRACK_GREEN = arcade.load_texture(":resources:gui_basic_assets/slider/track_green.png")

TEX_NINEPATCH_BASE = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")

TEX_ARCADE_LOGO = arcade.load_texture(":resources:/logo.png")

# Load animation for the sprite widget
frame_textures = []
for i in range(8):
    tex = arcade.load_texture(
        f":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk{i}.png"
    )
    frame_textures.append(tex)

TEX_ANIMATED_CHARACTER = arcade.TextureAnimation(
    [arcade.TextureKeyframe(frame) for frame in frame_textures]
)

TEXT_WIDGET_EXPLANATION = textwrap.dedent("""Welcome""").strip()


class ScrollableTextArea(UITextArea, UIAnchorLayout):
    """This widget is a text area that can be scrolled, like a UITextLayout, but shows indicator,
    that the text can be scrolled."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        indicator_size = 22
        self._down_indicator = UIImage(
            texture=TEX_SCROLL_DOWN, size_hint=None, width=indicator_size, height=indicator_size
        )
        self._down_indicator.visible = False
        self.add(self._down_indicator, anchor_x="right", anchor_y="bottom", align_x=3)

        self._up_indicator = UIImage(
            texture=TEX_SCROLL_UP, size_hint=None, width=indicator_size, height=indicator_size
        )
        self._up_indicator.visible = False
        self.add(self._up_indicator, anchor_x="right", anchor_y="top", align_x=3)

    def on_update(self, dt):
        self._up_indicator.visible = self.layout.view_y < 0
        self._down_indicator.visible = (
            abs(self.layout.view_y) < self.layout.content_height - self.layout.height
        )


class OptionView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.add_widget(UIAnchorLayout())

        # Setup side navigation
        nav_side = UIButtonRow(vertical=True, size_hint=(0.3, 1))
        nav_side.add(
            UILabel(
                "Options",
                font_name="arial",
                font_size=32,
                text_color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE,
                size_hint=(1, 0.1),
                align="center",
            )
        )
        nav_side.add(UISpace(size_hint=(1, 0.01), color=arcade.uicolor.DARK_BLUE_MIDNIGHT_BLUE))

        nav_side.with_padding(all=10)
        nav_side.with_background(color=arcade.uicolor.WHITE_CLOUDS)
        nav_side.add_button("Host Game", font_name="arial", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        nav_side.add_button("Join Game", font_name="arial", style=UIFlatButton.STYLE_BLUE, size_hint=(1, 0.1))
        root.add(nav_side, anchor_x="left", anchor_y="top")

        @nav_side.event("on_action")
        def on_action(event: UIOnActionEvent):
            if event.action == "Host Game":
                self.host_game()
            elif event.action == "Join Game":
                self.join_game()

        # Setup content to show widgets in

        self._body = UIAnchorLayout(size_hint=(0.7, 1))
        self._body.with_padding(all=20)
        root.add(self._body, anchor_x="right", anchor_y="top")

        # init start widgets
        self._show_start_widgets()

    def _show_start_widgets(self):
        """Show a short introduction message."""
        self._body.clear()
        self._body.add(
            UITextArea(
                text=textwrap.dedent("""
                                     
                Welcome to Team East Coast's Rendition of the classic game Clue!
                Choose an option on the left to decide whether you'd like to join an existing game or host your own.
                """).strip(),
                font_name="arial",
                font_size=32,
                text_color=arcade.uicolor.WHITE,
                size_hint=(0.8, 0.8),
            ),
            anchor_y="top",
        )

    def host_game(self):
        self._body.clear()

        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left")
        self._body.add(box)

        box.add(UISpace(size_hint=(0.2, 0.1)))
        text_area = box.add(
            UITextArea(
                text=textwrap.dedent("""
                       Your host id is: ABC123, share this with any friends who want to join!
                    """).strip(),
                font_name="arial",
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                size_hint=(1, 0.4),
            )
        )

        players_joined =box.add(
            UITextArea(
                text=textwrap.dedent("""
                       The following players have joined:
                    """).strip(),
                font_name="arial",
                font_size=16,
                text_color=arcade.uicolor.WHITE,
                size_hint=(1, 0.4),
            )
        )

        self.host_start_game_button = box.add(
            UIFlatButton(text="Click to Start Once All Players Have Joined", height=30, width=150, size_hint=(1, None)),
        )

        self.host_start_game_button.on_click = self.on_start_game_host

        
        text_area.with_padding(left=10, right=10)
        text_area.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)

        players_joined.with_padding(left=10, right=10)
        players_joined.with_border(color=arcade.uicolor.GRAY_CONCRETE, width=2)


    def join_game(self):
        self._body.clear()

        box = UIBoxLayout(vertical=True, size_hint=(1, 1), align="left")
        self._body.add(box)

        grid = box.add(UIGridLayout(
            size_hint=(0, 0),  # wrap children
            row_count=4,  # title | host id | join button
            column_count=2,  # label and input field
            vertical_spacing=10,
            horizontal_spacing=5,
        ))
        grid.with_padding(all=50)
        grid.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)

        title = grid.add(
            UILabel(text="Enter Host's Game Id", width=150, font_size=20, font_name="arial"),
            column=0,
            row=0,
            column_span=2,
        )
        
        title.with_padding(bottom=20)

        grid.add(UILabel(text="Game Id:", width=80, font_name="arial"), column=0, row=1)
        self.game_id_input = grid.add(
            UIInputText(width=150, font_name="arial"), column=1, row=1
        )

        self.join_button = grid.add(
            UIFlatButton(text="Join Game", height=30, width=150,font_name="arial", size_hint=(1, None)),
            column=0,
            row=3,
            column_span=2,
        )

        self.join_button.on_click = self.on_join_game

    def on_join_game(self, event: UIOnClickEvent | None):
        print("joined the game with id : " + self.game_id_input.text.strip())
        user_select_view = UserSelectView.UserSelectView()
        # board_view = BoardView.BoardView()
        self.window.show_view(user_select_view)

    def on_start_game_host(self, event: UIOnClickEvent | None):
        print("joined the game")
        # user_select_view = UserSelectView()
        #     window.show_view(OptionView())

        self.window.show_view(UserSelectView.UserSelectView())



def main():
    window = arcade.Window(title="Clue-less")
    window.show_view(OptionView())
    window.run()


if __name__ == "__main__":
    main()