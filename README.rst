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
docker run -it -v /home/crunch/projects/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli user create -e test@test.com -p password --first-name Test --last-name Me --graphql http://postgraphile_public:5000/graphql
docker run -it -v ~/projects/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli folder -e test@test.com -p password --graphql http://postgraphile_public:5000/graphql scan /tests/fixtures/folder1 /tests/fixtures/folder2
docker run -it -v /home/crunch/projects/musicbot/tests:/tests --network container:musicbot_db_1 musicbot_cli db cli --db postgresql://postgres:musicbot@db:5432/musicbot

Linting
------------

.. code-block:: bash

poetry run pylint -d line-too-long,too-many-arguments,protected-access,missing-docstring,invalid-name,too-many-public-methods,too-many-instance-attributes,duplicate-code,too-many-nested-blocks,too-many-branches,too-many-return-statements,too-many-statements,too-many-locals,too-few-public-methods,too-many-ancestors,abstract-method,anomalous-backslash-in-string,import-outside-toplevel,redefined-outer-name,unnecessary-lambda,c-extension-no-member musicbot tests

Documentation
------------

.. code-block:: bash

poetry build
pip3 install -U dist/musicbot-0.1.0-py3-none-any.whl
doc/gen.sh
Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...
  
    Music swiss knife, new gen.
  
  Options:
    -V, --version                                       Show the version and exit.
    -l, --log PATH                                      Log file path  [default: ~/musicbot.log]
    -i, --info                                          Same as --verbosity info"
    -d, --debug                                         Be very verbose, same as --verbosity debug + hide progress bars  [default: False]
    -t, --timings                                       Set verbosity to info and show execution timings  [default: False]
    -v, --verbosity [debug|info|warning|error|critical]
                                                        Verbosity levels  [default: warning]
    --dry                                               Take no real action  [default: False]
    -q, --quiet                                         Disable progress bars  [default: False]
    --colors / --no-colors                              Disable colorized output  [default: True]
    -h, --help                                          Show this message and exit.
  
  Commands:
    artist        Artist management
    config        Config management
    db            Database management (admin)
    filter        Filter management
    fingerprint   Fingerprint tool
    folder        Folder management
    genre         Genre management
    help          Print help
    play          Music player
    playlist      Playlist management
    postgraphile  Postgraphile management
    spotify       Spotify
    stats         Stats on your music
    user          User management
    version       Print version
    youtube       Youtube tool


musicbot artist
***************
.. code-block::

  Usage: musicbot artist [OPTIONS] COMMAND [ARGS]...
  
    Artist management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
  Commands:
    help  Print help
    list  List artists


musicbot artist help
********************
.. code-block::

  Usage: musicbot artist help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot artist list
********************
.. code-block::

  Usage: musicbot artist list [OPTIONS]
  
    List artists
  
  Options:
    -h, --help  Show this message and exit.


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
    clear (recreate)  Drop and recreate database and schema
    cli               Start PgCLI util
    create            Create database and load schema
    drop              Drop database
    help              Print help


musicbot db clear
*****************
.. code-block::

  Usage: musicbot db clear [OPTIONS]
  
    Drop and recreate database and schema
  
  Options:
    --db TEXT   DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    -y, --yes   Are you sure you want to drop and recreate db?
    -h, --help  Show this message and exit.


musicbot db cli
***************
.. code-block::

  Usage: musicbot db cli [OPTIONS] [PGCLI_ARGS]...
  
    Start PgCLI util
  
  Options:
    --db TEXT   DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    -h, --help  Show this message and exit.


musicbot db create
******************
.. code-block::

  Usage: musicbot db create [OPTIONS]
  
    Create database and load schema
  
  Options:
    --db TEXT   DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    -h, --help  Show this message and exit.


musicbot db drop
****************
.. code-block::

  Usage: musicbot db drop [OPTIONS]
  
    Drop database
  
  Options:
    --db TEXT   DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    -y, --yes   Are you sure you want to drop the DB ?
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


musicbot fingerprint
********************
.. code-block::

  Usage: musicbot fingerprint [OPTIONS] COMMAND [ARGS]...
  
    Fingerprint tool
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    help    Print help
    search  Find music with fingerprint


musicbot fingerprint help
*************************
.. code-block::

  Usage: musicbot fingerprint help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot fingerprint search
***************************
.. code-block::

  Usage: musicbot fingerprint search [OPTIONS] PATH
  
    Find music with fingerprint
  
  Options:
    --acoustid-apikey TEXT  AcoustID API Key
    -h, --help              Show this message and exit.


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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


musicbot genre
**************
.. code-block::

  Usage: musicbot genre [OPTIONS] COMMAND [ARGS]...
  
    Genre management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
    -h, --help           Show this message and exit.
  
  Commands:
    help  Print help
    list  List genres


musicbot genre help
*******************
.. code-block::

  Usage: musicbot genre help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot genre list
*******************
.. code-block::

  Usage: musicbot genre list [OPTIONS]
  
    List genres
  
  Options:
    -h, --help  Show this message and exit.


musicbot help
*************
.. code-block::

  Usage: musicbot help [OPTIONS] [COMMAND]...
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot play
*************
.. code-block::

  Usage: musicbot play [OPTIONS] COMMAND [ARGS]...
  
  Options:
    -e, --email TEXT        User email
    -p, --password TEXT     User password
    --token TEXT            User token
    --graphql TEXT          GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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


musicbot playlist
*****************
.. code-block::

  Usage: musicbot playlist [OPTIONS] COMMAND [ARGS]...
  
    Playlist management
  
  Options:
    -e, --email TEXT     User email
    -p, --password TEXT  User password
    --token TEXT         User token
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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
    --db TEXT                         DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    --graphql-private-port INTEGER    Postgraphile private API port  [default: 5001]
    --graphql-private-interface TEXT  Postgraphile private API interface  [default: localhost]
    --background                      Run in background  [default: False]
    -h, --help                        Show this message and exit.


musicbot postgraphile public
****************************
.. code-block::

  Usage: musicbot postgraphile public [OPTIONS] JWT_SECRET
  
    Start public backend
  
  Options:
    --db TEXT                        DB dsn string  [default: postgresql://postgres:musicbot@localhost:5432/musicbot_prod]
    --graphql-public-port INTEGER    Postgraphile public API port  [default: 5000]
    --graphql-public-interface TEXT  Postgraphile public API interface  [default: localhost]
    --background                     Run in background  [default: False]
    -h, --help                       Show this message and exit.


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
    --graphql TEXT       GraphQL endpoint  [default: http://127.0.0.1:5000/graphql]
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
    --token TEXT         User token
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
    --token TEXT         User token
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


