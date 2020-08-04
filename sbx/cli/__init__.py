"""
SBX Command line interface functionality
"""

import os
import sys
import typing
from argparse import ArgumentParser, Namespace
from pathlib import Path

from sbx.core.card import Card
from sbx.core.study import CardStack
from sbx.core.utility import Unbuffered
from sbx.ui.editor import EditorInterface
from sbx.ui.study import StudyInterface


def editor(args: Namespace):
    """Edit file command"""
    EditorInterface(Card(args.file)).run()


def _set_content(card: Card, content: typing.List[str], style: bool):
    title_prefix = ""
    answer_prefix = ""
    if style:
        title_prefix = "# "
        answer_prefix = "* "
    card.front = title_prefix + content[0]
    if len(content) > 1:
        card.back = os.linesep.join([answer_prefix + x for x in content[1:]])


def create(args: Namespace):
    """Create file command"""
    content = args.content
    path = Path(os.path.abspath(args.file))
    if path.is_file() or path.exists():
        print("File {!r} already exists!".format(str(path)))
        sys.exit(-1)
    card = Card(str(path))
    card.front = "Enter front of the card here ..."
    card.back = "Enter back of the card here..."
    if content:
        _set_content(card, content, args.markdown)
    card.save()
    print("File written to {!r}".format(str(path)))


def reset(args: Namespace):
    """Reset file command"""
    path = Path(os.path.abspath(args.file))
    if not (path.is_file() and path.exists()):
        print("File {!r} doesn't exist".format(str(path)))
        sys.exit(-1)
    card = Card(str(path))
    card.reset()
    card.save()
    print("File written to {!r}".format(str(path)))


def study(args: Namespace):
    """Study cards command"""
    StudyInterface(
        CardStack(args.path, args.rec, args.all, args.leech, args.zero)
    ).run()


def list_cards(args: Namespace):
    """List cards command"""
    stk = CardStack(args.path, args.rec, args.all, args.leech, args.zero)
    file_only = args.file_only

    for card in stk.iter():
        if file_only:
            print(card.path)
        elif args.no_color:
            print("- - - - - " * 4)
            print(str(card))
        else:
            print("- - - - - " * 4)
            card.to_formatted().print()


def _add_filtering_args(sub_parser):
    # Note these are common for both list & study commands
    sub_parser.add_argument(
        "path",
        type=str,
        help="path with collection of sbx flash-card format .md files",
    )
    sub_parser.add_argument(
        "-i",
        "--include-not-scheduled",
        dest="all",
        default=False,
        action="store_true",
        help="include cards that are not scheduled for today's study session",
    )
    sub_parser.add_argument(
        "-r",
        "--recursive",
        dest="rec",
        default=False,
        action="store_true",
        help="scan all sub directories for .md files",
    )
    sub_parser.add_argument(
        "-l",
        "--leech",
        dest="leech",
        default=False,
        action="store_true",
        help="select leech cards (of current subset)",
    )
    sub_parser.add_argument(
        "-z",
        "--zero",
        dest="zero",
        default=False,
        action="store_true",
        help="select cards that were marked zero"
        " last time (of current subset)",
    )


def run(arguments: typing.List[str]):
    """
    Run sbx command line program

    * `arguments` - List of arguments to passed to `sbx` command
    """
    parser = ArgumentParser(
        prog="sbx",
        description="Sbx - Flashcard application on the terminal",
        add_help=True,
    )

    parser.add_argument(
        "-u",
        "--unbuffered",
        dest="unbuffered",
        default=False,
        action="store_true",
        help="ensure output is unbuffered",
    )

    subparsers = parser.add_subparsers(dest="action")
    subparsers.required = True

    # Edit
    edit_parser = subparsers.add_parser("edit", help="edit a card")
    edit_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so "
        "you can use it in study mode)",
    )
    edit_parser.set_defaults(func=editor)
    # Create
    create_parser = subparsers.add_parser("create", help="create a new card")
    create_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so "
        "you can use it in study mode)",
    )
    create_parser.add_argument(
        "content",
        type=str,
        nargs="*",
        default=None,
        help="content of the card, first element is taken as front."
        "Rest is added to back as individual lines",
    )
    create_parser.add_argument(
        "-m",
        "--markdown-header-and-bullet",
        dest="markdown",
        default=False,
        action="store_true",
        help="if content is provided this will prepend card front content"
        "with a '# ' and all lines in back with '* '",
    )
    create_parser.set_defaults(func=create)

    # Reset
    reset_parser = subparsers.add_parser("reset", help="reset a card")
    reset_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so "
        "you can use it in study mode)",
    )
    reset_parser.set_defaults(func=reset)

    # Study
    study_parser = subparsers.add_parser(
        "study", help="start a study session on given path"
    )
    _add_filtering_args(study_parser)
    study_parser.set_defaults(func=study)

    # List Cards
    list_parser = subparsers.add_parser("list", help="list cards")
    _add_filtering_args(list_parser)
    list_parser.add_argument(
        "-n",
        "--file-name-only",
        dest="file_only",
        default=False,
        action="store_true",
        help="only list file name",
    )
    list_parser.add_argument(
        "--no-color",
        dest="no_color",
        default=False,
        action="store_true",
        help="don't use colours",
    )
    list_parser.set_defaults(func=list_cards)

    result = parser.parse_args(arguments)

    if result.unbuffered:
        sys.stdout = Unbuffered(sys.stdout)  # type: ignore

    result.func(result)
