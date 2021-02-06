#!/usr/bin/env python
import os, sys, re, sqlite3, subprocess, feedparser, time, threading, socket
from urllib.request import urlopen, Request, URLError, HTTPError
from lxml import html
from OpenSSL import SSL
from datetime import date
from modules.interfaces import PersistanceInterface
from modules.interfaces import FeedEntry
from modules.interfaces import FeedList
from modules.show import Show
from modules.rarbgclient import RarbgClient
# https://rarbg.unblocked.stream/torrents.php?imdb=

socket.setdefaulttimeout(3)


class TorrentFinder:
    _database = None
    _torrent_folder = ''
    _torrent_quality = ''
    _update_after = False
    _shows = []

    def __init__(
            self,
            database: PersistanceInterface,
            torrent_folder: str = '',
            torrent_quality: str = ''):
        self._database = database
        self._torrent_folder = torrent_folder
        self._torrent_quality = torrent_quality
        self._shows = []
        self.show = None
        self.invalidTorrents = []
        # self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41","https://kat.cr/usearch/category:tv%20age:hour/?rss=1"]
        # self.safeRSS = ["https://rarbg.to/rss.php?categories=18;41"]
        self.safeRSS = [
            "https://eztv.io/ezrss.xml",
            "http://rarbg.to/rss.php?category=1;18;41;49"]
        self.safeRSS = ["http://rarbg.to/rssdd.php?category=1;18;41;49"]
        self._set_show_list()

    def _set_show_list(self):
        for show in self._database.find():
            self._shows.append(show)

    def readRSS(self):
        rarbg_client = RarbgClient()
        self._check_feed_for_show(rarbg_client.read())

    def _check_feed_for_show(self, feed_list: FeedList):
        torrent = None
        torrentSeries = None
        foundBest = False
        for feed_entry in feed_list:
            print(feed_entry.title)
            for show in self._shows:
                torrent_link = None
                if self._should_download_torrent(
                        feed_entry.title,
                        show):
                    torrent_link = feed_entry.link
                elif self._should_download_torrent(
                        feed_entry.title,
                        show,
                        False):
                    torrent_link = feed_entry.link
                if torrent_link is not None:
                    print(torrent_link)
                    self.addTorrent(torrent_link, show)

    def checkByName(self):
        print("Searching by name. This might take a while (1-5 minutes)...\n")
        tmp = []
        for show in self._shows:
            tmp.append((show,))
        self.run_parallel_in_threads(self.lookupTorrents, tmp)

    def run_parallel_in_threads(self, target, args_list):
        threads = [threading.Thread(target=target, args=args) for args in args_list]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print("Search done!")

    def lookupTorrents(self, show: Show):
        torrent = None
        torrentSeries = None
        foundBest = False
        name = title = show.title
        name = name.lower()
        filename = (name.replace(' ', '.'))
        filename = filename+".S"+"{:02d}".format(show.season)+"E"+"{:02d}".format(show.episode)+".torrent"
        name = name.replace(' ', '-')
        name = re.sub(r'[\']', '', name)
        name = re.sub(r'[\.,]', '-', name)
        name = name.rstrip('-')
        url = "https://eztv.io/search/"+name
        try:
            hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                   'Accept-Encoding': 'none',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Connection': 'keep-alive'}
            req = Request(url, headers=hdr)
            con = urlopen(req)
            strHtml = con.read()
            con.close()
            print("'"+url+"' OK.")
            page = html.fromstring(strHtml)
            resultados = page.xpath("//a[@class='download_1']")
            for item in resultados:
                if foundBest:
                    break
                link = item.attrib['href'] 
                tmp = link.split('/')
                name = tmp[-1]
                if self.checkName(name, show):
                    print("Torrent found: '"+name+"'")
                    regex = "(LOL|FUM|DIMENSION|KILLERS|FLEET|AVS|SVA|TURBO|STRiFE|MiNX)"
                    m = re.search(regex, name)
                    if m:
                        print("First condition met: '"+regex+"'")
                        torrent = link
                        torrentSeries = show
                        foundBest = True
                        regex = "(%s[Pp])" % self._torrent_quality
                        m = re.search(regex, name)
                        if m:
                            print("Second condition met: '"+regex+"'")
                            torrent = link
                            torrentSeries = show
                            self._update_after = True
                            foundBest = True
                    regex = "(%s[Pp])" % self._torrent_quality
                    m = re.search(regex,name)
                    if m:
                        print("First condition met: '"+regex+"'")
                        torrent = link
                        torrentSeries = show
                        self._update_after = True
                        foundBest = True
            if torrent != None:
                self.addTorrent(torrent, torrentSeries)
                torrent = None
        except HTTPError as e:
            print("HTTP Error:", str(e), url)
        except URLError as e:
            print("URL Error:", str(e), url)
        except Exception as e:
            print("Error:", sys.exc_info()[0], url)

    def _should_download_torrent(
            self,
            title: str,
            show: Show,
            check_quality: bool = True) -> bool:
        if check_quality:
            return self._is_entry_scheduled(title, show) and\
                self._has_expected_quality(title) and\
                self._is_entry_current_episode(title, show)
        return self._is_entry_scheduled(title, show) and\
            self._is_entry_current_episode(title, show)

    def _is_entry_scheduled(self, title: str, show: Show) -> bool:
        match = re.search(show.regex, title.lower())
        return match is not None

    def _has_expected_quality(self, title: str) -> bool:
        if self._torrent_quality == "none":
            return True
        regexp = re.sub(
            r'[pP]',
            '[pP]',
            self._torrent_quality)
        match = re.search(regexp, title)
        if match is None:
            return False
        return True

    def _is_entry_current_episode(self, title: str, show: Show) -> bool:
        regexp = r'((S[0-9]{,2}E[0-9]{,2})|([0-9]{1,2}[xX][0-9]{1,2}))'
        match = re.search(regexp, title)
        feed_episode = match.group(0)
        current_episode = set([
            "S%02dE%02d" % (show.season, show.episode),
            "%dX%d" % (show.season, show.episode),
            "%dX%02d" % (show.season, show.episode),
        ])
        return feed_episode.upper() in current_episode

    def updateEpisode(self, show: Show):
        print("Updating database...")
        show.episode += 1
        show.save()

    def addTorrent(self, url, show: Show):
        folder = show.get_folder()
        if "magnet:" in url:
            print("Trying to add torrent '" + url + "' to download queue...")
            addCommand = "deluge-console add '"+url+" --path="+self._torrent_folder+"/"+folder+"/'"
            print(addCommand)
            result = subprocess.check_output(addCommand, shell=True)
            self.logOutput(url, result)
        else:
            try:
                torrentFile = show.title.replace("'", "")
                print("Descargando ", torrentFile)
                hdr = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'}
                req = Request(url, headers=hdr)
                f = urlopen(req)
                with open(str("/tmp/"+torrentFile), 'w') as fout:
                    fout.write(f.read())
                f.close()
            except HTTPError as e:
                print("HTTP Error:", str(e), url)
            except URLError as e:
                print("URL Error:", str(e), url)
            addCommand = "deluge-console add '/tmp/"+torrentFile+" --path="+self._torrent_folder+"/"+folder+"/'"
            print(addCommand)
            result = subprocess.check_output(addCommand, shell=True)
            self.logOutput(url, result)
        m = re.search("(ERROR|Torrent was not added!)", result)
        if m:
            self.invalidTorrents.append(url)
            return
        m = re.search("(Torrent added!)", result)
        if m:
            if self._update_after:
                self.updateEpisode(show)
        #        sys.exit(0)
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
    print("Deluged tv shows Manager.\n")
    option = None
    if len(argv) == 2:
        option = argv[1]
    if option != None:
        if option == "-n":
            finder = torrentFinder()
            finder.checkByName()
        else:
            print("Unknown Option.")
    else:
        finder = torrentFinder()
        finder.readRSS()
    return 0


if __name__ == '__main__':
    sys.exit(main())
