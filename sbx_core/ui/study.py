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
VI_STATUS_CELL = 2
BTN_3_CELL = 3
BTN_SHOW_CELL = 0
LABEL_CELL = 0
MODE_SHOW = 424
MODE_MARK = 124
MODE_DONE = 241


class StudyInterface(EditorInterface):
    def __init__(self, stack: CardStack, all=False):
        # TODO use list comprehension for this nonsense
        self._1_callback = self._continue_with_quality(0)
        self._2_callback = self._continue_with_quality(1)
        self._3_callback = self._continue_with_quality(2)
        self._4_callback = self._continue_with_quality(3)
        self._5_callback = self._continue_with_quality(4)
        self._6_callback = self._continue_with_quality(5)
        super().__init__(None)
        self._label_text_parts = ["SBX", "Press F1 for help", "--STUDY--"]
        if all:
            self._original_stack = list(stack.all())
        else:
            self._original_stack = list(stack.current())
        self._reset_stack()
        self._mode = MODE_SHOW

    def _reset_stack(self):
        self._stack = self._original_stack[:]
        if not self._stack:
            print("Nothing to study now, try again later. Or use --all option.")
            # TODO load all the cards and pick closest top 30
            sys.exit(-1)
        random.shuffle(self._stack)
        self._swap_button_bar(self.generic_button_bar, focus_idx=BTN_SHOW_CELL)
        self._current = self._stack.pop()
        self._show_front_only()
        self._mode = MODE_SHOW

    def _continue_with_quality(self, quality: int):
        def callback(_=None):
            self._mark_and_continue(quality)

        return callback

    def _mark_and_continue(self, quality: int):
        if self._mode != MODE_MARK:
            return
        if not self._stack:
            # WHY? Focus on label otherwise message_box cannot find current item in focus stack :)
            self._swap_button_bar(self.empty_button_bar, focus_idx=LABEL_CELL)
            self.message_box(TITLE, "You have completed all the cards for today.")
            self._mode = MODE_DONE
            self._mark_and_save(quality)
            return
        if not self._mark_and_save(quality):
            return
        self._swap_button_bar(self.generic_button_bar, focus_idx=BTN_SHOW_CELL)
        self._current = self._stack.pop()
        self._show_front_only()
        self._mode = MODE_SHOW

    def _mark_and_save(self, quality):
        self._current.mark(quality)
        try:
            self._current.save()
            return True
        except (IOError, OSError):
            self.message_box(TITLE, "Failed to update flash card\n"
                             "File = {!r}".format(self._current.path))
            return False

    def _show(self, _=None):
        if self._mode != MODE_SHOW:
            return
        self.text_area_back.text = self._current.back
        self._swap_button_bar(self.quality_button_bar, focus_idx=BTN_3_CELL)
        self._mode = MODE_MARK

    def _swap_button_bar(self, bar, focus_idx):
        root_child = list(self.root_container.children)
        root_child[0] = bar
        self.root_container.children = root_child
        self.layout.focus(bar.children[focus_idx])
        self.get_current_app().invalidate()

    def _show_front_only(self):
        self.text_area_front.text = self._current.front
        self.text_area_back.text = "... not visible ..."

    def _get_base_layout(self):
        self.text_area_front = MarkdownArea(readonly=True)
        self.text_area_back = MarkdownArea(readonly=True)
        self.text_area_front.text = "..."
        self.text_area_back.text = "..."
        self.label = Label(text=self._get_label_text, style="class:status")
        self.btn_1 = Button(text="1", handler=self._1_callback)
        self.btn_2 = Button(text="2", handler=self._2_callback)
        self.btn_3 = Button(text="3", handler=self._3_callback)
        self.btn_4 = Button(text="4", handler=self._4_callback)
        self.btn_5 = Button(text="5", handler=self._5_callback)
        self.btn_6 = Button(text="6", handler=self._6_callback)
        quality_buttons = [Label("How good were you?", style="#000000"),
                           self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6]
        self.btn_show = Button(text="Show", handler=self._show)
        self.generic_button_bar = VSplit([self.btn_show], style="bg:#cccccc")
        self.quality_button_bar = VSplit(quality_buttons, style="bg:#cccccc")
        self.empty_button_bar = VSplit([Label("All done!", style="#000000")], style="bg:#cccccc")
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

    def before_render(self, app: Application):
        pass

    def get_actions(self) -> dict:
        return {
            "exit": self.exit_clicked,
            "next": focus_next,
            "prev": focus_previous,
            "help": self._help,
            "1": self._1_callback,
            "2": self._2_callback,
            "3": self._3_callback,
            "4": self._4_callback,
            "5": self._5_callback,
            "6": self._6_callback,
            "show": self._show
        }

    def get_keybindings(self) -> dict:
        return {
            "exit": "c-e",
            "next": "c-right,c-up",
            "prev": "c-left,c-down",
            "save": "c-s",
            "help": "f1",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "show": "s"
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
        3              - I don't remember answer fully
        4              - I got the answer correct (about 80%)
        5              - I got the answer correct (100%)
        6              - I think I have memorised this, very easy.
        """
        self.message_box(TITLE, message)
