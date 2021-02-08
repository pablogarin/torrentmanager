#!/usr/bin/python3
import sys
import os
from pprint import pprint
from modules.config.config import Config
from modules.show_finder import ShowFinder
from modules.torrent_finder import TorrentFinder
from modules.show import ShowManager
from modules.tvdbclient import TVDBClient
from modules.rarbgclient import RarbgClient
from modules.eztvclient import EZTVClient


def main(args):
    # Config
    config = Config()
    torrent_folder = config.get_config("download_folder")
    torrent_quality = config.get_config("quality")
    # Database
    show_manager = ShowManager()
    # Show Info Client
    tvdb = TVDBClient(show_manager)
    # Workers
    show_finder = ShowFinder(
        show_manager,
        tvdb,
        torrent_folder)
    torrent_finder = TorrentFinder(
        show_manager,
        torrent_folder,
        torrent_quality)
    # Check Args
    if len(args) > 1:
        option = args[1]
    if len(args) == 2:
        if option == "--update" or option == "-u":
            for show in show_manager.find():
                seriesid = show.thetvdbID
                print("Updating show '%s'(%s)" % (show.title, show.thetvdbID))
                if seriesid is not None:
                    show_finder.schedule_show(seriesid, update=True)
        elif option == "--by-name" or option == "-n":
            torrent_finder.check_scheduled_shows(EZTVClient())
        elif option == "--search" or option == "-s":
            try:
                show_finder.interactive_search()
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
            shows = show_finder.search(value)
            if len(shows) == 0:
                print("No Matches for Show")
        elif option == "--add" or option == "-a":
            if show_finder.schedule_show(value):
                print("Show Added")
            else:
                print("Show not found!")
        else:
            print("Unknown Option.")
    else:
        torrent_finder.read_rss(RarbgClient())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt as e:
        print("Cancelled by user")
