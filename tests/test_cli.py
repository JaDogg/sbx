import os
from unittest import TestCase

from sbx.cli import run

from .utility import BOX_PATH, Capturing, ChangeDir


class TestCli(TestCase):
    def test_list_all_cards(self):
        expected = [
            "test-card-3.md",
            "test-card-zero.md",
            "test-card-2.md",
            "test-card.md",
            "test-card-leech-zero.md",
            "test-card-ok.md",
            "test-card-leech.md",
            "python/leech-python-card.md",
            "c/test-c-card-zero.md",
        ]

        with ChangeDir(BOX_PATH) as _:
            with Capturing() as cards:
                run(["list", "-rni", "."])
        self.assertCountEqual(cards, expected)
        with ChangeDir(BOX_PATH) as _:
            with Capturing() as cards:
                run(["list", "-rni", "."])

    def test_list_all_leech_cards(self):
        expected = [
            "test-card-leech-zero.md",
            "test-card-leech.md",
            "python/leech-python-card.md",
        ]

        with ChangeDir(BOX_PATH) as _:
            with Capturing() as cards:
                run(["list", "-rnil", "."])
        self.assertCountEqual(cards, expected)

    def test_create_card(self):
        expected = [
            "test-card-3.md",
            "test-card-zero.md",
            "test-card-2.md",
            "test-card.md",
            "test-card-leech-zero.md",
            "test-card-ok.md",
            "test-card-leech.md",
            "python/leech-python-card.md",
            "c/test-c-card-zero.md",
            "new/card-1.md",
            "new/card-2.md",
        ]

        with ChangeDir(BOX_PATH) as _:
            run(["create", "./new/card-1.md", "Front", "Back"])
            run(["create", "-m", "./new/card-2.md", "Front", "Back"])

        with ChangeDir(BOX_PATH) as _:
            with Capturing() as cards:
                run(["-u", "list", "-rni", "."])

        self.assertCountEqual(cards, expected)

        os.unlink(os.path.join(BOX_PATH, "new", "card-1.md"))
        os.unlink(os.path.join(BOX_PATH, "new", "card-2.md"))
