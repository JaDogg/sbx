import re

from pygments.lexers.html import HtmlLexer, XmlLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.css import CssLexer

from pygments.lexer import (
    RegexLexer,
    DelegatingLexer,
    include,
    bygroups,
    using,
    this,
    do_insertions,
    default,
    words,
)
from pygments.token import (
    Text,
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
    Punctuation,
    Generic,
    Other,
    Literal,
)
from pygments.util import get_bool_opt, ClassNotFound

# This lexer is basd on Pygments source code, we have done some changes here

BoldText = Number
HeadingText = Name.Label


class CustomMarkdownLexer(RegexLexer):
    name = "markdown"
    aliases = ["md"]
    filenames = ["*.md"]
    mimetypes = ["text/x-markdown"]
    flags = re.MULTILINE

    def _handle_codeblock(self, match):
        """
        match args: 1:backticks, 2:lang_name, 3:newline, 4:code, 5:backticks
        """
        from pygments.lexers import get_lexer_by_name

        # section header
        yield match.start(1), String, match.group(1)
        yield match.start(2), String, match.group(2)
        yield match.start(3), Text, match.group(3)

        # lookup lexer if wanted and existing
        lexer = None
        if self.handlecodeblocks:
            try:
                lexer = get_lexer_by_name(match.group(2).strip())
            except ClassNotFound:
                pass
        code = match.group(4)

        # no lexer for this language. handle it like it was a code block
        if lexer is None:
            yield match.start(4), String, code
        else:
            for item in do_insertions([], lexer.get_tokens_unprocessed(code)):
                yield item

        yield match.start(5), String, match.group(5)

    tokens = {
        "root": [
            # heading with pound prefix
            (r"^(#)([^#].+\n)", bygroups(Generic.Heading, HeadingText)),
            (r"^(#{2,6})(.+\n)", bygroups(Generic.Subheading, HeadingText)),
            # task list
            (
                r"^(\s*)([*-] )(\[[ xX]\])( .+\n)",
                bygroups(Text, Keyword, Keyword, using(this, state="inline")),
            ),
            # bulleted lists
            (
                r"^(\s*)([*-])(\s)(.+\n)",
                bygroups(Text, Keyword, Text, using(this, state="inline")),
            ),
            # numbered lists
            (
                r"^(\s*)([0-9]+\.)( .+\n)",
                bygroups(Text, Number, using(this, state="inline")),
            ),
            # quote
            (r"^(\s*>\s)(.+\n)", bygroups(Keyword, Generic.Emph)),
            # text block
            (r"^(```\n)([\w\W]*?)(^```$)", bygroups(String, Text, String)),
            # code block with language
            (r"^(```)(\w+)(\n)([\w\W]*?)(^```$)", _handle_codeblock),
            include("inline"),
        ],
        "inline": [
            # escape
            (r"\\.", Text),
            # italics
            (r"(\s)([*_][^*_]+[*_])(\W|\n)", bygroups(Text, Generic.Emph, Text)),
            # bold
            # warning: the following rule eats internal tags. eg. **foo _bar_ baz** bar is not italics
            (r"(\s)((\*\*|__).*\3)((?=\W|\n))", bygroups(Text, BoldText, None, Text)),
            # "proper way" (r'(\s)([*_]{2}[^*_]+[*_]{2})((?=\W|\n))', bygroups(Text, BoldText, Text)),
            # strikethrough
            (r"(\s)(~~[^~]+~~)((?=\W|\n))", bygroups(Text, Generic.Error, Text)),
            # inline code
            (r"`[^`]+`", String.Backtick),
            # mentions and topics (twitter and github stuff)
            (r"[@#][\w/:]+", Name.Entity),
            # (image?) links eg: ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            (
                r"(!?\[)([^]]+)(\])(\()([^)]+)(\))",
                bygroups(Text, Name.Tag, Text, Text, Name.Attribute, Text),
            ),
            # reference-style links, e.g.:
            #   [an example][id]
            #   [id]: http://example.com/
            (
                r"(\[)([^]]+)(\])(\[)([^]]*)(\])",
                bygroups(Text, Name.Tag, Text, Text, Name.Label, Text),
            ),
            (
                r"^(\s*\[)([^]]*)(\]:\s*)(.+)",
                bygroups(Text, Name.Label, Text, Name.Attribute),
            ),
            # general text, must come last!
            (r"[^\\\s]+", Text),
            (r".", Text),
        ],
    }

    def __init__(self, **options):
        self.handlecodeblocks = get_bool_opt(options, "handlecodeblocks", True)
        RegexLexer.__init__(self, **options)
