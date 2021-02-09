from abc import ABC
from abc import abstractmethod
from typing import List

from .torrent_link_interface import TorrentLinkInterface


TorrentLinkList = List[TorrentLinkInterface]


class TorrentProviderInterface(ABC):
    @abstractmethod
    def fetch_torrents(self, query: str) -> TorrentLinkList:
        pass
