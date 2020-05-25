from pathlib import Path
from typing import Iterator

from sbx_core.card import Card


class CardStack:
    def __init__(self, path: str):
        """
        Init a card stack with .md files in given location
        :param path: path containing sbx .md files
        """
        self._path = Path(path)
        self._files = self._path.glob("*.md")

    def current(self) -> Iterator[Card]:
        """
        Get cards we need to study today
        :return: Iterator of cards
        """
        for card_file in self._files:
            if not card_file.is_file():
                continue
            card = Card(str(card_file))
            if card.today:
                yield card
