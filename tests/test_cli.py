import os
import sys
from io import StringIO
from unittest import TestCase

from sbx.cli import run

BOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "box")

# `STDOUT` Capturing
# Ref https://stackoverflow.com/a/16571630/1355145


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class ChangeDir:
    def __init__(self, path):
        self._path = path
        self._prev_path = os.curdir

    def __enter__(self):
        os.chdir(self._path)

    def __exit__(self, *args):
        os.chdir(self._prev_path)


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
