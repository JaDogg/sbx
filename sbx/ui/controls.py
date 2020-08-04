"""
Reusable controls, components, classes  used in SBX
"""
import abc
from abc import ABCMeta

from prompt_toolkit import Application
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Float, FloatContainer
from prompt_toolkit.layout.processors import (
    DisplayMultipleCursors,
    TabsProcessor,
)
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.widgets import Button, Dialog, Label, TextArea

from sbx.ui.mdlexer import CustomMarkdownLexer


class MarkdownArea(TextArea):
    """
    Pre configured markdown component for prompt_toolkit
    """

    def __init__(self, readonly=False):
        super().__init__(
            lexer=PygmentsLexer(CustomMarkdownLexer),
            scrollbar=True,
            line_numbers=True,
            focus_on_click=not readonly,
            input_processors=[TabsProcessor(), DisplayMultipleCursors()],
            wrap_lines=True,
            read_only=readonly,
            focusable=not readonly,
        )

    def indent(self):
        """
        Insert a tab
        """
        if self.read_only:
            return
        current_doc = self.document
        self.document = current_doc.paste_clipboard_data(
            ClipboardData(text="\t")
        )


class BaseUi(metaclass=ABCMeta):
    """
    Core UI class for Editor & Study interfaces to inherit from
    """

    def __init__(self):
        self._layout_stack = []
        self._focus_stack = []
        self._float = None
        self.kb = KeyBindings()

    def hide_current_dialog(self):
        """
        Hide current displayed dialog box
        """
        # Nothing to hide, ignore
        if not self._float.floats:
            return

        # WHY: Ensure that we restore previous focused item
        prev_focus = self._focus_stack.pop()
        if prev_focus:
            self.get_current_layout().focus(prev_focus)

        # Garbage clean up
        float_dialog = self._float.floats.pop()
        del float_dialog
        self.get_current_app().invalidate()

    def exit_clicked(self, _=None):
        self.get_current_app().exit()

    @abc.abstractmethod
    def get_current_app(self) -> Application:
        pass

    @abc.abstractmethod
    def get_current_layout(self) -> Layout:
        pass

    @abc.abstractmethod
    def get_actions(self) -> dict:
        pass

    @abc.abstractmethod
    def get_keybindings(self) -> dict:
        pass

    def create_key_bindings(self):
        actions = self.get_actions()
        for action, keys in self.get_keybindings().items():
            if callable(keys):
                keys(self.kb, actions[action])
                continue
            for key in keys.split(","):
                try:
                    self.kb.add(key.strip())(actions[action])
                except KeyError:
                    pass

    def create_root_layout(self, container, focused_element):
        self._float = FloatContainer(container, floats=[])
        return Layout(self._float, focused_element=focused_element)

    def message_box(self, title: str, text: str):
        """
        Show a message box

        * `title` - title of the message box
        * `text` - text of the message box
        """
        self.custom_dialog(
            title, Label(text=text, dont_extend_height=True), show_ok=True
        )

    def confirm_box(self, title: str, text: str, on_yes, on_no):
        """
        Show a message box with yes/no confirmation

        * `title` - title of the message
        * `text` - text asking a question
        * `on_yes` - call back function (no args)
        * `on_no` - call back function (no args)
        """
        body = Label(text=text, dont_extend_height=True)
        yes_btn = Button(text="Yes", handler=self._hide_then_call(on_yes))
        no_btn = Button(text="No", handler=self._hide_then_call(on_no))
        self.custom_dialog(
            title, body, focus_element=yes_btn, buttons=[yes_btn, no_btn]
        )

    def _hide_then_call(self, fnc):
        def callback():
            self.hide_current_dialog()
            fnc()

        return callback

    def custom_dialog(
        self, title: str, body, show_ok=False, focus_element=None, buttons=None
    ):
        """
        Create a custom dialog

        * `title` - title of the message
        * `body` - prompt_toolkit widget to display as body
        * `show_ok` - show OK button (use this if you don't want to
            provide your own buttons)
        * `focus_element` - prompt_toolkit element to focus on.
        * `buttons` = list of prompt_toolkit buttons to show

        Note:

        * Please note that you need to call `hide_current_dialog` after a
            button is clicked and you no longer want to show a dialog.
        * All custom dialog are stored in a stack. If `n` dialog are shown
            then you need to call `hide_current_dialog` exactly `n` times.
        * Refer to code in `confirm_box` & `message_box` for samples.
        """
        ok = None
        if show_ok:
            ok = Button(text="OK", handler=self.hide_current_dialog)
            btns = [ok]
        elif buttons:
            btns = buttons
        else:
            btns = []
        dialog = Dialog(
            title=title, body=body, buttons=btns, with_background=False,
        )
        self._focus_stack.append(self.get_current_layout().current_window)
        self._float.floats.append(Float(dialog, allow_cover_cursor=True))
        if show_ok and ok:
            self.get_current_layout().focus(ok)
        if focus_element:
            self.get_current_layout().focus(focus_element)
        self.get_current_app().invalidate()
