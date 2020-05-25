import os
from unittest import TestCase

from sbx.card import Card

BOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "box")


class TestCard(TestCase):
    def test_write(self):
        card_path = os.path.join(BOX_PATH, "test-write-card.md")
        self._remove_file(card_path)

        self.assertFalse(os.path.exists(card_path))

        card = Card(card_path)
        card.front = "Hello World"
        card.back = "Hello World"
        card.mark(5)
        card.save()

        self.assertTrue(os.path.exists(card_path))

        self._remove_file(card_path)

    def test_read_write_read(self):
        card_path = os.path.join(BOX_PATH, "test-card.md")
        card = Card(card_path)
        self.assertTrue("print" in card.back)
        self.assertTrue("[[BACK]]" not in card.back)
        self.assertTrue("display" in card.front)
        self.assertTrue("[[FRONT]]" not in card.front)
        f = card.front
        b = card.back

        new_path = os.path.join(BOX_PATH, "new.md")
        self._remove_file(new_path)
        card._path = new_path
        card.save()

        card = Card(new_path)
        self.assertEqual(f, card.front)
        self.assertEqual(b, card.back)
        self._remove_file(new_path)

    def _remove_file(self, card_path):
        try:
            os.remove(card_path)
        except (OSError, IOError):
            pass
