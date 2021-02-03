from modules.persistence.persistence_interface import PersistanceInterface


class Show(object):
    __id = None
    __title = None
    __regex = None
    __season = None
    __episode = None
    __status = 1
    __imdbID = None
    __thetvdbID = None
    __lastDownload = None
    __database = None

    def __init__(self, data: dict, database: PersistanceInterface):
        if data == None:
            raise Exception('Cannot initialize an empty show')
        self.database = database
        self.set_data(data)
    
    def set_data(self, data: dict):
        #self.id = data['id']
        self.title = data['title']
        self.regex = data['regex']
        self.season = data['season']
        self.episode = data['episode']
        #self.status = data['status'] if 'status' in data else 1
        self.imdbID = data['imdbID']
        self.thetvdbID = data['thetvdbID']
        #self.lastDownload = data['lastDownload']
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'regex': self.regex,
            'season': self.season,
            'episode': self.episode,
            'status': self.status,
            'imdbID': self.imdbID,
            'thetvdbID': self.thetvdbID
        }

    def save(self):
        print("Saving %s" % self)
        self.database.write(self)

    def __repr__(self):
        return "Show %s" % self.to_dict

    def __str__(self):
        return "%s (Season %s, Episode %s)" % (self.title, self.season, self.episode)
    
    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    @property
    def regex(self):
        return self.__regex

    @regex.setter
    def regex(self, regex):
        self.__regex = regex

    @property
    def season(self):
        return self.__season

    @season.setter
    def season(self, season):
        self.__season = season

    @property
    def episode(self):
        return self.__episode

    @episode.setter
    def episode(self, episode):
        self.__episode = episode

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        self.__status = status

    @property
    def imdbID(self):
        return self.__imdbID

    @imdbID.setter
    def imdbID(self, imdbID):
        self.__imdbID = imdbID

    @property
    def thetvdbID(self):
        return self.__thetvdbID

    @thetvdbID.setter
    def thetvdbID(self, thetvdbID):
        self.__thetvdbID = thetvdbID

    @property
    def lastDownload(self):
        return self.__lastDownload

    @lastDownload.setter
    def lastDownload(self, lastDownload):
        self.__lastDownload = lastDownload

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, database: PersistanceInterface):
        self.__database = database
