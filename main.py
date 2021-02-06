#!/usr/bin/python3
import sys
import os
from modules.config.config import Config
from modules.tvdbclient.show_finder import ShowFinder
from modules.download_torrents import torrentFinder
from modules.show import ShowManager
from pprint import pprint


def main(args):
    show_manager = ShowManager()
    config = Config()
    torrent_folder = config.get_config("download_folder")
    torrent_quality = config.get_config("quality")
    if len(args) > 1:
        option = args[1]
    if len(args) == 2:
        if option == "--update" or option == "-u":
            series = torrentFinder().series
            for serie in series:
                id = serie['thetvdbID']
                print("Updating show '%s'(%s)" % (serie['title'], id))
                if id is not None:
                    obj = ShowFinder(show_manager, torrent_folder)
                    obj.insertName = serie['title']
                    obj.imdb = serie['imdbID']
                    obj.registerSeries(id)
        elif option == "--by-name" or option == "-n":
            torrentFinder().checkByName()
        elif option == "--search" or option == "-s":
            try:
                gs = ShowFinder(show_manager, torrent_folder)
                gs.promptName()
            except Exception as e:
                print(e)
                print("Cancelled by user")
        elif option == "--list-shows" or option == "-l":
            for show in show_manager.find():
                print(show)
        elif option == "--config" or option == "-c":
            config.initial_configuration()
        else:
            print("Unknown Option.")
    elif len(args) >= 3:
        value = ""
        for i in range(2, len(args)):
            value = value+args[i]+" "
        value = value.rstrip()
        if option == "--search" or option == "-s":
            gs = ShowFinder(show_manager, torrent_folder)
            shows = gs.search(value)
            if len(shows) == 0:
                print("No Matches for Show")
        elif option == "--add" or option == "-a":
            gs = ShowFinder(show_manager, torrent_folder)
            if gs.registerSeries(value):
                print("Show Added")
            else:
                print("Show not found!")
        else:
            print("Unknown Option.")
    else:
        torrentFinder().readRSS()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt as e:
        print("Cancelled by user")
