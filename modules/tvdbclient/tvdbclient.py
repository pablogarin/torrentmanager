import xmltodict
import re
from urllib.request import urlopen
from modules.interfaces import PersistanceInterface
from modules.interfaces import ClientInterface
from modules.show import Show


class TVDBClient(ClientInterface):
    __base_url = 'http://thetvdb.com/api/'
    __api_key = 'E16D53FBF4407C2B'
    __search_path = 'GetSeries.php?seriesname='
    __find_path = "%s/series/%s/all/en.xml"
    __database = None

    def __init__(self, database: PersistanceInterface):
        self.__database = database

    def search(self, query: str) -> list:
        url = self.__base_url+self.__search_path+query
        try:
            request = urlopen(url)
            response = xmltodict.parse(request.read())
            request.close()
        except Exception as e:
            raise Exception("TVDBClient.SearchException: Unable to connect to api => %s" % e)
        return self.show_list_from_response(response)

    def find(self, seriesid: any, prompt: bool = False) -> Show:
        url = self.__base_url+self.__find_path % (self.__api_key, seriesid)
        try:
            request = urlopen(url)
            response = xmltodict.parse(request.read())
            request.close()
        except Exception as e:
            raise Exception("TVDBClient.FindException: Unable to connect to api => %s" % e)
        season, episode = self.check_current_episode(response['Data']['Episode'])
        series = response['Data']['Series']
        return self.create_show_from_response(seriesid, series, season, episode)
    
    def show_list_from_response(self, response):
        series = response['Data']['Series']
        shows_found = series if type(series)==list else [series]
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

    def create_show_from_response(self, seriesid: str, data: dict, season, episode) -> Show:
        title = data['SeriesName']
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
        regex = title.title().strip()
        regex = re.sub("[:']","", regex)
        regex = re.sub('[ \.]',"[\\. ]{0,1}",regex)
        regex = re.sub("[A-Z]",lambda pat: "["+pat.group(0)+pat.group(0).lower()+"]",regex)
        return "(%s)" % regex

    def check_current_episode(self, episodes: list):
        return 1,1