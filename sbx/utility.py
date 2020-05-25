import time
from datetime import datetime

DAY_IN_SECONDS = 60 * 60 * 24


def unix_time():
    return int(time.time())


def in_days(last, days):
    return int(last + days * DAY_IN_SECONDS)


def unix_str(unix):
    if unix <= 0:
        return "N/A"
    return datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')


def is_today_or_earlier(a):
    return int(a) // DAY_IN_SECONDS <= unix_time() // DAY_IN_SECONDS
