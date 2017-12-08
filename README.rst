========
MusicBot
========
Build Status: |build-health|

.. |build-health|  image:: https://landscape.io/github/AdrienPensart/musicbot/master/landscape.svg?style=flat
   :target: https://landscape.io/github/AdrienPensart/musicbot/master
   :alt: Code Health

Description
-----------
Little script to manipulate music and create playlists

Some features :

- tag filters
- Plex playlist importer

Tips
----
Copy your best tracks to your favorite portable music player :

- musicbot sync --min-rating=4 --no-keywords cutoff,bad,demo,intro /media/user/destination

Generate the best playlists on your device :

- find /media/user/destination -name \*.m3u -delete
- musicbot bests --path /media/user/destination --relative --min-rating=4 --no-keywords=cutoff,bad,demo,intro

Don't forget to delete empty directories recursively :

- find /media/user/destination -type d -empty -delete

Generate the best playlists on your hard disk :

- musicbot bests --path /home/user/music --min-rating=4

Feed the playlist to Clementine or VLC players :

- using zsh : clementine =(musicbot playlist --shuffle /home/user/music)
- using bash : musicbot playlist --shuffle /home/user/music > /tmp/playlist.m3u; clementine /tmp/playlist.m3u
- using fish : clementine (musicbot playlist --shuffle /home/user/music | psub)

Enable auto-completion (works for bash and zsh) :

- pip install infi.docopt-completion
- docopt-completion musicbot

Installation
------------

.. code-block:: bash

  sudo apt-get install sox libsox-fmt-mp3 sqlite3 cmake libyaml-dev
  git clone https://github.com/taglib/taglib.git
  mkdir -p taglib/build &&  cd taglib/build
  cmake .. -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release
  make -j8
  sudo make install
  cd ../..

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot
  python-3.6 -m venv env
  source env/bin/activate
  pip install -r requirements.txt

ToDo
----
- application
  - invocation_id / logs
  - configuration : global conf -> user conf -> env var -> arguments
  - full API / template separation
  - CLI
- filters
  - backup all the music (all)
  - local selection (4.5+ ?)
  - portable x5 bests selection (4+ ?)
- youtube
  - playlists
- production
  - dockerize
- tests / optimizations
  - fast bulk inserts
  - web caching of templates
  - postgresql materialized view
  - fast stats

Bugs/Flows
--
- youtube live version crawling

Ideas
--
- in database consistency checks
- fuse driver
- tree views configuration (letter,artist,genre,keyword)
- OVH Functions test
- OVH with terraform
- re-handle UUID in music files, like first version of musicmaniac (C++)
- console UI
- music player

Commands
--------
.. code-block::



