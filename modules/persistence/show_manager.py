import sqlite3
import sys
from .persistence_interface import PersistanceInterface
from .models.show import Show


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
    
    def write(self, data: any):
        try:
            show = Show(data, self.conn)
            show.save()
        except Exception as e:
            print(e)

    def read(self, id):
        pass

    def find(self, query):
        series = []
        with self.conn:
            self.conn.row_factory = sqlite3.Row
            c = self.conn.cursor()
            c.execute("SELECT * FROM "+self.table+" ORDER BY lastDownload")
            while True:
                row = c.fetchone()
                if row==None:
                    break
                series.append(Show(row, self.conn))
        return series   

    @property
    def database(self):
        return self.__database
    
    @property
    def schema(self):
        return self.__schema
    
    @property
    def table(self):
        return self.__table
