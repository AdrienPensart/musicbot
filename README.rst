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

  sudo apt install build-essential libssl-dev libtag1-dev ffmpeg postgresql-11 libpcre3-dev postgresql-server-dev-all docker.io
  sudo usermod -aG docker $USER

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3
  poetry install

  echo "shared_preload_libraries = 'pg_stat_statements'" >> /etc/postgresql/11/main/postgresql.conf
  echo "pg_stat_statements.track = all" >> /etc/postgresql/11/main/postgresql.conf
  systemctl restart postgresql
  sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'musicbot';" && history -c
  poetry run pgcli postgresql://postgres:musicbot@localhost:5432

  git clone https://github.com/nginx/nginx.git
  git clone https://github.com/evanmiller/mod_zip.git
  auto/configure --prefix=/opt/nginx --add-module="$HOME/mod_zip"
  sudo make install
  sudo ln -s $HOME/musicbot/scripts/musicbot.service /etc/systemd/system/musicbot.service
  sudo ln -s $HOME/musicbot/scripts/nginx.service /etc/systemd/system/nginx.service
  sudo ln -s $HOME/musicbot/scripts/nginx.conf /opt/nginx/conf/nginx.conf
  sudo ln -s /opt/nginx/sbin/nginx /usr/sbin/nginx

  git clone https://github.com/michelp/pgjwt.git
  cd pgjwt
  sudo make install

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload

  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
  nvm install node
  curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
  echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
  sudo apt-get update && sudo apt-get install --no-install-recommends yarn
  yarn add postgraphile
  yarn add postgraphile-plugin-connection-filter
Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...
  
    Music swiss knife, new gen.
  
  Options:
    -V, --version                   Show the version and exit.
    -l, --log PATH                  Log file path  [default:
                                    /var/log/musicbot.log]
    -i, --info                      Same as --verbosity info"
    -d, --debug                     Be very verbose, same as --verbosity debug +
                                    hide progress bars  [default: False]
    -t, --timings                   Set verbosity to info and show execution
                                    timings  [default: False]
    -v, --verbosity [debug|info|warning|error|critical]
                                    Verbosity levels  [default: warning]
    --dry                           Take no real action  [default: False]
    -q, --quiet                     Disable progress bars  [default: False]
    --colors / --no-colors          Disable colorized output  [default: True]
    -h, --help                      Show this message and exit.
  
  Commands:
    completion    Completion tool
    config        Config management
    db            Database management (admin)
    filter        Filter management
    folder        Folder management
    help          Print help
    playlist      Playlist management
    postgraphile  Postgraphile management
    repl          Start an interactive shell.
    spotify       Spotify
    stats         Stats on your music
    user          User management
    version       Print version
    youtube       Youtube tool


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


musicbot db
***********
.. code-block::

  Usage: musicbot db [OPTIONS] COMMAND [ARGS]...
  
    Database management (admin)
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    clear   Drop and recreate database and schema
    create  Create database and load schema
    drop    Drop database
    help    Print help


musicbot db clear
*****************
.. code-block::

  Usage: musicbot db clear [OPTIONS]
  
    Drop and recreate database and schema
  
  Options:
    --db TEXT   DB dsn string  [default:
                postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    --yes       Are you sure you want to drop and recreate db?
    -h, --help  Show this message and exit.


musicbot db create
******************
.. code-block::

  Usage: musicbot db create [OPTIONS]
  
    Create database and load schema
  
  Options:
    --db TEXT   DB dsn string  [default:
                postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    -h, --help  Show this message and exit.


musicbot db drop
****************
.. code-block::

  Usage: musicbot db drop [OPTIONS]
  
    Drop database
  
  Options:
    --db TEXT   DB dsn string  [default:
                postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    --yes       Are you sure you want to drop the DB ?
    -h, --help  Show this message and exit.


musicbot db help
****************
.. code-block::

  Usage: musicbot db help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot filter
***************
.. code-block::

  Usage: musicbot filter [OPTIONS] COMMAND [ARGS]...
  
    Filter management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
  Commands:
    do            Filter music
    get           Print a filter
    help          Print help
    list          List filters
    load-default  Load default filters


musicbot filter do
******************
.. code-block::

  Usage: musicbot filter do [OPTIONS]
  
    Filter music
  
  Options:
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


musicbot filter get
*******************
.. code-block::

  Usage: musicbot filter get [OPTIONS] NAME
  
    Print a filter
  
  Options:
    -h, --help  Show this message and exit.


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
  
    List filters
  
  Options:
    -h, --help  Show this message and exit.


musicbot filter load-default
****************************
.. code-block::

  Usage: musicbot filter load-default [OPTIONS]
  
    Load default filters
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
  Commands:
    consistency  Check music files consistency
    csv          Export music files to csv file
    find         Just list music files
    flac2mp3     Convert all files in folders to mp3
    help         Print help
    list         List folders
    scan         (re)Load musics
    sync         Copy selected musics with filters to destination folder
    watch        Watch files changes in folders


musicbot folder consistency
***************************
.. code-block::

  Usage: musicbot folder consistency [OPTIONS] [FOLDERS]...
  
    Check music files consistency
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder csv
*******************
.. code-block::

  Usage: musicbot folder csv [OPTIONS] [PATH]
  
    Export music files to csv file
  
  Options:
    -h, --help  Show this message and exit.


musicbot folder find
********************
.. code-block::

  Usage: musicbot folder find [OPTIONS] [FOLDERS]...
  
    Just list music files
  
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


musicbot folder sync
********************
.. code-block::

  Usage: musicbot folder sync [OPTIONS] DESTINATION
  
    Copy selected musics with filters to destination folder
  
  Options:
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
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
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


musicbot postgraphile
*********************
.. code-block::

  Usage: musicbot postgraphile [OPTIONS] COMMAND [ARGS]...
  
    Postgraphile management
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help     Print help
    private  Start private backend
    public   Start public backend


musicbot postgraphile help
**************************
.. code-block::

  Usage: musicbot postgraphile help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot postgraphile private
*****************************
.. code-block::

  Usage: musicbot postgraphile private [OPTIONS]
  
    Start private backend
  
  Options:
    --db TEXT                       DB dsn string  [default: postgresql://postgr
                                    es:musicbot@localhost:5432/musicbot_prod]
    --graphql-private-port INTEGER  Postgraphile private API port  [default:
                                    5001]
    --graphql-private-interface TEXT
                                    Postgraphile private API interface
                                    [default: localhost]
    --background                    Run in background  [default: False]
    -h, --help                      Show this message and exit.


musicbot postgraphile public
****************************
.. code-block::

  Usage: musicbot postgraphile public [OPTIONS] JWT_SECRET
  
    Start public backend
  
  Options:
    --db TEXT                       DB dsn string  [default: postgresql://postgr
                                    es:musicbot@localhost:5432/musicbot_prod]
    --graphql-public-port INTEGER   Postgraphile public API port  [default:
                                    5000]
    --graphql-public-interface TEXT
                                    Postgraphile public API interface  [default:
                                    localhost]
    --background                    Run in background  [default: False]
    -h, --help                      Show this message and exit.


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
  
    Stats on your music
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
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
    register    Register a new user
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
    --graphql-admin TEXT  GraphQL endpoint  [default:
                          http://127.0.0.1:5001/graphql]
    -h, --help            Show this message and exit.


musicbot user login
*******************
.. code-block::

  Usage: musicbot user login [OPTIONS]
  
    Authenticate user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
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
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.


musicbot user unregister
************************
.. code-block::

  Usage: musicbot user unregister [OPTIONS]
  
    Remove a user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default:
                         http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.


musicbot version
****************
.. code-block::

  Usage: musicbot version [OPTIONS]
  
    Print version
  
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
    help    Print help
    search  Generate some stats for music collection with filters


musicbot youtube help
*********************
.. code-block::

  Usage: musicbot youtube help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot youtube search
***********************
.. code-block::

  Usage: musicbot youtube search [OPTIONS] ARTIST TITLE
  
    Generate some stats for music collection with filters
  
  Options:
    -h, --help  Show this message and exit.


