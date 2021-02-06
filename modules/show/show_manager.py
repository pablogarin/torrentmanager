import sqlite3
import sys
from modules.interfaces import PersistanceInterface
from .show import Show


class ShowManager(PersistanceInterface):
    _database = 'db/downloadTorrents.db'
    _table = 'tv_show'
    _schema = "CREATE TABLE IF NOT EXISTS tv_show(\
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
    _conn = None

    def __init__(self):
        self._conn = sqlite3.connect(self.database)
        try:
            self._conn.row_factory = sqlite3.Row
            c = self._conn.cursor()
            c.execute(self.schema)
        except Exception as e:
            print("Error: unable to create database. Details: "+str(e))
            sys.exit(1)

    def __del__(self):
        self._conn.close()

    def write(self, data: any):
        try:
            c = self._conn.cursor()
            c.execute(self._build_insert_query(data))
            self._conn.commit()
        except Exception as e:
            print("Error writing into database: %s" % e)

    def read(self, id):
        pass

    def find(self, query=''):
        series = []
        try:
            self._conn.row_factory = sqlite3.Row
            c = self._conn.cursor()
            c.execute("SELECT * FROM %s ORDER BY lastDownload" % self.table)
            while True:
                row = c.fetchone()
                if row is None:
                    break
                series.append(Show(row, self))
        except Exception as e:
            print("Error reading database: %s" % e)
        return series

    def _build_insert_query(self, show: Show) -> str:
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
        return self._table

    @property
    def database(self):
        return self._database

    @property
    def schema(self):
        return self._schema

    @property
    def table(self):
        return self._table
