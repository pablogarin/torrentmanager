Torrent Manager
====================

** WARNING **: V2 is in development. Please do not use!

To install, run "sudo ./install.sh"

<b>TORRENTMANAGER(1)</b><br/>
<br/>
<b>NAME:</b><br/>
<pre>
	torrentmanager - Auto Downloader for tv shows torrents<br/>
</pre>
<br/>
<b>SYNOPSIS:</b><br/>
<pre>
	torrentmanager<br/>
	torrentmanager [options] [value]<br/>
</pre>
<br/>
<b>DESCRIPTION:</b><br/>
<pre>
	Torrent Manager is a software dedicated to search and download the tv shows you watch daily. It must be preloaded with the shows you want it to search (see: --search and --add). It relies on Deluged torrent and deluge-console, all which will be installed with this software.<br/>
</pre>
<br/>
<b>OPTIONS:</b><br/>
<pre>
	--update, -u		 : Update Shows from Online source.<br/>
	--by-name, -n		 : Search new torrents by name.<br/>
	--list-shows, -l	 : List all the shows added.<br/>
	--search, -s [{SHOW_NAME}] : When no value is given, it will prompt for it. If given a show name, search for a tv show with the specified name. It returns a list with id and name. It also gives the imbd reference number to check the show.<br/>
	--add, -a {SHOW_ID}	 : Add a show with the specified id to the list. To find the show id, use --search {SHOW NAME}.<br/>
</pre>

