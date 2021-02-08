class TorrentError(Exception):
    _link = None

    def __init__(self, message, torrent: any):
        super().__init__(message)
        self._link = torrent.link
