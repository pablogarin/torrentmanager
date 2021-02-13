import os
import re
from pathlib import Path
from configparser import ConfigParser


class Config(object):
    _config_folder = "%s/.torrentmanager" % str(Path.home())
    _config_file = "%s/config.ini" % _config_folder
    _config = None

    def __init__(self):
        self._config = ConfigParser()
        if not os.path.isdir(self._config_folder):
            os.makedirs(self._config_folder)
        if os.path.isfile(self._config_file):
            self._config.read(self._config_file)
        else:
            self.initial_configuration()

    def set_config(
            self, key: str, value: str, section: str = "generals") -> str:
        self._config.set(section, key, value)

    def get_config(self, key: str, section: str = "generals") -> str:
        if section not in self._config.sections():
            return None
        if key not in dict(self._config.items(section)):
            return None
        return self._config.get(section, key)

    def _write_config(self):
        cfg_file_handle = open(self._config_file, "w")
        self._config.write(cfg_file_handle)
        cfg_file_handle.close()

    def initial_configuration(self):
        folder = self.define_folder()
        quality = self.define_quality()
        enforce_quality = self.define_enforce_quality()
        if "generals" not in self._config.sections():
            self._config.add_section("generals")
        self.set_config("download_folder", folder)
        self.set_config("quality", quality)
        self.set_config("enforce_quality", enforce_quality)
        if self.get_config("max_torrent_age") is None:
            self.set_config("max_torrent_age", "1")
        self._write_config()

    def define_folder(self) -> str:
        try:
            folder = input("Enter a folder to download your shows: ")
            if not folder:
                return self.define_folder()
            if not os.path.exists(folder):
                raise FileNotFoundError("Folder %s doesn't exists!" % folder)
            return folder
        except FileNotFoundError as e:
            print(e)
            return self.define_folder()
        return None

    def define_quality(self) -> str:
        quality = input("Enter the quality (none, 720p, 1080p or 2160p): ")
        if not quality:
            return self.define_quality()
        match = re.search(r"(none|720[pP]|1080[pP]|2160[pP])", quality)
        if match is None:
            print("Invalid input!")
            return self.define_quality()
        return quality

    def define_enforce_quality(self):
        answer_map = {
            "y": "yes",
            "n": "no"
        }
        enforce_quality = input(
            "Check quality before download? [y/n] (Default: 'n')")
        if not enforce_quality:
            enforce_quality = "n"
        if enforce_quality.lower() not in ("y", "n"):
            print("Answer must be 'y' for yes or 'n' for no")
            return self.define_enforce_quality()
        return answer_map[enforce_quality.lower()]
