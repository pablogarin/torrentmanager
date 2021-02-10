import re

from torrentmanager.interfaces import PersistanceInterface


class Show(object):
    _id = None
    _title = None
    _regex = None
    _season = None
    _episode = None
    _status = 1
    _imdbID = None
    _thetvdbID = None
    _lastDownload = None

    def __init__(self, data: dict):
        if data is None:
            raise Exception('Cannot initialize an empty show')
        self.set_data(data)

    def set_data(self, data: dict):
        # self.id = data['id']
        self.title = data['title']
        self.regex = data['regex']
        self.season = data['season']
        self.episode = data['episode']
        # self.status = data['status'] if 'status' in data else 1
        self.imdbID = data['imdbID']
        self.thetvdbID = data['thetvdbID']
        # self.lastDownload = data['lastDownload']

    def __iter__(self) -> dict:
        d = {
            'title': self.title,
            'regex': self.regex,
            'season': self.season,
            'episode': self.episode,
            'status': self.status,
            'imdbID': self.imdbID,
            'thetvdbID': self.thetvdbID
        }
        for key in d.keys():
            yield (key, d[key])

    def get_folder(self):
        sanitized_title = re.sub(r'[^ a-zA-Z0-9\.]', '', self.title)
        return sanitized_title.replace(' ', '.')

    def save(self, database: PersistanceInterface):
        print("Saving %s" % self)
        database.write(self)

    def __repr__(self):
        return "Show %s" % dict(self)

    def __str__(self):
        return "%s (Season %s, Episode %s)" % (
            self.title,
            self.season,
            self.episode)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, regex):
        self._regex = regex

    @property
    def season(self):
        return self._season

    @season.setter
    def season(self, season):
        self._season = season

    @property
    def episode(self):
        return self._episode

    @episode.setter
    def episode(self, episode):
        self._episode = episode

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def imdbID(self):
        return self._imdbID

    @imdbID.setter
    def imdbID(self, imdbID):
        self._imdbID = imdbID

    @property
    def thetvdbID(self):
        return self._thetvdbID

    @thetvdbID.setter
    def thetvdbID(self, thetvdbID):
        self._thetvdbID = thetvdbID

    @property
    def lastDownload(self):
        return self._lastDownload

    @lastDownload.setter
    def lastDownload(self, lastDownload):
        self._lastDownload = lastDownload

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, database: PersistanceInterface):
        self._database = database
