from torrentmanager.interfaces import TorrentLinkInterface


class RarbgTorrent(TorrentLinkInterface):
    def __init__(self, title, link):
        super().__init__(title, link)

    def get_title(self):
        return self.title

    def get_link(self):
        return self.link
