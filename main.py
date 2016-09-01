#!/usr/bin/python
import sys, downloadTorrents, getSeries

def main(args):
	if len(args)>1:
		option = args[1]
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
		if option == "--byname" or option == "-n":
			downloadTorrents.torrentFinder().checkByName()
		if option == "--search" or option == "-s":
			getSeries.getseries().promptName()
			
	else:
		downloadTorrents.torrentFinder().readRSS()
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
