from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.layout.processors import TabsProcessor
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.widgets import TextArea
from pygments.lexers.markup import MarkdownLexer


class MarkdownArea(TextArea):
    def __init__(self):
        super().__init__(lexer=PygmentsLexer(MarkdownLexer),
                         scrollbar=True, line_numbers=True,
                         focus_on_click=True, input_processors=[TabsProcessor()])

    def indent(self):
        current_doc = self.document
        self.document = current_doc.paste_clipboard_data(ClipboardData(text="\t"))