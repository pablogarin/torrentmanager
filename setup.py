from setuptools import find_packages
from setuptools import setup


setup(
    name="torrentmanager",
    version="1.0.0",
    description="Torrent manging tool which helps "
            "you schedule and download tv show episodes",
    author="Pablo Garin",
    author_email="pablo.garin@hotmail.com",
    url="https://github.com/pablogarin/torrentmanager",
    packages=find_packages(),
    install_requires=[
        "lxml",
        "feedparser",
        "xmltodict"
    ],
    entry_points={
        "console_scripts": [
            "torrentmanager-cli = torrentmanager:main",
            "torrentmanagerd = "
            "torrentmanager.torrentmanagerd:run_in_background",
        ]
    }
)
