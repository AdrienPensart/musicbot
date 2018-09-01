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
    folder       Folder scanning
    help         Print help
    playlist     Playlist management
    repl         Start an interactive shell.
    server       API Server
    stats        Youtube management
    tag          Music tags management
    task         Task management
    youtube      Youtube management


musicbot completion
*******************
.. code-block::

  Usage: musicbot completion [OPTIONS] COMMAND [ARGS]...
  
    Completion tool
  
  Options:
    -h, --help  Show this message and exit.
  
  Commands:
    install  Install the click-completion-command...
    show     Show the click-completion-command completion...


musicbot completion install
***************************
.. code-block::

  Usage: musicbot completion install [OPTIONS] [SHELL] [PATH]
  
    Install the click-completion-command completion
  
  Options:
    --append / --overwrite          Append the completion code to the file
    -i, --case-insensitive / --no-case-insensitive
                                    Case insensitive completion
    -h, --help                      Show this message and exit.


musicbot completion show
************************
.. code-block::

  Usage: musicbot completion show [OPTIONS] [SHELL]
  
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
    logging
    save     Save config
    show


musicbot config logging
***********************
.. code-block::

  Usage: musicbot config logging [OPTIONS]
  
  Options:
    -h, --help  Show this message and exit.


musicbot config save
********************
.. code-block::

  Usage: musicbot config save [OPTIONS]
  
    Save config
  
  Options:
    --redis-address TEXT    Redis URI  [default: redis://localhost]
    --redis-db INTEGER      Redis index DB  [default: 0]
    --redis-password TEXT   Redis password
    --db-host TEXT          DB host  [default: localhost]
    --db-port INTEGER       DB port  [default: 5432]
    --db-database TEXT      DB name  [default: musicbot_prod]
    --db-user TEXT          DB user  [default: postgres]
    --db-password TEXT      DB password  [default: musicbot]
    --http-host TEXT        Host interface to listen on  [default: 127.0.0.1]
    --http-server TEXT      Server name to use in links  [default: musicbot.ovh]
    --http-port INTEGER     HTTP port to listen on  [default: 8000]
    --http-workers INTEGER  Number of HTTP workers (not tested)  [default: 1]
    --http-user TEXT        HTTP Basic auth user  [default: musicbot]
    --http-password TEXT    HTTP Basic auth password  [default: musicbot]
    -h, --help              Show this message and exit.


musicbot config show
********************
.. code-block::

  Usage: musicbot config show [OPTIONS]
  
  Options:
    -h, --help  Show this message and exit.


musicbot consistency
********************
.. code-block::

  Usage: musicbot consistency [OPTIONS] COMMAND [ARGS]...
  
    Inconsistencies management
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot db
***********
.. code-block::

  Usage: musicbot db [OPTIONS] COMMAND [ARGS]...
  
    Database management
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    clean    Clean deleted musics from database
    clear    Drop and recreate database and schema
    create   Create database and load schema
    drop     Drop database schema
    refresh  Refresh database materialized views


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


musicbot db refresh
*******************
.. code-block::

  Usage: musicbot db refresh [OPTIONS]
  
    Refresh database materialized views
  
  Options:
    -h, --help  Show this message and exit.


musicbot file
*************
.. code-block::

  Usage: musicbot file [OPTIONS] COMMAND [ARGS]...
  
    Music tags management
  
  Options:
    --db-host TEXT          DB host  [default: localhost]
    --db-port INTEGER       DB port  [default: 5432]
    --db-database TEXT      DB name  [default: musicbot_prod]
    --db-user TEXT          DB user  [default: postgres]
    --db-password TEXT      DB password  [default: musicbot]
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.
  
  Commands:
    show    Show tags of musics with filters
    update


musicbot file show
******************
.. code-block::

  Traceback (most recent call last):
    File "doc/../musicbot", line 78, in <module>
      cli()
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 722, in __call__
      return self.main(*args, **kwargs)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 697, in main
      rv = self.invoke(ctx)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 1066, in invoke
      return _process_result(sub_ctx.command.invoke(sub_ctx))
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 1063, in invoke
      Command.invoke(self, ctx)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 895, in invoke
      return ctx.invoke(self.callback, **ctx.params)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 535, in invoke
      return callback(*args, **kwargs)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/decorators.py", line 17, in new_func
      return f(get_current_context(), *args, **kwargs)
    File "doc/../commands/file.py", line 16, in cli
      ctx.obj.db = collection.Collection(**kwargs)
    File "/home/ubuntu/musicbot/lib/collection.py", line 13, in __init__
      super().__init__(**kwargs)
    File "/home/ubuntu/musicbot/lib/database.py", line 29, in __init__
      self.set(**kwargs)
  TypeError: set() got an unexpected keyword argument 'limit'


musicbot file update
********************
.. code-block::

  Traceback (most recent call last):
    File "doc/../musicbot", line 78, in <module>
      cli()
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 722, in __call__
      return self.main(*args, **kwargs)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 697, in main
      rv = self.invoke(ctx)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 1066, in invoke
      return _process_result(sub_ctx.command.invoke(sub_ctx))
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 1063, in invoke
      Command.invoke(self, ctx)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 895, in invoke
      return ctx.invoke(self.callback, **ctx.params)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/core.py", line 535, in invoke
      return callback(*args, **kwargs)
    File "/home/ubuntu/.pyenv/versions/general/lib/python3.6/site-packages/click/decorators.py", line 17, in new_func
      return f(get_current_context(), *args, **kwargs)
    File "doc/../commands/file.py", line 16, in cli
      ctx.obj.db = collection.Collection(**kwargs)
    File "/home/ubuntu/musicbot/lib/collection.py", line 13, in __init__
      super().__init__(**kwargs)
    File "/home/ubuntu/musicbot/lib/database.py", line 29, in __init__
      self.set(**kwargs)
  TypeError: set() got an unexpected keyword argument 'limit'


musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...
  
    Folder scanning
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    find      Only list files in selected folders
    flac2mp3  Convert all files in folders to mp3
    list      List existing folders
    new       Add a new folder in database
    rescan    Rescan all folders registered in database
    scan      Load musics files in database
    sync      Copy selected musics with filters to...
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
    --crawl     Crawl youtube
    -h, --help  Show this message and exit.


musicbot folder scan
********************
.. code-block::

  Usage: musicbot folder scan [OPTIONS] [FOLDERS]...
  
    Load musics files in database
  
  Options:
    --crawl     Crawl youtube
    -h, --help  Show this message and exit.


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

  Usage: musicbot help [OPTIONS]
  
    Print help
  
  Options:
    -h, --help  Show this message and exit.


musicbot playlist
*****************
.. code-block::

  Usage: musicbot playlist [OPTIONS] COMMAND [ARGS]...
  
    Playlist management
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
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
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    start  Start musicbot web API


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
    --http-password TEXT    HTTP Basic auth password  [default: musicbot]
    --dev                   Watch for source file modification
    --watcher               Watch for music file modification
    --autoscan              Enable auto scan background job
    --server-cache          Activate server cache system
    --client-cache          Activate client cache system
    --no-auth               Disable authentication system
    -h, --help              Show this message and exit.


musicbot stats
**************
.. code-block::

  Usage: musicbot stats [OPTIONS] COMMAND [ARGS]...
  
    Youtube management
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    show  Generate some stats for music collection with...


musicbot stats show
*******************
.. code-block::

  Usage: musicbot stats show [OPTIONS]
  
    Generate some stats for music collection with filters
  
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
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    show  Show tags of musics with filters


musicbot tag show
*****************
.. code-block::

  Usage: musicbot tag show [OPTIONS]
  
    Show tags of musics with filters
  
  Options:
    --fields TEXT           Show only those fields
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    -h, --help              Show this message and exit.


musicbot task
*************
.. code-block::

  Usage: musicbot task [OPTIONS] COMMAND [ARGS]...
  
    Task management
  
  Options:
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
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
    --db-host TEXT      DB host  [default: localhost]
    --db-port INTEGER   DB port  [default: 5432]
    --db-database TEXT  DB name  [default: musicbot_prod]
    --db-user TEXT      DB user  [default: postgres]
    --db-password TEXT  DB password  [default: musicbot]
    -h, --help          Show this message and exit.
  
  Commands:
    albums  Fetch youtube links for each album
    musics  Fetch youtube links for each music
    only    Fetch youtube links for each album


musicbot youtube albums
***********************
.. code-block::

  Usage: musicbot youtube albums [OPTIONS]
  
    Fetch youtube links for each album
  
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    --concurrency INTEGER   Number of coroutines  [default: 8]
    --youtube-album TEXT    Select albums with a youtube link
    -h, --help              Show this message and exit.


musicbot youtube musics
***********************
.. code-block::

  Usage: musicbot youtube musics [OPTIONS]
  
    Fetch youtube links for each music
  
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
    --min-rating FLOAT      Minimum rating  [default: 0.0]
    --max-rating FLOAT      Maximum rating  [default: 5.0]
    --relative              Generate relatives paths
    --shuffle               Randomize selection
    --concurrency INTEGER   Number of coroutines  [default: 8]
    -h, --help              Show this message and exit.


musicbot youtube only
*********************
.. code-block::

  Usage: musicbot youtube only [OPTIONS]
  
    Fetch youtube links for each album
  
  Options:
    -h, --help  Show this message and exit.


