"""
SBX program entry point
"""

import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from .core.card import Card
from .core.study import CardStack
from .ui.editor import EditorInterface
from .ui.study import StudyInterface


# Reference: https://stackoverflow.com/a/107717
class Unbuffered(object):
    """
    Unbuffered stream wrapper - This flushes writes immediately.
    """

    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def editor(args: Namespace):
    EditorInterface(Card(args.file)).run()


def create(args: Namespace):
    path = Path(os.path.abspath(args.file))
    if path.is_file() or path.exists():
        print("File {!r} already exists!".format(str(path)))
        sys.exit(-1)
    card = Card(str(path))
    card.front = "Enter front of the card here ..."
    card.back = "Enter back of the card here..."
    card.save()
    print("File written to {!r}".format(str(path)))


def reset(args: Namespace):
    path = Path(os.path.abspath(args.file))
    if not (path.is_file() and path.exists()):
        print("File {!r} doesn't exist".format(str(path)))
        sys.exit(-1)
    card = Card(str(path))
    card.reset()
    card.save()
    print("File written to {!r}".format(str(path)))


def study(args: Namespace):
    StudyInterface(CardStack(args.path, args.rec, args.all)).run()


def list_cards(args: Namespace):
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


def add_filtering_args(sub_parser):
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


def main():
    """Run sbx command line program"""
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

    subparsers = parser.add_subparsers(dest="action", required=True)

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
    add_filtering_args(study_parser)
    study_parser.set_defaults(func=study)

    # List Cards
    list_parser = subparsers.add_parser("list", help="list cards")
    add_filtering_args(list_parser)
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

    result = parser.parse_args(sys.argv[1:])

    if result.unbuffered:
        sys.stdout = Unbuffered(sys.stdout)

    result.func(result)


if __name__ == "__main__":
    main()
