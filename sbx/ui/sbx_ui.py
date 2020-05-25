#!/usr/bin/env python

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
# from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window, BufferControl
from prompt_toolkit.styles import Style, style_from_pygments_cls
from prompt_toolkit.widgets import Label
from pygments.styles import get_style_by_name

from sbx.ui.controls import MarkdownArea

MARKDOWN_STYLE = style_from_pygments_cls(get_style_by_name('monokai'))

buffer1 = Buffer()  # Editable buffer.


class UserInterface:
    def __init__(self):
        self._create_ui()

    def _create_ui(self):
        # All the widgets for the UI.
        self.text_area_front = MarkdownArea()
        self.text_area_front.text = "# Front"

        self.text_area_back = MarkdownArea()
        self.text_area_back.text = "# Back"
        self.x = Window(content=BufferControl(buffer=buffer1, include_default_input_processors=False))
        root_container = HSplit(
            [
                Label(text="Press `Ctrl+e` to exit."),
                VSplit(
                    [
                        self.x,
                        self.text_area_front,
                        self.text_area_back
                    ]
                ),
            ]
        )

        layout = Layout(container=root_container, focused_element=self.x)
        self._set_key_bindings()

        # Styling.
        style = Style(
            [
                ("left-pane", "bg:#888800 #000000"),
                ("right-pane", "bg:#00aa00 #000000"),
                ("button", "#000000"),
                ("button-arrow", "#000000"),
                ("button focused", "bg:#ff0000"),
                ("red", "#ff0000"),
                ("green", "#00ff00"),
            ] + MARKDOWN_STYLE.style_rules
        )
        self.application = Application(
            layout=layout, key_bindings=self.kb, style=style, full_screen=True, mouse_support=True,
        )

    def tab(self):
        self.text_area_front.indent()

    def _set_key_bindings(self):
        self.kb = KeyBindings()

        actions = {
            "indent": self.tab,
            "exit": self._exit_clicked
        }
        key_bindings = {
            "indent": "tab",
            "exit": "c-e"
        }

        for action, keys in key_bindings:
            for key in keys.split(","):
                try:
                    self.kb.add(key.strip())(actions[action])
                except KeyError:
                    pass

    @staticmethod
    def _exit_clicked(_=None):
        get_app().exit()

    def run(self):
        self.application.run()


def main():
    UserInterface().run()


if __name__ == "__main__":
    main()
