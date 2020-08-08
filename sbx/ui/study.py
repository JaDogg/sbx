"""
Study interface
"""
import random
import sys
from typing import Optional

from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next,
    focus_previous,
)
from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.widgets import Button, Label

from sbx.core.study import CardStack
from sbx.core.utility import print_error, simplify_path
from sbx.ui.controls import MarkdownArea
from sbx.ui.editor import EditorInterface

TITLE = "---- SBX - Flashcards ----"
BTN_3_CELL = 3
BTN_SHOW_CELL = 0
LABEL_CELL = 0
PATH_CELL = 1
MODE_BEFORE_ANSWER_VISIBLE = 424
MODE_SELF_EVAL = 124
MODE_DONE = 241


class StudyInterface(EditorInterface):
    """
    Study user interface that can work with a `CardStack`
    """

    def __init__(self, stack: CardStack):
        self._0_callback = self._continue_with_quality(0)
        self._1_callback = self._continue_with_quality(1)
        self._2_callback = self._continue_with_quality(2)
        self._3_callback = self._continue_with_quality(3)
        self._4_callback = self._continue_with_quality(4)
        self._5_callback = self._continue_with_quality(5)
        super().__init__(None)
        self._label_text_parts = [
            "SBX",
            "PATH",
            "Press F1 for help",
            "--STUDY--",
        ]
        self._original_stack = list(stack.iter())
        self._reset_stack()

    def _reset_stack(self):
        self._stack = self._original_stack[:]
        if not self._stack:
            print_error(
                "Nothing to study now, try again later. Or use -i option."
            )
            sys.exit(-1)
        random.shuffle(self._stack)
        self._swap_button_bar(self.generic_button_bar)
        self._current = self._stack.pop()
        self._show_front_only()
        self._mode = MODE_BEFORE_ANSWER_VISIBLE

    def _continue_with_quality(self, quality: int):
        def callback(_=None):
            self._mark_and_continue(quality)

        return callback

    def _mark_and_continue(self, quality: int):
        if self._mode != MODE_SELF_EVAL:
            return
        if not self._stack:
            # WHY? Focus on label otherwise message_box cannot
            #    find current item in focus stack :)
            self._swap_button_bar(self.empty_button_bar)
            self.message_box(
                TITLE, "You have completed all the cards for today."
            )
            self._mode = MODE_DONE
            self._mark_and_save(quality)
            return
        if not self._mark_and_save(quality):
            return
        self._swap_button_bar(self.generic_button_bar)
        self._current = self._stack.pop()
        self._show_front_only()
        self._mode = MODE_BEFORE_ANSWER_VISIBLE

    def _mark_and_save(self, quality):
        self._current.mark(quality)
        try:
            self._current.save()
            return True
        except (IOError, OSError):
            self.message_box(
                TITLE,
                "Failed to update flash card\n"
                "File = {!r}".format(self._current.path),
            )
            return False

    def _show(self, _=None):
        if self._mode != MODE_BEFORE_ANSWER_VISIBLE:
            return
        self.text_area_back.text = self._current.back
        self._swap_button_bar(self.quality_button_bar)
        self._mode = MODE_SELF_EVAL

    def _swap_button_bar(self, bar):
        root_child = list(self.root_container.children)
        root_child[0] = bar
        self.root_container.children = root_child
        self.layout.focus(self.text_area_scratch)
        self.get_current_app().invalidate()

    def _show_front_only(self):
        self._label_text_parts[PATH_CELL] = simplify_path(self._current.path)
        self.text_area_front.text = self._current.front
        self.text_area_back.text = "... not visible ..."
        self.text_area_scratch.text = ""

    def _get_base_layout(self):
        self.text_area_front = MarkdownArea(readonly=True)
        self.text_area_back = MarkdownArea(readonly=True)
        self.text_area_scratch = MarkdownArea(readonly=False)
        self.text_area_front.text = "..."
        self.text_area_back.text = "..."
        self.label = Label(text=self._get_label_text, style="class:status")
        self.btn_0 = Button(text="0", handler=self._0_callback)
        self.btn_1 = Button(text="1", handler=self._1_callback)
        self.btn_2 = Button(text="2", handler=self._2_callback)
        self.btn_3 = Button(text="3", handler=self._3_callback)
        self.btn_4 = Button(text="4", handler=self._4_callback)
        self.btn_5 = Button(text="5", handler=self._5_callback)
        quality_buttons = [
            Label("How good were you?", style="#000000"),
            self.btn_0,
            self.btn_1,
            self.btn_2,
            self.btn_3,
            self.btn_4,
            self.btn_5,
        ]
        self.btn_show = Button(text="Show", handler=self._show)
        self.generic_button_bar = VSplit([self.btn_show], style="bg:#cccccc")
        self.quality_button_bar = VSplit(quality_buttons, style="bg:#cccccc")
        self.empty_button_bar = VSplit(
            [Label("All done!", style="#000000")], style="bg:#cccccc"
        )
        self.root_container = HSplit(
            [
                self.generic_button_bar,
                VSplit(
                    [
                        HSplit(
                            [
                                Label(
                                    text="[Flashcard Front]",
                                    style="class:status",
                                ),
                                self.text_area_front,
                                Label(
                                    text="[Scratch Pad]", style="class:status"
                                ),
                                self.text_area_scratch,
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
        return self.root_container

    def _is_mark(self):
        return self._mode == MODE_SELF_EVAL

    def only_on_mark(self, key):
        def fnc(kbd, action):
            kbd.add(key.strip(), filter=Condition(self._is_mark))(action)

        return fnc

    def _get_stat(self):
        return self._current.human_readable_info

    def _current_text_area(self):
        if not self.layout.buffer_has_focus:
            return None
        buffer = self.layout.current_control
        if id(buffer) == id(self.text_area_scratch.control):
            return self.text_area_scratch
        return None

    def get_keybindings(self) -> dict:
        return {
            "exit": "c-e",
            "next": "c-right,c-down",
            "prev": "c-left,c-up",
            "save": "c-s",
            "help": "f1",
            "info": "c-d",
            "show": "c-r",
            "tab": "tab",
        }

    def get_actions(self) -> dict:
        return {
            "exit": self.exit_clicked,
            "next": focus_next,
            "prev": focus_previous,
            "help": self._help,
            "show": self._show,
            "info": self.display_info,
            "tab": self._indent,
        }

    def _help(self, _):
        message = """
        Main UI
        -----------
        Control+e      - Exit
        Control+Left   - Focus Previous
        Control+Up     - Focus Previous
        Control+Right  - Focus Next
        Control+Down   - Focus Next
        Control+d      - Display Card Stat/Meta Data

        Study Buttons
        -----------
        Control+r      - Reveal

        Voting (You need to manually navigate)
        -----------
        0              - I have no idea what this is?
        1              - I have a vague memory
        2              - I don't remember answer fully
        3              - I got the answer correct (about 80%)
        4              - I got the answer correct (100%)
        5              - I think I have memorised this, very easy.
        """
        self.message_box(TITLE, message)
