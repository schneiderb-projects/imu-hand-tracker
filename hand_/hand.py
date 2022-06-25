from typing import Callable

from hand_.finger import Finger


class Hand:
    def __init__(
        self,
        thumb: Finger,
        pointer: Finger,
        middle: Finger,
        ring: Finger,
        pinky: Finger,
        palm: Finger,
    ):
        self._thumb: Finger = thumb
        self._pointer: Finger = pointer
        self._middle: Finger = middle
        self._ring: Finger = ring
        self._pinky: Finger = pinky
        self._palm: Finger = palm
        self._dict: dict[str, Callable[[], Finger]] = {
            "thumb": self.thumb,
            "pointer": self.pointer,
            "middle": self.middle,
            "ring": self.ring,
            "pinky": self.pinky,
            "palm": self.palm,
        }

    def thumb(self) -> Finger:
        return self._thumb

    def pointer(self) -> Finger:
        return self._pointer

    def middle(self) -> Finger:
        return self._middle

    def ring(self) -> Finger:
        return self._ring

    def pinky(self) -> Finger:
        return self._pinky

    def palm(self) -> Finger:
        return self._palm

    def __getitem__(self, item) -> Finger:
        return self._dict[item]()

    def __str__(self):
        toreturn = "{"
        for k in self._dict.keys():
            toreturn += str(k) + ": ["
            for j in self._dict[k]().joints():
                toreturn += str(j) + ", "
            toreturn = toreturn[:-2] + "], "

        return toreturn[:-2] + "}"
