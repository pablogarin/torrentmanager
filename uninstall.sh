#!/bin/bash
pip uninstall feedparser xmltodict lxml -q
apt-get -q autoremove deluged deluge-console python-dev python-pip
rm /usr/bin/torrentmanager
