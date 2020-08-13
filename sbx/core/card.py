"""
Contains important `Card`, `CardMeta`, `CardAlgo` classes
"""
import abc
import json
from abc import ABCMeta
from typing import Dict, List, Optional, Union

from sbx.core.utility import (
    Text,
    in_days,
    is_today,
    is_today_or_earlier,
    pack_int_list,
    unix_str,
    unix_time,
    unpack_int_list,
)

BAD_QUALITY_THRESHOLD = 3
PAST_STAT_COUNT = 20
LEECH_MIN_QUALITY = 3

NEWLINE = "\n"
CARD_VERSION = "v1"
REQUIRED_FIELDS = ["reps", "last", "next", "pastq", "algo", "sbx"]


class InvalidCardLoadAttempted(Exception):
    """Type of exception raised when an invalid class is loaded"""

    pass


class CardAlgo(metaclass=ABCMeta):
    """Card Scheduling Algorithm"""

    @abc.abstractmethod
    def mark(self, meta: "CardMeta", quality: int):
        """
        Modify a card & mark it with given quality

        * `meta` - meta data of a card
        * `quality` - quality of a card given by user
        """
        pass

    def can_study_now(self, meta: "CardMeta") -> bool:
        """Is this card scheduled for now?"""
        # WHY: You already studied today, come again tomorrow!
        if is_today(meta.last_session):
            return False
        if meta.next_session == -1 or meta.actual_repetitions == 0:
            return True
        return is_today_or_earlier(meta.next_session)

    def is_leech(self, meta: "CardMeta") -> bool:
        """Is this card a leech?"""
        if len(meta.past_quality) < LEECH_MIN_QUALITY:
            return False
        return (
            meta.past_quality[-1] < BAD_QUALITY_THRESHOLD
            and meta.past_quality[-2] < BAD_QUALITY_THRESHOLD
            and meta.past_quality[-3] < BAD_QUALITY_THRESHOLD
        )

    def is_last_zero(self, meta: "CardMeta") -> bool:
        """Is last quality of the card zero?"""
        if len(meta.past_quality) < 1:
            return False
        return meta.past_quality[-1] == 0


class CardMeta:
    """Card meta data"""

    def __init__(self, data: Optional[dict] = None):
        self.algo_state: Dict[str, Union[str, float, int, bool]] = {}
        self.actual_repetitions: int = 0
        self.next_session: int = -1
        self.last_session: int = -1
        self.past_quality: List[int] = []
        self.version = "v1"
        self.algo = "sm2"
        if data:
            self.update_from_dict(data)

    def reset(self):
        """Reset card meta data"""
        self.algo_state = {}
        self.actual_repetitions = 0
        self.next_session = -1
        self.last_session = -1
        self.past_quality = []

    def to_dict(self) -> dict:
        """Pack card meta data to a dictionary"""
        temp = self.algo_state.copy()
        temp.update(
            {
                "next": self.next_session,
                "last": self.last_session,
                "pastq": pack_int_list(self.past_quality),
                "reps": self.actual_repetitions,
                "algo": self.algo,
                "sbx": self.version,
            }
        )
        return temp

    def update_from_dict(self, data: dict):
        """
        Set internal data based on given dictionary

        * `data` - dictionary to read data from
        """
        self.algo = data["algo"]
        self.version = data["sbx"]
        self.next_session = data["next"]
        self.last_session = data["last"]
        self.past_quality = unpack_int_list(data["pastq"])

        # Revert to length of past_quality if reps are not set
        possible_rep = len(self.past_quality)
        self.actual_repetitions = data.get("reps", possible_rep)

        # Other keys are used by algorithm
        self.algo_state = data.copy()
        for required_key in REQUIRED_FIELDS:
            del self.algo_state[required_key]

    def __repr__(self):
        data = self.to_dict()
        data["next"] = unix_str(data["next"])
        data["last"] = unix_str(data["last"])
        return "CardStat(" + repr(data) + ")"


class Sm2(CardAlgo):
    """
    Super Memo 2 Algorithm for Card Scheduling
    based on - https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
    """

    def mark(self, meta: "CardMeta", quality: int):
        """
        Update card meta data based on given quality

        * `meta` -  saved details of this given card
        * `quality` -  how good you remember it
            0-5 inclusive -> 0 - blackout, 5 - remember clearly

        This will mutate meta data object
        """
        # repetitions - a, interval - b, easiness - c
        state = meta.algo_state
        repetitions = int(state.get("a", 0))
        interval = float(state.get("b", 1))
        easiness = float(state.get("c", 2.5))

        # New easiness based on quality
        easiness = easiness - 0.8 + 0.28 * quality - 0.02 * quality * quality
        easiness = max(1.3, easiness)

        if quality < BAD_QUALITY_THRESHOLD:
            repetitions = 0
        else:
            repetitions += 1

        if repetitions <= 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval *= easiness

        tmp = PAST_STAT_COUNT - 1
        meta.past_quality = meta.past_quality[-tmp:] + [quality]

        current_time = unix_time()
        meta.next_session = in_days(
            max(meta.last_session, current_time), days=int(interval)
        )
        meta.last_session = current_time
        # actual repetitions will not change by algorithm
        meta.actual_repetitions += 1

        state["a"] = repetitions
        state["b"] = interval
        state["c"] = easiness


class Card:
    """A flash card"""

    def __init__(self, path_: str, algorithm_factory=Sm2):
        self._front: str = ""
        self._back: str = ""
        self._stat = CardMeta()
        self._path = path_
        self._fully_loaded = False
        self._algorithm: CardAlgo = algorithm_factory()
        self._load_headers()

    @property
    def meta(self) -> CardMeta:
        """Get meta data of a card"""
        return self._stat

    @property
    def path(self) -> str:
        """Get path of the card"""
        return self._path

    def _pack(self):
        return self._stat.to_dict()

    def _unpack(self, data: dict):
        self._stat.update_from_dict(data)

    def mark(self, quality: int):
        """
        Mark a card with quality

        * `quality` - 0-5 (inclusive) level of how much you remember
        """
        assert 0 <= quality <= 5
        self._algorithm.mark(self._stat, quality)

    @property
    def today(self) -> bool:
        """Is this card scheduled for today?"""
        return self._algorithm.can_study_now(self._stat)

    @property
    def leech(self) -> bool:
        """Is this card a leech?"""
        return self._algorithm.is_leech(self._stat)

    @property
    def zero(self) -> bool:
        """Is this card's last quality is set to zero?"""
        return self._algorithm.is_last_zero(self._stat)

    @property
    def front(self) -> str:
        """Get front of the card"""
        if not self._fully_loaded:
            self._load()
        return self._front

    @front.setter
    def front(self, new_front: str):
        """
        Set front of the card

        * `new_front` - new front of the card (Cannot be empty)
        """
        if not new_front:
            raise ValueError("Cannot be empty")
        self._front = new_front

    @property
    def back(self) -> str:
        """Get back of the card"""
        if not self._fully_loaded:
            self._load()
        return self._back

    @back.setter
    def back(self, new_back: str):
        """
        Update card's back

        * `new_back` - new front of the card (Cannot be empty)
        """
        if not new_back:
            raise ValueError("Cannot be empty")
        self._back = new_back

    def reset(self):
        """Reset card's meta data"""
        self._stat = CardMeta()

    @property
    def human_readable_info(self) -> str:
        """Get a human readable info dump of the card"""
        next_session = unix_str(self._stat.next_session)
        last_session = unix_str(self._stat.last_session)
        return """
        Next Session: {}
        Last Session: {}
        Repetitions: {}
        Health: {}
        ------------------------
        Past Quality (last 20):
        ------------------------
        {}
        """.format(
            next_session,
            last_session,
            self._stat.actual_repetitions,
            self._health(),
            self._past_quality_graph(),
        )

    def _health(self) -> str:
        """Get card health as a human readable string"""
        bad = []
        if self.leech:
            bad.append("leech")
        if self.zero:
            bad.append("last quality was zero")

        if not bad:
            return "OK"
        else:
            return " & ".join(bad)

    def _past_quality_graph(self) -> str:
        """Get past quality as an ASCII graph"""
        if not self._stat.past_quality:
            return "No information available"

        table = [[" "] * 20 for x in range(6)]
        table_format = """
        q  |
        u 5|{5}
        a 4|{4}
        l 3|{3}
        i 2|{2}
        t 1|{1}
        y 0|{0}
        ------------------------
        rep 1       10        20
        """.strip()
        for idx, quality in enumerate(self._stat.past_quality):
            table[quality][idx] = "*"

        return table_format.format(*["".join(x) for x in table])

    def __str__(self):
        front_first_3 = "\n".join(self.front.splitlines()[:2]).strip()
        last_session = unix_str(self._stat.last_session)
        next_session = unix_str(self._stat.next_session)
        return "{}\nlast={}\nnext={}\npath={}".format(
            front_first_3, last_session, next_session, self.path
        )

    def to_formatted(self) -> Text:
        """Create formatted text representation of the card"""
        front_first_3 = "\n".join(self.front.splitlines()[:2]).strip()
        last_session = unix_str(self._stat.last_session)
        next_session = unix_str(self._stat.next_session)
        formatted = Text()
        formatted = formatted.yellow(front_first_3).newline()
        formatted = (
            formatted.cyan("last").normal("=").normal(last_session).newline()
        )
        formatted = formatted.cyan("next").normal("=")
        if self.today:
            formatted = formatted.red(next_session).newline()
        else:
            formatted = formatted.green(next_session).newline()
        formatted = formatted.cyan("path").normal("=").normal(self.path)
        return formatted

    def save(self):
        """Save card to storage"""
        if not self._fully_loaded:
            self._load()
        with open(self._path, "w+") as h:
            h.write("<!-- | ")
            h.write(json.dumps(self._pack()))
            h.write(" | -->")
            h.write(NEWLINE)
            h.write("<!-- [[FRONT]] -->")
            h.write(NEWLINE)
            h.write(self._front)
            h.write(NEWLINE)
            h.write("<!-- [[BACK]] -->")
            h.write(NEWLINE)
            h.write(self._back)
            h.write(NEWLINE)

    def _load_headers(self):
        try:
            with open(self._path, "r") as h:
                data = h.readline()
                _, json_data, _ = data.split("|")
                self._unpack(json.loads(json_data.strip()))
        except FileNotFoundError:
            self._fully_loaded = True
        except (ValueError, KeyError) as ex:
            raise InvalidCardLoadAttempted(
                "Unable to load file: {!r}".format(self._path)
            ) from ex

    def _load(self):
        with open(self._path, "r") as h:
            _ = (
                h.readline()
            )  # we already loaded stats line no need to load it again.
            front = []
            back = []
            mode = 0
            for line in h:
                if mode != 1 and "[[FRONT]]" in line:
                    mode = 1
                    continue
                if mode == 1 and "[[BACK]]" in line:
                    mode = 2
                    continue
                if mode == 1:
                    front.append(line.rstrip())
                elif mode == 2:
                    back.append(line.rstrip())

            self._front = NEWLINE.join(front)
            self._back = NEWLINE.join(back)

        self._fully_loaded = True
