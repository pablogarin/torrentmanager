import sqlite3


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

    def __init__(self, data: dict, conn: sqlite3.Connection):
        if data == None:
            raise Exception('Cannot initialize an empty show')
        self.conn = conn
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
        print("set_data", self)
    
    def get_insert_query(self):
        query = "INSERT OR REPLACE\
            INTO tv_show\
            VALUES(\
                COALESCE(\
                    (SELECT id FROM tv_show WHERE title='"+self.title+"'),\
                    (SELECT MAX(id) FROM tv_show) + 1\
                ),\
                '%s',\
                '%s',\
                %d,\
                %d,\
                %d,\
                '%s',\
                '%s',\
                datetime()\
            )" % (
                self.title,
                self.regex,
                self.season,
                self.episode,
                self.status,
                self.imdbID,
                self.thetvdbID
            )
        print(query)
        return query

    def save(self):
        print("Saving %s" % self.title)
        try:
            c = self.conn.cursor()
            c.execute(self.get_insert_query())
            self.conn.commit()
        except Exception as e:
            print(e)

    def __str__(self):
        return "Show {\n\
            title: %s\n\
            season: %s\n\
            episode: %s\n\
            status: %s\n\
            }" % (
                self.title,
                self.season,
                self.episode,
                self.status
            )
    
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