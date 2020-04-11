import base64
import json
import logging
import functools
import click
import click_spinner
import requests
from tqdm import tqdm
from . import helpers
from .graphql import GraphQL
from .config import config
from .helpers import config_string
from .exceptions import FailedAuthentication
from .music import file, mfilter

logger = logging.getLogger(__name__)


DEFAULT_EMAIL = None
email_option = [click.option('--email', '-e', help='User email', default=DEFAULT_EMAIL, is_eager=True, callback=config_string)]

DEFAULT_PASSWORD = None
password_option = [click.option('--password', '-p', help='User password', default=DEFAULT_PASSWORD, is_eager=True, callback=config_string)]

DEFAULT_FIRST_NAME = None
first_name_option = [click.option('--first-name', help='User first name', default=DEFAULT_FIRST_NAME, is_eager=True, callback=config_string, show_default=True)]

DEFAULT_LAST_NAME = None
last_name_option = [click.option('--last-name', help='User last name', default=DEFAULT_FIRST_NAME, is_eager=True, callback=config_string, show_default=True)]

DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'
graphql_option = [click.option('--graphql', help='GraphQL endpoint', default=DEFAULT_GRAPHQL, is_eager=True, callback=config_string, show_default=True)]


def sane_user(ctx, param, value):  # pylint: disable=unused-argument
    email = ctx.params['email']
    ctx.params.pop('email')

    password = ctx.params['password']
    ctx.params.pop('password')

    graphql = ctx.params['graphql']
    ctx.params.pop('graphql')

    token = value
    ctx.params['user'] = User(
        email=email,
        password=password,
        graphql=graphql,
        token=token,
    )
    return ctx.params['user']


DEFAULT_TOKEN = None
token_option = [click.option('--token', '-t', help='User token', expose_value=False, callback=sane_user)]

register_options = email_option + password_option + first_name_option + last_name_option + graphql_option
login_options = email_option + password_option + graphql_option
auth_options = login_options + token_option


class User(GraphQL):
    @helpers.timeit
    def __init__(self, graphql=None, email=None, password=None, token=None):
        self.graphql = graphql if graphql is not None else DEFAULT_GRAPHQL
        self.email = email
        self.password = password
        self.token = token
        self.authenticated = False

        if self.token:
            logger.debug("using token : %s", self.token)
        elif self.email and self.password:
            query = f"""
            mutation
            {{
                authenticate(input: {{email: "{self.email}", password: "{self.password}"}})
                {{
                    jwtToken
                }}
            }}"""
            self.headers = None

            response = self._post(query, failure=FailedAuthentication(f"Authentication failed for email {self.email}"))
            try:
                self.token = response['data']['authenticate']['jwtToken']
            except KeyError:
                raise FailedAuthentication(f"Invalid response received : {response}")
            if not self.token:
                raise FailedAuthentication(f"Invalid token received : {self.token}")
        else:
            raise FailedAuthentication("No credentials or token provided")
        self.authenticated = True
        GraphQL.__init__(self, graphql=graphql, headers={"Authorization": f"Bearer {self.token}"})

    @classmethod
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def new(cls, **kwargs):
        self = User(**kwargs)
        return self

    @helpers.timeit
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
        return self._post(query)

    @helpers.timeit
    def playlist(self, mf=None):
        mf = mf if mf is not None else mfilter.Filter()
        query = f"""
        {{
            playlist({mf.to_graphql()})
        }}"""
        return self._post(query)['data']['playlist']

    @helpers.timeit
    def bests(self, mf=None):
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
        return self._post(query)['data']['bests']['nodes']

    @helpers.timeit
    def do_filter(self, mf=None):
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
        return self._post(query)['data']['doFilter']['nodes']

    @helpers.timeit
    def do_stat(self, mf=None):
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
        return self._post(query)['data']['doStat']

    @helpers.timeit
    def upsert_music(self, music):
        query = f"""
        mutation
        {{
            upsertMusic(input: {{{music.to_graphql()}}})
            {{
                clientMutationId
            }}
        }}"""
        return self._post(query)

    @helpers.timeit
    def bulk_insert(self, musics):
        if not musics:
            logger.info("no musics to insert")
            return None
        if config.debug:
            with tqdm(total=len(musics), desc="inserting music one by one") as pbar:
                for music in musics:
                    logger.debug("inserting %s", music)
                    self.upsert_music(music)
                    pbar.update(1)
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
        with click_spinner.spinner(disable=config.quiet):
            return self._post(query)

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def folders(self):
        query = """
        {
            foldersList
        }"""
        return self._post(query)['data']['foldersList']

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
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
        return self._post(query)['data']['artistsTreeList']

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def genres(self):
        query = """
        {
          genresTreeList {
            name
          }
        }"""
        return self._post(query)['data']['genresTreeList']

    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def filter(self, name):
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
        return self._post(query)['data']['filtersList'][0]

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
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
        return self._post(query)['data']['filtersList']

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
                logger.debug('Deleting entry in DB for: %s %s', event.src_path, event.event_type)
                self.user.delete_music(event.src_path)

            def on_moved(self, event):
                logger.debug('Moving entry in DB for: %s %s', event.src_path, event.event_type)
                self.user.delete_music(event.src_path)
                self.update_music(event.dest_path)

            def update_music(self, path):
                for folder in self.user.folders:
                    if path.startswith(folder) and path.endswith(tuple(file.supported_formats)):
                        logger.debug('Creating/modifying DB for: %s', path)
                        f = file.File(path, folder)
                        self.user.upsert_music(f)
                        return

        logger.info('Watching: %s', self.folders)
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
    @helpers.timeit
    def register(cls, graphql=None, first_name=None, last_name=None, email=None, password=None):
        first_name = first_name if first_name is not None else DEFAULT_FIRST_NAME
        last_name = last_name if last_name is not None else DEFAULT_LAST_NAME
        email = email if email is not None else DEFAULT_EMAIL
        password = password if password is not None else DEFAULT_PASSWORD

        if email is None:
            raise click.BadParameter('Missing value for email')
        if password is None:
            raise click.BadParameter('Missing value for password')

        query = f"""
        mutation
        {{
            registerUser(input: {{firstName: "{first_name}", lastName: "{last_name}", email: "{email}", password: "{password}"}})
            {{
                clientMutationId
            }}
        }}"""
        logger.debug(query)
        response = requests.post(graphql, json={'query': query})
        json_response = response.json()
        logger.debug(json_response)
        if response.status_code != 200:
            raise FailedAuthentication(f"Cannot create user: {email}")
        if 'errors' in json_response and json_response['errors']:
            errors = [e['message'] for e in json_response['errors']]
            raise FailedAuthentication(f"Cannot create user: {errors}")
        return User(graphql, email, password)

    @helpers.timeit
    def unregister(self):
        query = """
        mutation
        {
            unregisterUser(input: {})
            {
                clientMutationId
            }
        }"""
        result = self._post(query, failure=FailedAuthentication(f"Cannot delete user {self.email}"))
        self.authenticated = False
        return result

    @helpers.timeit
    def delete_music(self, path):
        query = f"""
        mutation
        {{
            deleteMusic(input: {{path: "{path}"}})
            {{
                clientMutationId
            }}
        }}"""
        return self._post(query)

    @helpers.timeit
    def clean_musics(self):
        query = """
        mutation
        {
            deleteAllMusic(input: {})
            {
                clientMutationId
            }
        }"""
        return self._post(query)
