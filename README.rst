========
MusicBot
========
+---------------+-----------------+
|     Tools     |      Result     |
+===============+=================+
| Code Quality  | |build-health|  |
+---------------+-----------------+
| Code Coverage | |code-coverage| |
+---------------+-----------------+

.. |code-coverage| image:: https://api.codacy.com/project/badge/Grade/621acf3309b24c538c40824f9af467de
   :target: https://www.codacy.com/app/AdrienPensart/musicbot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=AdrienPensart/musicbot&amp;utm_campaign=Badge_Grade
   :alt: Code coverage
.. |build-health|  image:: https://landscape.io/github/AdrienPensart/musicbot/master/landscape.svg?style=flat
   :target: https://landscape.io/github/AdrienPensart/musicbot/master
   :alt: Code Health

Description
-----------
CLI / API / Website to manipulate music and create smart playlists, and play it !

Installation
------------

.. code-block:: bash

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot
  python-3.6 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
ToDo
----
- tests :
  - web
  - cli
  - coverage
  - db
- javascript
- better CSS
- bests playlist without live versions

Bugs/Flows
--
- live versions of song / album when searching on youtube
- youtube caching
- pagination
- rename tags to keywords
- copy prod database
- cache must be disabled when shuffle = 1

Ideas
--
- in database consistency checks
- tree views configuration (letter,artist,genre,keyword)
- OVH with terraform plugin
- use prometheous for metrics
- use OVH Data Logs
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
  --quiet                         Disable progress bars
  --invocation TEXT               Resumable execution ID (experimental)
  -h, --help                      Show this message and exit.

Commands:
  config       Config management
  consistency  Inconsistencies management
  db           Database management
  folder       Folder scanning
  playlist     Playlist management
  server       API Server
  stats        Generate some stats for music collection with...
  tag          Music tags management
  task         Task management
  youtube      Youtube management


musicbot config
***************
.. code-block::

  Usage: musicbot config [OPTIONS] COMMAND [ARGS]...
  
    Config management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    save  Save config


musicbot config save
********************
.. code-block::

  Usage: musicbot config save [OPTIONS]
  
    Save config
  
  Options:
    --redis-address TEXT    Redis URI
    --redis-db INTEGER      Redis index DB
    --redis-password TEXT   Redis password
    --db-host TEXT          DB host
    --db-port INTEGER       DB port
    --db-database TEXT      DB name
    --db-user TEXT          DB user
    --db-password TEXT      DB password
    --http-host TEXT        Host interface to listen on
    --http-port INTEGER     HTTP port to listen on
    --http-workers INTEGER  Number of HTTP workers (not tested)
    --http-user TEXT        HTTP Basic auth user
    --http-password TEXT    HTTP Basic auth password
    -h, --help              Show this message and exit.


musicbot consistency
********************
.. code-block::

  Usage: musicbot consistency [OPTIONS] COMMAND [ARGS]...
  
    Inconsistencies management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    errors  Detect errors


musicbot consistency errors
***************************
.. code-block::

  Usage: musicbot consistency errors [OPTIONS]
  
    Detect errors
  
  Options:
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot db
***********
.. code-block::

  Usage: musicbot db [OPTIONS] COMMAND [ARGS]...
  
    Database management
  
  Options:
    --db-host TEXT      DB host
    --db-port INTEGER   DB port
    --db-database TEXT  DB name
    --db-user TEXT      DB user
    --db-password TEXT  DB password
    -h, --help          Show this message and exit.
  
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
    --yes       Are you sure you want to drop the db?
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
    --yes       Are you sure you want to drop the db?
    -h, --help  Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder scanning
  
  Options:
    --db-host TEXT      DB host
    --db-port INTEGER   DB port
    --db-database TEXT  DB name
    --db-user TEXT      DB user
    --db-password TEXT  DB password
    -h, --help          Show this message and exit.
  
  Commands:
    find    Only list files in selected folders
    list    List existing folders
    new     Add a new folder in database
    rescan  Rescan all folders registered in database
    scan    Load musics files in database
    sync    Copy selected musics with filters to...
    watch   Watch files changes in folders


musicbot folder find
********************
.. code-block::

  Usage: musicbot folder find [OPTIONS] [FOLDERS]...
  
    Only list files in selected folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder list
********************
.. code-block::

  Usage: musicbot folder list [OPTIONS]
  
    List existing folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder new
*******************
.. code-block::

  Usage: musicbot folder new [OPTIONS] [FOLDERS]...
  
    Add a new folder in database
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder rescan
**********************
.. code-block::

  Usage: musicbot folder rescan [OPTIONS]
  
    Rescan all folders registered in database
  
  Options:
    --concurrency INTEGER  Number of coroutines
    --concurrency INTEGER  Number of coroutines
    --crawl                Crawl youtube
    -h, --help             Show this message and exit.


musicbot folder scan
********************
.. code-block::

  Usage: musicbot folder scan [OPTIONS] [FOLDERS]...
  
    Load musics files in database
  
  Options:
    --concurrency INTEGER  Number of coroutines
    --crawl                Crawl youtube
    -h, --help             Show this message and exit.


musicbot folder sync
********************
.. code-block::

  Usage: musicbot folder sync [OPTIONS] DESTINATION
  
    Copy selected musics with filters to destination folder
  
  Options:
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot folder watch
*********************
.. code-block::

  Usage: musicbot folder watch [OPTIONS]
  
    Watch files changes in folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot playlist
*****************
.. code-block::

  Usage: musicbot playlist [OPTIONS] COMMAND [ARGS]...
  
    Playlist management
  
  Options:
    --db-host TEXT      DB host
    --db-port INTEGER   DB port
    --db-database TEXT  DB name
    --db-user TEXT      DB user
    --db-password TEXT  DB password
    -h, --help          Show this message and exit.
  
  Commands:
    bests  Generate bests playlists with some rules
    new    Generate a new playlist


musicbot playlist bests
***********************
.. code-block::

  Usage: musicbot playlist bests [OPTIONS] PATH
  
    Generate bests playlists with some rules
  
  Options:
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    --prefix TEXT           Append prefix before each path (implies relative)
    --suffix TEXT           Append this suffix to playlist name
    -h, --help              Show this message and exit.


musicbot playlist new
*********************
.. code-block::

  Usage: musicbot playlist new [OPTIONS] [PATH]
  
    Generate a new playlist
  
  Options:
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot server
***************
.. code-block::

  Usage: musicbot server [OPTIONS] COMMAND [ARGS]...
  
    API Server
  
  Options:
    --db-host TEXT      DB host
    --db-port INTEGER   DB port
    --db-database TEXT  DB name
    --db-user TEXT      DB user
    --db-password TEXT  DB password
    --dev               Watch for source file modification
    --watcher           Watch for music file modification
    --autoscan          Enable auto scan background job
    --server-cache      Activate server cache system
    --client-cache      Activate client cache system
    -h, --help          Show this message and exit.
  
  Commands:
    start  Start musicbot web API


musicbot server start
*********************
.. code-block::

  Usage: musicbot server start [OPTIONS]
  
    Start musicbot web API
  
  Options:
    --http-host TEXT        Host interface to listen on
    --http-port INTEGER     HTTP port to listen on
    --http-workers INTEGER  Number of HTTP workers (not tested)
    --http-user TEXT        HTTP Basic auth user
    --http-password TEXT    HTTP Basic auth password
    -h, --help              Show this message and exit.


musicbot stats
**************
.. code-block::

  Usage: musicbot stats [OPTIONS] COMMAND [ARGS]...
  
    Generate some stats for music collection with filters
  
  Options:
    --db-host TEXT          DB host
    --db-port INTEGER       DB port
    --db-database TEXT      DB name
    --db-user TEXT          DB user
    --db-password TEXT      DB password
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot tag
************
.. code-block::

  Usage: musicbot tag [OPTIONS] COMMAND [ARGS]...
  
    Music tags management
  
  Options:
    --db-host TEXT          DB host
    --db-port INTEGER       DB port
    --db-database TEXT      DB name
    --db-user TEXT          DB user
    --db-password TEXT      DB password
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.
  
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
    -h, --help  Show this message and exit.


musicbot tag delete
*******************
.. code-block::

  Usage: musicbot tag delete [OPTIONS]
  
    Delete tags - Not implemented
  
  Options:
    -h, --help  Show this message and exit.


musicbot tag show
*****************
.. code-block::

  Usage: musicbot tag show [OPTIONS]
  
    Show tags of musics with filters
  
  Options:
    --fields TEXT  Show only those fields
    -h, --help     Show this message and exit.


musicbot task
*************
.. code-block::

  Usage: musicbot task [OPTIONS] COMMAND [ARGS]...
  
    Task management
  
  Options:
    --db-host TEXT      DB host
    --db-port INTEGER   DB port
    --db-database TEXT  DB name
    --db-user TEXT      DB user
    --db-password TEXT  DB password
    -h, --help          Show this message and exit.
  
  Commands:
    list  List tasks in database
    new   Add a new task in database


musicbot task list
******************
.. code-block::

  Usage: musicbot task list [OPTIONS]
  
    List tasks in database
  
  Options:
    -h, --help  Show this message and exit.


musicbot task new
*****************
.. code-block::

  Usage: musicbot task new [OPTIONS] NAME
  
    Add a new task in database
  
  Options:
    -h, --help  Show this message and exit.


musicbot youtube
****************
.. code-block::

  Usage: musicbot youtube [OPTIONS] COMMAND [ARGS]...
  
    Youtube management
  
  Options:
    --db-host TEXT          DB host
    --db-port INTEGER       DB port
    --db-database TEXT      DB name
    --db-user TEXT          DB user
    --db-password TEXT      DB password
    --limit INTEGER         Fetch a maximum limit of music
    --youtube TEXT          Select musics with a youtube link
    --formats TEXT          Select musics with file format
    --no-formats TEXT       Filter musics without format
    --keywords TEXT         Select musics with keywords
    --no-keywords TEXT      Filter musics without keywords
    --artists TEXT          Select musics with artists
    --no-artists TEXT       Filter musics without artists
    --albums TEXT           Select musics with albums
    --no-albums TEXT        Filter musics without albums
    --titles TEXT           Select musics with titles
    --no-titles TEXT        Filter musics without titless
    --genres TEXT           Select musics with genres
    --no-genres TEXT        Filter musics without genres
    --min-duration INTEGER  Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER  Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER      Minimum file size filter (in bytes)
    --max-size INTEGER      Maximum file size filter (in bytes)
    --min-rating FLOAT      Minimum rating
    --max-rating FLOAT      Maximum rating
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    --concurrency INTEGER   Number of coroutines
    -h, --help              Show this message and exit.
  
  Commands:
    albums  Fetch youtube links for each album
    musics  Fetch youtube links for each music


musicbot youtube albums
***********************
.. code-block::

  Usage: musicbot youtube albums [OPTIONS]
  
    Fetch youtube links for each album
  
  Options:
    --youtube-album TEXT  Select albums with a youtube link
    -h, --help            Show this message and exit.


musicbot youtube musics
***********************
.. code-block::

  Usage: musicbot youtube musics [OPTIONS]
  
    Fetch youtube links for each music
  
  Options:
    -h, --help  Show this message and exit.


