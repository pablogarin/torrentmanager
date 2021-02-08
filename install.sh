#!/bin/bash
apt-get -qy install deluged deluge-console python-dev python3-pip libxml2-dev libxslt-dev
pip install -r requirements.txt --quiet
touch /usr/bin/torrentmanager
echo '#!/bin/bash' > /usr/bin/torrentmanager
echo "$(pwd)/main.py \$@" >> /usr/bin/torrentmanager
chmod +x /usr/bin/torrentmanager
torrentmanager -c
