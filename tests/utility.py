import os
import sys
from io import StringIO

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
