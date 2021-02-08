from modules.interfaces import TorrentInterface
from modules.interfaces import TorrentClientInterface


class EZTVTorrent(TorrentInterface):
    _client = None

    def __init__(self, title, link):
        super().__init__(title, link)

    def get_title(self):
        return self.title

    def get_link(self):
        return self.client.download_torrent_file(self)

    @property
    def client(self) -> TorrentClientInterface:
        return self._client

    @client.setter
    def client(self, client: TorrentClientInterface):
        self._client = client
