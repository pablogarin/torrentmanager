import feedparser
from modules.interfaces import FeedClientInterface
from modules.interfaces import FeedEntry
from modules.interfaces import FeedList


class RarbgClient(FeedClientInterface):
    _url = "http://rarbg.to/rssdd.php?category=1;18;41;49"

    def __init__(self):
        pass

    def read(self) -> FeedList:
        try:
            feed = feedparser.parse(self._url)
            feedentries = feed['entries']
            feed = None
            return list(map(
                self._create_feed_entry,
                feedentries))
        except Exception as e:
            print("Error while reading the feed: %s" % e)

    def _create_feed_entry(self, entry: dict) -> FeedEntry:
        title = entry['title']
        link = entry['link']
        return FeedEntry(title, link)
