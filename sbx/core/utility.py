import time
import typing
from datetime import datetime

import pytz
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from tzlocal import get_localzone

DAY_IN_SECONDS = 60 * 60 * 24


class Text:
    """
    Print coloured text
    >>> Text().normal("Hello").red(" World").print()
    Hello World
    """

    def __init__(self):
        self.text = []

    def red(self, text: str) -> "Text":
        """
        Append red coloured text
        :param text: str: text
        """
        self.text.append(("#ff0000", text))
        return self

    def yellow(self, text: str) -> "Text":
        """
        Append yellow coloured text
        :param text: str: text
        """
        self.text.append(("#ffff00", text))
        return self

    def blue(self, text: str) -> "Text":
        """
        Append blue coloured text
        :param text: str: text
        """
        self.text.append(("#0000ff", text))
        return self

    def green(self, text: str) -> "Text":
        """
        Append green coloured text
        :param text: str: text
        """
        self.text.append(("#00ff00", text))
        return self

    def cyan(self, text: str) -> "Text":
        """
        Append cyan coloured text
        :param text: str: text
        """
        self.text.append(("#00ffff", text))
        return self

    def normal(self, text: str) -> "Text":
        """
        Append text
        :param text: str: text

        """
        self.text.append(("", text))
        return self

    def newline(self) -> "Text":
        """Append a new line"""
        self.text.append(("", "\n"))
        return self

    def print(self):
        """Display current configured text"""
        print_formatted_text(FormattedText(self.text))

    def to_formatted(self) -> FormattedText:
        """Get current configured formatted text"""
        return FormattedText(self.text)


def pack_int_list(qualities: typing.List[int]) -> str:
    """
    Pack a list of integers to a string.
    This is useful for packing a list of qualities to a string
    :param qualities: typing.List[int]: list of qualities
    """
    return "".join([str(x) for x in qualities])


def unpack_int_list(qualities) -> typing.List[int]:
    """
    Unpack a string containing list of qualities to a list of integers
    :param qualities: qualities list as a string
    """
    return [int(x) for x in qualities]


def print_error(text: str):
    """
    Print an error in red colour
    :param text: str: text to print
    """
    print_formatted_text(FormattedText([("#ff0000", text)]))


def unix_time() -> int:
    """Get UNIX timestamp"""
    return int(time.time())


def in_days(last: int, days: int) -> int:
    """
    Add days to given UNIX timestamp
    :param last: int: day to start from (UNIX timestamp)
    :param days: int: number of days in future

    """
    return int(last + days * DAY_IN_SECONDS)


def unix_str(unix: int) -> str:
    """
    Convert a UNIX timestamp to a string
    :param unix: int: UNIX timestamp
    """
    if unix <= 0:
        return "N/A"
    tz = get_localzone()
    dt = datetime.fromtimestamp(unix)
    local_dt = tz.localize(dt)
    return local_dt.strftime("%Y-%b-%d (%a) [%I:%M:%S %p]")


def is_today(unix: int) -> bool:
    """
    Is given UNIX timestamp sometime today?
    :param unix: int: UNIX timestamp
    """
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) == strip_time(utc_time())


def is_today_or_earlier(unix: int) -> bool:
    """
    Is given UNIX timestmap occur sometime today, or earlier
    :param unix: int: UNIX timestamp
    """
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) <= strip_time(utc_time())


def strip_time(dt: datetime) -> datetime:
    """
    Strip a given datetime object of hours, minutes, seconds, ms
    :param dt: datetime: date time object to strip
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def utc_time() -> datetime:
    """Get standard UTC time"""
    return datetime.now(pytz.UTC)
