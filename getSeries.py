#!/usr/bin/env python
import urllib2, os, sys, re, sqlite3, xmltodict,time

def main():
	get = getseries()
	get.promptName()

class getseries:
	database = '/home/pi/torrentManager/downloadTorrents.db'
	prompt = False

	def __init__(self):
		self.conn = sqlite3.connect(self.database)

	def promptName(self):
		query = raw_input("Ingrese el nombre de la serie: ")
		self.query = query
		self.prompt = True
		self.search(query)

	def search(self,query):
		seriesName = query.replace('.','')
		seriesName = seriesName.replace(' ','%20')

		url = 'http://thetvdb.com/api/GetSeries.php?seriesname='+seriesName
		print url
		file = urllib2.urlopen(url)
		data = file.read()
		file.close()

		data = xmltodict.parse(data)
		self.multiple = type(data['Data']['Series'])==list

		data = data['Data']['Series']
		self.series = []
		self.titles = []
		self.imdbIds= []
		self.insertName=""
		if self.multiple:
			n = 0
			for row in data:
				name = row['SeriesName']
				id = row['seriesid']
				if 'IMDB_ID' in row.keys():
					imdb = row['IMDB_ID']
				else:
					imdb = 'Null'
				print `n+1` + ')' + name + ' = ' + id
				self.series.append(id)
				self.titles.append(name)
				self.imdbIds.append(imdb)
				n+=1
			if n>0:
				i = int(raw_input("Por favor indique la serie a agregar: "))-1
			else:
				i = n

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
		print self.insertName
		self.registerSeries(self.id)

	def registerSeries(self,id):
		self.id = id
		url = 'http://thetvdb.com/api/E16D53FBF4407C2B/series/'+id+'/all/'
		file = urllib2.urlopen(url)
		data = file.read()
		file.close

		data = xmltodict.parse(data)
		data = data['Data']
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
				except Exception, e:
					S = 1
					E = 1
				if S < 10:
					S = '0'+`S`
				else:
					S = `S`
				if E < 10:
					E = '0'+`E`
				else:
					E = `E`
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
						print "S"+S+"E"+E+": "+title+"(Aired "+time.strftime(airDate)+")"
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
							print "S"+S+"E"+E+": "+title+"(Pending "+time.strftime(airDate)+")"
						except:
							print "S"+S+"E"+E
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

		if lastSes < 10:
			lastSes = '0'+`lastSes`
		else:
			lastSes = `lastSes`
		if lastEp < 10:
			lastEp = '0'+`lastEp`
		else:
			lastEp = `lastEp`
		if lastSes==100:
			lastEp = " Pending confirmation"
		else:
			lastEp = 'S'+lastSes+'E'+lastEp
		if self.prompt:
			print ""
			print "Last Episode: "+lastEp

		if nextSes < 10:
			nextSes = '0'+`nextSes`
		else:
			nextSes = `nextSes`
		if nextEp < 10:
			nextEp = '0'+`nextEp`
		else:
			nextEp = `nextEp`
		if nextSes==100:
			nextEp = " Pending confirmation"
		else:
			nextEp = 'S'+nextSes+'E'+nextEp
		if self.prompt:
			print ""
			print "Next Episode: "+nextEp

		if self.prompt:
			grabar = raw_input("Desea agendar la serie?[Y/n]:")
			grabar = r'y'==grabar.lower()
		else:
			grabar = True

		if grabar:
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
			regex = re.sub('[ \.]',"[\\. ]{0,1}",regex)
			regex = re.sub("[A-Z]",lambda pat: "["+pat.group(0)+pat.group(0).lower()+"]",regex)
			
			regex = "("+regex+")"
			with self.conn:
				c = self.conn.cursor()
		#		try:
		#			c.execute("SELECT MAX(id) FROM tv_show")
		#			id = c.fetchone()
		#			id = id[0]
		#			id = int(id)+1
		#		except:
		#			id=1
				query = "INSERT OR REPLACE INTO tv_show VALUES(COALESCE((SELECT id FROM tv_show WHERE title='"+title+"'),(SELECT MAX(id) FROM tv_show) + 1),'"+title+"','"+regex+"',"+`nextReg['season']`+","+`nextReg['episode']`+",1,'"+self.imdb+"','"+id+"',datetime())"
				#print query
				c.execute(query)
				if self.prompt:
					print "Serie '"+title+"' fue agendada con exito"
				path = "/mnt/drive/download/Series/"+title.replace(' ','.');
				if not os.path.exists(path):
					os.makedirs(path)


if __name__ == "__main__":
	sys.exit(main())





