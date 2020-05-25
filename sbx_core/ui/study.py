import random
import sys

from prompt_toolkit import Application
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.widgets import Label, Button

from sbx_core.study import CardStack
from sbx_core.ui.controls import MarkdownArea
from sbx_core.ui.editor import EditorInterface

TITLE = "---- SBX - Flashcards ----"


class StudyInterface(EditorInterface):
    def __init__(self, stack: CardStack):
        super().__init__(None)
        self._label_text_parts = ["SBX", "Press F1 for help", "--STUDY--"]
        self._original_stack = list(stack.current())
        self._reset_stack()
        self._answer_visible = False
        self._next()

    def _reset_stack(self):
        self._stack = self._original_stack[:]
        if not self._stack:
            print("Nothing to study now, try again later. :)")
            sys.exit(-1)
        random.shuffle(self._stack)

    def _next(self, _=None):
        if not self._stack:
            self.message_box(TITLE, "You have completed all the cards for today.")
            return
        self._swap_button_bar(self.generic_button_bar, focus_idx=0)
        self._current = self._stack.pop()
        self._show_front_only()

    def _swap_button_bar(self, bar, focus_idx):
        root_child = list(self.root_container.children)
        root_child[0] = bar
        self.root_container.children = root_child
        self.layout.focus(bar.children[focus_idx])
        self.get_current_app().invalidate()

    def _show(self, _=None):
        self.text_area_back.text = self._current.back
        self._swap_button_bar(self.quality_button_bar, focus_idx=3)

    def _show_front_only(self):
        self.text_area_front.text = self._current.front
        self.text_area_back.text = "... not visible ..."

    def _get_base_layout(self):
        self.text_area_front = MarkdownArea(readonly=True)
        self.text_area_back = MarkdownArea(readonly=True)
        self.text_area_front.text = "..."
        self.text_area_back.text = "..."
        self.label = Label(text=self._get_label_text, style="class:status")
        self.btn_1 = Button(text="1", handler=self._next)
        self.btn_2 = Button(text="2", handler=self._next)
        self.btn_3 = Button(text="3", handler=self._next)
        self.btn_4 = Button(text="4", handler=self._next)
        self.btn_5 = Button(text="5", handler=self._next)
        self.btn_6 = Button(text="6", handler=self._next)
        quality_buttons = [Label("How good were you?", style="#000000"),
                           self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6]
        self.btn_show = Button(text="Show", handler=self._show)
        self.generic_button_bar = VSplit([self.btn_show], style="bg:#cccccc")
        self.quality_button_bar = VSplit(quality_buttons, style="bg:#cccccc")
        self.root_container = HSplit(
            [
                self.generic_button_bar,
                VSplit(
                    [
                        HSplit([Label(text="Flashcard Front", style="class:status"), self.text_area_front]),
                        HSplit([Label(text="Flashcard Back", style="class:status"), self.text_area_back]),
                    ]
                ),
                self.label
            ], style="class:main-panel"
        )
        return self.root_container

    # There's no need to update anything!
    def before_render(self, app: Application):
        pass

    def get_actions(self) -> dict:
        return {
            "exit": self.exit_clicked,
            "next": focus_next,
            "prev": focus_previous,
            "help": self._help
        }

    def get_keybindings(self) -> dict:
        return {
            "exit": "c-e",
            "next": "c-right,c-up",
            "prev": "c-left,c-down",
            "save": "c-s",
            "help": "f1"
        }

    def _help(self, _):
        message = """
        Main UI
        -----------
        Control+e      - Exit
        Control+Left   - Focus Previous
        Control+Down   - Focus Previous
        Control+Right  - Focus Next
        Control+Up     - Focus Next

        Study Buttons
        -----------
        S              - Show
        
        Voting
        -----------
        1              - I have no idea what this is?
        2              - I have a vague memory
        3              - I don't remember answer
        4              - I got the answer correct (about 90%)
        5              - I got the answer correct (100%)
        6              - I think I have memorised this, very easy.
        """
        self.message_box(TITLE, message)
