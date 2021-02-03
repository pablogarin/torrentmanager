import sqlite3
import sys
from modules.persistence.persistence_interface import PersistanceInterface
from modules.persistence.models.show import Show


class ShowManager(PersistanceInterface):
    __database = 'db/downloadTorrents.db'
    __table = 'tv_show'
    __schema = "CREATE TABLE IF NOT EXISTS tv_show(\
            id integer primary key autoincrement,\
            title varchar(255),\
            regex varchar(255),\
            season int,\
            episode int,\
            status int,\
            imdbID varchar(120),\
            thetvdbID varchar(120),\
            lastDownload datetime\
        );"
    def __init__(self):
        self.conn = sqlite3.connect(self.database)
        try:
            self.conn.row_factory = sqlite3.Row
            c = self.conn.cursor()
            c.execute(self.schema)
        except Exception as e:
            print("Error: unable to create database. Details: "+str(e))
            sys.exit(1)
    
    def __del__(self):
        self.conn.close()
    
    def write(self, data: any):
        try:
            c = self.conn.cursor()
            c.execute(self.build_insert_query(data))
            self.conn.commit()
        except Exception as e:
            print("Error writing into database: %s" % e)

    def read(self, id):
        pass

    def find(self, query=''):
        series = []
        try:
            self.conn.row_factory = sqlite3.Row
            c = self.conn.cursor()
            c.execute("SELECT * FROM "+self.table+" ORDER BY lastDownload")
            while True:
                row = c.fetchone()
                if row==None:
                    break
                series.append(Show(row, self))
        except Exception as e:
            print("Error reading database: %s" % e)
        return series
    
    def build_insert_query(self, show: Show) -> str:
        query = "INSERT OR REPLACE\
            INTO tv_show\
            VALUES(\
                COALESCE(\
                    (SELECT id FROM tv_show WHERE title='%s'),\
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
                show.title,
                show.title,
                show.regex,
                show.season,
                show.episode,
                show.status,
                show.imdbID,
                show.thetvdbID
            )
        return query

    def table(self) -> str:
        return self.__table

    @property
    def database(self):
        return self.__database
    
    @property
    def schema(self):
        return self.__schema
    
    @property
    def table(self):
        return self.__table
