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
    StudyInterface(CardStack(args.path), all=args.all).run()


def main(args):
    parser = ArgumentParser(prog="sbx", description="Sbx - Flashcard application on the terminal",
                            add_help=True)

    subparsers = parser.add_subparsers(dest="action", required=True)

    # Edit
    edit_parser = subparsers.add_parser('edit', help="edit a card")
    edit_parser.add_argument('file', type=str, help="card file (ensure it's a .md so "
                                                    "you can use it in study mode)")
    edit_parser.set_defaults(func=editor)
    # Create
    create_parser = subparsers.add_parser('create', help="create a new card")
    create_parser.add_argument('file', type=str, help="card file (ensure it's a .md so "
                                                      "you can use it in study mode)")
    create_parser.set_defaults(func=create)

    # Reset
    reset_parser = subparsers.add_parser('reset', help="reset a card")
    reset_parser.add_argument('file', type=str, help="card file (ensure it's a .md so "
                                                     "you can use it in study mode)")
    reset_parser.set_defaults(func=reset)

    # Study
    study_parser = subparsers.add_parser('study', help="create a new card")
    study_parser.add_argument('path', type=str, help="path with collection of sbx flash-card format .md files")
    study_parser.add_argument("--all", dest="all",
                              default=False, action="store_true", help="study all cards if this is set,"
                                                                       " else we will only load cards we need to study")
    study_parser.set_defaults(func=study)

    result = parser.parse_args(args)
    result.func(result)


if __name__ == "__main__":
    main(sys.argv[1:])
