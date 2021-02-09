from torrentmanager.interfaces import BittorrentClientInterface
from torrentmanager.interfaces import TorrentLinkInterface
from torrentmanager.interfaces import TorrentInterface
from torrentmanager.interfaces import TorrentList


class DelugedClient(BittorrentClientInterface):
    _command = "deluge-console"
    _add = "add %s --path=%s"
    _del = "del"
    _info = "info -v"

    def add_torrent(
            self,
            torrent: TorrentLinkInterface,
            folder: str = '') -> bool:
        add_command = "%s %s" % (
            self._command,
            (self._add % (torrent.get_link(), folder))
        )
        try:
            add_result = subprocess.check_output(add_command, shell=True)
        except Exception as e:
            print("Unable to execute add command: %s" % e)
            return False
        return True

    def _parse_add_result(self, result: str):
        print(result.split("\n"))

    def find(self, query: str, status=None) -> TorrentList:
        find_command = "%s %s %s %s" % (
            self._command,
            self._info,
            ("-s%s" % status if status is not None else ''),
            query
        )
        try:
            find_result = subprocess.check_output(find_command, shell=True)
            print(find_result)
        except Exception as e:
            print("Unable to list torrents: %s" % e)
        return None

    def list_torrents(self) -> TorrentList:
        pass

    def delete_torrent(self, torrent: TorrentInterface):
        pass
