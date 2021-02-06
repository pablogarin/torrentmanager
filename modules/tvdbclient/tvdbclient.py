import xmltodict
import re
import time
from urllib.request import urlopen
from modules.interfaces import PersistanceInterface
from modules.interfaces import ClientInterface
from modules.show import Show
from modules.exceptions import ShowFindException
from modules.exceptions import ShowSearchException


class TVDBClient(ClientInterface):
    __base_url = 'http://thetvdb.com/api/'
    __api_key = 'E16D53FBF4407C2B'
    __search_path = 'GetSeries.php?seriesname='
    __find_path = "%s/series/%s/all/en.xml"
    __database = None

    def __init__(self, database: PersistanceInterface):
        self.__database = database
        str_date = time.strftime("%Y-%m-%d")
        self.__current_date = time.strptime(str_date, "%Y-%m-%d")

    def search(self, query: str) -> list:
        url = self.__base_url+self.__search_path+query
        try:
            request = urlopen(url)
            response = xmltodict.parse(request.read())
            request.close()
        except Exception as e:
            raise ShowSearchException(
                "Unable to connect to api => %s" % e,
                query)
        return self.show_list_from_response(response)

    def find(self, seriesid: any, prompt: bool = False) -> Show:
        url = self.__base_url+self.__find_path % (self.__api_key, seriesid)
        try:
            request = urlopen(url)
            response = xmltodict.parse(request.read())
            request.close()
        except Exception as e:
            raise ShowFindException(
                "Unable to connect to api => %s" % e,
                seriesid)
        data = response['Data']
        if data['Series']['id'] == "0":
            return None
        episodes = data['Episode'] if 'Episode' in data else None
        season, episode = self.check_current_episode(episodes)
        series = data['Series']
        return self.create_show_from_response(
            seriesid,
            series,
            season,
            episode)

    def show_list_from_response(self, response):
        if response['Data'] is None:
            return list([])
        series = response['Data']['Series']
        shows_found = series if type(series) == list else [series]
        show_list = map(self.map_to_show_dict, shows_found)
        return list(show_list)

    def map_to_show_dict(self, data: dict):
        show_id = data['seriesid']
        title = data['SeriesName']
        imdb = data['IMDB_ID'] if 'IMDB_ID' in data else 'Null'
        return {
            'id': show_id,
            'title': title,
            'imdb': imdb
        }

    def create_show_from_response(
            self,
            seriesid: str,
            data: dict,
            season,
            episode) -> Show:
        series_name = re.sub(
            r'\([0-9]{,4}\)',
            "",
            data['SeriesName'])
        title = series_name\
            .strip()\
            .replace("'", "\\'")
        imdb = data['IMDB_ID'] if 'IMDB_ID' in data else 'Null'
        show_dict = {
            'title': title,
            'regex': self.build_regex(title),
            'season': season,
            'episode': episode,
            'imdbID': imdb,
            'thetvdbID': seriesid
        }
        return Show(show_dict, self.__database)

    def build_regex(self, title):
        # FIXME: too many mutations on the same str
        regex = title.title().strip()
        regex = re.sub("[:']", "", regex)
        regex = re.sub(r'[ \.]', "[\\. ]{0,1}", regex)
        regex = re.sub(
            "[A-Z]",
            lambda pat: "["+pat.group(0)+pat.group(0).lower()+"]",
            regex)
        return "(%s)" % regex

    def check_current_episode(self, episodes: list) -> list:
        print("Searching current episode...")
        last_aired = None
        if episodes is not None:
            episode_list = episodes if type(episodes) == list else [episodes]
            for episode in map(self.format_episode, episode_list):
                if episode['aired']:
                    if last_aired is None:
                        last_aired = episode
                    elif last_aired['date'] < episode['date']:
                        last_aired = episode
                print("S%02dE%02d (%s): %s" % (
                    episode['season'],
                    episode['episode'],
                    time.strftime("%Y-%m-%d", episode['date']),
                    episode['title']))
        if last_aired is None:
            print("No episode has aired")
            return 1, 0
        return last_aired['season'], last_aired['episode']

    def format_episode(self, episode_dict) -> dict:
        title = episode_dict['EpisodeName']
        season = int(episode_dict['SeasonNumber'])
        episode = int(episode_dict['EpisodeNumber'])
        date = self.get_air_date(episode_dict)
        aired = self.has_episode_aired(date)
        return {
            'title': title,
            'season': season,
            'episode': episode,
            'date': date,
            'aired': aired
        }

    def has_episode_aired(self, air_date) -> bool:
        if self.__current_date < air_date:
            return False
        return True

    def get_air_date(self, episode) -> any:
        if 'FirstAired' not in episode:
            return None
        air_date = episode['FirstAired']
        try:
            date = time.strptime(air_date, "%Y-%m-%d")
            return date
        except Exception as e:
            print("Couldn't parse date: %s" % e)
        return None
