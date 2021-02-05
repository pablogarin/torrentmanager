import xmltodict
from urllib.request import urlopen
from modules.interfaces import ClientInterface
from modules.show import Show


class TVDBClient(ClientInterface):
    base_url = 'http://thetvdb.com/api/'
    api_key = 'E16D53FBF4407C2B'
    search_path = 'GetSeries.php?seriesname='
    find_path = '%s/series/:id/all/en.xml'

    def search(self, query: str) -> list:
        url = self.base_url+self.search_path+query
        request = urlopen(url)
        response = xmltodict.parse(request.read())
        request.close()
        return self.show_list_from_response(response)

    def find(self, id: any) -> Show:
        pass
    
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
