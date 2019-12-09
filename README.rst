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

  sudo apt install -y build-essential libtag1-dev ffmpeg postgresql-12 libpcre3-dev postgresql-server-dev-all docker.io libchromaprint-tools libbz2-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev tk-dev liblzma-dev libssl-dev libreadline-dev
  sudo usermod -aG docker $USER

  git clone https://github.com/AdrienPensart/musicbot.git
  cd musicbot

  https://pyenv.run | bash
  pyenv install --verbose $(cat .python-version) -ks
  pyenv global $(cat .python-version)
  eval "$(pyenv init -)"

  python <(curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py) --preview
  poetry install

  echo "shared_preload_libraries = 'pg_stat_statements'" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
  echo "pg_stat_statements.track = all" | sudo tee -a /etc/postgresql/12/main/postgresql.conf
  sudo systemctl restart postgresql
  sudo -u postgres psql -d postgres -c "create user postgres with password 'musicbot' superuser;" && history -c
  sudo -u postgres psql -d postgres -c "alter user postgres password 'musicbot';" && history -c
  poetry run pgcli postgresql://postgres:musicbot@localhost:5432

  git clone https://github.com/nginx/nginx.git
  git clone https://github.com/evanmiller/mod_zip.git
  cd nginx
  auto/configure --prefix=/opt/nginx --add-module="$HOME/mod_zip" --with-http_auth_request_module
  sudo make install
  sudo ln -s $HOME/musicbot/scripts/musicbot.service /etc/systemd/system/musicbot.service
  sudo ln -s $HOME/musicbot/scripts/nginx.service /etc/systemd/system/nginx.service
  sudo rm /opt/nginx/conf/nginx.conf
  sudo ln -s $HOME/musicbot/scripts/nginx.conf /opt/nginx/conf/nginx.conf
  sudo ln -s /opt/nginx/sbin/nginx /usr/sbin/nginx

  git clone https://github.com/michelp/pgjwt.git
  cd pgjwt
  sudo make install

  sudo systemctl enable nginx
  sudo systemctl enable musicbot
  sudo systemctl daemon-reload

  # in your user folder
  curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
  nvm install node
  yarn global add @vue/cli
  npm install -g postgraphile graphile-contrib/pg-simplify-inflector postgraphile-plugin-connection-filter

Testing
------------

.. code-block:: bash

poetry run pytest --disable-warnings --cov-report term-missing --durations=0 --cov musicbot -x -n auto tests
poetry run coverage-badge > doc/coverage.svg

Docker
------------

.. code-block:: bash

docker-compose build
docker-compose up
docker run -it -v ~/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli user create -e test@test.com -p password --first-name Test --last-name Me --graphql http://postgraphile_public:5000/graphql
docker run -it -v ~/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli folder -e test@test.com -p password --graphql http://postgraphile_public:5000/graphql scan /tests/fixtures/folder1 /tests/fixtures/folder2
docker run -it -v ~/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli db cli --db postgresql://postgres:musicbot@db:5432/musicbot

Linting
------------

.. code-block:: bash

poetry run pylint musicbot tests

Documentation
------------

.. code-block:: bash

poetry build
poetry run doc/gen.sh
Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...
  
    Music swiss knife, new gen.
  
  Options:
    -V, --version                                       Show the version and exit.
    -c, --config PATH                                   Config file path  [default: ~/musicbot.ini]
    -l, --log PATH                                      Log file path  [default: ~/musicbot.log]
    -i, --info                                          Same as --verbosity info"
    -d, --debug                                         Be very verbose, same as --verbosity debug + hide progress bars  [default: False]
    -t, --timings                                       Set verbosity to info and show execution timings  [default: False]
    -v, --verbosity [debug|info|warning|error|critical]
                                                        Verbosity levels  [default: warning]
    -q, --quiet                                         Disable progress bars  [default: False]
    --colors / --no-colors                              Disable colorized output  [default: True]
    -h, --help                                          Show this message and exit.
  
  Commands:
    config   Config management
    filter   Filter management
    help     Print help
    local    Local music management
    spotify  Spotify
    user     User management
    version  Print version
    youtube  Youtube tool


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


musicbot filter
***************
.. code-block::

  Usage: musicbot filter [OPTIONS] COMMAND [ARGS]...
  
    Filter management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    -t, --token TEXT     User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    -t, --token TEXT     User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
  Commands:
    artists      List artists
    bests        Generate bests playlists with some rules
    consistency  Check music files consistency
    csv          Export music files to csv file
    find         Just list music files
    fingerprint  Find music with fingerprint
    flac2mp3     Convert all files in folders to mp3
    folders      List folders
    help         Print help
    playlist     Generate a new playlist
    scan         (re)Load musics
    stats        Generate some stats for music collection with filters
    sync         Copy selected musics with filters to destination folder
    tracks       List tracks
    watch        Watch files changes in folders


musicbot local artists
**********************
.. code-block::

  Usage: musicbot local artists [OPTIONS]
  
    List artists
  
  Options:
    -h, --help  Show this message and exit.


musicbot local bests
********************
.. code-block::

  Usage: musicbot local bests [OPTIONS] PATH
  
    Generate bests playlists with some rules
  
  Options:
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


musicbot local consistency
**************************
.. code-block::

  Usage: musicbot local consistency [OPTIONS] [FOLDERS]...
  
    Check music files consistency
  
  Options:
    -h, --help  Show this message and exit.


musicbot local csv
******************
.. code-block::

  Usage: musicbot local csv [OPTIONS] [PATH]
  
    Export music files to csv file
  
  Options:
    -h, --help  Show this message and exit.


musicbot local find
*******************
.. code-block::

  Usage: musicbot local find [OPTIONS] [FOLDERS]...
  
    Just list music files
  
  Options:
    -h, --help  Show this message and exit.


musicbot local fingerprint
**************************
.. code-block::

  Usage: musicbot local fingerprint [OPTIONS] PATH
  
    Find music with fingerprint
  
  Options:
    --acoustid-apikey TEXT  AcoustID API Key
    -h, --help              Show this message and exit.


musicbot local flac2mp3
***********************
.. code-block::

  Usage: musicbot local flac2mp3 [OPTIONS] [FOLDERS]...
  
    Convert all files in folders to mp3
  
  Options:
    --concurrency INTEGER  Number of coroutines  [default: 8]
    --dry                  Take no real action  [default: False]
    -h, --help             Show this message and exit.


musicbot local folders
**********************
.. code-block::

  Usage: musicbot local folders [OPTIONS]
  
    List folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot local help
*******************
.. code-block::

  Usage: musicbot local help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot local playlist
***********************
.. code-block::

  Usage: musicbot local playlist [OPTIONS] [PATH]
  
    Generate a new playlist
  
  Options:
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


musicbot local scan
*******************
.. code-block::

  Usage: musicbot local scan [OPTIONS] [FOLDERS]...
  
    (re)Load musics
  
  Options:
    -h, --help  Show this message and exit.


musicbot local stats
********************
.. code-block::

  Usage: musicbot local stats [OPTIONS]
  
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


musicbot local sync
*******************
.. code-block::

  Usage: musicbot local sync [OPTIONS] DESTINATION
  
    Copy selected musics with filters to destination folder
  
  Options:
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


musicbot local tracks
*********************
.. code-block::

  Usage: musicbot local tracks [OPTIONS]
  
    List tracks
  
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


musicbot local watch
********************
.. code-block::

  Usage: musicbot local watch [OPTIONS]
  
    Watch files changes in folders
  
  Options:
    -h, --help  Show this message and exit.


musicbot spotify
****************
.. code-block::

  Usage: musicbot spotify [OPTIONS] COMMAND [ARGS]...
  
    Spotify
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    albums     Show albums
    artists    Show artists
    help       Print help
    playlist   Show playlist
    playlists  List playlists
    search     Search tracks
    token      Get spotify token
    tracks     Show tracks


musicbot spotify albums
***********************
.. code-block::

  Usage: musicbot spotify albums [OPTIONS]
  
    Show albums
  
  Options:
    --spotify-id TEXT             Spotify ID
    --spotify-secret TEXT         Spotify secret
    --spotify-token TEXT          Spotify token
    --spotify-refresh-token TEXT  Spotify refresh token
    -h, --help                    Show this message and exit.


musicbot spotify artists
************************
.. code-block::

  Usage: musicbot spotify artists [OPTIONS]
  
    Show artists
  
  Options:
    --spotify-id TEXT             Spotify ID
    --spotify-secret TEXT         Spotify secret
    --spotify-token TEXT          Spotify token
    --spotify-refresh-token TEXT  Spotify refresh token
    -h, --help                    Show this message and exit.


musicbot spotify help
*********************
.. code-block::

  Usage: musicbot spotify help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot spotify playlist
*************************
.. code-block::

  Usage: musicbot spotify playlist [OPTIONS] NAME
  
    Show playlist
  
  Options:
    --spotify-id TEXT             Spotify ID
    --spotify-secret TEXT         Spotify secret
    --spotify-token TEXT          Spotify token
    --spotify-refresh-token TEXT  Spotify refresh token
    -h, --help                    Show this message and exit.


musicbot spotify playlists
**************************
.. code-block::

  Usage: musicbot spotify playlists [OPTIONS]
  
    List playlists
  
  Options:
    --spotify-id TEXT             Spotify ID
    --spotify-secret TEXT         Spotify secret
    --spotify-token TEXT          Spotify token
    --spotify-refresh-token TEXT  Spotify refresh token
    -h, --help                    Show this message and exit.


musicbot spotify search
***********************
.. code-block::

  Usage: musicbot spotify search [OPTIONS] TRACK
  
    Search tracks
  
  Options:
    --spotify-id TEXT      Spotify ID
    --spotify-secret TEXT  Spotify secret
    -h, --help             Show this message and exit.


musicbot spotify token
**********************
.. code-block::

  Usage: musicbot spotify token [OPTIONS]
  
    Get spotify token
  
  Options:
    --spotify-id TEXT      Spotify ID
    --spotify-secret TEXT  Spotify secret
    -h, --help             Show this message and exit.


musicbot spotify tracks
***********************
.. code-block::

  Usage: musicbot spotify tracks [OPTIONS]
  
    Show tracks
  
  Options:
    --spotify-id TEXT             Spotify ID
    --spotify-secret TEXT         Spotify secret
    --spotify-token TEXT          Spotify token
    --spotify-refresh-token TEXT  Spotify refresh token
    -h, --help                    Show this message and exit.


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
    --graphql-admin TEXT  GraphQL endpoint  [default: http://127.0.0.1:5001/graphql]
    -h, --help            Show this message and exit.


musicbot user login
*******************
.. code-block::

  Usage: musicbot user login [OPTIONS]
  
    Authenticate user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    -t, --token TEXT     User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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
    -h, --help           Show this message and exit.


musicbot user unregister
************************
.. code-block::

  Usage: musicbot user unregister [OPTIONS]
  
    Remove a user
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    -t, --token TEXT     User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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
    find         Search a youtube link with artist and title
    fingerprint  Fingerprint a youtube video
    help         Print help
    search       Search a youtube link with artist and title


musicbot youtube find
*********************
.. code-block::

  Usage: musicbot youtube find [OPTIONS] PATH
  
    Search a youtube link with artist and title
  
  Options:
    --acoustid-apikey TEXT  AcoustID API Key
    -h, --help              Show this message and exit.


musicbot youtube fingerprint
****************************
.. code-block::

  Usage: musicbot youtube fingerprint [OPTIONS] URL
  
    Fingerprint a youtube video
  
  Options:
    --acoustid-apikey TEXT  AcoustID API Key
    -h, --help              Show this message and exit.


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
  
    Search a youtube link with artist and title
  
  Options:
    -h, --help  Show this message and exit.


