from argparse import ArgumentParser, Namespace

from sbx_core.card import Card
from sbx_core.ui.sbx_ui import EditorInterface


def editor(args: Namespace):
    EditorInterface(Card(args.file)).run()


def main():
    parser = ArgumentParser(prog="sbx", description="Sbx - Flashcard application on the terminal",
                            add_help=True)

    subparsers = parser.add_subparsers(dest="action", required=True)
    edit_parser = subparsers.add_parser('edit', help="edit a card")
    edit_parser.add_argument('file', type=str)
    edit_parser.set_defaults(func=editor)

    result = parser.parse_args()
    result.func(result)


if __name__ == "__main__":
    main()
