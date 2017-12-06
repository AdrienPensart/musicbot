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
- filters
  - backup all the music (all)
  - local selection (4.5+ ?)
  - portable x5 bests selection (4+ ?)
- youtube
  - playlists
- production
  - domain
  - letsencrypt with caddy
  - nginx for static files
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

Usage: musicbot [OPTIONS] COMMAND [ARGS]...

  Music swiss knife, new gen.

Options:
  --version                       Show the version and exit.
  --verbosity [debug|info|warning|error|critical]
                                  Verbosity levels
  --dry                           Take no real action
  --quiet                         Silence any output (like progress bars)
  -h, --help                      Show this message and exit.

Commands:
  db        Database management
  filter    Filter creation
  folder    Folder scanning
  playlist  Playlist management
  server    API Server
  stats     Generate some stats for music collection with...
  tag       Music tags management
  youtube   Youtube management


musicbot db
***********
.. code-block::

  Usage: musicbot db [OPTIONS] COMMAND [ARGS]...
  
    Database management
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    -h, --help       Show this message and exit.
  
  Commands:
    clean   Clean deleted musics from database
    clear   Drop and recreate database and schema
    create  Create database and load schema
    drop    Drop database schema


musicbot db clean
*****************
.. code-block::

  Usage: musicbot db clean [OPTIONS]
  
    Clean deleted musics from database
  
  Options:
    -h, --help  Show this message and exit.


musicbot db clear
*****************
.. code-block::

  Usage: musicbot db clear [OPTIONS]
  
    Drop and recreate database and schema
  
  Options:
    -h, --help  Show this message and exit.


musicbot db create
******************
.. code-block::

  Usage: musicbot db create [OPTIONS]
  
    Create database and load schema
  
  Options:
    -h, --help  Show this message and exit.


musicbot db drop
****************
.. code-block::

  Usage: musicbot db drop [OPTIONS]
  
    Drop database schema
  
  Options:
    -h, --help  Show this message and exit.


musicbot filter
***************
.. code-block::

  Usage: musicbot filter [OPTIONS] [PATH] COMMAND [ARGS]...
  
    Filter creation
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder scanning
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    -h, --help       Show this message and exit.
  
  Commands:
    find    Only list files in selected folders
    rescan  Rescan all folders registered in database
    scan    Load musics files in database
    sync    Copy selected musics with filters to...
    watch   Check file modification in realtime and...


musicbot folder find
********************
.. code-block::

  Usage: musicbot folder find [OPTIONS] [FOLDERS]...
  
    Only list files in selected folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder rescan
**********************
.. code-block::

  Usage: musicbot folder rescan [OPTIONS]
  
    Rescan all folders registered in database
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder scan
********************
.. code-block::

  Usage: musicbot folder scan [OPTIONS] [FOLDERS]...
  
    Load musics files in database
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder sync
********************
.. code-block::

  Usage: musicbot folder sync [OPTIONS] DESTINATION
  
    Copy selected musics with filters to destination folder
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


musicbot folder watch
*********************
.. code-block::

  Usage: musicbot folder watch [OPTIONS]
  
    Check file modification in realtime and updates database
  
  Options:
    -h, --help  Show this message and exit.


musicbot playlist
*****************
.. code-block::

  Usage: musicbot playlist [OPTIONS] COMMAND [ARGS]...
  
    Playlist management
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    -h, --help       Show this message and exit.
  
  Commands:
    bests  Generate bests playlists with some rules
    new    Generate a new playlist


musicbot playlist bests
***********************
.. code-block::

  Usage: musicbot playlist bests [OPTIONS] PATH
  
    Generate bests playlists with some rules
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    --prefix TEXT             Append prefix before each path (implies relative)
    --suffix TEXT             Append this suffix to playlist name
    -h, --help                Show this message and exit.


musicbot playlist new
*********************
.. code-block::

  Usage: musicbot playlist new [OPTIONS] [PATH]
  
    Generate a new playlist
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    --prefix TEXT             Append prefix before each path (implies relative)
    -h, --help                Show this message and exit.


musicbot server
***************
.. code-block::

  Usage: musicbot server [OPTIONS] COMMAND [ARGS]...
  
    API Server
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    --dev            Dev mode, reload server on file changes
    -h, --help       Show this message and exit.
  
  Commands:
    start  Start musicbot web API


musicbot server start
*********************
.. code-block::

  Usage: musicbot server start [OPTIONS]
  
    Start musicbot web API
  
  Options:
    --host TEXT        Host interface to listen on
    --port INTEGER     Port to listen on
    --workers INTEGER  Number of workers
    -h, --help         Show this message and exit.


musicbot stats
**************
.. code-block::

  Usage: musicbot stats [OPTIONS] COMMAND [ARGS]...
  
    Generate some stats for music collection with filters
  
  Options:
    --host TEXT               DB host
    --port INTEGER            DB port
    --database TEXT           DB name
    --user TEXT               DB user
    --password TEXT           DB password
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


musicbot tag
************
.. code-block::

  Usage: musicbot tag [OPTIONS] COMMAND [ARGS]...
  
    Music tags management
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    -h, --help       Show this message and exit.
  
  Commands:
    add     Add tags - Not Implemented
    delete  Delete tags - Not implemented
    show    Show tags of musics with filters


musicbot tag add
****************
.. code-block::

  Usage: musicbot tag add [OPTIONS]
  
    Add tags - Not Implemented
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


musicbot tag delete
*******************
.. code-block::

  Usage: musicbot tag delete [OPTIONS]
  
    Delete tags - Not implemented
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


musicbot tag show
*****************
.. code-block::

  Usage: musicbot tag show [OPTIONS]
  
    Show tags of musics with filters
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    --fields TEXT             Show only those fields
    --output TEXT             Tags output format
    -h, --help                Show this message and exit.


musicbot youtube
****************
.. code-block::

  Usage: musicbot youtube [OPTIONS] COMMAND [ARGS]...
  
    Youtube management
  
  Options:
    --host TEXT      DB host
    --port INTEGER   DB port
    --database TEXT  DB name
    --user TEXT      DB user
    --password TEXT  DB password
    -h, --help       Show this message and exit.
  
  Commands:
    sync  Fetch youtube links for each music


musicbot youtube sync
*********************
.. code-block::

  Usage: musicbot youtube sync [OPTIONS]
  
    Fetch youtube links for each music
  
  Options:
    --filter FILENAME         Filter file to load
    --limit INTEGER           Fetch a maximum limit of music
    --youtube                 Select musics with a youtube link
    --formats <TEXT TEXT>...  Select musics with file format
    --no-formats TEXT         Filter musics without format
    --keywords TEXT           Select musics with keywords
    --no-keywords TEXT        Filter musics without keywords
    --artists TEXT            Select musics with artists
    --no-artists TEXT         Filter musics without artists
    --albums TEXT             Select musics with albums
    --no-albums TEXT          Filter musics without albums
    --titles TEXT             Select musics with titles
    --no-titles TEXT          Filter musics without titless
    --genres TEXT             Select musics with genres
    --no-genres TEXT          Filter musics without genres
    --min-duration TEXT       Minimum duration filter (hours:minutes:seconds)
    --max-duration TEXT       Maximum duration filter (hours:minutes:seconds))
    --min-size TEXT           Minimum file size filter (in bytes)
    --max-size TEXT           Maximum file size filter (in bytes)
    --min-rating FLOAT        Minimum rating
    --max-rating FLOAT        Maximum rating
    --relative                Generate relatives paths
    --shuffle                 Randomize selection
    -h, --help                Show this message and exit.


