import os
import sys
import re
from modules.interfaces.persistence_interface import PersistanceInterface
from modules.show import Show
from modules.tvdbclient import TVDBClient


class ShowFinder(object):
    prompt = False

    def __init__(
            self,
            database: PersistanceInterface,
            torrent_folder: str = ''):
        self.database = database
        self.__torrent_folder = torrent_folder
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
            self.schedule_show(show_to_insert['id'])
        return search_result

    def schedule_show(self, seriesid, update: bool = False):
        show = self.tvdb.find(seriesid)
        if show is None:
            return False
        show.episode += 1
        should_save_show = True
        if self.prompt:
            print("Next episode: %s" % show)
            save_show = input("Do you wish to schedule the show?[Y/n]:")
            should_save_show = r'y' == save_show.lower()
        if should_save_show:
            show.save()
            if update:
                return True
            try:
                show_folder = show.title.replace(' ', '.')
                path = self.__torrent_folder+"/"+show_folder
                escaped_path = re.sub(r'[^ /a-zA-Z0-9\.]', '', path)
                print("Path: %s" % escaped_path)
                if not os.path.exists(escaped_path):
                    os.makedirs(escaped_path)
            except Exception as e:
                print("The system was unable to create the folder: %s" % e)
            return True
