from abc import ABC, abstractmethod
from typing import List


class FeedEntry(object):
    __title = None
    __link = None

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def __repr__(self):
        return "FeedEntry { %s }" % self.title

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def link(self):
        return self.__link

    @link.setter
    def link(self, link):
        self.__link = link


FeedList = List[FeedEntry]


class FeedClientInterface(ABC):
    @abstractmethod
    def read(self, query: str) -> FeedList:
        pass
