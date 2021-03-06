import re

from urllib.request import urlopen
from urllib.request import Request
from urllib.request import HTTPError
from urllib.request import URLError
from urllib.parse import quote
from lxml import html

from torrentmanager.eztvclient.eztv_torrent import EZTVTorrent
from torrentmanager.exceptions import TorrentError
from torrentmanager.interfaces import TorrentProviderInterface
from torrentmanager.interfaces import TorrentLinkInterface
from torrentmanager.interfaces import TorrentLinkList
from torrentmanager.show import Show


class EZTVClient(TorrentProviderInterface):
    _base_url = "https://eztv.re"
    _find_path = ""
    _search_path = "/search/%s"
    _accept_types = [
        "text/html",
        "application/xhtml+xml",
        "application/xml;q=0.9",
        "*/*;q=0.8"
    ]
    _user_agent = "Mozilla/5.0 (X11; Linux x86_64) " \
        "AppleWebKit/537.11 (KHTML, like Gecko) " \
        "Chrome/23.0.1271.64 Safari/537.11"
    _hdr = {
        "User-Agent": _user_agent,
        "Accept": ",".join(_accept_types),
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }

    def __init__(self):
        pass

    def fetch_torrents(self, show: Show) -> TorrentLinkList:
        url = self._base_url+self._search_path % \
            self._url_encode_title(show.title)
        try:
            request = Request(url, headers=self._hdr)
            con = urlopen(request)
            strHTML = con.read()
            con.close()
            page = html.fromstring(strHTML)
            results = page.xpath("//a[@class='download_1']")
            return list(
                map(self._create_torrent_from_link, results))
        except HTTPError as e:
            print("HTTP Error:", str(e), url)
        except URLError as e:
            print("URL Error:", str(e), url)

    def _url_encode_title(self, title) -> str:
        sanitized_title = re.sub(r"[^ \.,a-z0-9]", "", title.lower())
        return re.sub(r"[ \.,]", "-", sanitized_title)

    def _create_torrent_from_link(self, anchor) -> TorrentLinkInterface:
        link = anchor.attrib["href"]
        title = link.split("/")[-1]
        torrent = EZTVTorrent(title, link)
        torrent.client = self
        return torrent

    def download_torrent_file(self, torrent: TorrentLinkInterface) -> str:
        try:
            filename = "/tmp/%s" % quote(torrent.title, safe="[]")
            request = Request(
                quote(torrent.link, safe=":/[]"),
                headers=self._hdr)
            f = urlopen(request)
            with open(filename, "wb") as fout:
                fout.write(f.read())
            f.close()
            return filename
        except HTTPError as e:
            print("HTTP Error:", str(e), url)
        except URLError as e:
            print("URL Error:", str(e), url)
        raise TorrentError("Couldn't download torrent file", torrent)
