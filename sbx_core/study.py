from pathlib import Path
from typing import Iterator

from sbx_core.card import Card, InvalidCardLoadAttempted

# TODO Refactor this better.. 
class CardStack:
    def __init__(self, path: str, recursive: bool = False):
        """
        Init a card stack with .md files in given location
        :param path: path containing sbx .md files
        """
        self._path = Path(path)
        if recursive:
            self._files = self._path.glob("**/*.md")
        else:
            self._files = self._path.glob("*.md")

    def current(self) -> Iterator[Card]:
        """
        Get cards we need to study today
        :return: Iterator of cards
        """
        for card_file in self._files:
            if not card_file.is_file():
                continue
            try:
                card = Card(str(card_file))
            except InvalidCardLoadAttempted:
                continue
            if card.today:
                yield card

    def all(self) -> Iterator[Card]:
        """
        Get all cards
        :return: Iterator of cards
        """
        for card_file in self._files:
            if not card_file.is_file():
                continue
            try:
                card = Card(str(card_file))
            except InvalidCardLoadAttempted:
                continue
            yield card
