from modules.interfaces import TorrentClientInterface
from modules.interfaces import Torrent
from modules.interfaces import TorrentList
from modules.show import Show
from urllib.request import urlopen, Request
from lxml import html
import re


class EZTVClient(TorrentClientInterface):
    _base_url = "https://eztv.re"
    _find_path = ""
    _search_path = "/search/%s"
    _hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
            AppleWebKit/537.11 (KHTML, like Gecko) \
            Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    def __init__(self):
        pass

    def fetch_torrents(self, show: Show) -> TorrentList:
        url = self._base_url+self._search_path % \
            self._url_encode_title(show.title)
        request = Request(url, headers=self._hdr)
        con = urlopen(request)
        strHTML = con.read()
        con.close()
        page = html.fromstring(strHTML)
        results = page.xpath("//a[@class='download_1']")
        return list(
            map(self._create_torrent_from_link, results)
        )

    def _url_encode_title(self, title) -> str:
        sanitized_title = re.sub(r'[^ \.,a-z0-9]', '', title.lower())
        return re.sub(r'[ \.,]', '-', sanitized_title)

    def _create_torrent_from_link(self, anchor) -> Torrent:
        link = anchor.attrib['href']
        title = link.split('/')[-1]
        return Torrent(title, link)

    def download_torrent_file(self, show: Show, torrent: Torrent) -> str:
        filename = "/tmp/%s.S%02dE%02d.torrent" % (
            show.title.replace(' ', '.'),
            show.season,
            show.episode
        )
        request = Request(torrent.link, headers=self._hdr)
        f = urlopen(request)
        with open(filename, 'w') as fout:
            fout.write(f.read())
        f.close()
        return filename
