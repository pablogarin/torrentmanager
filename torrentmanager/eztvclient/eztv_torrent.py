from torrentmanager.interfaces import TorrentProviderInterface
from torrentmanager.interfaces import TorrentLinkInterface


class EZTVTorrent(TorrentLinkInterface):
    _client = None

    def __init__(self, title, link):
        super().__init__(title, link)

    def get_title(self):
        return self.title

    def get_link(self):
        return self.client.download_torrent_file(self)

    @property
    def client(self) -> TorrentProviderInterface:
        return self._client

    @client.setter
    def client(self, client: TorrentProviderInterface):
        self._client = client
