import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from sbx_core.card import Card
from sbx_core.study import CardStack
from sbx_core.ui.editor import EditorInterface
from sbx_core.ui.study import StudyInterface


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
    stk = CardStack(args.path, args.rec, args.all)
    file_only = args.file_only

    for card in stk.iter():
        if file_only:
            print(card.path)
        else:
            print("- - - - - " * 4)
            print(str(card))


def main(args):
    parser = ArgumentParser(
        prog="sbx",
        description="Sbx - Flashcard application on the terminal",
        add_help=True,
    )

    subparsers = parser.add_subparsers(dest="action", required=True)

    # Edit
    edit_parser = subparsers.add_parser("edit", help="edit a card")
    edit_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so " "you can use it in study mode)",
    )
    edit_parser.set_defaults(func=editor)
    # Create
    create_parser = subparsers.add_parser("create", help="create a new card")
    create_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so " "you can use it in study mode)",
    )
    create_parser.set_defaults(func=create)

    # Reset
    reset_parser = subparsers.add_parser("reset", help="reset a card")
    reset_parser.add_argument(
        "file",
        type=str,
        help="card file (ensure it's a .md so " "you can use it in study mode)",
    )
    reset_parser.set_defaults(func=reset)

    # Study
    study_parser = subparsers.add_parser(
        "study", help="start a study session on given path"
    )
    study_parser.add_argument(
        "path", type=str, help="path with collection of sbx flash-card format .md files"
    )
    study_parser.add_argument(
        "-i",
        "--include-not-scheduled" "-i",
        "--include-not-scheduled",
        dest="all",
        default=False,
        action="store_true",
        help="include cards that are not scheduled for study session",
    )
    study_parser.add_argument(
        "-r",
        "--recursive",
        dest="rec",
        default=False,
        action="store_true",
        help="scan all sub directories for .md files",
    )
    study_parser.set_defaults(func=study)

    # List Cards
    list_parser = subparsers.add_parser("list", help="list cards")
    list_parser.add_argument(
        "path", type=str, help="path with collection of sbx flash-card format .md files"
    )
    list_parser.add_argument(
        "-i",
        "--include-not-scheduled",
        dest="all",
        default=False,
        action="store_true",
        help="include cards that are not scheduled for study session",
    )
    list_parser.add_argument(
        "-r",
        "--recursive",
        dest="rec",
        default=False,
        action="store_true",
        help="scan all sub directories for .md files",
    )
    list_parser.add_argument(
        "-n",
        "--file-name-only",
        dest="file_only",
        default=False,
        action="store_true",
        help="only list file name",
    )
    list_parser.set_defaults(func=list_cards)

    result = parser.parse_args(args)
    result.func(result)


if __name__ == "__main__":
    main(sys.argv[1:])
