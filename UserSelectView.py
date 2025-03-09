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

DETAILS_FONT = ("arial", "arial Narrow")
DEFAULT_FONT = ("arial", "arial")


class UserSelectView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.uicolor.BLUE_BELIZE_HOLE

        root = self.add_widget(UIAnchorLayout())

        self._body = UIAnchorLayout(size_hint=(1, 1))
        self._body.with_padding(all=20)
        root.add(self._body, anchor_x="right", anchor_y="top")

        # init start widgets
        self._show_character_selection()

    def _show_character_selection(self):
        """Show a short introduction message."""
        self._body.clear()

        # self._body.add(box)

        grid = self._body.add(
            UIGridLayout(
                size_hint=(0, 0),  # wrap children
                row_count=4,  # title | instructions | dropdown | join button
                column_count=2,  # label and input field
                vertical_spacing=10,
                horizontal_spacing=5,
            )
        )
        grid.with_padding(all=50)
        grid.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)

        title = grid.add(
            UILabel(
                text="Select which character you'd like, then click join game",
                width=150,
                font_size=20,
                font_name="arial",
            ),
            column=0,
            row=0,
            column_span=2,
        )

        title.with_padding(bottom=20)

        grid.add(
            UILabel("Select your character!", width=80, font_name="arial"),
            column=0,
            row=1,
        )

        # TODO: instead of using suspects list, at some point should only do remaining characters once calculated
        self.dropdown = UIDropdown(
            default=players.SUSPECTS[0],
            options=players.SUSPECTS,
            size_hint=(1, None),
        )

        grid.add(self.dropdown, column=1, row=1, size_hint=(1, 0.1))

        self.selected_character = players.SUSPECTS[0]

        self.dropdown.on_change = self.on_dropdown_change

        self.join_game_as_character_button = UIFlatButton(
            text="Click Here to Join As {}".format(self.selected_character),
            font_name="arial",
            text_color=arcade.uicolor.WHITE,
            size_hint=(1, None),
        )
        grid.add(
            self.join_game_as_character_button,
            column=0,
            row=3,
            column_span=2,
            size_hint=(1, 0.1),
        )

        self.join_game_as_character_button.on_click = self.join_game_as_character

    def on_dropdown_change(self, event: UIOnChangeEvent | None):
        """Called when the dropdown value changes."""
        self.selected_character = event.new_value
        self.join_game_as_character_button.text = "Click here to join as {}".format(
            self.selected_character
        )

    def join_game_as_character(self, event: UIOnClickEvent | None):
        print("joined the game as " + self.selected_character)
        # user_select_view = UserSelectView()
        #     window.show_view(OptionView())

        # self.window.show_view(UserSelectView.UserSelectView())


def main():
    window = arcade.Window(title="Clue-less")
    window.show_view(UserSelectView())
    window.run()


if __name__ == "__main__":
    main()
