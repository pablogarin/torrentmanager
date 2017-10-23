#!/usr/bin/env python
import os, sys, re, sqlite3, subprocess, urllib2, feedparser, time, threading, socket, ConfigParser
from urllib2 import urlopen, Request, URLError, HTTPError
from lxml import html
from OpenSSL import SSL
from datetime import date
#https://rarbg.unblocked.stream/torrents.php?imdb=

socket.setdefaulttimeout(3)

class torrentFinder:
	folder = os.path.dirname(os.path.realpath(__file__))
	database = folder+'/downloadTorrents.db'
	updateAfter = False
	def __init__(self):
		print "Initializing..."
		self.serie = None
		self.series = []
		self.invalidTorrents = []
		# self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41","https://kat.cr/usearch/category:tv%20age:hour/?rss=1"]
		#self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41"]
                self.safeRSS = ["https://eztv.ag/ezrss.xml","http://rarbg.to/rss.php?category=1;18;41;49"]
                self.safeRSS = ["http://rarbg.to/rssdd.php?category=1;18;41;49"]
		print "Conecting to Data Base...\n"
		conn = sqlite3.connect(self.database)
		try:
			with conn:
				conn.row_factory = sqlite3.Row
				c = conn.cursor()
				c.execute("CREATE TABLE IF NOT EXISTS tv_show(id integer primary key autoincrement, title varchar(255), regex varchar(255), season int, episode int, status int, imdbID varchar(120), thetvdbID varchar(120), lastDownload datetime);")
		except Exception, e:
                        print "Error: unable to create database. Details: "+str(e)
			sys.exit(1)
		# if not os.path.exists(self.folder+"/logs"):
		# 	os.makedirs(self.folder+"/logs")
		self.loadDatabase()
		self.defineDownloadFolder()
	
	def loadDatabase(self):
		print "Listing Shows...\n"
		conn = sqlite3.connect(self.database)
		try:
			with conn:
				conn.row_factory = sqlite3.Row
				c = conn.cursor()
				c.execute("SELECT * FROM tv_show ORDER BY lastDownload");
				while True:
					row = c.fetchone()
					if row==None:
						break
					self.series.append(row)
		except Exception, e:
                        print "Error: Unable to read database. Details: "+str(e)
			sys.exit(1)
		
	def defineDownloadFolder(self):
		Config = ConfigParser.ConfigParser()
		if not os.path.isfile(self.folder+"/config.ini"):
			folder = raw_input("Please, enter the download folder: ")
			if not folder:
				self.defineDownloadFolder()
                                return
			quality = raw_input("Please, enter the download quality: ")
			if not quality:
				self.defineDownloadFolder()
                                return
                        Config.add_section("generals")
                        Config.set("generals", "download_folder", folder)
                        Config.set("generals", "quality", quality)
                        self.downloadFolder = folder
                        self.quality = quality
                        cfgfile = open(self.folder+"/config.ini", 'w')
                        Config.write(cfgfile)
                        cfgfile.close()
		else:
			Config.read(self.folder+"/config.ini")
			self.downloadFolder = Config.get("generals", "download_folder")
			self.quality = Config.get("generals", "quality")

	def getSeries(self):
		return self.series
		
	def readRSS(self):
		for url in self.safeRSS:
			print "Reading RSS Feed '%s'" % url
			try:
				feed=feedparser.parse(url)
				feedEntries = feed['entries']
				feed = None
				self.checkAllNames(feedEntries)
			except Exception, e:
                                print "Error: unable to connect to '%s'. Details:" % url
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
			if link != None:
                                print link
				for serie in self.series:
					self.logProcess(str(serie['title']+" => "+name))
					if foundBest:
						break
					if self.checkName(name,serie):
						print "Torrent found: '%s'" % name
						filename = feedEntries[i]['torrent_filename']+".torrent"
						#regex = "(\[rartv\]|\[rarbg\]|\[ettv\]|\[VTV\]|\[eztv\])$"
						#m = re.search(regex,name)
						#if m:
						print "First condition met!"
						regex = "(LOL|FUM|DIMENSION|KILLERS|FLEET|AVS|TURBO|STRiFE)"
						m = re.search(regex,name)
						if m:
							print "Second condition met!"
							regex = "(%s[Pp])" % self.quality
							m = re.search(regex,name)
							torrent = link
							torrentSeries = serie
							foundBest = True
							if m:
								print "Third condition met!"
								torrent = link
								self.updateAfter = True
								torrentSeries = serie
								foundBest = True
                                                regex = "(%s[Pp])" % self.quality
						m = re.search(regex,name)
						if m:
							print "Second condition met!"
							torrent = link
							self.updateAfter = True
							torrentSeries = serie
				if torrent != None:
					self.addTorrent(torrent,torrentSeries,filename)
					torrent = None
				else:
					print "No torrents found."
                        else:
                            entry = feedEntries[i]
                            name = entry['title']
                            print "Checking '%s'" % name
                            for serie in self.series:
                                    if foundBest:
                                            break
                                    if self.checkName(name,serie):
                                        filename = (serie['title'].replace(' ','.'))
                                        filename = filename+".S"+"{:02d}".format(serie['season'])+"E"+"{:02d}".format(serie['episode'])+".torrent"
                                        regex = "(%s[Pp])" % self.quality
                                        m = re.search(regex,name)
                                        if m:
                                            print "Condition met!: %s" % regex
                                            link = entry['link']
                                            # hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                                            #        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                            #        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                                            #        'Accept-Encoding': 'none',
                                            #        'Accept-Language': 'en-US,en;q=0.8',
                                            #        'Connection': 'keep-alive'}
                                            # req = Request(link, headers=hdr);
                                            # f = urlopen(req)
                                            # link = f.geturl()
                                            # link = link.replace('torrent/','download.php?id=')
                                            print "%s: %s" % (name, link)
                                            print "Found!"
                                            # self.addTorrent(link,serie,filename)
		
	def checkByName(self):
		print "Searching by name. This might take a while (1-5 minutes)...\n"
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
		print "Search done!"

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
					print "Torrent found: '"+name+"'"
					regex = "(LOL|FUM|DIMENSION|KILLERS|FLEET|AVS|TURBO|STRiFE)"
					m = re.search(regex,name)
					if m:
						print "First condition met: '"+regex+"'"
						torrent = link
						torrentSeries = serie
						foundBest = True
						regex = "(%s[Pp])" % self.quality
						m = re.search(regex,name)
						if m:
							print "Second condition met: '"+regex+"'"
							torrent = link
							torrentSeries = serie
							self.updateAfter = True
							foundBest = True
                                        regex = "(%s[Pp])" % self.quality
					m = re.search(regex,name)
					if m:
						print "First condition met: '"+regex+"'"
						torrent = link
						torrentSeries = serie
						self.updateAfter = True
						foundBest = True
			if torrent != None:
				self.addTorrent(torrent,torrentSeries,filename)
				torrent = None
		except HTTPError, e:
			print "HTTP Error:",str(e), url
		except URLError, e:
			print "URL Error:",str(e), url
		except:
			print "Error:",sys.exc_info()[0], url

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
		print "Updating database..."
		idSerie = serie['id']
		conn = sqlite3.connect(self.database)
		with conn:
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			c.execute("UPDATE tv_show SET episode="+`serie['episode']+1`+", lastDownload=datetime() WHERE id='"+`idSerie`+"'")

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
		print "Trying to add torrent '" + url + "' to download queue..."
		try:
			torrentFile = fileName.replace("'","")
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
			print "HTTP Error:", str(e), url
		except URLError, e:
			print "URL Error:", str(e), url
		folder = serie['title'].replace(' ','.')
		folder = folder.replace("'",'')
		addCommand = "deluge-console add '/tmp/"+torrentFile+" --path="+self.downloadFolder+"/"+folder+"/'"
		print addCommand
		result = subprocess.check_output(addCommand, shell=True)
		self.logOutput(url,result)
		m = re.search("(ERROR|Torrent was not added!)", result)
		if m:
			invalidTorrents.append(url)
			return
		m = re.search("(Torrent added!)", result)
		if m:
			if self.updateAfter:
				self.updateEpisode(serie)
		#		sys.exit(0)
		else:
			self.invalidTorrents.append(url)
			return

	def logOutput(self,torrent,output):
		# handle = open(self.folder+'/logs/deluged-'+str(date.today())+'.log','a')
		# handle.write("Torrent '"+torrent+"':\n")
		# handle.write(output)
		# handle.write("\n")
		# handle.close()
		return

	def logProcess(self,strLog):
		# handle = open(self.folder+'/logs/whathappened-'+str(date.today())+'.log','a')
		# handle.write(strLog+"\n")
		# handle.close()
		return

def main(argv=None):
	if argv is None:
		argv = sys.argv
	print "Deluged tv shows Manager.\n"
	option = None
	if len(argv) == 2:
		option = argv[1]
	if option != None:
		if option == "-n":
			finder = torrentFinder()
			finder.checkByName()
		else:
			print "Unknown Option."
	else:
		finder = torrentFinder()
		finder.readRSS()
	return 0

if __name__ == '__main__':
	sys.exit(main())
