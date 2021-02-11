import re
import subprocess

from .deluge_torrent import DelugeTorrent
from torrentmanager.interfaces import BittorrentClientInterface
from torrentmanager.interfaces import TorrentLinkInterface
from torrentmanager.interfaces import TorrentInterface
from torrentmanager.interfaces import TorrentList


class DelugedClient(BittorrentClientInterface):
    _client_name = "Deluge"
    _command = "deluge-console"
    _add = "add '%s' --path=%s"
    _del = "del %s"
    _info = "info -v"
    _download_folder = None

    def __init__(self, folder):
        super().__init__(folder)

    @property
    def download_folder(self) -> str:
        return self._download_folder

    @download_folder.setter
    def download_folder(self, folder: str):
        self._download_folder = folder

    def add_torrent(
            self,
            torrent: TorrentLinkInterface,
            folder: str = '') -> bool:
        torrent_folder = self._download_folder+"/"+folder
        add_command = "%s %s" % (
            self._command,
            (self._add % (torrent.get_link(), torrent_folder))
        )
        try:
            print("Attempting to add %s" % torrent.title)
            add_result = subprocess.check_output(add_command, shell=True)\
                .decode('utf-8')
            parsed_result = self._parse_add_result(add_result)
            if len(parsed_result) > 1 and parsed_result[1] == 'Torrent added!':
                return True
            else:
                print(parsed_result)
        except Exception as e:
            print("Unable to execute add command: %s" % e)
            return False
        return False

    def _parse_add_result(self, result: str):
        return result.split("\n")

    def find(self, query: str = '', status=None) -> TorrentList:
        find_command = "%s %s %s %s" % (
            self._command,
            self._info,
            ("-s%s" % status if status is not None else ''),
            query
        )
        try:
            find_result = subprocess.check_output(find_command, shell=True)\
                .decode('utf-8')
            if len(find_result) == 0:
                print("No matches for the query '%s'" % query)
                return None
            return self._create_torrents_from_output(find_result)
        except Exception as e:
            print("Unable to list torrents: %s" % e)
        return None

    def list_torrents(self) -> TorrentList:
        return self.find(query='')

    def delete_torrent_batch(self, torrent_list: TorrentList):
        for torrent in torrent_list:
            self.delete_torrent(torrent)

    def delete_torrent(self, torrent: TorrentInterface):
        delete_command = "%s %s" % (
            self._command,
            self._del % (
                torrent.id_))
        try:
            delete_result = subprocess.check_output(
                delete_command,
                shell=True).decode('utf-8')
            return True
        except Exception as e:
            print("Unable to delete torrent: %s" % e)
        return False

    def _create_torrents_from_output(self, find_result: str):
        return list(
            map(self._create_torrent_object, find_result.split("\n \n"))
        )

    def _create_torrent_object(self, output: str) -> DelugeTorrent:
        torrent_dict = self._parse_output(output)
        torrent = DelugeTorrent()
        torrent.set_data_from_dict(torrent_dict)
        return torrent

    def _parse_output(self, output: str) -> dict:
        try:
            name = self._extract_value_from_output(
                "Name",
                output,
                regex=r"%s: ([^\n]+)")
            id_ = self._extract_value_from_output("ID", output)
            status = self._extract_value_from_output("State", output)
            progress = self._extract_value_from_output("Progress", output)
            size = self._extract_value_from_output(
                "Size",
                output,
                regex=r"%s: ([^\n]+)")
            sizes_array = size.split(" Ratio")[0].split("/")
            size_dict = {}
            if len(sizes_array) > 0:
                size_dict['current_size'] = sizes_array[0]
                size_dict['actual_size'] = sizes_array[1]
            age = self._extract_value_from_output(
                "Seed time",
                output,
                regex=r"%s: (.*)")
            ages_array = age.split(" Active: ")
            age_dict = {}
            if len(ages_array) > 0:
                age_dict['seeding'] = ages_array[0]
                age_dict['added'] = ages_array[1]

            return {
                'id': id_,
                'name': name,
                'status': status,
                'progress': progress,
                'size': size_dict,
                'age': age_dict
            }
        except Exception as e:
            print("Couldn't parse torrent: %s" % e)

    def _extract_value_from_output(
            self,
            field: str,
            output: str,
            regex: str = r"%s: ([^\s]+)"):
        match = re.search((regex % field), output)
        if match is None:
            raise Exception('Not a valid torrent')
        return match.group(1)
