#!/usr/bin/python
import sys, os, downloadTorrents, getSeries, ConfigParser
from pprint import pprint

def main(args):
	if len(args)>1:
		option = args[1]
	if len(args)==2:
		if option == "--update" or option == "-u":
			series = downloadTorrents.torrentFinder().series
			for serie in series:
				id = serie['thetvdbID']
				print "Actualizando serie '"+serie['title']+"'("+id+")"
				if id != None:
					obj = getSeries.getseries()
					obj.insertName = serie['title']
					obj.imdb = serie['imdbID']
					obj.registerSeries(id)
		elif option == "--by-name" or option == "-n":
			downloadTorrents.torrentFinder().checkByName()
		elif option == "--list-shows" or option == "-l":
			for show in downloadTorrents.torrentFinder().getSeries():
				print show['title']+" (Temporada "+str(show['season'])+", Capitulo "+str(show['episode'])+")"
		elif option == "--config" or option == "-c":
			defineDownloadFolder()
		else:
			print "Parametro no encontrado."
	elif len(args)>=3:
		value = ""
		for i in range(2,len(args)):
			value = value+args[i]+" "
		value = value.rstrip()
		if option == "--search" or option == "-s":
			gs = getSeries.getseries()
			if gs.search(value):
				print "Encontrada"
				for show in gs.getShows():
					pprint(show)
			else:
				print "No se encontraron series"
		elif option == "--add" or option == "-a":
			gs = getSeries.getseries()
			if gs.registerSeries(value):
				print "Serie agregada"
			else:
				print "Serie no encontrada"
		else:
			print "Parametro no encontrado."
			
	else:
		downloadTorrents.torrentFinder().readRSS()
	return 0

def defineDownloadFolder():
	path = os.path.dirname(os.path.realpath(__file__))
	Config = ConfigParser.ConfigParser()
	folder = raw_input("Por favor ingrese una carpeta para la descarga de los torrents: ")
	if not folder:
		print "Debe definir una carpeta."
		defineDownloadFolder()
	else:
		Config.add_section("generals")
		Config.set("generals", "download_folder", folder)
		cfgfile = open(path+"/config.ini", 'w')
		Config.write(cfgfile)
		cfgfile.close()

if __name__ == "__main__":
	sys.exit(main(sys.argv))
