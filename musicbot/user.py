import base64
import json
import logging
import functools
import sys
from typing import Collection, Optional
import enlighten
from click_option_group import optgroup
from .graphql import GraphQL
from .config import config
from .helpers import config_string
from .exceptions import MusicbotError, FailedAuthentication, FailedRegistration
from .music import file, mfilter

logger = logging.getLogger(__name__)


DEFAULT_EMAIL = None
email_option = [
    optgroup.option(
        '--email', '-e',
        help='User email',
        default=DEFAULT_EMAIL,
        is_eager=True,
        callback=config_string,
    )
]

DEFAULT_PASSWORD = None
password_option = [
    optgroup.option(
        '--password', '-p',
        help='User password',
        default=DEFAULT_PASSWORD,
        is_eager=True,
        callback=config_string,
    )
]

DEFAULT_FIRST_NAME = None
first_name_option = [
    optgroup.option(
        '--first-name',
        help='User first name',
        default=DEFAULT_FIRST_NAME,
        is_eager=True,
        callback=config_string,
        show_default=True,
    )
]

DEFAULT_LAST_NAME = None
last_name_option = [
    optgroup.option(
        '--last-name',
        help='User last name',
        default=DEFAULT_FIRST_NAME,
        is_eager=True,
        callback=config_string,
        show_default=True,
    )
]

DEFAULT_TOKEN = None
token_option = [
    optgroup.option(
        '--token', '-t',
        help='User token',
    )
]

DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'
graphql_option = [
    optgroup.option(
        '--graphql',
        help='GraphQL endpoint',
        default=DEFAULT_GRAPHQL,
        is_eager=True,
        callback=config_string,
        show_default=True,
    )
]


class User(GraphQL):
    @config.timeit
    def __init__(self, graphql: str, email: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None):
        self.authenticated = False

        if token:
            self.token = token
            logger.debug(f"using token : {self.token}")
        elif email and password:
            query = f"""
            mutation
            {{
                authenticate(input: {{email: "{email}", password: "{password}"}})
                {{
                    jwtToken
                }}
            }}"""
            response = None
            try:
                graphql_auth = GraphQL(graphql=graphql)
                response = graphql_auth.post(query)
                self.token = response['data']['authenticate']['jwtToken']
                self.email = email
                self.password = password
            except MusicbotError as e:
                raise FailedAuthentication(f"Authentication failed for email {email}") from e
            except KeyError as e:
                raise FailedAuthentication(f"Invalid response received : {response}") from e
        else:
            raise FailedAuthentication("No credentials or token provided")
        GraphQL.__init__(self, graphql, authorization=f"Bearer {self.token}")
        self.authenticated = True

    @classmethod
    @functools.lru_cache(maxsize=None)
    @config.timeit
    def new(cls, **kwargs):
        self = User(**kwargs)
        return self

    @config.timeit
    def load_default_filters(self):
        query = """
        mutation
        {
            default:           createFilter(input: {filter: {name: "default"                                                                           }}){clientMutationId}
            no_artist_set:     createFilter(input: {filter: {name: "no artist set",     artists:    ""                                                 }}){clientMutationId}
            no_album_set:      createFilter(input: {filter: {name: "no album set",      albums:     ""                                                 }}){clientMutationId}
            no_title_set:      createFilter(input: {filter: {name: "no title set",      titles:     ""                                                 }}){clientMutationId}
            no_genre_set:      createFilter(input: {filter: {name: "no genre set",      genres:     ""                                                 }}){clientMutationId}
            youtube_not_found: createFilter(input: {filter: {name: "youtube not found", youtubes:   ["not found"]                                      }}){clientMutationId}
            spotify_not_found: createFilter(input: {filter: {name: "spotify not found", spotifys:   ["not found"]                                      }}){clientMutationId}
            no_youtube_links:  createFilter(input: {filter: {name: "no youtube links",  youtubes:   []                                                 }}){clientMutationId}
            no_spotify_links:  createFilter(input: {filter: {name: "no spotify links",  spotifys:   ["not found"]                                      }}){clientMutationId}
            no_rating:         createFilter(input: {filter: {name: "no rating",         minRating:  0.0, maxRating: 0.0                                }}){clientMutationId}
            bests_40:          createFilter(input: {filter: {name: "best (4.0+)",       minRating:  4.0, noKeywords: ["cutoff", "bad", "demo", "intro"]}}){clientMutationId}
            bests_45:          createFilter(input: {filter: {name: "best (4.5+)",       minRating:  4.5, noKeywords: ["cutoff", "bad", "demo", "intro"]}}){clientMutationId}
            bests_50:          createFilter(input: {filter: {name: "best (5.0+)",       minRating:  5.0, noKeywords: ["cutoff", "bad", "demo", "intro"]}}){clientMutationId}
            no_live:           createFilter(input: {filter: {name: "no live",           noKeywords: ["live"]                                           }}){clientMutationId}
            only_live:         createFilter(input: {filter: {name: "only live",         keywords:   ["live"]                                           }}){clientMutationId}
        }"""
        return self.post(query)

    @config.timeit
    def playlist(self, mf: Optional[mfilter.Filter] = None):
        mf = mf if mf is not None else mfilter.Filter()
        query = f"""
        {{
            playlist({mf.to_graphql()})
        }}"""
        return self.post(query)['data']['playlist']

    @config.timeit
    def bests(self, mf: Optional[mfilter.Filter] = None):
        mf = mf if mf is not None else mfilter.Filter()
        query = f"""
        {{
            bests({mf.to_graphql()})
            {{
                nodes
                {{
                    name,
                    content
                }}
            }}
        }}"""
        return self.post(query)['data']['bests']['nodes']

    @config.timeit
    def do_filter(self, mf: Optional[mfilter.Filter] = None):
        mf = mf if mf is not None else mfilter.Filter()
        if mf.name:
            kwargs = self.filter(mf.name)
            print(kwargs)
            mf = mfilter.Filter(**kwargs)

        query = f"""
        {{
            doFilter({mf.to_graphql()})
            {{
                nodes
                {{
                    title,
                    album,
                    genre,
                    artist,
                    folder,
                    youtube,
                    spotify,
                    number,
                    path,
                    rating,
                    duration,
                    size,
                    keywords
                }}
            }}
        }}"""
        return self.post(query)['data']['doFilter']['nodes']

    @config.timeit
    def do_stat(self, mf: Optional[mfilter.Filter] = None):
        mf = mf if mf is not None else mfilter.Filter()
        query = f"""
        {{
            doStat({mf.to_graphql()})
            {{
              musics,
              artists,
              albums,
              genres,
              keywords,
              size,
              duration
            }}
        }}"""
        return self.post(query)['data']['doStat']

    @config.timeit
    def upsert_music(self, music: file.File):
        query = f"""
        mutation
        {{
            upsertMusic(input: {{{music.to_graphql()}}})
            {{
                clientMutationId
            }}
        }}"""
        return self.post(query)

    @config.timeit
    def bulk_insert(self, musics: Collection[file.File]):
        if not musics:
            logger.info("no musics to insert")
            return None
        if config.debug:
            with enlighten.Manager(stream=sys.stderr) as manager:
                with manager.counter(total=len(musics), desc="inserting music one by one") as pbar:
                    for music in musics:
                        logger.debug(f"inserting {music}")
                        self.upsert_music(music)
                        pbar.update()
            return None

        j = json.dumps([m.to_dict() for m in musics])
        b64 = j.encode('utf-8')
        data = base64.b64encode(b64)
        query = f'''
        mutation
        {{
            bulkInsert(input: {{data: "{data.decode()}"}})
            {{
                clientMutationId
            }}
        }}'''
        return self.post(query)

    @property
    @functools.lru_cache(maxsize=None)
    @config.timeit
    def folders(self):
        query = """
        {
            foldersList
        }"""
        return self.post(query)['data']['foldersList']

    @property
    @functools.lru_cache(maxsize=None)
    @config.timeit
    def artists(self):
        query = """
        {
          artistsTreeList {
            name
            albums {
              name
              musics {
                folder
                name
                path
              }
            }
          }
        }"""
        return self.post(query)['data']['artistsTreeList']

    @property
    @functools.lru_cache(maxsize=None)
    @config.timeit
    def genres(self):
        query = """
        {
          genresTreeList {
            name
          }
        }"""
        return self.post(query)['data']['genresTreeList']

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def filter(self, name: str):
        default_filter = mfilter.Filter()
        filter_members = ','.join(default_filter.ordered_dict().keys())
        query = f"""
        {{
            filtersList(filter: {{name: {{equalTo: "{name}"}}}})
            {{
                name,
                {filter_members}
            }}
        }}"""
        return self.post(query)['data']['filtersList'][0]

    @property
    @functools.lru_cache(maxsize=None)
    @config.timeit
    def filters(self):
        default_filter = mfilter.Filter()
        filter_members = ','.join(default_filter.ordered_dict().keys())
        query = f"""
        {{
            filtersList
            {{
                name,
                {filter_members}
            }}
        }}"""
        return self.post(query)['data']['filtersList']

    def watch(self):
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
        import time

        class MusicWatcherHandler(PatternMatchingEventHandler):
            patterns = []

            def __init__(self, user):
                super().__init__()
                self.user = user
                MusicWatcherHandler.patterns = ['*.' + f for f in file.supported_formats]

            def on_modified(self, event):
                self.update_music(event.src_path)

            def on_created(self, event):
                self.update_music(event.src_path)

            def on_deleted(self, event):
                logger.debug(f'Deleting entry in DB for: {event.src_path} {event.event_type}')
                self.user.delete_music(event.src_path)

            def on_moved(self, event):
                logger.debug(f'Moving entry in DB for: {event.src_path} {event.event_type}')
                self.user.delete_music(event.src_path)
                self.update_music(event.dest_path)

            def update_music(self, path: str):
                for folder in self.user.folders:
                    if path.startswith(folder) and path.endswith(tuple(file.supported_formats)):
                        logger.debug(f'Creating/modifying DB for: {path}')
                        f = file.File(path, folder)
                        self.user.upsert_music(f)
                        return

        logger.info(f'Watching: {self.folders}')
        event_handler = MusicWatcherHandler(self)
        observer = Observer()
        for f in self.folders:
            observer.schedule(event_handler, f, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(50)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @classmethod
    @config.timeit
    def register(cls, graphql: str, email: str, password: str, first_name: str, last_name: str):
        query = f"""
        mutation
        {{
            registerUser(input: {{firstName: "{first_name}", lastName: "{last_name}", email: "{email}", password: "{password}"}})
            {{
                clientMutationId
            }}
        }}"""

        try:
            graphql_register = GraphQL(graphql=graphql)
            graphql_register.post(query)
        except MusicbotError as e:
            raise FailedRegistration(f"Registration failed for {first_name} | {last_name} | {email} | {password}") from e
        return User(
            graphql=graphql,
            email=email,
            password=password
        )

    @config.timeit
    def unregister(self):
        query = """
        mutation
        {
            unregisterUser(input: {})
            {
                clientMutationId
            }
        }"""
        try:
            result = self.post(query)
            self.authenticated = False
            return result
        except MusicbotError as e:
            raise FailedAuthentication(f"Cannot delete user {self.email}") from e

    @config.timeit
    def delete_music(self, path: str):
        query = f"""
        mutation
        {{
            deleteMusic(input: {{path: "{path}"}})
            {{
                clientMutationId
            }}
        }}"""
        return self.post(query)

    @config.timeit
    def clean_musics(self):
        query = """
        mutation
        {
            deleteAllMusic(input: {})
            {
                clientMutationId
            }
        }"""
        return self.post(query)


def sane_user(ctx, param, value) -> User:  # pylint: disable=unused-argument
    kwargs = {}
    for field in ('token', 'email', 'password', 'graphql'):
        kwargs[field] = ctx.params.get(field, None)
        ctx.params.pop(field, None)
    ctx.params['user'] = User(**kwargs)
    return ctx.params['user']


DEFAULT_FILTER = None
user_option = [
    optgroup.option(
        '--user',
        help='Music Filter',
        expose_value=False,
        callback=sane_user,
        hidden=True,
    )
]


register_options =\
    [optgroup.group('Register options')] +\
    graphql_option +\
    email_option +\
    password_option +\
    first_name_option +\
    last_name_option

login_options =\
    [optgroup.group('User options')] +\
    graphql_option +\
    email_option +\
    password_option +\
    user_option

auth_options =\
    [optgroup.group('Auth options')] +\
    graphql_option +\
    email_option +\
    password_option +\
    token_option +\
    user_option
