#!/bin/bash
apt-get -q install deluged deluge-console python-dev python-pip
pip install feedparser xmltodict lxml -q
touch /usr/bin/torrentmanager
echo '#!/bin/bash' > /usr/bin/torrentmanager
echo "$(pwd)/main.py \$@" >> /usr/bin/torrentmanager
chmod +x /usr/bin/torrentmanager
torrentmanager -c
