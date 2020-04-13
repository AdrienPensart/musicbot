========
MusicBot
========
+---------------+-----------------+
|     Tools     |      Result     |
+===============+=================+
|     Codacy    |    |codacy|     |
+---------------+-----------------+
|     Coverage  |   |coverage|    |
+---------------+-----------------+

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/621acf3309b24c538c40824f9af467de
   :target: https://www.codacy.com/app/AdrienPensart/musicbot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=AdrienPensart/musicbot&amp;utm_campaign=Badge_Grade
   :alt: Codacy badge
.. |coverage| image:: https://github.com/AdrienPensart/musicbot/blob/master/doc/coverage.svg
   :alt: Coverage badge

Description
-----------
CLI / API / Website to manipulate music and create smart playlists, and play it !

It uses poetry and pyenv tools to manage project life and docker to test it.

Under the hood, there is a postgraphile API frontend backed by a postgresql database, it allow us
to have users and security integrated.

Dev Environment
---------------

.. code-block:: bash

  sudo apt install -y vlc libtag1-dev postgresql-server-dev-all ffmpeg python3-pip docker.io libchromaprint-tools libbz2-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev tk-dev liblzma-dev libssl-dev libreadline-dev
  sudo usermod -aG docker $(whoami)

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  https://pyenv.run | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)

  # you should put that at your shell startup
  eval "$(pyenv init -)"

  python <(curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py)
  poetry install

Testing
------------

.. code-block:: bash

  poetry run pytest
  poetry run coverage-badge -f -o doc/coverage.svg

How to use
------------

.. code-block:: bash

  poetry run docker-compose build --parallel
  poetry run docker-compose up
  musicbot user create --email your_email --password your_password --save
  musicbot local scan /tests/fixtures/folder1 /tests/fixtures/folder2
  musicbot local tracks

Linting
------------

.. code-block:: bash

  poetry run pylint musicbot tests

Documentation
-------------

.. code-block:: bash

  poetry run rstcheck doc/help.rst
  poetry run doc/gen.sh
  poetry run rstcheck README.rst

Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...
  
    Music swiss knife, new gen.
  
  Options:
    -V, --version                                       Show the version and exit.
    -c, --config PATH                                   Config file path  [default: ~/musicbot.ini]
    -l, --log PATH                                      Log file path
    -i, --info                                          Same as "--verbosity info"
    -d, --debug                                         Be very verbose, same as "--verbosity debug" + hide progress bars  [default: False]
    -t, --timings                                       Set verbosity to info and show execution timings  [default: False]
    -v, --verbosity [debug|info|warning|error|critical]
                                                        Verbosity levels  [default: warning]
    -q, --quiet                                         Disable progress bars  [default: False]
    -h, --help                                          Show this message and exit.
  
  Commands:
    completion  Shell completion
    folder      Manage folders
    help        Print help
    local       Local music management
    music       Music file
    spotify     Spotify tool
    user        User management
    version     Print version
    youtube     Youtube tool


musicbot completion
*******************
.. code-block::

  Usage: musicbot completion [OPTIONS] COMMAND [ARGS]...
  
    Shell completion
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help     Print help
    install  Install the click-completion-command completion
    show     Show the click-completion-command completion code


musicbot completion install
***************************
.. code-block::

  Usage: musicbot completion install [OPTIONS] [[bash|fish|zsh|powershell]] [PATH]
  
    Install the click-completion-command completion
  
  Options:
    --append / --overwrite                          Append the completion code to the file
    -i, --case-insensitive / --no-case-insensitive  Case insensitive completion
    -h, --help                                      Show this message and exit.


musicbot completion show
************************
.. code-block::

  Usage: musicbot completion show [OPTIONS] [[bash|fish|zsh|powershell]]
  
    Show the click-completion-command completion code
  
  Options:
    -i, --case-insensitive / --no-case-insensitive  Case insensitive completion
    -h, --help                                      Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Manage folders
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    flac2mp3  Convert all files in folders to mp3
    help      Print help
    tracks    List tracks


musicbot folder flac2mp3
************************
.. code-block::

  Usage: musicbot folder flac2mp3 [OPTIONS] [FOLDERS]...
  
    Convert all files in folders to mp3
  
  Options:
    --concurrency INTEGER  Number of coroutines  [default: 8]
    --dry                  Take no real action  [default: False]
    -h, --help             Show this message and exit.


musicbot folder tracks
**********************
.. code-block::

  Usage: musicbot folder tracks [OPTIONS] [FOLDERS]...
  
    List tracks
  
  Options:
    --output [table|json]  Output format  [default: table]
    -h, --help             Show this message and exit.


musicbot help
*************
.. code-block::

  Usage: musicbot help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot local
**************
.. code-block::

  Usage: musicbot local [OPTIONS] COMMAND [ARGS]...
  
    Local music management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    bests          Generate bests playlists with some rules
    clean          Clean all musics
    consistency    Check music files consistency
    execute        Raw query
    filter         Print a filter
    filters        List filters
    find           Just list music files
    folders        List folders
    help           Print help
    load-filters   Load default filters
    player (play)  Music player
    playlist       Generate a new playlist
    scan           (re)Load musics
    stats          Generate some stats for music collection with filters
    sync           Copy selected musics with filters to destination folder
    watch          Watch files changes in folders


musicbot local bests
********************
.. code-block::

  Usage: musicbot local bests [OPTIONS] PATH
  
    Generate bests playlists with some rules
  
  Options:
    -e, --email TEXT        User email
    -p, --password TEXT     User password
    --graphql TEXT          GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT        User token
    --dry                   Take no real action  [default: False]
    --name TEXT             Filter name
    --limit INTEGER         Fetch a maximum limit of music
    --youtubes TEXT         Select musics with a youtube link
    --no-youtubes TEXT      Select musics without youtube link
    --spotifys TEXT         Select musics with a spotifys link
    --no-spotifys TEXT      Select musics without spotifys link
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    --prefix TEXT           Append prefix before each path (implies relative)
    --suffix TEXT           Append this suffix to playlist name
    -h, --help              Show this message and exit.


musicbot local clean
********************
.. code-block::

  Usage: musicbot local clean [OPTIONS]
  
    Clean all musics
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local consistency
**************************
.. code-block::

  Usage: musicbot local consistency [OPTIONS] [FOLDERS]...
  
    Check music files consistency
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local execute
**********************
.. code-block::

  Usage: musicbot local execute [OPTIONS] QUERY
  
    Raw query
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local filter
*********************
.. code-block::

  Usage: musicbot local filter [OPTIONS] NAME
  
    Print a filter
  
  Options:
    -e, --email TEXT       User email
    -p, --password TEXT    User password
    --graphql TEXT         GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT       User token
    --output [table|json]  Output format  [default: table]
    -h, --help             Show this message and exit.


musicbot local filters
**********************
.. code-block::

  Usage: musicbot local filters [OPTIONS]
  
    List filters
  
  Options:
    -e, --email TEXT       User email
    -p, --password TEXT    User password
    --graphql TEXT         GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT       User token
    --output [table|json]  Output format  [default: table]
    -h, --help             Show this message and exit.


musicbot local find
*******************
.. code-block::

  Usage: musicbot local find [OPTIONS] [FOLDERS]...
  
    Just list music files
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local folders
**********************
.. code-block::

  Usage: musicbot local folders [OPTIONS]
  
    List folders
  
  Options:
    -e, --email TEXT       User email
    -p, --password TEXT    User password
    --graphql TEXT         GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT       User token
    --output [table|json]  Output format  [default: table]
    -h, --help             Show this message and exit.


musicbot local load-filters
***************************
.. code-block::

  Usage: musicbot local load-filters [OPTIONS]
  
    Load default filters
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local player
*********************
.. code-block::

  Usage: musicbot local player [OPTIONS]
  
    Music player
  
  Options:
    -e, --email TEXT        User email
    -p, --password TEXT     User password
    --graphql TEXT          GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT        User token
    --name TEXT             Filter name
    --limit INTEGER         Fetch a maximum limit of music
    --youtubes TEXT         Select musics with a youtube link
    --no-youtubes TEXT      Select musics without youtube link
    --spotifys TEXT         Select musics with a spotifys link
    --no-spotifys TEXT      Select musics without spotifys link
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot local playlist
***********************
.. code-block::

  Usage: musicbot local playlist [OPTIONS] [PATH]
  
    Generate a new playlist
  
  Options:
    -e, --email TEXT           User email
    -p, --password TEXT        User password
    --graphql TEXT             GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT           User token
    --dry                      Take no real action  [default: False]
    --name TEXT                Filter name
    --limit INTEGER            Fetch a maximum limit of music
    --youtubes TEXT            Select musics with a youtube link
    --no-youtubes TEXT         Select musics without youtube link
    --spotifys TEXT            Select musics with a spotifys link
    --no-spotifys TEXT         Select musics without spotifys link
    --formats TEXT             Select musics with file format
    --no-formats TEXT          Filter musics without format
    --keywords TEXT            Select musics with keywords
    --no-keywords TEXT         Filter musics without keywords
    --artists TEXT             Select musics with artists
    --no-artists TEXT          Filter musics without artists
    --albums TEXT              Select musics with albums
    --no-albums TEXT           Filter musics without albums
    --titles TEXT              Select musics with titles
    --no-titles TEXT           Filter musics without titless
    --genres TEXT              Select musics with genres
    --no-genres TEXT           Filter musics without genres
    --min-duration INTEGER     Minimum duration filter (hours:minutes:seconds)
    --max-duration INTEGER     Maximum duration filter (hours:minutes:seconds))
    --min-size INTEGER         Minimum file size filter (in bytes)
    --max-size INTEGER         Maximum file size filter (in bytes)
    --min-rating FLOAT         Minimum rating  [default: 0.0]
    --max-rating FLOAT         Maximum rating  [default: 5.0]
    --relative                 Generate relatives paths
    --shuffle                  Randomize selection
    --output [json|m3u|table]  Output format  [default: table]
    -h, --help                 Show this message and exit.


musicbot local scan
*******************
.. code-block::

  Usage: musicbot local scan [OPTIONS] [FOLDERS]...
  
    (re)Load musics
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot local stats
********************
.. code-block::

  Usage: musicbot local stats [OPTIONS]
  
    Generate some stats for music collection with filters
  
  Options:
    -e, --email TEXT        User email
    -p, --password TEXT     User password
    --graphql TEXT          GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT        User token
    --output [table|json]   Output format  [default: table]
    --name TEXT             Filter name
    --limit INTEGER         Fetch a maximum limit of music
    --youtubes TEXT         Select musics with a youtube link
    --no-youtubes TEXT      Select musics without youtube link
    --spotifys TEXT         Select musics with a spotifys link
    --no-spotifys TEXT      Select musics without spotifys link
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot local sync
*******************
.. code-block::

  Usage: musicbot local sync [OPTIONS] DESTINATION
  
    Copy selected musics with filters to destination folder
  
  Options:
    -e, --email TEXT        User email
    -p, --password TEXT     User password
    --graphql TEXT          GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT        User token
    --dry                   Take no real action  [default: False]
    --name TEXT             Filter name
    --limit INTEGER         Fetch a maximum limit of music
    --youtubes TEXT         Select musics with a youtube link
    --no-youtubes TEXT      Select musics without youtube link
    --spotifys TEXT         Select musics with a spotifys link
    --no-spotifys TEXT      Select musics without spotifys link
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot local watch
********************
.. code-block::

  Usage: musicbot local watch [OPTIONS]
  
    Watch files changes in folders
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot music
**************
.. code-block::

  Usage: musicbot music [OPTIONS] COMMAND [ARGS]...
  
    Music file
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    fingerprint  Print music fingerprint
    help         Print help


musicbot music fingerprint
**************************
.. code-block::

  Usage: musicbot music fingerprint [OPTIONS] PATH
  
    Print music fingerprint
  
  Options:
    --acoustid-api-key TEXT  AcoustID API Key
    -h, --help               Show this message and exit.


musicbot spotify
****************
.. code-block::

  Usage: musicbot spotify [OPTIONS] COMMAND [ARGS]...
  
    Spotify tool
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    diff       Diff between local and spotify
    help       Print help
    playlist   Show playlist
    playlists  List playlists
    tracks     Show tracks


musicbot spotify diff
*********************
.. code-block::

  Usage: musicbot spotify diff [OPTIONS]
  
    Diff between local and spotify
  
  Options:
    -e, --email TEXT      User email
    -p, --password TEXT   User password
    --graphql TEXT        GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT      User token
    --username TEXT       Spotify username
    --client-id TEXT      Spotify client ID
    --client-secret TEXT  Spotify client secret
    --token TEXT          Spotify token
    --cache-path TEXT     Spotify cache path
    --scopes TEXT         Spotify scopes
    --redirect-uri TEXT   Spotify redirect URI
    -h, --help            Show this message and exit.


musicbot spotify playlist
*************************
.. code-block::

  Usage: musicbot spotify playlist [OPTIONS] NAME
  
    Show playlist
  
  Options:
    --username TEXT       Spotify username
    --client-id TEXT      Spotify client ID
    --client-secret TEXT  Spotify client secret
    --token TEXT          Spotify token
    --cache-path TEXT     Spotify cache path
    --scopes TEXT         Spotify scopes
    --redirect-uri TEXT   Spotify redirect URI
    -h, --help            Show this message and exit.


musicbot spotify playlists
**************************
.. code-block::

  Usage: musicbot spotify playlists [OPTIONS]
  
    List playlists
  
  Options:
    --username TEXT       Spotify username
    --client-id TEXT      Spotify client ID
    --client-secret TEXT  Spotify client secret
    --token TEXT          Spotify token
    --cache-path TEXT     Spotify cache path
    --scopes TEXT         Spotify scopes
    --redirect-uri TEXT   Spotify redirect URI
    -h, --help            Show this message and exit.


musicbot spotify tracks
***********************
.. code-block::

  Usage: musicbot spotify tracks [OPTIONS]
  
    Show tracks
  
  Options:
    --username TEXT        Spotify username
    --client-id TEXT       Spotify client ID
    --client-secret TEXT   Spotify client secret
    --token TEXT           Spotify token
    --cache-path TEXT      Spotify cache path
    --scopes TEXT          Spotify scopes
    --redirect-uri TEXT    Spotify redirect URI
    --output [table|json]  Output format  [default: table]
    -h, --help             Show this message and exit.


musicbot user
*************
.. code-block::

  Usage: musicbot user [OPTIONS] COMMAND [ARGS]...
  
    User management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help                        Print help
    list                        List users (admin)
    login (token)               Authenticate user
    register (add,create,new)   Register a new user
    unregister (delete,remove)  Remove a user


musicbot user list
******************
.. code-block::

  Usage: musicbot user list [OPTIONS]
  
    List users (admin)
  
  Options:
    --output [table|json]  Output format  [default: table]
    --graphql-admin TEXT   GraphQL endpoint  [default: http://127.0.0.1:5001/graphql]
    -h, --help             Show this message and exit.


musicbot user login
*******************
.. code-block::

  Usage: musicbot user login [OPTIONS]
  
    Authenticate user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -s, --save           Save to config file  [default: False]
    -h, --help           Show this message and exit.


musicbot user register
**********************
.. code-block::

  Usage: musicbot user register [OPTIONS]
  
    Register a new user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --first-name TEXT    User first name
    --last-name TEXT     User last name
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -s, --save           Save to config file  [default: False]
    -h, --help           Show this message and exit.


musicbot user unregister
************************
.. code-block::

  Usage: musicbot user unregister [OPTIONS]
  
    Remove a user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -t, --token TEXT     User token
    -h, --help           Show this message and exit.


musicbot version
****************
.. code-block::

  Usage: musicbot version [OPTIONS]
  
    Print version
  
    Equivalent : -V
  
  Options:
    -h, --help  Show this message and exit.


musicbot youtube
****************
.. code-block::

  Usage: musicbot youtube [OPTIONS] COMMAND [ARGS]...
  
    Youtube tool
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    download     Download a youtube link with artist and title
    find         Search a youtube link with artist and title
    fingerprint  Fingerprint a youtube video
    help         Print help
    search       Search a youtube link with artist and title


musicbot youtube download
*************************
.. code-block::

  Usage: musicbot youtube download [OPTIONS] ARTIST TITLE
  
    Download a youtube link with artist and title
  
  Options:
    --path TEXT
    -h, --help   Show this message and exit.


musicbot youtube find
*********************
.. code-block::

  Usage: musicbot youtube find [OPTIONS] PATH
  
    Search a youtube link with artist and title
  
  Options:
    --acoustid-api-key TEXT  AcoustID API Key
    -h, --help               Show this message and exit.


musicbot youtube fingerprint
****************************
.. code-block::

  Usage: musicbot youtube fingerprint [OPTIONS] URL
  
    Fingerprint a youtube video
  
  Options:
    --acoustid-api-key TEXT  AcoustID API Key
    -h, --help               Show this message and exit.


musicbot youtube search
***********************
.. code-block::

  Usage: musicbot youtube search [OPTIONS] ARTIST TITLE
  
    Search a youtube link with artist and title
  
  Options:
    -h, --help  Show this message and exit.


