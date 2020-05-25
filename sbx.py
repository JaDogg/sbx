import os
import sys
from argparse import ArgumentParser, Namespace

from sbx_core.card import Card
from sbx_core.study import CardStack
from sbx_core.ui.editor import EditorInterface
from sbx_core.ui.study import StudyInterface


def editor(args: Namespace):
    EditorInterface(Card(args.file)).run()


def create(args: Namespace):
    path = os.path.abspath(args.file)
    card = Card(path)
    card.front = "Enter front of the card here ..."
    card.back = "Enter back of the card here..."
    card.save()
    print("File written to {!r}".format(path))


def study(args: Namespace):
    StudyInterface(CardStack(args.path)).run()


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
    # Study
    create_parser = subparsers.add_parser('study', help="create a new card")
    create_parser.add_argument('path', type=str, help="path with set of sbx flash-card format .md files")
    create_parser.set_defaults(func=study)

    result = parser.parse_args(args)
    result.func(result)


if __name__ == "__main__":
    main(sys.argv[1:])
