from abc import ABC
from abc import abstractmethod


class TorrentLinkInterface(ABC):
    _title = None
    _link = None

    def __init__(self, title, link):
        self.title = title
        self.link = link

    def __repr__(self):
        return "Torrent { %s }" % self.title

    @abstractmethod
    def get_title(self):
        pass

    @abstractmethod
    def get_link(self):
        pass

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
