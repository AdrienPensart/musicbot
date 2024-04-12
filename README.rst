
Commands
--------
.. code-block::

  Usage: musicbot [OPTIONS] COMMAND [ARGS]...

    Music swiss knife, new gen.

  Options:
    Global options: 
      -c, --config FILE             Config file path  [default: ~/musicbot.ini]
      -l, --log FILE                Log file path
      -q, --quiet / --no-quiet      Disable progress bars  [default: no-quiet]
      --color / --no-color          Enable or disable color in output  [default: color]
    Verbosity: [mutually_exclusive]
      --debug                       Debug verbosity
      --info                        Info verbosity
      --warning                     Warning verbosity
      --error                       Error verbosity
      --critical                    Critical verbosity
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    -V, --version                   Show the version and exit.
    -h, --help                      Show this message and exit.

  Commands:
    console               Starts interpreter
    database (db,edgedb)  DB management
    folder                Manage folders
    help                  Print help
    local                 Local music management
    music (file)          Music file
    readme (doc)          Generates a README.rst
    spotify               Spotify tool
    version               Print version
    youtube               Youtube tool

musicbot console
****************
.. code-block::

  Usage: musicbot console [OPTIONS]

    Starts an embedded ipython interpreter

  Options:
    -h, --help  Show this message and exit.

musicbot database
*****************
.. code-block::

  Usage: musicbot database [OPTIONS] COMMAND [ARGS]...

    DB management

  Options:
    -h, --help  Show this message and exit.

  Commands:
    clean (clean-db,erase)        Clean all musics in DB
    drop                          Drop entire schema from DB
    edgeql (execute,fetch,query)  EdgeDB raw query
    graphiql                      Explore with GraphiQL
    graphql                       GraphQL query
    help                          Print help
    pgcli                         Connect with PgCLI
    soft-clean                    Clean entities without musics associated
    ui                            Explore with EdgeDB UI

musicbot database clean
***********************
.. code-block::

  Usage: musicbot database clean [OPTIONS]

    Clean all musics in DB

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -y, --yes          Confirm action
    -h, --help         Show this message and exit.

musicbot database drop
**********************
.. code-block::

  Usage: musicbot database drop [OPTIONS]

    Drop entire schema from DB

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -y, --yes          Confirm action
    -h, --help         Show this message and exit.

musicbot database edgeql
************************
.. code-block::

  Usage: musicbot database edgeql [OPTIONS] QUERY

    EdgeDB raw query

  Options:
    MusicDB options: 
      --dsn TEXT               DSN to MusicBot EdgeDB
      --graphql TEXT           DSN to MusicBot GrapQL
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot database graphiql
**************************
.. code-block::

  Usage: musicbot database graphiql [OPTIONS]

    Explore with GraphiQL

  Options:
    MusicDB options: 
      --dsn TEXT        DSN to MusicBot EdgeDB
      --graphql TEXT    DSN to MusicBot GrapQL
    --open / --no-open  [default: open]
    -h, --help          Show this message and exit.

musicbot database graphql
*************************
.. code-block::

  Usage: musicbot database graphql [OPTIONS] QUERY

    GraphQL query

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -h, --help         Show this message and exit.

musicbot database pgcli
***********************
.. code-block::

  Usage: musicbot database pgcli [OPTIONS] [PGCLI_ARGS]...

    Connect with PgCLI

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -h, --help         Show this message and exit.

musicbot database soft-clean
****************************
.. code-block::

  Usage: musicbot database soft-clean [OPTIONS]

    Clean entities without musics associated

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -h, --help         Show this message and exit.

musicbot database ui
********************
.. code-block::

  Usage: musicbot database ui [OPTIONS] [EDGEDB_ARGS]...

    Explore with EdgeDB UI

  Options:
    --open / --no-open  [default: open]
    MusicDB options: 
      --dsn TEXT        DSN to MusicBot EdgeDB
      --graphql TEXT    DSN to MusicBot GrapQL
    -h, --help          Show this message and exit.

musicbot folder
***************
.. code-block::

  Usage: musicbot folder [OPTIONS] COMMAND [ARGS]...

    Manage folders

  Options:
    -h, --help  Show this message and exit.

  Commands:
    add-keywords                   Add keywords to music
    delete-keywords                Delete keywords to music
    find                           Just list music files
    flac2mp3 (flac-to-mp3)         Convert all files in folders to mp3
    help                           Print help
    issues                         Show music files issues in folders
    manual-fix                     Fix music files in folders
    playlist (musics,tags,tracks)  Generates a playlist
    set-tags (set-tag)             Set music title

musicbot folder add-keywords
****************************
.. code-block::

  Usage: musicbot folder add-keywords [OPTIONS] [SCAN_FOLDERS]...

    Add keywords to music

  Options:
    --keywords TEXT     Keywords
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    -h, --help          Show this message and exit.

musicbot folder delete-keywords
*******************************
.. code-block::

  Usage: musicbot folder delete-keywords [OPTIONS] [SCAN_FOLDERS]...

    Delete keywords to music

  Options:
    --keywords TEXT     Keywords
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    -h, --help          Show this message and exit.

musicbot folder find
********************
.. code-block::

  Usage: musicbot folder find [OPTIONS] [SCAN_FOLDERS]...

    Just list music files

  Options:
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    -h, --help          Show this message and exit.

musicbot folder flac2mp3
************************
.. code-block::

  Usage: musicbot folder flac2mp3 [OPTIONS] DESTINATION [SCAN_FOLDERS]...

    Convert all files in folders to mp3

  Options:
    --dry / --no-dry           Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER          Limit number of music files
      --extension TEXT         Supported formats  [default: flac, mp3]
    --threads INTEGER          Number of threads  [default: 8]
    --flat                     Do not create subfolders
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot folder issues
**********************
.. code-block::

  Usage: musicbot folder issues [OPTIONS] [SCAN_FOLDERS]...

    Show music files issues in folders

  Options:
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    -h, --help          Show this message and exit.

musicbot folder manual-fix
**************************
.. code-block::

  Usage: musicbot folder manual-fix [OPTIONS] [SCAN_FOLDERS]...

    Fix music files in folders

  Options:
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    -h, --help          Show this message and exit.

musicbot folder playlist
************************
.. code-block::

  Usage: musicbot folder playlist [OPTIONS] [SCAN_FOLDERS]...

    Generates a playlist

  Options:
    --dry / --no-dry           Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER          Limit number of music files
      --extension TEXT         Supported formats  [default: flac, mp3]
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot folder set-tags
************************
.. code-block::

  Usage: musicbot folder set-tags [OPTIONS] [SCAN_FOLDERS]...

    Set music title

  Options:
    --dry / --no-dry        Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER       Limit number of music files
      --extension TEXT      Supported formats  [default: flac, mp3]
    Music options: 
      --keywords TEXT       Keywords
      --artist TEXT         Artist
      --album TEXT          Album
      --title TEXT          Title
      --genre TEXT          Genre
      --track TEXT          Track number
      --rating FLOAT RANGE  Rating  [0.0<=x<=5.0]
    -h, --help              Show this message and exit.

musicbot help
*************
.. code-block::

  Usage: musicbot help [OPTIONS]

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
    artists           Artists descriptions
    bests             Generate bests playlists with some rules
    clean (wipe)      Clean all musics
    custom-playlists  Generate custom playlists inside music folders (and for Buckethead)
    folders           List folders and some stats
    help              Print help
    playlist          Generate a new playlist
    remove (delete)   Remove one or more music
    scan              Load musics
    sync              Copy selected musics with filters to destination folder
    watch (watcher)   Watch files changes in folders

musicbot local artists
**********************
.. code-block::

  Usage: musicbot local artists [OPTIONS]

  Options:
    MusicDB options: 
      --dsn TEXT               DSN to MusicBot EdgeDB
      --graphql TEXT           DSN to MusicBot GrapQL
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot local bests
********************
.. code-block::

  Usage: musicbot local bests [OPTIONS] SCAN_FOLDER

    to-fix: keyword=(tofix|todo|spotify-error)
    no-artist: artist=^$
    no-album: album=^$
    no-title: title=^$
    no-genre: genre=^$
    no-keyword: keyword=^$
    no-rating: max_rating=0.0
    bests-4.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.0
    bests-4.5: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.5
    bests-5.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=5.0

  Options:
    Filter options: 
      --prefilter [bests-4.0|bests-4.5|bests-5.0|no-album|no-artist|no-genre|no-keyword|no-rating|no-title|to-fix]
                                    Music pre filters (repeatable)
      --filter TEXT                 Music filters (repeatable), fields: genre,keyword,artist,title,album,pattern,min_size,max_size,min_length,
                                    max_length,min_rating,max_rating,limit
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    Links options: 
      --kind, --kinds [all|local|local-http|local-ssh|remote|remote-http|remote-ssh]
                                    Generate musics paths of types  [default: local]
      --relative / --no-relative    Generate relative links  [default: no-relative]
    Ordering options: [mutually_exclusive]
      --shuffle / --no-shuffle      Randomize selection  [default: no-shuffle]
      --interleave / --no-interleave
                                    Interleave tracks by artist  [default: no-interleave]
    Bests options: 
      --min-playlist-size INTEGER   Minimum size of playlist to write  [default: 1]
    -h, --help                      Show this message and exit.

musicbot local clean
********************
.. code-block::

  Usage: musicbot local clean [OPTIONS]

    Clean all musics

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -y, --yes          Confirm action
    -h, --help         Show this message and exit.

musicbot local custom-playlists
*******************************
.. code-block::

  Usage: musicbot local custom-playlists [OPTIONS] SCAN_FOLDER

  Options:
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    Links options: 
      --kind, --kinds [all|local|local-http|local-ssh|remote|remote-http|remote-ssh]
                                    Generate musics paths of types  [default: local]
      --relative / --no-relative    Generate relative links  [default: no-relative]
    Ordering options: [mutually_exclusive]
      --shuffle / --no-shuffle      Randomize selection  [default: no-shuffle]
      --interleave / --no-interleave
                                    Interleave tracks by artist  [default: no-interleave]
    Bests options: 
      --min-playlist-size INTEGER   Minimum size of playlist to write  [default: 1]
    --coroutines INTEGER            Limit number of coroutines  [default: 64]
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    --fast / --no-fast              [default: no-fast]
    -h, --help                      Show this message and exit.

musicbot local folders
**********************
.. code-block::

  Usage: musicbot local folders [OPTIONS]

    List folders and some stats

  Options:
    MusicDB options: 
      --dsn TEXT               DSN to MusicBot EdgeDB
      --graphql TEXT           DSN to MusicBot GrapQL
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot local playlist
***********************
.. code-block::

  Usage: musicbot local playlist [OPTIONS] [OUT]

    to-fix: keyword=(tofix|todo|spotify-error)
    no-artist: artist=^$
    no-album: album=^$
    no-title: title=^$
    no-genre: genre=^$
    no-keyword: keyword=^$
    no-rating: max_rating=0.0
    bests-4.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.0
    bests-4.5: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.5
    bests-5.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=5.0

  Options:
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    --output [json|table|m3u]       Output format  [default: table]
    Filter options: 
      --prefilter [bests-4.0|bests-4.5|bests-5.0|no-album|no-artist|no-genre|no-keyword|no-rating|no-title|to-fix]
                                    Music pre filters (repeatable)
      --filter TEXT                 Music filters (repeatable), fields: genre,keyword,artist,title,album,pattern,min_size,max_size,min_length,
                                    max_length,min_rating,max_rating,limit
    Links options: 
      --kind, --kinds [all|local|local-http|local-ssh|remote|remote-http|remote-ssh]
                                    Generate musics paths of types  [default: local]
      --relative / --no-relative    Generate relative links  [default: no-relative]
    Ordering options: [mutually_exclusive]
      --shuffle / --no-shuffle      Randomize selection  [default: no-shuffle]
      --interleave / --no-interleave
                                    Interleave tracks by artist  [default: no-interleave]
    -h, --help                      Show this message and exit.

musicbot local remove
*********************
.. code-block::

  Usage: musicbot local remove [OPTIONS] [FILES]...

    Remove one or more music

  Options:
    MusicDB options: 
      --dsn TEXT       DSN to MusicBot EdgeDB
      --graphql TEXT   DSN to MusicBot GrapQL
    -h, --help         Show this message and exit.

musicbot local scan
*******************
.. code-block::

  Usage: musicbot local scan [OPTIONS] [SCAN_FOLDERS]...

    Load musics

  Options:
    --dry / --no-dry           Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER          Limit number of music files
      --extension TEXT         Supported formats  [default: flac, mp3]
    MusicDB options: 
      --dsn TEXT               DSN to MusicBot EdgeDB
      --graphql TEXT           DSN to MusicBot GrapQL
    -s, --save                 Save to config file
    --output [json|table|m3u]  Output format  [default: table]
    --clean                    Delete musics before
    --coroutines INTEGER       Limit number of coroutines  [default: 64]
    -h, --help                 Show this message and exit.

musicbot local sync
*******************
.. code-block::

  Usage: musicbot local sync [OPTIONS] DESTINATION

    to-fix: keyword=(tofix|todo|spotify-error)
    no-artist: artist=^$
    no-album: album=^$
    no-title: title=^$
    no-genre: genre=^$
    no-keyword: keyword=^$
    no-rating: max_rating=0.0
    bests-4.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.0
    bests-4.5: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=4.5
    bests-5.0: keyword=^((?!cutoff|bad|demo|intro).)$,min_rating=5.0

  Options:
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    -y, --yes                       Confirm action
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    Filter options: 
      --prefilter [bests-4.0|bests-4.5|bests-5.0|no-album|no-artist|no-genre|no-keyword|no-rating|no-title|to-fix]
                                    Music pre filters (repeatable)
      --filter TEXT                 Music filters (repeatable), fields: genre,keyword,artist,title,album,pattern,min_size,max_size,min_length,
                                    max_length,min_rating,max_rating,limit
    --flat                          Do not create subfolders
    --delete                        Delete files on destination if not present in library
    -h, --help                      Show this message and exit.

musicbot local watch
********************
.. code-block::

  Usage: musicbot local watch [OPTIONS] [SCAN_FOLDERS]...

    Watch files changes in folders

  Options:
    --dry / --no-dry    Do not launch real action  [default: no-dry]
    Folders options: 
      --limit INTEGER   Limit number of music files
      --extension TEXT  Supported formats  [default: flac, mp3]
    MusicDB options: 
      --dsn TEXT        DSN to MusicBot EdgeDB
      --graphql TEXT    DSN to MusicBot GrapQL
    --sleep INTEGER     Clean music every X seconds  [default: 1800]
    --timeout INTEGER   How many seconds until we terminate
    -h, --help          Show this message and exit.

musicbot music
**************
.. code-block::

  Usage: musicbot music [OPTIONS] COMMAND [ARGS]...

    Music file

  Options:
    -h, --help  Show this message and exit.

  Commands:
    add-keywords                    Add keywords to music
    delete-keywords (delete-keyword,remove-keyword,remove-keywords)
                                    Delete keywords to music
    fingerprint                     Print music AcoustID fingerprint
    flac2mp3 (flac-to-mp3)          Convert flac music to mp3
    help                            Print help
    issues                          Check music consistency
    manual-fix                      Fix music file
    replace-keyword                 Replace one keyword in music
    set-tags (set-tag)              Set music title
    shazam (recognize)              Recognize music using Shazam
    show                            Show music
    tags (tag)                      Print music tags

musicbot music add-keywords
***************************
.. code-block::

  Usage: musicbot music add-keywords [OPTIONS] SCAN_FOLDER FILE [KEYWORDS]...

    Add keywords to music

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music delete-keywords
******************************
.. code-block::

  Usage: musicbot music delete-keywords [OPTIONS] SCAN_FOLDER FILE [KEYWORDS]...

    Delete keywords to music

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music fingerprint
**************************
.. code-block::

  Usage: musicbot music fingerprint [OPTIONS] SCAN_FOLDER FILE

    Print music AcoustID fingerprint

  Options:
    --dry / --no-dry         Do not launch real action  [default: no-dry]
    --acoustid-api-key TEXT  AcoustID API Key
    -h, --help               Show this message and exit.

musicbot music flac2mp3
***********************
.. code-block::

  Usage: musicbot music flac2mp3 [OPTIONS] SCAN_FOLDER FILE DESTINATION

    Convert flac music to mp3

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music issues
*********************
.. code-block::

  Usage: musicbot music issues [OPTIONS] SCAN_FOLDER FILE

    Check music consistency

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music manual-fix
*************************
.. code-block::

  Usage: musicbot music manual-fix [OPTIONS] SCAN_FOLDER FILE

    Fix music file

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music replace-keyword
******************************
.. code-block::

  Usage: musicbot music replace-keyword [OPTIONS] SCAN_FOLDER FILE OLD_KEYWORD NEW_KEYWORD

    Replace one keyword in music

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music set-tags
***********************
.. code-block::

  Usage: musicbot music set-tags [OPTIONS] [PATHS]...

    Set music title

  Options:
    --dry / --no-dry        Do not launch real action  [default: no-dry]
    Music options: 
      --keywords TEXT       Keywords
      --artist TEXT         Artist
      --album TEXT          Album
      --title TEXT          Title
      --genre TEXT          Genre
      --track TEXT          Track number
      --rating FLOAT RANGE  Rating  [0.0<=x<=5.0]
    -h, --help              Show this message and exit.

musicbot music shazam
*********************
.. code-block::

  Usage: musicbot music shazam [OPTIONS] SCAN_FOLDER FILE

    Recognize music using Shazam

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music show
*******************
.. code-block::

  Usage: musicbot music show [OPTIONS] SCAN_FOLDER FILE

    Show music

  Options:
    --dry / --no-dry  Do not launch real action  [default: no-dry]
    -h, --help        Show this message and exit.

musicbot music tags
*******************
.. code-block::

  Usage: musicbot music tags [OPTIONS] SCAN_FOLDER FILE

    Print music tags

  Options:
    --dry / --no-dry           Do not launch real action  [default: no-dry]
    --output [json|table|m3u]  Output format  [default: table]
    -h, --help                 Show this message and exit.

musicbot readme
***************
.. code-block::

  Usage: musicbot readme [OPTIONS]

    Generates a complete readme

  Options:
    --output [rst|markdown]  README output format  [default: rst]
    -h, --help               Show this message and exit.

musicbot spotify
****************
.. code-block::

  Usage: musicbot spotify [OPTIONS] COMMAND [ARGS]...

    Spotify tool

  Options:
    -h, --help  Show this message and exit.

  Commands:
    artist-diff             Artists diff between local and spotify
    cached-token            Token informations
    help                    Print help
    new-token (auth,login)  Generate a new token
    playlist                Show playlist
    playlists               List playlists
    refresh-token           Get a new token
    to-download             Show download playlist
    track-diff              Diff between local and spotify
    tracks (liked)          Show liked tracks

musicbot spotify artist-diff
****************************
.. code-block::

  Usage: musicbot spotify artist-diff [OPTIONS]

    Artists diff between local and spotify

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    -h, --help                      Show this message and exit.

musicbot spotify cached-token
*****************************
.. code-block::

  Usage: musicbot spotify cached-token [OPTIONS]

    Token informations

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    -h, --help                      Show this message and exit.

musicbot spotify new-token
**************************
.. code-block::

  Usage: musicbot spotify new-token [OPTIONS]

    Generate a new token

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    -h, --help                      Show this message and exit.

musicbot spotify playlist
*************************
.. code-block::

  Usage: musicbot spotify playlist [OPTIONS] NAME

    Show playlist

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --output [json|table|m3u]       Output format  [default: table]
    -h, --help                      Show this message and exit.

musicbot spotify playlists
**************************
.. code-block::

  Usage: musicbot spotify playlists [OPTIONS]

    List playlists

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    -h, --help                      Show this message and exit.

musicbot spotify refresh-token
******************************
.. code-block::

  Usage: musicbot spotify refresh-token [OPTIONS]

    Get a new token

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --dry / --no-dry                Do not launch real action  [default: no-dry]
    -h, --help                      Show this message and exit.

musicbot spotify to-download
****************************
.. code-block::

  Usage: musicbot spotify to-download [OPTIONS]

    Show download playlist

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --output [json|table|m3u]       Output format  [default: table]
    -h, --help                      Show this message and exit.

musicbot spotify track-diff
***************************
.. code-block::

  Usage: musicbot spotify track-diff [OPTIONS]

    Diff between local and spotify

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    MusicDB options: 
      --dsn TEXT                    DSN to MusicBot EdgeDB
      --graphql TEXT                DSN to MusicBot GrapQL
    --output [json|table|m3u]       Output format  [default: table]
    --download-playlist             Create the download playlist
    --min-threshold FLOAT RANGE     Minimum distance threshold  [default: 90; 0<=x<=100]
    --max-threshold FLOAT RANGE     Maximum distance threshold  [default: 100; 0<=x<=100]
    -h, --help                      Show this message and exit.

musicbot spotify tracks
***********************
.. code-block::

  Usage: musicbot spotify tracks [OPTIONS]

    Show liked tracks

  Options:
    Spotify options: 
      --spotify-username TEXT       Spotify username
      --spotify-client-id TEXT      Spotify client ID
      --spotify-client-secret TEXT  Spotify client secret
      --spotify-cache-path FILE     Spotify cache path
      --spotify-scope TEXT          Spotify OAuth scopes, comma separated
      --spotify-redirect-uri TEXT   Spotify redirect URI
      --spotify-token TEXT          Spotify token
    --output [json|table|m3u]       Output format  [default: table]
    -h, --help                      Show this message and exit.

musicbot version
****************
.. code-block::

  Usage: musicbot version [OPTIONS]

    Print version, equivalent to -V and --version

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

  Usage: musicbot youtube find [OPTIONS] SCAN_FOLDER FILE

    Search a youtube link with artist and title

  Options:
    --dry / --no-dry         Do not launch real action  [default: no-dry]
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
