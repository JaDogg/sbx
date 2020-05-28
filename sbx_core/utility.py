import time
from datetime import datetime

import pytz
from tzlocal import get_localzone


DAY_IN_SECONDS = 60 * 60 * 24


def unix_time():
    return int(time.time())


def in_days(last, days):
    return int(last + days * DAY_IN_SECONDS)


def unix_str(unix):
    if unix <= 0:
        return "N/A"
    tz = get_localzone()
    dt = datetime.fromtimestamp(unix)
    local_dt = tz.localize(dt)
    return local_dt.strftime("%Y-%b-%d (%a) [%I:%M:%S %p]")


def strip_time(dt):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def utc_time():
    return datetime.now(pytz.UTC)


def is_today(unix):
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) == strip_time(utc_time())


def is_today_or_earlier(unix):
    dt = datetime.fromtimestamp(unix, pytz.UTC)
    return strip_time(dt) <= strip_time(utc_time())
