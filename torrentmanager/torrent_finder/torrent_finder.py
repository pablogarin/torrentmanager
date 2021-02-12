import re
import subprocess
import sys
import time
import threading
from queue import PriorityQueue

from torrentmanager.interfaces import PersistanceInterface
from torrentmanager.interfaces import TorrentProviderInterface
from torrentmanager.interfaces import BittorrentClientInterface
from torrentmanager.interfaces import TorrentLinkInterface
from torrentmanager.interfaces import TorrentLinkList
from torrentmanager.show import Show


class TorrentFinder:
    _database = None
    _bittorrent_client = ""
    _torrent_quality = ""
    _enforce_quality = ""
    _updates = []
    _shows = []

    def __init__(
            self,
            database: PersistanceInterface,
            bittorrent_client: BittorrentClientInterface,
            torrent_quality: str = "",
            enforce_quality: str = "no"):
        self._database = database
        self._bittorrent_client = bittorrent_client
        self._torrent_quality = torrent_quality
        self._enforce_quality = enforce_quality
        self._shows = []
        self._set_show_list()

    def _set_show_list(self):
        for show in self._database.find():
            self._shows.append(show)

    def read_rss(self, torrent_client: TorrentProviderInterface):
        torrent_list = torrent_client.fetch_torrents()
        for show in self._shows:
            print("%s | Checking show %s" % (
                time.strftime("%Y-%m-%d %H:%M:%S"),
                show.title))
            index = self._find_show_in_torrent_list(show, torrent_list)
            if index >= 0:
                torrent = torrent_list[index]
                self._add_torrent(torrent, show)
        self._finished_show_check()

    def _find_show_in_torrent_list(
            self,
            show: Show,
            torrent_list: TorrentLinkList) -> int:
        matches = PriorityQueue()
        accept_any = self._enforce_quality == "no"
        for index, torrent in enumerate(torrent_list):
            if self._should_download_torrent(
                    torrent.title,
                    show):
                matches.put((1, index))
            elif accept_any and self._should_download_torrent(
                    torrent.title,
                    show,
                    False):
                matches.put((2, index))
        if not matches.empty():
            _, index = matches.get()
            return index
        return -1

    def check_scheduled_shows(self, torrent_client: TorrentProviderInterface):
        print("Checking all scheduled shows.")
        print("This might take a while (1-5 minutes)")
        tmp = []
        for show in self._shows:
            tmp.append((show, torrent_client))
        self.run_parallel_in_threads(
            self._find_episode_for_show,
            tmp,
            self._finished_show_check)

    def _finished_show_check(self):
        print("Finished check!")
        if len(self._updates) > 0:
            print("Updating shows")
            for show in self._updates:
                self._update_episode(show)
            self._updates = []

    def run_parallel_in_threads(self, target, args_list, callback):
        threads = [
            threading.Thread(target=target, args=args) for args in args_list
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if callback.__class__.__name__ == "method":
            callback()

    def _find_episode_for_show(
            self,
            show: Show,
            torrent_client: TorrentProviderInterface):
        torrent_list = torrent_client.fetch_torrents(show)
        index = self._find_show_in_torrent_list(show, torrent_list)
        if index < 0:
            return
        print(
            "Found new episode: %s, Season: %s, Episode: %s" % (
                show.title,
                show.season,
                show.episode))
        torrent = torrent_list[index]
        self._add_torrent(torrent, show)

    def _should_download_torrent(
            self,
            title: str,
            show: Show,
            check_quality: bool = True) -> bool:
        if check_quality:
            return self._is_entry_scheduled(title, show) and \
                self._has_expected_quality(title) and \
                self._is_entry_current_episode(title, show)
        return self._is_entry_scheduled(title, show) and \
            self._is_entry_current_episode(title, show)

    def _is_entry_scheduled(self, title: str, show: Show) -> bool:
        match = re.search(show.regex, title.lower())
        return match is not None

    def _has_expected_quality(self, title: str) -> bool:
        if self._torrent_quality == "none":
            return True
        regexp = re.sub(
            r"[pP]",
            "[pP]",
            self._torrent_quality)
        match = re.search(regexp, title)
        if match is None:
            return False
        return True

    def _is_entry_current_episode(self, title: str, show: Show) -> bool:
        regexp = r"((S[0-9]{,2}E[0-9]{,2})|([0-9]{1,2}[xX][0-9]{1,2}))"
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
        show.episode += 1
        show.save(self._database)

    def _add_torrent(self, torrent: TorrentLinkInterface, show: Show):
        if self._bittorrent_client.add_torrent(
                torrent,
                folder=show.get_folder()):
            print(
                "%s | Torrent added successfully!"
                % time.strftime("%Y-%m-%d %H:%M:%S"))
            self._updates.append(show)
        return
