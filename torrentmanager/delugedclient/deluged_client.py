from torrentmanager.interfaces import BittorrentClientInterface
from torrentmanager.interfaces import TorrentLinkInterface
from torrentmanager.interfaces import TorrentInterface
from torrentmanager.interfaces import TorrentList


class DelugedClient(BittorrentClientInterface):
    def add_torrent(self, torrent: TorrentLinkInterface) -> bool:
        pass

    def find(self, query: str) -> TorrentList:
        pass

    def list_torrents(self) -> TorrentList:
        pass

    def delete_torrent(self, torrent: TorrentInterface):
        pass
