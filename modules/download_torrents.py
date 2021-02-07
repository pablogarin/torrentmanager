#!/usr/bin/env python
import os
import sys
import re
import subprocess
import time
import threading
import socket
from urllib.request import urlopen, Request, URLError, HTTPError
from lxml import html
from OpenSSL import SSL
from datetime import date
from queue import PriorityQueue
from modules.interfaces import PersistanceInterface
from modules.interfaces import TorrentClientInterface
from modules.interfaces import Torrent
from modules.interfaces import TorrentList
from modules.show import Show
from modules.eztvclient import EZTVClient
# https://rarbg.unblocked.stream/torrents.php?imdb=

socket.setdefaulttimeout(3)


class TorrentFinder:
    _database = None
    _torrent_folder = ''
    _torrent_quality = ''
    _update_after = False
    _shows = []

    def __init__(
            self,
            database: PersistanceInterface,
            torrent_folder: str = '',
            torrent_quality: str = ''):
        self._database = database
        self._torrent_folder = torrent_folder
        self._torrent_quality = torrent_quality
        self._shows = []
        """
        self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41",
        "https://kat.cr/usearch/category:tv%20age:hour/?rss=1"]
        """
        # self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41"]
        self.safeRSS = [
            "https://eztv.io/ezrss.xml",
            "http://rarbg.to/rss.php?category=1;18;41;49"]
        self.safeRSS = ["http://rarbg.to/rssdd.php?category=1;18;41;49"]
        self._set_show_list()
        # FIXME: Decouple this!
        self._eztv = EZTVClient()

    def _set_show_list(self):
        for show in self._database.find():
            self._shows.append(show)

    def readRSS(self, torrent_client: TorrentClientInterface):
        self._check_torrent_list_for_show(torrent_client.fetch_torrents())

    def _check_torrent_list_for_show(self, torrent_list: TorrentList):
        for show in self._shows:
            print("Checking show %s" % show.title)
            matches = PriorityQueue()
            for index, torrent in enumerate(torrent_list):
                if self._should_download_torrent(
                        torrent.title,
                        show):
                    matches.put((1, index))
                elif self._should_download_torrent(
                        torrent.title,
                        show,
                        False):
                    matches.put((2, index))
            if not matches.empty():
                _, index = matches.get()
                torrent = torrent_list[index]
                self._add_torrent(torrent, show)

    def checkByName(self):
        print("Searching by name. This might take a while (1-5 minutes)...\n")
        tmp = []
        for show in self._shows:
            tmp.append((show,))
        self.run_parallel_in_threads(self.lookupTorrents, tmp)

    def run_parallel_in_threads(self, target, args_list):
        threads = [
            threading.Thread(target=target, args=args) for args in args_list
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("Search done!")

    def lookupTorrents(self, show: Show):
        self._check_torrent_list_for_show(self._eztv.fetch_torrents(show))

    def _should_download_torrent(
            self,
            title: str,
            show: Show,
            check_quality: bool = True) -> bool:
        if check_quality:
            return self._is_entry_scheduled(title, show) and\
                self._has_expected_quality(title) and\
                self._is_entry_current_episode(title, show)
        return self._is_entry_scheduled(title, show) and\
            self._is_entry_current_episode(title, show)

    def _is_entry_scheduled(self, title: str, show: Show) -> bool:
        match = re.search(show.regex, title.lower())
        return match is not None

    def _has_expected_quality(self, title: str) -> bool:
        if self._torrent_quality == "none":
            return True
        regexp = re.sub(
            r'[pP]',
            '[pP]',
            self._torrent_quality)
        match = re.search(regexp, title)
        if match is None:
            return False
        return True

    def _is_entry_current_episode(self, title: str, show: Show) -> bool:
        regexp = r'((S[0-9]{,2}E[0-9]{,2})|([0-9]{1,2}[xX][0-9]{1,2}))'
        match = re.search(regexp, title)
        if not match:
            return False
        feed_episode = match.group(0)
        current_episode = set([
            "S%02dE%02d" % (show.season, show.episode),
            "%dX%d" % (show.season, show.episode),
            "%dX%02d" % (show.season, show.episode),
        ])
        return feed_episode.upper() in current_episode

    def _update_episode(self, show: Show):
        print("Updating database...")
        show.episode += 1
        show.save()

    def _add_torrent(self, torrent: Torrent, show: Show):
        folder = show.get_folder()
        torrent_path = torrent.link
        if "magnet:" not in torrent_path:
            torrent_path = self._eztv.download_torrent_file(show, torrent)
        addCommand = "deluge-console add '%s' --path=%s" % (
            torrent_path,
            self._torrent_folder+folder
        )
        print(addCommand)
        result = subprocess.check_output(addCommand, shell=True)
        print(result)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    print("Deluged tv shows Manager.\n")
    option = None
    if len(argv) == 2:
        option = argv[1]
    if option is not None:
        if option == "-n":
            finder = torrentFinder()
            finder.checkByName()
        else:
            print("Unknown Option.")
    else:
        finder = torrentFinder()
        finder.readRSS()
    return 0


if __name__ == '__main__':
    sys.exit(main())
