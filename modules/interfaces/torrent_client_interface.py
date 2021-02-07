from abc import ABC, abstractmethod
from typing import List


class Torrent(object):
    _title = None
    _link = None

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def __repr__(self):
        return "Torrent { %s }" % self.title

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


TorrentList = List[Torrent]


class TorrentClientInterface(ABC):
    @abstractmethod
    def fetch_torrents(self, query: str) -> TorrentList:
        pass
