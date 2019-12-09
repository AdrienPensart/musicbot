import os
import base64
import json
import logging
import functools
from functools import partial
import requests
import click
import click_spinner
from . import helpers
from .config import config
from .helpers import config_string
from .music import file, mfilter

MB_TOKEN = 'MB_TOKEN'
DEFAULT_TOKEN = None
token_option = [click.option('--token', '-t', help='User token', default=DEFAULT_TOKEN, callback=partial(config_string, MB_TOKEN, 'token', False))]

MB_EMAIL = 'MB_EMAIL'
DEFAULT_EMAIL = None
email_option = [click.option('--email', '-e', help='User email', default=DEFAULT_EMAIL, callback=partial(config_string, MB_EMAIL, 'email', False))]

MB_PASSWORD = 'MB_PASSWORD'
DEFAULT_PASSWORD = None
password_option = [click.option('--password', '-p', help='User password', default=DEFAULT_PASSWORD, callback=partial(config_string, MB_PASSWORD, 'password', False))]

MB_FIRST_NAME = 'MB_FIRST_NAME'
DEFAULT_FIRST_NAME = None
first_name_option = [click.option('--first-name', envvar=MB_FIRST_NAME, help='User first name', default=DEFAULT_FIRST_NAME, show_default=True)]

MB_LAST_NAME = 'MB_LAST_NAME'
DEFAULT_LAST_NAME = None
last_name_option = [click.option('--last-name', envvar=MB_LAST_NAME, help='User last name', default=DEFAULT_FIRST_NAME, show_default=True)]

MB_GRAPHQL_ADMIN = 'MB_GRAPHQL_ADMIN'
DEFAULT_GRAPHQL_ADMIN = 'http://127.0.0.1:5001/graphql'
graphql_admin_option = [click.option('--graphql-admin', envvar=MB_GRAPHQL_ADMIN, help='GraphQL endpoint', default=DEFAULT_GRAPHQL_ADMIN, show_default=True)]

MB_GRAPHQL = 'MB_GRAPHQL'
DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'
graphql_option = [click.option('--graphql', envvar=MB_GRAPHQL, help='GraphQL endpoint', default=DEFAULT_GRAPHQL, show_default=True)]

options = email_option + password_option + first_name_option + last_name_option + graphql_option
logger = logging.getLogger(__name__)

auth_options = email_option + password_option + token_option + graphql_option


class MusicbotError(Exception):
    pass


class FailedAuthentication(MusicbotError):
    pass


class FailedRequest(MusicbotError):
    pass


class GraphQL:  # pylint: disable=too-few-public-methods
    def __init__(self, graphql, headers=None):
        self.graphql = graphql
        self.headers = headers

    def _post(self, query, failure=None):
        logger.debug(query)
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        json_response = response.json()
        logger.debug(json_response)
        if response.status_code != 200:
            failure = failure if failure is not None else FailedRequest("Query failed: {}".format(json_response))
            raise failure
        if 'errors' in json_response and json_response['errors']:
            failure = failure if failure is not None else FailedRequest("Query failed: {}".format([e['message'] for e in json_response['errors']]))
            raise failure
        return json_response


class Admin(GraphQL):  # pylint: disable=too-few-public-methods
    @helpers.timeit
    def __init__(self, graphql=None):
        graphql = graphql if graphql is not None else os.getenv(MB_GRAPHQL_ADMIN, DEFAULT_GRAPHQL_ADMIN)
        GraphQL.__init__(self, graphql=graphql)

    @helpers.timeit
    def users(self):
        query = """
        {
          usersList{
              firstName,
              lastName,
              createdAt,
              updatedAt,
              accountByUserId{
                userId,
                email,
                passwordHash
              }
          }
        }"""
        return self._post(query)['data']['usersList']


class User(GraphQL):
    @helpers.timeit
    def __init__(self, graphql=None, email=None, password=None, token=None):
        self.graphql = graphql if graphql is not None else os.getenv(MB_GRAPHQL, DEFAULT_GRAPHQL)
        self.email = email
        self.password = password
        self.token = token
        self.authenticated = False

        if self.token:
            pass
        elif self.email and self.password:
            query = """
            mutation
            {{
                authenticate(input: {{email: "{}", password: "{}"}})
                {{
                    jwtToken
                }}
            }}""".format(self.email, self.password)
            self.headers = None
            self.token = self._post(query, failure=FailedAuthentication("Authentication failed for email {}".format(self.email)))['data']['authenticate']['jwtToken']
        else:
            raise FailedAuthentication("No credentials or token provided")
        self.authenticated = True
        GraphQL.__init__(self, graphql=graphql, headers={"Authorization": "Bearer {}".format(self.token)})

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
            loadDefaultFilters(input: {})
            {
                clientMutationId
            }
        }"""
        return self._post(query)

    @helpers.timeit
    def playlist(self, mf=None):
        mf = mf if mf is not None else mfilter.Filter()
        query = """
        {{
            playlist({})
        }}""".format(mf.to_graphql())
        return self._post(query)['data']['playlist']

    @helpers.timeit
    def bests(self, mf=None):
        mf = mf if mf is not None else mfilter.Filter()
        query = """
        {{
            bests({})
            {{
                nodes
                {{
                    name,
                    content
                }}
            }}
        }}""".format(mf.to_graphql())
        return self._post(query)['data']['bests']['nodes']

    @helpers.timeit
    def do_filter(self, mf=None):
        mf = mf if mf is not None else mfilter.Filter()
        if mf.name:
            kwargs = self.filter(mf.name)
            print(kwargs)
            mf = mfilter.Filter(**kwargs)

        query = """
        {{
            doFilter({})
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
        }}""".format(mf.to_graphql())
        return self._post(query)['data']['doFilter']['nodes']

    @helpers.timeit
    def do_stat(self, mf=None):
        mf = mf if mf is not None else mfilter.Filter()
        query = """
        {{
            doStat({})
            {{
              musics,
              artists,
              albums,
              genres,
              keywords,
              size,
              duration
            }}
        }}""".format(mf.to_graphql())
        return self._post(query)['data']['doStat']

    @helpers.timeit
    def upsert_music(self, music):
        query = """
        mutation
        {{
            upsertMusic(input: {{{}}})
            {{
                clientMutationId
            }}
        }}""".format(music.to_graphql())
        return self._post(query)

    @helpers.timeit
    def bulk_insert(self, musics):
        if not musics:
            logger.info("no musics to insert")
            return None
        j = json.dumps([m.to_dict() for m in musics])
        b64 = j.encode('utf-8')
        data = base64.b64encode(b64)
        query = '''
        mutation
        {{
            bulkInsert(input: {{data: "{}"}})
            {{
                clientMutationId
            }}
        }}'''.format(data.decode())
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
        query = """
        {{
            filtersList(filter: {{name: {{equalTo: "{}"}}}})
            {{
                name,
                {}
            }}
        }}""".format(name, ','.join(default_filter.ordered_dict().keys()))
        return self._post(query)['data']['filtersList'][0]

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def filters(self):
        default_filter = mfilter.Filter()
        query = """
        {{
            filtersList
            {{
                name,
                {}
            }}
        }}""".format(','.join(default_filter.ordered_dict().keys()))
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
    def register(cls, graphql, first_name, last_name, email, password):
        query = """
        mutation
        {{
            registerUser(input: {{firstName: "{}", lastName: "{}", email: "{}", password: "{}"}})
            {{
                clientMutationId
            }}
        }}""".format(first_name, last_name, email, password)
        logger.debug(query)
        response = requests.post(graphql, json={'query': query})
        json_response = response.json()
        logger.debug(json_response)
        if response.status_code != 200:
            raise FailedAuthentication("Cannot create user: {}".format(email))
        if 'errors' in json_response and json_response['errors']:
            raise FailedAuthentication("Cannot create user: {}".format([e['message'] for e in json_response['errors']]))
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
        result = self._post(query, failure=FailedAuthentication("Cannot delete user {}".format(self.email)))
        self.authenticated = False
        return result

    @helpers.timeit
    def delete_music(self, path):
        query = """
        mutation
        {{
            deleteMusic(input: {{path: "{}"}})
            {{
                clientMutationId
            }}
        }}""".format(path)
        return self._post(query)
