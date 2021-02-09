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
    def progress(self) -> str:
        pass

    @progress.setter
    @abstractmethod
    def progress(self, progress: str):
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @size.setter
    @abstractmethod
    def size(self, size: str):
        pass

    @property
    @abstractmethod
    def age(self):
        pass

    @age.setter
    @abstractmethod
    def age(self, age: str):
        pass


TorrentList = List[TorrentInterface]
