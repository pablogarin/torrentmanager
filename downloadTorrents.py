#!/usr/bin/env python
import os, sys, re, sqlite3, subprocess, urllib2, feedparser, time, threading, socket
from urllib2 import urlopen, Request, URLError, HTTPError
from lxml import html
from OpenSSL import SSL
from datetime import date
#https://rarbg.unblocked.stream/torrents.php?imdb=

socket.setdefaulttimeout(3)

class torrentFinder:
	folder = os.path.dirname(os.path.realpath(__file__))
	database = folder+'/downloadTorrents.db'
	def __init__(self):
		print "Inicializando variables..."
		self.serie = None
		self.series = []
		self.invalidTorrents = []
		# self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41","https://kat.cr/usearch/category:tv%20age:hour/?rss=1"]
		#self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41"]
		self.safeRSS = ["https://eztv.ag/ezrss.xml"]
		print "Conectando a la base de datos...\n"
		conn = sqlite3.connect(self.database)
		try:
			with conn:
				conn.row_factory = sqlite3.Row
				c = conn.cursor()
				c.execute("CREATE TABLE IF NOT EXISTS tv_show(id integer primary key autoincrement, title varchar(255), regex varchar(255), season int, episode int, status int, imdbID varchar(120), thetvdbID varchar(120), ultimoCapitulo datetime);")
		except Exception, e:
			print "Error al crear la base de datos: "+str(e)
			sys.exit(1)
	
	def loadDatabase(self):
		print "Leyendo Series...\n"
		conn = sqlite3.connect(self.database)
		try:
			with conn:
				print "Leyendo Series...\n"
				conn.row_factory = sqlite3.Row
				c = conn.cursor()
				c.execute("SELECT * FROM tv_show ORDER BY ultimoCapitulo");
				while True:
					row = c.fetchone()
					if row==None:
						break
					self.series.append(row)
		except Exception, e:
			print "Error al leer la base de datos: "+str(e)
			sys.exit(1)
		
	
	def readRSS(self):
		for url in self.safeRSS:
			print "Leyendo Feed RSS '"+url+"'"
			try:
				feed=feedparser.parse(url)
				feedEntries = feed['entries']
				feed = None
				self.checkAllNames(feedEntries)
			except Exception, e:
				print "Error al comunicarse con '"+url+"'. Motivo:"
				print str(e)

	def checkAllNames(self,feedEntries):
		torrent = None
		torrentSeries = None
		foundBest = False
		for i in range(0,len(feedEntries)):
			foundBest = False
			name = feedEntries[i]['title']
			#id = feedEntries[i]['link'].split('/')[-1]
			#link = "https://rarbg.to/download.php?id="+id+"&f="+name+".torrent"
			link = None
			links = feedEntries[i]['links']
			for anchor in links:
				if anchor.type == 'application/x-bittorrent':
					link = anchor.href
			print link
			if link != None:
				for serie in self.series:
					self.logProcess(str(serie['title']+" => "+name))
					if foundBest:
						break
					if self.checkName(name,serie):
						print "Torrent encontrado: '"+name+"'"
						filename = feedEntries[i]['torrent_filename']+".torrent"
						#regex = "(\[rartv\]|\[rarbg\]|\[ettv\]|\[VTV\]|\[eztv\])$"
						#m = re.search(regex,name)
						#if m:
						print "paso la primera"
						regex = "(LOL|FUM|DIMENSION|KILLERS|FLEET|AVS)"
						m = re.search(regex,name)
						if m:
							print "paso la segunda"
							regex = "(720[Pp])"
							m = re.search(regex,name)
							if m:
								print "paso la tercera"
								torrent = link
								torrentSeries = serie
								foundBest = True
						regex = "(720[Pp])"
						m = re.search(regex,name)
						if m:
							print "paso la segunda"
							torrent = link
							torrentSeries = serie
				if torrent != None:
					self.addTorrent(torrent,torrentSeries,filename)
					torrent = None
				else:
					print "No se encontraron torrents."
		
	def checkByName(self):
		print "Buscando por nombre, esto puede tardar un poco (1 a 5 minutos)...\n"
		tmp = []
		for serie in self.series:
			tmp.append((serie,))
		self.run_parallel_in_threads(self.lookupTorrents, tmp)

	def run_parallel_in_threads(self, target, args_list):
		threads = [threading.Thread(target=target, args=args) for args in args_list]
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		print "Busqueda finalizada!"

	def lookupTorrents(self,serie):
		torrent = None
		torrentSeries = None
		foundBest = False
		name = title = serie['title']
		name = name.lower()
		filename = (name.replace(' ','.'))
		filename = filename+".S"+"{:02d}".format(serie['season'])+"E"+"{:02d}".format(serie['episode'])+".torrent"
		name = name.replace(' ','-')
		name = re.sub(r'[\']','',name)
		name = re.sub(r'[\.,]','-',name)
		name = name.rstrip('-')
		url  = "https://eztv.ag/search/"+name
		try:
			hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			       'Accept-Encoding': 'none',
			       'Accept-Language': 'en-US,en;q=0.8',
			       'Connection': 'keep-alive'}
			req = Request(url, headers=hdr);
			con = urlopen(req)
			strHtml = con.read()
			con.close()
			print "'"+url+"' OK."
			page = html.fromstring(strHtml)
			resultados = page.xpath("//a[@class='download_1']")
			for item in resultados:
				if foundBest:
					break
				link = item.attrib['href'] 
				tmp = link.split('/');
				name = tmp[-1]
				if self.checkName(name, serie):
					print "Torrent encontrado: '"+name+"'"
					regex = "(LOL|FUM|DIMENSION|KILLERS|FLEET|AVS)"
					m = re.search(regex,name)
					if m:
						print "paso la primera: '"+regex+"'"
						regex = "(720[Pp])"
						m = re.search(regex,name)
						if m:
							print "paso la segunda: '"+regex+"'"
							torrent = link
							torrentSeries = serie
							foundBest = True
					regex = "(720[Pp])"
					m = re.search(regex,name)
					if m:
						print "paso la primera: '"+regex+"'"
						torrent = link
						torrentSeries = serie
						foundBest = True
			if torrent != None:
				self.addTorrent(torrent,torrentSeries,filename)
				torrent = None
		except HTTPError, e:
			print "Error de HTTP:",str(e), url
		except URLError, e:
			print "Error de URL:",str(e), url

	def checkName(self,name,serie):
		#TODO: add the best match, not the first
		best = False
		regex = serie['regex']#+".*(\[rartv\]|\[rarbg\]|\[eztv\]|\[ettv\]|\[VTV\]|\[eztv\])"
		m = re.search(regex,name)
		if m:
			if self.checkEpisode(name,serie):
				return True
		return False

	def checkEpisode(self,name,serie):
		regex = '(S[0-9]{,2}E[0-9]{,2})'
		m = re.search(regex,name)
		if m:
			actual = m.group(0)
			season = serie['season']
			episode = serie['episode']
			current = "S"
			if season<10:
				current += "0"+`season`
			else:
				current += `season`
			current += "E"
			if episode<10:
				current += "0"+`episode`
			else:
				current += `episode`
			if actual==current:
				return True
		regex = '([0-9]{1,2}[xX][0-9]{1,2})'
		m = re.search(regex,name)
		if m:
			actual = m.group(0)			
			season = serie['season']
			episode = serie['episode']
			current = `season`+"x"
			if episode<10:
				current += "0"+`episode`
			else:
				current += `episode`
			if actual==current:
				return True
			current = `season`+"x"+`episode`
			if actual==current:
				return True
		return False

	def updateEpisode(self,serie):
		print "Actualizando base de datos..."
		idSerie = serie['id']
		conn = sqlite3.connect(self.database)
		with conn:
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			c.execute("UPDATE tv_show SET episode="+`serie['episode']+1`+", ultimoCapitulo=datetime() WHERE id='"+`idSerie`+"'")

		self.series = []
		conn = sqlite3.connect(self.database)
		with conn:
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			c.execute("SELECT * FROM tv_show");
			while True:
				row = c.fetchone()
				if row==None:
					break
				self.series.append(row)

	def addTorrent(self,url,serie, fileName):
		print "Intentando agregar el torrent '" + url + "' a la cola de descargas..."
		try:
			torrentFile = fileName
			print "Descargando ", torrentFile
			hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
			       'Accept-Encoding': 'none',
			       'Accept-Language': 'en-US,en;q=0.8',
			       'Connection': 'keep-alive'}
			req = Request(url, headers=hdr);
			f = urlopen(req)
			with open(str("/tmp/"+torrentFile),'w') as fout:
				fout.write(f.read())
			f.close()
		except HTTPError, e:
			print "Error de HTTP:", str(e), url
		except URLError, e:
			print "Error de URL:", str(e), url
		folder = serie['title'].replace(' ','.')
		folder = folder.replace("'",'')
		addCommand = "deluge-console add '/tmp/"+torrentFile+" --path=/mnt/drive/download/Series/"+folder+"/'"
		print addCommand
		result = subprocess.check_output(addCommand, shell=True)
		self.logOutput(url,result)
		m = re.search("(ERROR|Torrent was not added!)", result)
		if m:
			invalidTorrents.append(url)
			return
		m = re.search("(Torrent added!)", result)
		if m:
			self.updateEpisode(serie)
	#		sys.exit(0)
		else:
			self.invalidTorrents.append(url)
			return

	def logOutput(self,torrent,output):
		handle = open(self.folder+'/logs/deluged-'+str(date.today())+'.log','a')
		handle.write("Torrent '"+torrent+"':\n")
		handle.write(output)
		handle.write("\n")
		handle.close()

	def logProcess(self,strLog):
		handle = open(self.folder+'/logs/whathappened-'+str(date.today())+'.log','a')
		handle.write(strLog+"\n")
		handle.close()

def main(argv=None):
	if argv is None:
		argv = sys.argv
	print "Gestor de series automatico.\n"
	option = None
	if len(argv) == 2:
		option = argv[1]
	if option != None:
		if option == "-n":
			finder = torrentFinder()
			finder.checkByName()
		else:
			print "Comando no reconocido."
	else:
		finder = torrentFinder()
		finder.readRSS()
	return 0

if __name__ == '__main__':
	sys.exit(main())
