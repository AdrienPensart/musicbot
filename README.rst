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

It uses poetry tool to manage project life.

Installation
------------

.. code-block:: bash

  sudo apt install build-essential libssl-dev libtag1-dev ffmpeg postgresql-11 libpcre3-dev postgresql-server-dev-all
  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3
  poetry install

  systemctl status postgresql
  sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'musicbot';" && history -c
  poetry run pgcli postgresql://postgres:musicbot@localhost:5432

  git clone https://github.com/nginx/nginx.git
  git clone https://github.com/evanmiller/mod_zip.git
  auto/configure --prefix=/opt/nginx --add-module="$HOME/mod_zip"
  sudo make install
  sudo ln -s /home/crunch/musicbot/scripts/musicbot.service /etc/systemd/system/musicbot.service
  sudo ln -s /home/crunch/musicbot/scripts/nginx.service /etc/systemd/system/nginx.service
  sudo ln -s /home/crunch/musicbot/scripts/nginx.conf /opt/nginx/conf/nginx.conf
  sudo ln -s /opt/nginx/sbin/nginx /usr/sbin/nginx

  git clone https://github.com/michelp/pgjwt.git
  cd pgjwt
  sudo make install

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload

  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
  nvm install node
  npm install -g postgraphile
Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...
  
    Music swiss knife, new gen.
  
  Options:
    --version                       Show the version and exit.
    --log PATH                      Log file path  [default:
                                    /var/log/musicbot.log]
    --debug                         Be very verbose, same as --verbosity debug +
                                    hide progress bars
    --timings                       Set verbosity to info and show execution
                                    timings
    --verbosity [debug|info|warning|error|critical]
                                    Verbosity levels  [default: warning]
    --dry                           Take no real action
    --quiet                         Disable progress bars
    --no-colors                     Disable colorized output
    -h, --help                      Show this message and exit.
  
  Commands:
    completion   Completion tool
    config       Config management
    consistency  Inconsistencies management
    db           Database management
    file         Music tags management
    filter       Filter management
    folder       Folder management
    help         Print help
    playlist     Playlist management
    repl         Start an interactive shell.
    server       API Server
    spotify      Spotify
    stats        Youtube management
    tag          Music tags management
    user         User management
    youtube      Youtube management


musicbot completion
*******************
.. code-block::

  Usage: musicbot completion [OPTIONS] COMMAND [ARGS]...
  
    Completion tool
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help     Print help
    install  Install the click-completion-command completion
    show     Show the click-completion-command completion code


musicbot completion help
************************
.. code-block::

  Usage: musicbot completion help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot completion install
***************************
.. code-block::

  Usage: musicbot completion install [OPTIONS] [[bash|fish|zsh|powershell]]
                                     [PATH]
  
    Install the click-completion-command completion
  
  Options:
    --append / --overwrite          Append the completion code to the file
    -i, --case-insensitive / --no-case-insensitive
                                    Case insensitive completion
    -h, --help                      Show this message and exit.


musicbot completion show
************************
.. code-block::

  Usage: musicbot completion show [OPTIONS] [[bash|fish|zsh|powershell]]
  
    Show the click-completion-command completion code
  
  Options:
    -i, --case-insensitive / --no-case-insensitive
                                    Case insensitive completion
    -h, --help                      Show this message and exit.


musicbot config
***************
.. code-block::

  Usage: musicbot config [OPTIONS] COMMAND [ARGS]...
  
    Config management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help     Print help
    logging  Show loggers tree
    show     Print default config


musicbot config help
********************
.. code-block::

  Usage: musicbot config help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot config logging
***********************
.. code-block::

  Usage: musicbot config logging [OPTIONS]
  
    Show loggers tree
  
  Options:
    -h, --help  Show this message and exit.


musicbot config show
********************
.. code-block::

  Usage: musicbot config show [OPTIONS]
  
    Print default config
  
  Options:
    -h, --help  Show this message and exit.


musicbot consistency
********************
.. code-block::

  Usage: musicbot consistency [OPTIONS] COMMAND [ARGS]...
  
    Inconsistencies management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    errors  Detect errors
    help    Print help


musicbot consistency errors
***************************
.. code-block::

  Usage: musicbot consistency errors [OPTIONS]
  
    Detect errors
  
  Options:
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


musicbot consistency help
*************************
.. code-block::

  Usage: musicbot consistency help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot db
***********
.. code-block::

  Usage: musicbot db [OPTIONS] COMMAND [ARGS]...
  
    Database management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    clean   Clean deleted musics from database
    clear   Drop and recreate database and schema
    cli     Start PgCLI util
    create  Create database and load schema
    drop    Drop database schema
    empty   Empty databases
    help    Print help
    stats   Get stats about database


musicbot db clean
*****************
.. code-block::

  Usage: musicbot db clean [OPTIONS]
  
    Clean deleted musics from database
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.


musicbot db clear
*****************
.. code-block::

  Usage: musicbot db clear [OPTIONS]
  
    Drop and recreate database and schema
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    --yes             Are you sure you want to drop the db?
    -h, --help        Show this message and exit.


musicbot db cli
***************
.. code-block::

  Usage: musicbot db cli [OPTIONS]
  
    Start PgCLI util
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.


musicbot db create
******************
.. code-block::

  Usage: musicbot db create [OPTIONS]
  
    Create database and load schema
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.


musicbot db drop
****************
.. code-block::

  Usage: musicbot db drop [OPTIONS]
  
    Drop database schema
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    --yes             Are you sure you want to drop the DB ?
    -h, --help        Show this message and exit.


musicbot db empty
*****************
.. code-block::

  Usage: musicbot db empty [OPTIONS]
  
    Empty databases
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    --yes             Are you sure you want to drop all objects in DB ?
    -h, --help        Show this message and exit.


musicbot db help
****************
.. code-block::

  Usage: musicbot db help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot db stats
*****************
.. code-block::

  Usage: musicbot db stats [OPTIONS]
  
    Get stats about database
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.


musicbot file
*************
.. code-block::

  Usage: musicbot file [OPTIONS] COMMAND [ARGS]...
  
    Music tags management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    help    Print help
    show    Show tags of musics with filters
    update


musicbot file help
******************
.. code-block::

  Usage: musicbot file help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot file show
******************
.. code-block::

  Usage: musicbot file show [OPTIONS]
  
    Show tags of musics with filters
  
  Options:
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


musicbot file update
********************
.. code-block::

  Usage: musicbot file update [OPTIONS]
  
  Options:
    --keywords TEXT         Keywords
    --artist TEXT           Artist
    --album TEXT            Album
    --title TEXT            Title
    --genre TEXT            Genre
    --number TEXT           Track number
    --rating TEXT           Rating
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


musicbot filter
***************
.. code-block::

  Usage: musicbot filter [OPTIONS] COMMAND [ARGS]...
  
    Filter management
  
  Options:
    --email TEXT     User email
    --password TEXT  User password
    --token TEXT     User token
    --graphql TEXT   GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help       Show this message and exit.
  
  Commands:
    do
    help          Print help
    list
    load-default


musicbot filter do
******************
.. code-block::

  Usage: musicbot filter do [OPTIONS]
  
  Options:
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


musicbot filter help
********************
.. code-block::

  Usage: musicbot filter help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot filter list
********************
.. code-block::

  Usage: musicbot filter list [OPTIONS]
  
  Options:
    -h, --help  Show this message and exit.


musicbot filter load-default
****************************
.. code-block::

  Usage: musicbot filter load-default [OPTIONS]
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder management
  
  Options:
    --email TEXT     User email
    --password TEXT  User password
    --token TEXT     User token
    --graphql TEXT   GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help       Show this message and exit.
  
  Commands:
    find      Only list files in selected folders
    flac2mp3  Convert all files in folders to mp3
    help      Print help
    list      List folders
    scan      (re)Load musics
    watch     Watch files changes in folders


musicbot folder find
********************
.. code-block::

  Usage: musicbot folder find [OPTIONS] [FOLDERS]...
  
    Only list files in selected folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder flac2mp3
************************
.. code-block::

  Usage: musicbot folder flac2mp3 [OPTIONS] [FOLDERS]...
  
    Convert all files in folders to mp3
  
  Options:
    --concurrency INTEGER  Number of coroutines  [default: 8]
    -h, --help             Show this message and exit.


musicbot folder help
********************
.. code-block::

  Usage: musicbot folder help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder list
********************
.. code-block::

  Usage: musicbot folder list [OPTIONS]
  
    List folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder scan
********************
.. code-block::

  Usage: musicbot folder scan [OPTIONS] [FOLDERS]...
  
    (re)Load musics
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder watch
*********************
.. code-block::

  Usage: musicbot folder watch [OPTIONS]
  
    Watch files changes in folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot help
*************
.. code-block::

  Usage: musicbot help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot playlist
*****************
.. code-block::

  Usage: musicbot playlist [OPTIONS] COMMAND [ARGS]...
  
    Playlist management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    bests  Generate bests playlists with some rules
    help   Print help
    new    Generate a new playlist


musicbot playlist bests
***********************
.. code-block::

  Usage: musicbot playlist bests [OPTIONS] PATH
  
    Generate bests playlists with some rules
  
  Options:
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


musicbot playlist help
**********************
.. code-block::

  Usage: musicbot playlist help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot playlist new
*********************
.. code-block::

  Usage: musicbot playlist new [OPTIONS] [PATH]
  
    Generate a new playlist
  
  Options:
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


musicbot repl
*************
.. code-block::

  Usage: musicbot repl [OPTIONS]
  
    Start an interactive shell. All subcommands are available in it.
  
    :param old_ctx: The current Click context. :param prompt_kwargs:
    Parameters passed to     :py:func:`prompt_toolkit.shortcuts.prompt`.
  
    If stdin is not a TTY, no prompt will be printed, but only commands read
    from stdin.
  
  Options:
    -h, --help  Show this message and exit.


musicbot server
***************
.. code-block::

  Usage: musicbot server [OPTIONS] COMMAND [ARGS]...
  
    API Server
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    help   Print help
    start  Start musicbot web API


musicbot server help
********************
.. code-block::

  Usage: musicbot server help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot server start
*********************
.. code-block::

  Usage: musicbot server start [OPTIONS]
  
    Start musicbot web API
  
  Options:
    --http-host TEXT        Host interface to listen on  [default: 127.0.0.1]
    --http-server TEXT      Server name to use in links  [default: musicbot.ovh]
    --http-port INTEGER     HTTP port to listen on  [default: 8000]
    --http-workers INTEGER  Number of HTTP workers (not tested)  [default: 1]
    --http-user TEXT        HTTP Basic auth user  [default: musicbot]
    --http-password TEXT    HTTP Basic auth password
    --dev                   Watch for source file modification
    --watcher               Watch for music file modification
    --autoscan              Enable auto scan background job
    --server-cache          Activate server cache system
    --client-cache          Activate client cache system
    --no-auth               Disable authentication system
    -h, --help              Show this message and exit.


musicbot spotify
****************
.. code-block::

  Usage: musicbot spotify [OPTIONS] COMMAND [ARGS]...
  
    Spotify
  
  Options:
    --client-id TEXT      Spotify client ID
    --client-secret TEXT  Spotify client secret
    --token TEXT          Spotify token
    -h, --help            Show this message and exit.
  
  Commands:
    help   Print help
    track  Search track


musicbot spotify help
*********************
.. code-block::

  Usage: musicbot spotify help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot spotify track
**********************
.. code-block::

  Usage: musicbot spotify track [OPTIONS] ARTIST TITLE
  
    Search track
  
  Options:
    -h, --help  Show this message and exit.


musicbot stats
**************
.. code-block::

  Usage: musicbot stats [OPTIONS] COMMAND [ARGS]...
  
    Youtube management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    help  Print help
    show  Generate some stats for music collection with filters


musicbot stats help
*******************
.. code-block::

  Usage: musicbot stats help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot stats show
*******************
.. code-block::

  Usage: musicbot stats show [OPTIONS]
  
    Generate some stats for music collection with filters
  
  Options:
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


musicbot tag
************
.. code-block::

  Usage: musicbot tag [OPTIONS] COMMAND [ARGS]...
  
    Music tags management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    help  Print help
    show  Show tags of musics with filters


musicbot tag help
*****************
.. code-block::

  Usage: musicbot tag help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot tag show
*****************
.. code-block::

  Usage: musicbot tag show [OPTIONS]
  
    Show tags of musics with filters
  
  Options:
    --fields TEXT           Show only those fields
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


musicbot user
*************
.. code-block::

  Usage: musicbot user [OPTIONS] COMMAND [ARGS]...
  
    User management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help        Print help
    list        List users (admin)
    login       Authenticate user
    new         Register a new user
    unregister  Remove a user


musicbot user help
******************
.. code-block::

  Usage: musicbot user help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot user list
******************
.. code-block::

  Usage: musicbot user list [OPTIONS]
  
    List users (admin)
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.


musicbot user login
*******************
.. code-block::

  Usage: musicbot user login [OPTIONS]
  
    Authenticate user
  
  Options:
    --email TEXT     User email
    --password TEXT  User password
    --token TEXT     User token
    --graphql TEXT   GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help       Show this message and exit.


musicbot user new
*****************
.. code-block::

  Usage: musicbot user new [OPTIONS]
  
    Register a new user
  
  Options:
    --email TEXT       User email
    --password TEXT    User password
    --first-name TEXT  User first name
    --last-name TEXT   User last name
    --graphql TEXT     GraphQL endpoint  [default:
                       http://127.0.0.1:5000/graphql]
    -h, --help         Show this message and exit.


musicbot user unregister
************************
.. code-block::

  Usage: musicbot user unregister [OPTIONS]
  
    Remove a user
  
  Options:
    --email TEXT     User email
    --password TEXT  User password
    --token TEXT     User token
    --graphql TEXT   GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help       Show this message and exit.


musicbot youtube
****************
.. code-block::

  Usage: musicbot youtube [OPTIONS] COMMAND [ARGS]...
  
    Youtube management
  
  Options:
    --db TEXT         DB dsn string  [default: postgresql://postgres:musicbot@lo
                      calhost:5432/musicbot_prod]
    --db-max INTEGER  DB maximum number of connections  [default: 32]
    --db-single       DB will use only one connection  [default: False]
    --db-cert TEXT    DB SSL certificate  [default: ~/.postgresql/root.crt]
    -h, --help        Show this message and exit.
  
  Commands:
    help    Print help
    musics  Fetch youtube links for each music


musicbot youtube help
*********************
.. code-block::

  Usage: musicbot youtube help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot youtube musics
***********************
.. code-block::

  Usage: musicbot youtube musics [OPTIONS]
  
    Fetch youtube links for each music
  
  Options:
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
    --concurrency INTEGER   Number of coroutines  [default: 8]
    -h, --help              Show this message and exit.


