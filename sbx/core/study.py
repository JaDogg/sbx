"""
Contains classes used for selecting cards to study
"""
from pathlib import Path
from typing import Iterator

from sbx.core.card import Card, InvalidCardLoadAttempted


class CardStack:
    """Stack of cards that you can iterate"""

    def __init__(
        self,
        path: str,
        recursive: bool = False,
        include_unscheduled: bool = False,
        filter_to_leech: bool = False,
        filter_to_last_zero: bool = False,
    ):
        """
        Initialize a card stack with `.md` files in given location

        * `path` - path containing SBX `.md` files
        * `recursive` - scan recursively for `.md` files
        * `include_unscheduled` - include cards not scheduled for today
        * `filter_to_leech` - create a subset where all cards are leech
        * `filter_to_last_zero` - create a subset where all cards have
            marked last time as zero
        """
        self._path = Path(path)
        self._recursive = recursive
        self._all = include_unscheduled
        self._filter_to_leech = filter_to_leech
        self._filter_to_last_zero = filter_to_last_zero

    def _get_files(self):
        if self._recursive:
            files = self._path.glob("**/*.md")
        else:
            files = self._path.glob("*.md")

        return files

    def iter(self) -> Iterator[Card]:
        """
        Get cards we need to study (depend on how you constructed the class)
        """
        for card_file in self._get_files():
            if not card_file.is_file():
                continue
            try:
                card = Card(str(card_file))
            except InvalidCardLoadAttempted:
                continue
            if (
                (self._all or card.today)
                and (
                    not self._filter_to_leech
                    or (self._filter_to_leech and card.leech)
                )
                and (
                    not self._filter_to_last_zero
                    or (self._filter_to_last_zero and card.zero)
                )
            ):
                yield card
