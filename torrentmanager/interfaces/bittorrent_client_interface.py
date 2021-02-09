from abc import ABC
from abc import abstractmethod
from .torrent_link_interface import TorrentLinkInterface
from .torrent_interface import TorrentInterface
from .torrent_interface import TorrentList


class BittorrentClientInterface(ABC):
    @abstractmethod
    def __init__(self, download_folder: str):
        self.download_folder = download_folder

    @property
    @abstractmethod
    def download_folder(self) -> str:
        pass

    @download_folder.setter
    @abstractmethod
    def download_folder(self, folder: str):
        pass

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
