"""
Built in editor
"""
from typing import Optional

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.layout import HSplit, Layout, VSplit
from prompt_toolkit.styles import Style, style_from_pygments_cls
from prompt_toolkit.widgets import Label
from pygments.styles import get_style_by_name

from sbx.core.card import Card
from sbx.core.utility import simplify_path
from sbx.ui.controls import BaseUi, MarkdownArea

MARKDOWN_STYLE = style_from_pygments_cls(get_style_by_name("vim"))
TITLE = "---- SBX - Flashcards ----"
VI_STATUS_CELL = 3
PATH_CELL = 1


class EditorInterface(BaseUi):
    """
    UI class for built in editor
    """

    def __init__(self, card: Optional[Card]):
        super().__init__()
        self._card = card
        path = "-"
        if card:
            path = simplify_path(card.path)
        self._label_text_parts = [
            "SBX",
            path,
            "Press F1 for help",
            "--NAVIGATION--",
        ]
        self._create_ui()
        self._saved = False

    def _create_ui(self):
        self.layout = self.create_root_layout(
            container=self._get_base_layout(),
            focused_element=self.text_area_front,
        )
        self.create_key_bindings()
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self._get_style(),
            full_screen=True,
            editing_mode=EditingMode.VI,
            before_render=self.before_render,
            paste_mode=False,
        )

    def _get_style(self):
        return Style(
            [
                ("status", "bg:ansigreen ansiblack"),
                ("button", "ansiblack"),
                ("button-arrow", "ansiblack"),
                ("button focused", "bg:ansired"),
                ("main-panel", "bg:ansiblack"),
            ]
            + MARKDOWN_STYLE.style_rules
        )

    def _get_base_layout(self):
        self.text_area_front = MarkdownArea()
        self.text_area_front.text = self._card.front
        self.text_area_back = MarkdownArea()
        self.text_area_back.text = self._card.back
        self.label = Label(text=self._get_label_text, style="class:status")
        root_container = HSplit(
            [
                VSplit(
                    [
                        HSplit(
                            [
                                Label(
                                    text="[Flashcard Front]",
                                    style="class:status",
                                ),
                                self.text_area_front,
                            ]
                        ),
                        HSplit(
                            [
                                Label(
                                    text="[Flashcard Back]",
                                    style="class:status",
                                ),
                                self.text_area_back,
                            ]
                        ),
                    ]
                ),
                self.label,
            ],
            style="class:main-panel",
        )
        return root_container

    def before_render(self, app: Application):
        if app.vi_state.input_mode == InputMode.NAVIGATION:
            self._label_text_parts[VI_STATUS_CELL] = "--NAVIGATION--"
        if app.vi_state.input_mode == InputMode.INSERT_MULTIPLE:
            self._label_text_parts[VI_STATUS_CELL] = "--INSERT (MULTI)--"
        if app.vi_state.input_mode == InputMode.REPLACE:
            self._label_text_parts[VI_STATUS_CELL] = "--REPLACE--"
        if app.vi_state.input_mode == InputMode.INSERT:
            self._label_text_parts[VI_STATUS_CELL] = "--INSERT--"
        if app.vi_state.recording_register is not None:
            self._label_text_parts[VI_STATUS_CELL] = "recording..."

    def _get_label_text(self):
        return " | ".join(self._label_text_parts)

    def _indent(self, _):
        text = self._current_text_area()
        if text:
            text.indent()

    def _save(self, _):
        error_message = """
        Failed to save file - {!r}
        --------
        {}
        """
        self._saved = False
        front, back = self.text_area_front.text, self.text_area_back.text
        if not front:
            self.message_box(TITLE, "Card front cannot be empty")
            return
        if not back:
            self.message_box(TITLE, "Card back cannot be empty")
            return
        self._card.front = front
        self._card.back = back
        try:
            self._card.save()
        except (IOError, OSError) as ex:
            self.message_box(
                TITLE, error_message.format(self._card.path, str(ex))
            )
            return
        self._saved = True

    def _current_text_area(self):
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

    def _help(self, _):
        message = """
        Main UI
        -----------
        Control+e      - Exit
        Control+w      - Write/Save
        Control+Left   - Focus Previous
        Control+Up     - Focus Previous
        Control+Right  - Focus Next
        Control+Down   - Focus Next
        Control+d      - Display Card Stat/Meta Data

        Editor
        -----------
        Escape         - Enter Normal Mode (Vi)
        i              - Enter Insert Mode
        * We start in Insert mode
        * In Normal mode you can use `i` to go
        |   back in to insert mode
        * Macros & other Vi features
        |   in prompt-toolkit are supported
        """.strip()
        message = "\n".join([x.strip() for x in message.splitlines()])
        self.message_box(TITLE, message)

    def _exit(self, _):
        message = """
        Do you want to save before exit?
        (You will loose changes if you select no)
        File = {!r}
        """
        front, back = self.text_area_front.text, self.text_area_back.text

        dirty = front != self._card.front or back != self._card.back

        if dirty:
            self.confirm_box(
                TITLE,
                message.format(self._card.path),
                self._save_exit,
                lambda: self.exit_clicked(None),
            )
        else:
            self.exit_clicked(None)

    def _save_exit(self):
        self._save(None)
        if self._saved:
            self.exit_clicked(None)

    def get_actions(self) -> dict:
        return {
            "indent": self._indent,
            "exit": self._exit,
            "next": focus_next,
            "prev": focus_previous,
            "navigation": self._navigation,
            "save": self._save,
            "help": self._help,
            "info": self.display_info,
        }

    def get_keybindings(self) -> dict:
        return {
            "indent": "tab",
            "exit": "c-e",
            "next": "c-right,c-down",
            "prev": "c-left,c-up",
            "navigation": "escape",
            "save": "c-w",
            "help": "f1",
            "info": "c-d",
        }

    def debug(self, x):
        self.message_box("DEBUG", repr(x))

    def get_current_app(self) -> Application:
        return self.application

    def get_current_layout(self) -> Layout:
        return self.layout

    def display_info(self, _=None):
        message = self._get_stat().strip()
        message = "\n".join([x.strip() for x in message.splitlines()])
        self.message_box(TITLE, message)

    def _get_stat(self):
        return self._card.human_readable_info

    def run(self):
        # Start in the insertion mode
        self.application.vi_state.input_mode = InputMode.INSERT
        self.application.run()
