import os
import re
from configparser import ConfigParser


class Config(object):
    _config_file = 'config.ini'
    _config = None

    def __init__(self):
        self._config = ConfigParser()
        if os.path.isfile(self._config_file):
            self._config.read(self._config_file)
        else:
            self.initial_configuration()

    def get_config(self, key: str, section: str = "generals") -> str:
        return self._config.get(section, key)

    def initial_configuration(self):
        folder = self.define_folder()
        quality = self.define_quality()
        try:
            self._config.add_section("generals")
        except Exception as e:
            print("Section already created")
        self._config.set("generals", "download_folder", folder)
        self._config.set("generals", "quality", quality)
        cfg_file_handle = open(self._config_file, 'w')
        self._config.write(cfg_file_handle)
        cfg_file_handle.close()

    def define_folder(self):
        try:
            folder = input("Enter a folder to download your shows: ")
            if not folder:
                return self.define_folder()
            if not os.path.exists(folder):
                raise FileNotFoundError("Folder %s doesn't exists!" % folder)
            return folder
        except KeyboardInterrupt as e:
            print("Action cancelled by user")
        except FileNotFoundError as e:
            print(e)
            return self.define_folder()
        return None

    def define_quality(self):
        try:
            quality = input("Enter the quality (none, 720p, 1080p or 2160p): ")
            if not quality:
                return self.define_quality()
            match = re.search(r'(none|720[pP]|1080[pP]|2160[pP])', quality)
            if match is None:
                print("Invalid input!")
                return self.define_quality()
            return quality
        except KeyboardInterrupt as e:
            print("Action cancelled by user")
        return None
