import feedparser

from torrentmanager.interfaces import TorrentClientInterface
from torrentmanager.interfaces import TorrentInterface
from torrentmanager.interfaces import TorrentList
from torrentmanager.rarbgclient.rarbg_torrent import RarbgTorrent


class RarbgClient(TorrentClientInterface):
    _url = "http://rarbg.to/rssdd.php?category=1;18;41;49"

    def __init__(self):
        pass

    def fetch_torrents(self) -> TorrentList:
        try:
            feed = feedparser.parse(self._url)
            feedentries = feed['entries']
            feed = None
            return list(map(
                self._create_feed_entry,
                feedentries))
        except Exception as e:
            print("Error while reading the feed: %s" % e)

    def _create_feed_entry(self, entry: dict) -> TorrentInterface:
        title = entry['title']
        link = entry['link']
        return RarbgTorrent(title, link)