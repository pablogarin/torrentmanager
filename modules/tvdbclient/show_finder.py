#!/usr/bin/env python
import os
import sys
import re
import sqlite3
import xmltodict
import time
from xml import parsers
from urllib.request import urlopen
from configparser import ConfigParser
from pprint import pprint
from modules.interfaces.persistence_interface import PersistanceInterface
from modules.show import Show
from modules.tvdbclient import TVDBClient


class getShow(object):
    prompt = False

    def __init__(
            self,
            database: PersistanceInterface,
            torrent_folder: str = ''):
        self.database = database
        self.defineDownloadFolder()
        self.tvdb = TVDBClient(self.database)

    def promptName(self):
        query = input("Please input the show to find: ")
        self.query = query
        self.prompt = True
        self.search(query)

    def search(self, query: str) -> list:
        seriesName = query.replace('.', '')
        seriesName = seriesName.replace(' ', '%20')
        search_result = self.tvdb.search(seriesName)
        show_to_insert = None
        if len(search_result) == 0:
            if self.prompt:
                print("Show not found.")
            return []
        for i, show in enumerate(search_result):
            print("%d) %s = %s" % (i+1, show['title'], show['id']))
        if self.prompt:
            if len(search_result) == 1:
                i = 0
            else:
                i = int(input("Please select a show from the list: "))-1
            show_to_insert = search_result[i]
        if show_to_insert is not None:
            self.registerSeries(show_to_insert['id'])
        return search_result

    def registerSeries(self, id):
        show = self.tvdb.find(id)
        show.episode += 1
        if self.prompt:
            print("Next episode: %s" % show)
            save_show = input("Do you wish to schedule the show?[Y/n]:")
            if r'y' == save_show.lower():
                show.save()
                path = self.downloadFolder+"/"+title.replace(' ', '.')
                path = re.sub(r'[^ a-zA-Z0-9\.]', '', path)
                if not os.path.exists(path):
                    os.makedirs(path)


if __name__ == "__main__":
    sys.exit(main())
