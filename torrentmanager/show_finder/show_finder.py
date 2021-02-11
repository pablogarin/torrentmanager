import os
import sys
import re

from torrentmanager.interfaces import PersistanceInterface
from torrentmanager.interfaces import ClientInterface
from torrentmanager.show import Show


class ShowFinder(object):
    _interactive = False
    _client = None

    def __init__(
            self,
            database: PersistanceInterface,
            client: ClientInterface,
            torrent_folder: str = ''):
        self._database = database
        self._torrent_folder = torrent_folder
        self._client = client

    def interactive_search(self):
        query = input("Please input the show to find: ")
        self._interactive = True
        self._client.verbose = True
        self.search(query)

    def search(self, query: str) -> list:
        seriesName = query.replace('.', '')
        seriesName = seriesName.replace(' ', '%20')
        search_result = self._client.search(seriesName)
        show_to_insert = None
        if len(search_result) == 0:
            if self._interactive:
                print("Show not found.")
            return []
        for i, show in enumerate(search_result):
            print("%d) %s = %s" % (i+1, show['title'], show['id']))
        if self._interactive:
            if len(search_result) == 1:
                i = 0
            else:
                selected = input("Please select a show from the list: ")
                if not selected.isnumeric():
                    raise Exception(
                        "Option must be a number. Received: '%s'"
                        % selected)
                i = int(selected)-1
            show_to_insert = search_result[i]
        if show_to_insert is not None:
            self.schedule_show(show_to_insert['id'])
        return search_result

    def schedule_show(
            self,
            seriesid,
            update: bool = False):
        show = self._client.find(seriesid)
        if show is None:
            return False
        should_save_show = True
        if self._interactive:
            print("Next episode: %s" % show)
            save_show = input("Do you wish to schedule the show?[y/n]: ")
            should_save_show = r'y' == save_show.lower()
        if should_save_show:
            show.save(self._database)
            if update:
                return True
            try:
                show_folder = show.get_folder()
                path = self._torrent_folder+"/"+show_folder
                escaped_path = re.sub(r'[^ /a-zA-Z0-9\.]', '', path)
                print("Path: %s" % escaped_path)
                if not os.path.exists(escaped_path):
                    os.makedirs(escaped_path)
            except Exception as e:
                print("The system was unable to create the folder: %s" % e)
            return True
