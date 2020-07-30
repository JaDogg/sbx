import json
from typing import List, Optional

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

SM2_BAD_QUALITY_THRESHOLD = 3
PAST_STAT_COUNT = 20
LEECH_MIN_QUALITY = 3

NEWLINE = "\n"


class InvalidCardLoadAttempted(Exception):
    pass


class CardStat:
    def __init__(self, data: Optional[dict] = None):
        self.repetitions: int = 0
        self.actual_repetitions: int = 0
        self.interval: int = 1
        self.easiness: float = 2.5
        self.next_session: int = -1
        self.last_session: int = -1
        self.past_quality: List[int] = []
        self._version = "v1"
        self._algo = "sm2"
        if data:
            self.unpack_from(data)

    def reset(self):
        self.repetitions = 0
        self.actual_repetitions = 0
        self.interval = 1
        self.easiness = 2.5
        self.next_session = -1
        self.last_session = -1
        self.past_quality = []

    def pack(self) -> dict:
        return {
            "a": self.repetitions,
            "b": self.interval,
            "c": self.easiness,
            "next": self.next_session,
            "last": self.last_session,
            "pastq": pack_int_list(self.past_quality),
            "reps": self.actual_repetitions,
            "algo": self._algo,
            "sbx": self._version,
        }

    def unpack_from(self, data: dict):
        self._algo = data["algo"]
        self._version = data["sbx"]
        self.repetitions = data["a"]
        self.interval = data["b"]
        self.easiness = data["c"]
        self.next_session = data["next"]
        self.last_session = data["last"]
        self.past_quality = unpack_int_list(data["pastq"])
        possible_rep = max(self.repetitions, len(self.past_quality))
        self.actual_repetitions = data.get("reps", possible_rep)

    def today(self) -> bool:
        # WHY: You already studied today, come again tomorrow!
        if is_today(self.last_session):
            return False
        if self.next_session == -1 or self.repetitions == 0:
            return True
        return is_today_or_earlier(self.next_session)

    def leech(self) -> bool:
        if len(self.past_quality) < LEECH_MIN_QUALITY:
            return False
        return (
            self.past_quality[-1] < SM2_BAD_QUALITY_THRESHOLD
            and self.past_quality[-2] < SM2_BAD_QUALITY_THRESHOLD
            and self.past_quality[-3] < SM2_BAD_QUALITY_THRESHOLD
        )

    def last_zero(self) -> bool:
        if len(self.past_quality) < 1:
            return False
        return self.past_quality[-1] == 0

    def _past_quality_graph(self) -> str:
        if not self.past_quality:
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
        for idx, quality in enumerate(self.past_quality):
            table[quality][idx] = "*"

        return table_format.format(*["".join(x) for x in table])

    def _card_health(self) -> str:
        bad = []
        if self.leech():
            bad.append("leech")
        if self.last_zero():
            bad.append("last quality was zero")

        if not bad:
            return "OK"
        else:
            return " & ".join(bad)

    def __repr__(self):
        data = self.pack()
        data["next_session"] = unix_str(data["next_session"])
        data["last_session"] = unix_str(data["last_session"])
        return "CardStat(" + repr(data) + ")"

    def __str__(self):
        next_session = unix_str(self.next_session)
        last_session = unix_str(self.last_session)
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
            self.actual_repetitions,
            self._card_health(),
            self._past_quality_graph(),
        )


class Algo:
    def mark(self, stats: CardStat, quality: int) -> CardStat:
        pass


class Sm2(Algo):
    def mark(self, stats: CardStat, quality: int) -> CardStat:
        """
        # https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
        Update card stats based on given quality
        :param stats: saved details of this given card
        :param quality: how good you remember it
            0-5 inclusive -> 0 - blackout, 5 - remember clearly
        This will mutate stats object
        """
        # New easiness based on quality
        easiness = (
            stats.easiness - 0.8 + 0.28 * quality - 0.02 * quality * quality
        )
        stats.easiness = max(1.3, easiness)

        if quality < SM2_BAD_QUALITY_THRESHOLD:
            stats.repetitions = 0
        else:
            stats.repetitions += 1

        if stats.repetitions <= 1:
            stats.interval = 1
        elif stats.repetitions == 2:
            stats.interval = 6
        else:
            stats.interval *= easiness

        tmp = PAST_STAT_COUNT - 1
        stats.past_quality = stats.past_quality[-tmp:] + [quality]

        current_time = unix_time()
        stats.next_session = in_days(
            max(stats.last_session, current_time), days=stats.interval
        )
        stats.last_session = current_time
        # actual repetitions will not change by algorithm
        stats.actual_repetitions += 1

        return stats


class Card:
    def __init__(self, path_: str, algorithm_factory=Sm2):
        self._front: str = ""
        self._back: str = ""
        self._stat = CardStat()
        self._path = path_
        self._id = ""
        self._tags = []
        self._fully_loaded = False
        self._algorithm: Algo = algorithm_factory()
        self._load_headers()

    @property
    def stat(self):
        return self._stat

    @property
    def path(self):
        return self._path

    def _pack(self):
        return self._stat.pack()

    def _unpack(self, data: dict):
        self._stat.unpack_from(data)

    def mark(self, quality: int):
        assert 0 <= quality <= 5
        self._algorithm.mark(self._stat, quality)

    @property
    def today(self):
        return self._stat.today()

    @property
    def leech(self):
        return self._stat.leech()

    @property
    def zero(self):
        return self._stat.last_zero()

    @property
    def front(self):
        if not self._fully_loaded:
            self._load()
        return self._front

    @front.setter
    def front(self, new_front):
        if not new_front:
            raise ValueError("Cannot be empty")
        self._front = new_front

    @property
    def back(self):
        if not self._fully_loaded:
            self._load()
        return self._back

    @back.setter
    def back(self, new_back):
        if not new_back:
            raise ValueError("Cannot be empty")
        self._back = new_back

    def reset(self):
        self._stat = CardStat()

    def __str__(self):
        front_first_3 = "\n".join(self.front.splitlines()[:2]).strip()
        last_session = unix_str(self._stat.last_session)
        next_session = unix_str(self._stat.next_session)
        return "{}\nlast={}\nnext={}\npath={}".format(
            front_first_3, last_session, next_session, self.path
        )

    def to_formatted(self) -> Text:
        last_session = unix_str(self._stat.last_session)
        next_session = unix_str(self._stat.next_session)
        formatted = Text()
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
        except ValueError:
            raise InvalidCardLoadAttempted("Unable to load file")

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
