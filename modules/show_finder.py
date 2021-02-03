#!/usr/bin/env python
import os, sys, re, sqlite3, xmltodict, time
from xml import parsers
from urllib.request import urlopen
from configparser import ConfigParser
from pprint import pprint
from .persistence import PersistanceInterface, ShowManager
from .persistence.models.show import Show

def main():
	try:
		get = getShow(ShowManager())
		get.promptName()
	except:
		print("Cancelled by user.")

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

	def search(self,query):
		seriesName = query.replace('.','')
		seriesName = seriesName.replace(' ','%20')

		url = 'http://thetvdb.com/api/GetSeries.php?seriesname='+seriesName
		if self.prompt:
			print(url)
		file = urlopen(url)
		data = file.read()
		file.close()

		self.series = []
		self.titles = []
		self.imdbIds= []
		data = xmltodict.parse(data)
		if data['Data']!=None:
			self.multiple = type(data['Data']['Series'])==list

			data = data['Data']['Series']
			self.insertName=""
			if self.multiple:
				n = 0
				i = None
				for row in data:
					name = row['SeriesName']
					id = row['seriesid']
					if 'IMDB_ID' in row.keys():
						imdb = row['IMDB_ID']
					else:
						imdb = 'Null'

					self.series.append(id)
					self.titles.append(name)
					self.imdbIds.append(imdb)
					self.shows.append({'id':id, 'name':name, 'imdb': imdb})

					if self.prompt:
						print("%d) %s = %s" % (n+1, name,id))
					n+=1
				if n>0:
					if self.prompt:
						i = int(input("Please input the show to find: "))-1
				else:
					i = n

				if i != None:
					self.id = self.series[i]
					self.insertName = title = self.titles[i]
					self.imdb = self.imdbIds[i]
			else:
				self.id = data['seriesid']
				self.insertName = title = data['SeriesName']
				if 'IMDB_ID' in data.keys():
					self.imdb = data['IMDB_ID']
				else:
					self.imdb = 'Null'
				self.shows.append({'id':self.id, 'name':self.insertName, 'imdb': self.imdb})
			if self.prompt:
				print(self.insertName)
				self.registerSeries(self.id)
		else:
			if self.prompt:
				print("Show not found.")
			return False
		return True
	
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
					regex = ""
					self.insertName = re.sub("\([0-9]{,4}\)","",self.insertName)
					self.insertName = self.insertName.strip()
					title = self.insertName.replace("'","''")
					for word in self.insertName.split(' '):
						firstLetter = word[:1]
						firstLetter = firstLetter.upper()
						word = firstLetter+word[1:]
						regex += word+" "
					regex = regex.strip()
					regex = regex.replace("'","")
					regex = regex.replace(":","")
					regex = re.sub('[ \.]',"[\\. ]{0,1}",regex)
					regex = re.sub("[A-Z]",lambda pat: "["+pat.group(0)+pat.group(0).lower()+"]",regex)
					
					regex = "("+regex+")"
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
				print("Unable to save show: {0}", e)
				return False


if __name__ == "__main__":
	sys.exit(main())





