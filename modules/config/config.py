import os
import re
from configparser import ConfigParser


class Config(object):
    __config_file = 'config.ini'
    __config = None

    def __init__(self):
        self.__config = ConfigParser()
        if os.path.isfile(self.__config_file):
            self.__config.read(self.__config_file)
        else:
            self.initial_configuration()

    def get_config(self, key: str, section: str = "generals") -> str:
        return self.__config.get(section, key)

    def initial_configuration(self):
        folder = self.define_folder()
        quality = self.define_quality()
        try:
            self.__config.add_section("generals")
        except Exception as e:
            print("Section already created")
        self.__config.set("generals", "download_folder", folder)
        self.__config.set("generals", "quality", quality)
        cfg_file_handle = open(self.__config_file, 'w')
        self.__config.write(cfg_file_handle)
        cfg_file_handle.close()

    def define_folder(self):
        try:
            folder = input("Enter a folder to download your shows: ")
            if not folder:
                return self.define_folder()
            return folder
        except KeyboardInterrupt as e:
            print("Action cancelled by user")
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
