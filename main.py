#!/usr/bin/python3
import sys, os
from configparser import ConfigParser
from modules import torrentFinder, getShow
from pprint import pprint

def main(args):
    if len(args)>1:
        option = args[1]
    if len(args)==2:
        if option == "--update" or option == "-u":
            series = torrentFinder().series
            for serie in series:
                id = serie['thetvdbID']
                print("Updating show '%s'(%s)" % (serie['title'],id))
                if id != None:
                    obj = getShow()
                    obj.insertName = serie['title']
                    obj.imdb = serie['imdbID']
                    obj.registerSeries(id)
        elif option == "--by-name" or option == "-n":
            torrentFinder().checkByName()
        elif option == "--search" or option == "-s":
            try:
                gs = getShow()
                gs.promptName()
            except:
                print("Cancelled by user")
        elif option == "--list-shows" or option == "-l":
            for show in torrentFinder().getSeries():
                print("%s (Season %s, Episode %s)" % \
                    (show['title'], str(show['season']), str(show['episode'])))
        elif option == "--config" or option == "-c":
            defineDownloadFolder()
        else:
            print("Unknown Option.")
    elif len(args)>=3:
        value = ""
        for i in range(2,len(args)):
            value = value+args[i]+" "
        value = value.rstrip()
        if option == "--search" or option == "-s":
            gs = getShow()
            if gs.search(value):
                print("Match Found!")
                for show in gs.getShows():
                    pprint(show)
            else:
                print("No Matches for Show")
        elif option == "--add" or option == "-a":
            gs = getShow()
            if gs.registerSeries(value):
                print("Show Added")
            else:
                print("Show not found!")
        else:
            print("Unknown Option.")
            
    else:
        torrentFinder().readRSS()
    return 0

def defineDownloadFolder():
    path = os.path.dirname(os.path.realpath(__file__))
    Config = ConfigParser()
    folder = input("Please, enter the download folder: ")
    if not folder:
        print("You must define a download folder.")
        defineDownloadFolder()
    quality = input("Please, enter the download quality: ")
    if not quality:
        print("You must define a download quality.")
        defineDownloadFolder()
        Config.add_section("generals")
        Config.set("generals", "download_folder", folder)
        Config.set("generals", "quality", quality)
        cfgfile = open(path+"/config.ini", 'w')
        Config.write(cfgfile)
        cfgfile.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
