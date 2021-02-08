#!/usr/bin/env python
import re
import subprocess
import sys
import threading
from queue import PriorityQueue

from torrentmanager.interfaces import PersistanceInterface
from torrentmanager.interfaces import TorrentClientInterface
from torrentmanager.interfaces import TorrentInterface
from torrentmanager.interfaces import TorrentList
from torrentmanager.show import Show


class TorrentFinder:
    _database = None
    _torrent_folder = ''
    _torrent_quality = ''
    _updates = []
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
        self._set_show_list()

    def _set_show_list(self):
        for show in self._database.find():
            self._shows.append(show)

    def read_rss(self, torrent_client: TorrentClientInterface):
        torrent_list = torrent_client.fetch_torrents()
        for show in self._shows:
            print("Checking show %s" % show.title)
            index = self._find_show_in_torrent_list(show, torrent_list)
            if index >= 0:
                torrent = torrent_list[index]
                self._add_torrent(torrent, show)

    def _find_show_in_torrent_list(
            self,
            show: Show,
            torrent_list: TorrentList) -> int:
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
            return index
        return -1

    def check_scheduled_shows(self, torrent_client: TorrentClientInterface):
        print("Checking all scheduled shows.")
        print("This might take a while (1-5 minutes)")
        tmp = []
        for show in self._shows:
            tmp.append((show, torrent_client))
        self.run_parallel_in_threads(
            self.lookupTorrents,
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

    def lookupTorrents(
            self,
            show: Show,
            torrent_client: TorrentClientInterface):
        torrent_list = torrent_client.fetch_torrents(show)
        index = self._find_show_in_torrent_list(show, torrent_list)
        if index < 0:
            return
        torrent = torrent_list[index]
        self._add_torrent(torrent, show)

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
        print("Updating Show episode")
        show.episode += 1
        show.save()

    def _add_torrent(self, torrent: TorrentInterface, show: Show):
        folder = show.get_folder()
        torrent_path = torrent.get_link()
        addCommand = "deluge-console add '%s' --path=%s" % (
            torrent_path,
            self._torrent_folder+"/"+folder
        )
        print(addCommand)
        try:
            result = subprocess.check_output(addCommand, shell=True)
            print(result)
        except Exception as e:
            print("Error adding torrent: %s" % e)
        self._updates.append(show)


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
            finder.check_scheduled_shows()
        else:
            print("Unknown Option.")
    else:
        finder = torrentFinder()
        finder.read_rss()
    return 0


if __name__ == '__main__':
    sys.exit(main())
