Torrent Manager
====================

To install, run "sudo ./install.sh"

TORRENTMANAGER(1)

NAME:
	torrentmanager - Auto Downloader for tv shows torrents

SYNOPSIS:
	torrentmanager
	torrentmanager [options] [value]

DESCRIPTION:
	Torrent Manager is a software dedicated to search and download the tv shows you watch daily. It must be preloaded with the shows you want it to search (see: --search and --add). It relies on Deluged torrent and deluge-console, all which will be installed with this software.

OPTIONS:
	--update, -u		 : Update Shows from Internet for more actual data.
	--by-name, -n		 : Search all torrents by name.
	--list-shows, -l	 : List all shows in the queue.
	--search, -s {SHOW_NAME} : search for a tv show with the specified name. It returns a list with id and name. It also gives the imbd reference number to check the show.
	--add, -a {SHOW_ID}	 : Add a show with the specified id to the list. To find the show id, use --search {SHOW NAME}.
