from abc import ABC
from abc import abstractmethod
from typing import List


class TorrentInterface(ABC):
    @property
    @abstractmethod
    def id_(self) -> str:
        pass

    @id_.setter
    @abstractmethod
    def id_(self, id_: str):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @name.setter
    @abstractmethod
    def name(self, name: str):
        pass

    @property
    @abstractmethod
    def status(self) -> str:
        pass

    @status.setter
    @abstractmethod
    def status(self, status: str):
        pass

    @property
    @abstractmethod
    def progress(self):
        pass

    @progress.setter
    @abstractmethod
    def progress(self, progress: str):
        pass


TorrentList = List[TorrentInterface]
