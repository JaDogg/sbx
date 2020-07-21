from unittest import TestCase

from sbx.sbx_core.utility import *


class TestUtility(TestCase):
    def test_unix_time(self):
        self.assertTrue(unix_time() > 0)

    def test_in_days(self):
        in_four = in_days(unix_time(), 4)
        in_five = in_days(unix_time(), 5)
        self.assertTrue(in_five > in_four)

    def test_is_today(self):
        self.assertTrue(is_today(unix_time()))
        self.assertFalse(is_today(in_days(unix_time(), 5)))

    def test_is_today_or_earlier(self):
        self.assertTrue(is_today_or_earlier(unix_time()))
        self.assertFalse(is_today_or_earlier(in_days(unix_time(), 5)))
        self.assertTrue(is_today_or_earlier(in_days(unix_time(), -2)))

    def test_unix_str(self):
        timestamp = 1590799096
        self.assertIsNotNone(unix_str(timestamp))
        # Even in other timezones 20 should be present in the time string
        self.assertTrue("20" in unix_str(timestamp))
