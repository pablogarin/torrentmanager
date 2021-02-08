import os
import sys
import argparse
from pprint import pprint

from torrentmanager.config import Config
from torrentmanager.eztvclient import EZTVClient
from torrentmanager.rarbgclient import RarbgClient
from torrentmanager.show import ShowManager
from torrentmanager.show_finder import ShowFinder
from torrentmanager.torrent_finder import TorrentFinder
from torrentmanager.tvdbclient import TVDBClient


def _get_arguments() -> dict:
    parser = argparse.ArgumentParser(
        argument_default=argparse.SUPPRESS,
        description='Torrent Manager and Scheduler'
    )
    parser.add_argument(
        '-s',
        '--search',
        nargs='*',
        metavar='SHOW_NAME',
        help='Search show to schedule.')
    parser.add_argument(
        '-a',
        '--add',
        nargs=1,
        metavar='SHOW_ID',
        help='Add show by id.')
    parser.add_argument(
        '-n',
        '--by-name',
        action='store_true',
        help='Check all scheduled shows for releases.')
    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='List all scheduled shows.')
    parser.add_argument(
        '-u',
        '--update',
        action='store_true',
        help='update the current show episode')
    parser.add_argument(
        '-c',
        '--config',
        action='store_true',
        help='update the current show episode')
    parsed_args = parser.parse_args()
    return vars(parsed_args)


def main():
    args = _get_arguments()
    if len(args) > 1:
        raise Exception('too many arguments')
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
    if len(args) == 0:
        torrent_finder.read_rss(RarbgClient())
    elif 'update' in args and args['update']:
        for show in show_manager.find():
            seriesid = show.thetvdbID
            print("Updating show '%s'(%s)" % (show.title, show.thetvdbID))
            if seriesid is not None:
                show_finder.schedule_show(seriesid, update=True)
    elif 'by_name' in args and args['by_name']:
        torrent_finder.check_scheduled_shows(EZTVClient())
    elif 'list' in args and args['list']:
        for show in show_manager.find():
            print(show)
    elif 'config' in args and args['config']:
        config.initial_configuration()
    elif 'search' in args:
        if len(args['search']) > 0:
            query = " ".join(args['search'])
            shows = show_finder.search(query)
            if len(shows) == 0:
                print("No Matches for Show")
        else:
            show_finder.interactive_search()
    elif 'add' in args:
        for show_id in args['add']:
            print(show_id)
            if show_finder.schedule_show(show_id):
                print("Show Added")
            else:
                print("Show not found!")
    else:
        print("¯\\_(ツ)_/¯")
    return 0
