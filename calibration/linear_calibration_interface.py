from abc import ABC, abstractmethod


class ILinearCalibratorInterface(ABC):
    @abstractmethod
    def make_fist(self):
        raise NotImplemented

    @abstractmethod
    def outstretch_hand(self):
        raise NotImplemented

    @abstractmethod
    def fold_thumb(self):
        raise NotImplemented

    @abstractmethod
    def finished(self):
        raise NotImplemented
