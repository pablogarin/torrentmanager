from abc import ABC
from abc import abstractmethod
from .torrent_link_interface import TorrentLinkInterface
from .torrent_interface import TorrentInterface
from .torrent_interface import TorrentList


class BittorrentClientInterface(ABC):
    @abstractmethod
    def add_torrent(self, torrent: TorrentLinkInterface) -> bool:
        pass

    @abstractmethod
    def find(self, query: str) -> TorrentList:
        pass

    @abstractmethod
    def list_torrents(self) -> TorrentList:
        pass

    @abstractmethod
    def delete_torrent(self, torrent: TorrentInterface) -> bool:
        pass
