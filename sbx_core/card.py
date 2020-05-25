import json
from typing import List

from sbx_core.utility import unix_time, in_days, is_today_or_earlier, unix_str

SM2_BAD_QUALITY_THRESHOLD = 3

NEWLINE = "\n"


class CardStat:
    def __init__(self):
        self.repetitions: int = 0
        self.interval: int = 1
        self.easiness: float = 2.5
        self.next_session: int = -1
        self.last_session: int = -1
        self.past_quality: List[int] = []  # last 5 card quality levels

    def reset(self):
        self.repetitions = 0
        self.interval = 1
        self.easiness = 2.5
        self.next_session = -1
        self.last_session = -1
        self.past_quality = []  # last 5 card quality levels

    def pack(self) -> dict:
        return {
            "repetitions": self.repetitions,
            "interval": self.interval,
            "easiness": self.easiness,
            "next_session": self.next_session,
            "last_session": self.last_session,
            "past_quality": self.past_quality
        }

    def unpack_from(self, data: dict):
        self.repetitions = data["repetitions"]
        self.interval = data["interval"]
        self.easiness = data["easiness"]
        self.next_session = data["next_session"]
        self.last_session = data["last_session"]
        self.past_quality = data["past_quality"]

    def today(self) -> bool:
        if self.next_session == -1 or self.repetitions == 0:
            return True
        return is_today_or_earlier(self.next_session)

    def __str__(self):
        data = self.pack()
        data["next_session"] = unix_str(data["next_session"])
        data["last_session"] = unix_str(data["last_session"])
        return repr(data)


class Algo:
    def mark(self, stats: CardStat, quality: int) -> CardStat:
        pass


class Sm2(Algo):
    def mark(self, stats: CardStat, quality: int) -> CardStat:
        """
        # https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
        Update card stats based on given quality
        :param stats: saved details of this given card
        :param quality: number that is 0-5 inclusive -> 0 - blackout, 5 - remember very clearly
        This will update stats object
        """
        # New easiness based on quality
        easiness = stats.easiness - 0.8 + 0.28 * quality - 0.02 * quality * quality
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

        stats.past_quality = stats.past_quality[-4:] + [quality]

        current_time = unix_time()
        stats.next_session = in_days(max(stats.last_session, current_time), days=stats.interval)
        stats.last_session = current_time

        return stats


class Card:
    def __init__(self, path_: str, algo=Sm2):
        self._front: str = ""
        self._back: str = ""
        self._stat = CardStat()
        self._path = path_
        self._id = ""
        self._tags = []
        self._fully_loaded = False
        self._algo: Algo = algo()
        self._load_headers()

    @property
    def path(self):
        return self._path

    def _pack(self):
        return {
            "id": self._id,
            "tags": self._tags,
            "stats": self._stat.pack()
        }

    def _unpack(self, data: dict):
        self._id = data["id"]
        self._tags = data["tags"]
        self._stat.unpack_from(data["stats"])

    def mark(self, quality: int):
        assert 0 <= quality <= 5
        self._algo.mark(self._stat, quality)

    @property
    def today(self):
        return self._stat.today()

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

    def _load(self):
        with open(self._path, "r") as h:
            _ = h.readline()  # we already loaded stats line no need to load it again.
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
