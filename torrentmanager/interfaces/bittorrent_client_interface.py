from abc import ABC
from abc import abstractmethod
from . import TorrentInterface


class BittorrentClientInterface(ABC):
    @abstractmethod
    def add_torrent(self, torrent: TorrentInterface) -> bool:
        pass

    def list_torrents(self) -> list:
        pass

    def delete_torrent(self, torrent: TorrentInterface) -> bool:
        pass
