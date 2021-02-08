from abc import ABC, abstractmethod
from typing import List
from .torrent_interface import TorrentInterface


TorrentList = List[TorrentInterface]


class TorrentClientInterface(ABC):
    @abstractmethod
    def fetch_torrents(self, query: str) -> TorrentList:
        pass
