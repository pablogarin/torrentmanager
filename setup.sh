#!/bin/bash
apt-get install deluged deluge-console python-dev python-pip
pip install feedparser xmltodict
touch /usr/bin/torrentmanager
echo '#!/bin/bash' > /usr/bin/torrentmanager
echo "$(pwd)/main.py \$@" >> /usr/bin/torrentmanager
