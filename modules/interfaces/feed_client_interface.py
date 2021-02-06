from abc import ABC, abstractmethod
from typing import List


class FeedEntry(object):
    _title = None
    _link = None

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def __repr__(self):
        return "FeedEntry { %s }" % self.title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, link):
        self._link = link


FeedList = List[FeedEntry]


class FeedClientInterface(ABC):
    @abstractmethod
    def read(self, query: str) -> FeedList:
        pass
