#!/usr/bin/env python
from typing import Optional

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.styles import Style, style_from_pygments_cls
from prompt_toolkit.widgets import Label
from pygments.styles import get_style_by_name

from sbx_core.card import Card
from sbx_core.ui.controls import MarkdownArea

MARKDOWN_STYLE = style_from_pygments_cls(get_style_by_name('monokai'))


class EditorInterface:
    def __init__(self, card: Card):
        self._card = card
        self._label_text_parts = ["Press Ctrl+e to exit, Ctrl+s to save, Ctrl+arrows to change focus", "--NAVIGATION--"]
        self._create_ui()

    def _create_ui(self):
        self.text_area_front = MarkdownArea()
        self.text_area_front.text = self._card.front
        self.text_area_back = MarkdownArea()
        self.text_area_back.text = self._card.back
        self.label = Label(text=self._get_label_text, style="class:status")
        root_container = HSplit(
            [
                VSplit(
                    [
                        self.text_area_front,
                        self.text_area_back
                    ]
                ),
                self.label
            ]
        )

        self.layout = Layout(container=root_container, focused_element=self.text_area_front)
        self._set_key_bindings()

        # Styling.
        style = Style(
            [
                ("status", "bg:#00ff00 #000000"),
            ] + MARKDOWN_STYLE.style_rules
        )
        self.application = Application(
            layout=self.layout, key_bindings=self.kb, style=style, full_screen=True,
            editing_mode=EditingMode.VI, before_render=self.before_render, paste_mode=False
        )

    def before_render(self, app: Application):
        if app.vi_state.input_mode == InputMode.NAVIGATION:
            self._label_text_parts[1] = "--NAVIGATION--"
        if app.vi_state.input_mode == InputMode.INSERT_MULTIPLE:
            self._label_text_parts[1] = "--INSERT (MULTI)--"
        if app.vi_state.input_mode == InputMode.REPLACE:
            self._label_text_parts[1] = "--REPLACE--"
        if app.vi_state.input_mode == InputMode.INSERT:
            self._label_text_parts[1] = "--INSERT--"
        if app.vi_state.recording_register is not None:
            self._label_text_parts[1] = "recording..."

    def _get_label_text(self):
        return " | ".join(self._label_text_parts)

    def _indent(self, _):
        text = self._current_text_area()
        if text:
            text.indent()

    def _save(self, _):
        self._card.back = self.text_area_back.text
        self._card.front = self.text_area_front.text
        self._card.save()

    def _current_text_area(self) -> Optional[MarkdownArea]:
        if not self.layout.buffer_has_focus:
            return None
        buffer = self.layout.current_control
        if id(buffer) == id(self.text_area_front.control):
            return self.text_area_front
        elif id(buffer) == id(self.text_area_back.control):
            return self.text_area_back
        return None

    def _navigation(self, _):
        self.application.vi_state.input_mode = InputMode.NAVIGATION

    def _set_key_bindings(self):
        self.kb = KeyBindings()

        actions = {
            "indent": self._indent,
            "exit": self._exit_clicked,
            "next": focus_next,
            "prev": focus_previous,
            "navigation": self._navigation,
            "save": self._save
        }
        key_bindings = {
            "indent": "tab",
            "exit": "c-e",
            "next": "c-right,c-up",
            "prev": "c-left,c-down",
            "navigation": "escape",
            "save": "c-s",
        }

        for action, keys in key_bindings.items():
            for key in keys.split(","):
                try:
                    self.kb.add(key.strip())(actions[action])
                except KeyError:
                    pass

    @staticmethod
    def _exit_clicked(_=None):
        get_app().exit()

    def run(self):
        # Start in the insertion mode
        self.application.vi_state.input_mode = InputMode.INSERT
        self.application.run()
