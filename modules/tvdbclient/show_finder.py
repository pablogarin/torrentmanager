#!/usr/bin/env python
import os, sys, re, sqlite3, xmltodict, time
from xml import parsers
from urllib.request import urlopen
from configparser import ConfigParser
from pprint import pprint
from modules.interfaces.persistence_interface import PersistanceInterface
from modules.show import Show
from modules.tvdbclient import TVDBClient


class getShow(object):
    folder = os.path.dirname(os.path.realpath(__file__))
    database = folder+'/downloadTorrents.db'
    prompt = False
    insertName = None
    series = []
    titles = []
    imdbIds= []
    shows  = []

    def __init__(self, database: PersistanceInterface):
        self.database = database
        self.defineDownloadFolder()
        self.tvdb = TVDBClient()

    def defineDownloadFolder(self):
        Config = ConfigParser()
        if not os.path.isfile("config.ini"):
            folder = input("Por favor ingrese una carpeta para la descarga de los torrents: ")
            if not folder:
                self.defineDownloadFolder()
            else:
                Config.add_section("generals")
                Config.set("generals", "download_folder", folder)
                self.downloadFolder = folder
                cfgfile = open("config.ini", 'w')
                Config.write(cfgfile)
                cfgfile.close()
        else:
            Config.read("config.ini")
            self.downloadFolder = Config.get("generals", "download_folder")
        
    def promptName(self):
        query = input("Please input the show to find: ")
        self.query = query
        self.prompt = True
        self.search(query)

    def search(self, query: str) -> bool:
        seriesName = query.replace('.','')
        seriesName = seriesName.replace(' ','%20')
        search_result = self.tvdb.search(seriesName)
        show_to_insert = None
        if len(search_result) == 0:
            if self.prompt:
                print("Show not found.")
            return False
        for i, show in enumerate(search_result):
            print("%d) %s = %s" % (i+1, show['title'], show['id']))
        if self.prompt:
            if len(search_result) == 1:
                i = 0
            else:
                i = int(input("Please input the show to find: "))-1
            show_to_insert = search_result[i]
        if show_to_insert is not None:
            self.registerSeries(show_to_insert['id'])
        return len(search_result) > 0
    
    def getShows(self):
        return self.shows

    def registerSeries(self,id):
        self.id = id
        url = 'http://thetvdb.com/api/E16D53FBF4407C2B/series/'+id+'/all/en.xml'
        print(url)
        data = None
        try:
            file = urlopen(url)
            data = file.read()
            file.close
        except Exception as e:
            print("Unable to connect to web service.")
        if data != None:
            try:
                data = xmltodict.parse(data)
                data = data['Data']
                if self.insertName==None:
                    self.insertName = data['Series']['SeriesName']
                    self.imdb = data['Series']['IMDB_ID']
                episodes = data['Episode']

                now = time.strftime("%Y-%m-%d")
                now = time.strptime(now,"%Y-%m-%d")

                lastSes = 0
                lastEp = 0

                nextSes = 100
                nextEp = 100

                if type(episodes) is list:
                    for episode in episodes:
                        try:
                            S = int(episode['SeasonNumber'])
                            E = int(episode['EpisodeNumber'])
                        except Exception as e:
                            S = 1
                            E = 1
                        S = "%02d" % S
                        E = "%02d" % E
                        title = episode['EpisodeName']
                        airDate = " - "
                        if 'FirstAired' in episode.keys():
                            airDate = episode['FirstAired']
                            try:
                                aired = now > time.strptime(airDate,"%Y-%m-%d")
                            except:
                                airDate = " - "
                                aired = False
                        else:
                            aired = False
                        if aired:
                            if self.prompt:
                                if title == None:
                                    title = ''
                                D=time.strftime(airDate)
                                print("S%sE%s: %s(Aired %s)" % (S,E,title,D))
                            curSes = int(S)
                            curEp = int(E)
                            if curSes>=lastSes:
                                lastSes = curSes
                                lastEp = 0
                                if lastEp<curEp:
                                        lastEp = curEp
                                nextEp = lastEp+1
                                nextSes = lastSes
                        else:
                            if self.prompt:
                                try:
                                    print("S%sE%s: %s(Pending %s)" % (S,E,title,time.strftime(airDate)))
                                except:
                                    print("S%sE%s" % (S,E))
                            curSes = int(S)
                            curEp = int(E)
                            if nextSes<curSes:
                                nextEp = 1
                                nextSes = curSes
                else:
                    nextSes = 1
                    lastSes = 1
                    nextEp = 1
                    lastEp = 1
                if nextSes==100:
                    nextSes = 1
                    lastSes = 1
                    nextEp = 1
                    lastEp = 1
                nextReg = {'season':nextSes,'episode':nextEp}
                lastSes = "%02d" % lastSes
                lastEp = "%02d" % lastEp
                if lastSes=="100":
                    lastEp = " Pending confirmation"
                else:
                    lastEp = "S%sE%s" % (lastSes,lastEp)
                if self.prompt:
                    print("")
                    print("Last Episode: %s" % lastEp)
                nextSes = "%02d" % nextSes
                nextEp = "%02d" % nextEp
                if nextSes=="100":
                    nextEp = " Pending confirmation"
                else:
                    nextEp = "S%sE%s" % (nextSes,nextEp)
                if self.prompt:
                    print("")
                    print("Next Episode: %s" % nextEp)

                if self.prompt:
                    saveShow = input("Do you wish to schedule the show?[Y/n]:")
                    saveShow = r'y'==saveShow.lower()
                else:
                    saveShow = True

                if saveShow:
                    try:
                        self.insertName = re.sub(r'\([0-9]{,4}\)',"",self.insertName)
                        #.strip()
                            #.replace("'","\\")
                        title = self.insertName
                    except Exception as e:
                        print("Here %s" % e)
                    
                    regex = self.build_regex(title)
                    data = {
                        'title': title,
                        'regex': regex,
                        'season': nextReg['season'],
                        'episode': nextReg['episode'],
                        'imdbID': self.imdb,
                        'thetvdbID': id
                    }
                    show = Show(data, self.database)
                    show.save()
                    if self.prompt:
                        print("Show '%s' scheduled!" % title)
                    path = self.downloadFolder+"/"+title.replace(' ','.')
                    path = re.sub('[^ a-zA-Z0-9\.]','', path)
                    if not os.path.exists(path):
                        os.makedirs(path)
                return True
            except Exception as e:
                print("Unable to save show: %s" % e)
                return False

    def build_regex(self, title):
        regex = title.title().strip()
        regex = re.sub("[:']","", regex)
        regex = re.sub('[ \.]',"[\\. ]{0,1}",regex)
        regex = re.sub("[A-Z]",lambda pat: "["+pat.group(0)+pat.group(0).lower()+"]",regex)
        return "(%s)" % regex

if __name__ == "__main__":
    sys.exit(main())





