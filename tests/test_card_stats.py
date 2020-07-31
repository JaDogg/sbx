import os
from unittest import TestCase

from sbx.core.card import Card, CardMeta, Sm2

BOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "box")


class TestCardMeta(TestCase):
    def test_sm2_high_quality_becomes_later(self):
        sm2 = Sm2()
        stats = CardMeta()

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
        stats = CardMeta()

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
        stats = CardMeta()

        sm2.mark(stats, 5)
        a = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 2)
        b = stats.next_session

        stats.last_session = stats.next_session
        sm2.mark(stats, 0)
        c = stats.next_session

        self.assertLessEqual(c - b, b - a)

    def test_card_health_info(self):
        card_path = os.path.join(BOX_PATH, "test-card-ok.md")
        card = Card(card_path)
        self.assertTrue("leech" not in (card.human_readable_info))
        self.assertTrue("zero" not in (card.human_readable_info))
        self.assertTrue("OK" in (card.human_readable_info))

        card_path = os.path.join(BOX_PATH, "test-card-leech.md")
        card = Card(card_path)
        self.assertTrue("leech" in (card.human_readable_info))
        self.assertTrue("zero" not in (card.human_readable_info))
        self.assertTrue("OK" not in (card.human_readable_info))

        card_path = os.path.join(BOX_PATH, "test-card-zero.md")
        card = Card(card_path)
        self.assertTrue("leech" not in (card.human_readable_info))
        self.assertTrue("zero" in (card.human_readable_info))
        self.assertTrue("OK" not in (card.human_readable_info))

        card_path = os.path.join(BOX_PATH, "test-card-leech-zero.md")
        card = Card(card_path)
        self.assertTrue("leech" in (card.human_readable_info))
        self.assertTrue("zero" in (card.human_readable_info))
        self.assertTrue("OK" not in (card.human_readable_info))
