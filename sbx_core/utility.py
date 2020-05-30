import time
from datetime import datetime

import pytz
from tzlocal import get_localzone
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText

DAY_IN_SECONDS = 60 * 60 * 24


class Text:
    def __init__(self):
        self.text = []

    def red(self, text):
        self.text.append(("#ff0000", text))
        return self

    def yellow(self, text):
        self.text.append(("#ffff00", text))
        return self

    def blue(self, text):
        self.text.append(("#0000ff", text))
        return self

    def green(self, text):
        self.text.append(("#00ff00", text))
        return self

    def cyan(self, text):
        self.text.append(("#00ffff", text))
        return self

    def normal(self, text):
        self.text.append(("", text))
        return self

    def newline(self):
        self.text.append(("", "\n"))
        return self

    def print(self):
        print_formatted_text(FormattedText(self.text))

    def to_formatted(self):
        return FormattedText(self.text)


def print_error(text):
    print_formatted_text(FormattedText([("#ff0000", text)]))


def unix_time() -> int:
    return int(time.time())


def in_days(last: int, days: int) -> int:
    return int(last + days * DAY_IN_SECONDS)


def unix_str(unix: int) -> str:
    if unix <= 0:
        return "N/A"
    tz = get_localzone()
    dt = datetime.fromtimestamp(unix)
    local_dt = tz.localize(dt)
    return local_dt.strftime("%Y-%b-%d (%a) [%I:%M:%S %p]")


def is_today(unix: int) -> bool:
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) == strip_time(utc_time())


def is_today_or_earlier(unix: int) -> bool:
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) <= strip_time(utc_time())


def strip_time(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def utc_time() -> datetime:
    return datetime.now(pytz.UTC)
