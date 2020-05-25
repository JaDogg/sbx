from unittest import TestCase

from sbx_core.card import Sm2, CardStat


class TestCardStats(TestCase):
    def test_sm2_high_quality_becomes_later(self):
        sm2 = Sm2()
        stats = CardStat()

        sm2.mark(stats, 3)
        a = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 4)
        b = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 5)
        c = stats.next_session

        self.assertGreater(c - b, b - a)

    def test_sm2_high_quality_becomes_later_from_zero(self):
        sm2 = Sm2()
        stats = CardStat()

        sm2.mark(stats, 0)
        a = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 4)
        b = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 5)
        c = stats.next_session

        self.assertGreater(c - b, b - a)

    def test_sm2_low_quality_become_repeat_often(self):
        sm2 = Sm2()
        stats = CardStat()

        sm2.mark(stats, 5)
        a = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 2)
        b = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 0)
        c = stats.next_session

        self.assertLessEqual(c - b, b - a)
