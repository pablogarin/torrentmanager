import argparse
import datetime
import os
import re
import sys
import time
from pprint import pprint

from torrentmanager.config import Config
from torrentmanager.interfaces import BittorrentClientInterface
from torrentmanager.eztvclient import EZTVClient
from torrentmanager.rarbgclient import RarbgClient
from torrentmanager.show import ShowManager
from torrentmanager.show_finder import ShowFinder
from torrentmanager.torrent_finder import TorrentFinder
from torrentmanager.tvdbclient import TVDBClient
from torrentmanager.delugedclient import DelugedClient


def _get_arguments() -> dict:
    parser = argparse.ArgumentParser(
        argument_default=argparse.SUPPRESS,
        description="Torrent Manager and Scheduler")
    parser.add_argument(
        "-s",
        "--search",
        nargs="*",
        metavar="SHOW_NAME",
        help="Search show to schedule.")
    parser.add_argument(
        "-a",
        "--add",
        nargs=1,
        metavar="SHOW_ID",
        help="Add show by id.")
    parser.add_argument(
        "-n",
        "--by-name",
        action="store_true",
        help="Check all scheduled shows for releases.")
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all scheduled shows.")
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="update the current show episode")
    parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        help="update the current show episode")
    parser.add_argument(
        "--display-torrent-client",
        nargs="*",
        metavar="TORRENT NAME",
        help="Display the bittorrent client info")
    parser.add_argument(
        "--delete-torrent",
        nargs="*",
        metavar="TORRENT NAME OR ID",
        help="Display the bittorrent client info")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Start in watch mode")
    parsed_args = parser.parse_args()
    return vars(parsed_args)


def _schedule_watch(*callbacks, minutes=1):
    print("Initializing in watch mode")
    while True:
        for callback in callbacks:
            if callable(callback):
                callback()
            else:
                raise Exception(
                    "Invalid argument passed to _schedule_watch")
        curr_date = datetime.datetime.today()
        next_tick = curr_date + datetime.timedelta(minutes=minutes)
        print("Sleeping for %d minutes" % minutes)
        time.sleep((next_tick-curr_date).total_seconds())


def _get_old_torrents(bittorrent_client: BittorrentClientInterface, max_age=1):
    torrents_to_delete = []
    regex = r"([0-9]+) days ([0-9]+):([0-9]+):([0-9]+)"
    for torrent in bittorrent_client.list_torrents():
        match = re.search(regex, torrent.age["added"])
        if match is None:
            break
        days = match.group(1)
        hours = match.group(2)
        minutes = match.group(3)
        seconds = match.group(4)
        if not days.isnumeric():
            break
        if int(days) >= max_age:
            torrents_to_delete.append(torrent)
    return torrents_to_delete


def main(args=None):
    try:
        if args is None:
            args = _get_arguments()
        if len(args) > 1:
            raise Exception("too many arguments")
        # Config
        config = Config()
        torrent_folder = config.get_config("download_folder")
        torrent_quality = config.get_config("quality")
        enforce_quality = config.get_config("enforce_quality")
        max_torrent_age = config.get_config("max_torrent_age")
        if not max_torrent_age or not max_torrent_age.isnumeric():
            max_torrent_age = "1"
        max_torrent_age = int(max_torrent_age)
        # Database
        show_manager = ShowManager()
        # Show Info Client
        tvdb = TVDBClient(show_manager)
        # BitTorrent Client
        bittorrent_client = DelugedClient(torrent_folder)
        # Workers
        show_finder = ShowFinder(
            show_manager,
            tvdb,
            torrent_folder)
        torrent_finder = TorrentFinder(
            show_manager,
            bittorrent_client,
            torrent_quality=torrent_quality,
            enforce_quality=enforce_quality)
        # Check Args
        if len(args) == 0:
            torrent_finder.read_rss(RarbgClient())
        elif "update" in args and args["update"]:
            for show in show_manager.find():
                seriesid = show.thetvdbID
                print("Updating show '%s'(%s)" % (show.title, show.thetvdbID))
                if seriesid is not None:
                    show_finder.schedule_show(seriesid, update=True)
        elif "by_name" in args and args["by_name"]:
            torrent_finder.check_scheduled_shows(EZTVClient())
        elif "list" in args and args["list"]:
            show_list = show_manager.find()
            if show_list is None:
                return 0
            for show in show_list:
                print(show)
        elif "config" in args and args["config"]:
            config.initial_configuration()
        elif "search" in args:
            if len(args["search"]) > 0:
                query = " ".join(args["search"])
                shows = show_finder.search(query)
                if len(shows) == 0:
                    print("No Matches for Show")
            else:
                show_finder.interactive_search()
        elif "add" in args:
            for show_id in args["add"]:
                print(show_id)
                if show_finder.schedule_show(show_id):
                    print("Show Added")
                else:
                    print("Show not found!")
        elif "display_torrent_client" in args:
            query = ""
            if args["display_torrent_client"] is not None:
                query = " ".join(args["display_torrent_client"])
            torrent_list = bittorrent_client.find(query)
            if torrent_list is None:
                return
            for torrent in torrent_list:
                print(torrent)
        elif "delete_torrent" in args:
            if args["delete_torrent"] is None:
                print("You must specify a torrent")
                return 1
            query = " ".join(args["delete_torrent"])
            torrent_list = bittorrent_client.find(query)
            if torrent_list is None:
                return
            torrent = None
            if len(torrent_list) > 1:
                for index, torr in enumerate(torrent_list):
                    print("%d) %s (%s)" % (
                        index+1,
                        torr.name,
                        torr.id_))
                selected = input("Please specify a torrent from the list: ")
                if not selected.isnumeric():
                    raise Exception("Invalid option")
                index = int(selected)-1
                torrent = torrent_list[index]
                print("\n")
            else:
                torrent = torrent_list[0]
            print(
                "Are you sure? Deleting '%s' cannot be undone." % torrent.name)
            delete = input("Confirm deletion? [y/n] (default 'n'): ")
            should_delete = delete.lower() == "y"
            if should_delete:
                has_deleted = bittorrent_client.delete_torrent(torrent)
                if has_deleted:
                    print("Torrent deleted")
                    return 0
                print("Coulnd't delete the torrent for unknown reasons.")
        elif "watch" in args:
            _schedule_watch(
                lambda: torrent_finder.read_rss(RarbgClient()),
                lambda: bittorrent_client.delete_torrent_batch(
                    _get_old_torrents(
                        bittorrent_client, max_age=max_torrent_age)),
                minutes=5)
        else:
            print("¯\\_(ツ)_/¯")
        return 0
    except KeyboardInterrupt:
        print("Exit: Cancelled by User")
        return 1
    except Exception as e:
        print("Program halted: %s" % e)
        return 2
