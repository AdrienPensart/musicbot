import click
import os
import base64
import json
import logging
import requests
import functools
from . import helpers
from .music import file, mfilter

MB_TOKEN = 'MB_TOKEN'
DEFAULT_TOKEN = None
token_argument = [click.argument('token')]
token_option = [click.option('--token', envvar=MB_TOKEN, help='User token', default=DEFAULT_TOKEN, show_default=False)]

MB_EMAIL = 'MB_EMAIL'
DEFAULT_EMAIL = None
email_argument = [click.argument('email')]
email_option = [click.option('--email', '-e', envvar=MB_EMAIL, help='User email', default=DEFAULT_EMAIL, show_default=True)]

MB_PASSWORD = 'MB_PASSWORD'
DEFAULT_PASSWORD = None
password_argument = [click.argument('password')]
password_option = [click.option('--password', '-p', envvar=MB_PASSWORD, help='User password', default=DEFAULT_PASSWORD, show_default=False)]

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


class FailedAuthentication(Exception):
    pass


class FailedRequest(Exception):
    pass


class GraphQL:
    def __init__(self, graphql, headers=None):
        self.graphql = graphql
        self.headers = headers

    def _post(self, query, failure=None):
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            failure = failure if failure is not None else FailedRequest("Query failed: {}".format(response.json()))
            raise failure
        return response.json()


class Admin(GraphQL):
    @helpers.timeit
    def __init__(self, graphql_admin=None):
        self.graphql_admin = graphql_admin if graphql_admin is not None else os.getenv(MB_GRAPHQL_ADMIN, DEFAULT_GRAPHQL_ADMIN)
        GraphQL.__init__(self, graphql=graphql_admin)

    @helpers.timeit
    def users(self):
        query = """
        {
          allUsersList{
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
        return self._post(query)['data']['allUsersList']


class User(GraphQL):
    @helpers.timeit
    def __init__(self, graphql=None, email=None, password=None, token=None):
        self.graphql = graphql if graphql is not None else os.getenv(MB_GRAPHQL, DEFAULT_GRAPHQL)
        self.email = email
        self.password = password
        self.token = token
        self.authenticated = False

        if self.email and self.password:
            query = """
            mutation
            {{
                authenticate(input: {{email: "{}", password: "{}"}})
                {{
                    jwtToken
                }}
            }}""".format(self.email, self.password)
            response = requests.post(self.graphql, json={'query': query})
            logger.debug(response)
            if response.status_code == 200:
                self.token = response.json()['data']['authenticate']['jwtToken']
                if self.token is None:
                    raise FailedAuthentication("Register failed")
            else:
                raise FailedAuthentication("Register failed")
        elif self.token is None:
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
        j = json.dumps([m.to_dict() for m in musics])
        data = base64.b64encode(j.encode('utf-8'))
        query = '''
        mutation
        {{
            bulkInsert(input: {{data: "{}"}})
            {{
                clientMutationId
            }}
        }}'''.format(data.decode())
        return self._post(query)

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def folders(self):
        query = """
        {
            folders
            {
                nodes
            }
        }"""
        return self._post(query)['data']['folders']['nodes']

    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def filter(self, name):
        default_filter = mfilter.Filter()
        query = """
        {{
            allFiltersList(filter: {{name: {{equalTo: "{}"}}}})
            {{
                name,
                {}
            }}
        }}""".format(name, ','.join(default_filter.ordered_dict().keys()))
        return self._post(query)['data']['allFiltersList'][0]

    @property
    @functools.lru_cache(maxsize=None)
    @helpers.timeit
    def filters(self):
        default_filter = mfilter.Filter()
        query = """
        {{
            allFiltersList
            {{
                name,
                {}
            }}
        }}""".format(','.join(default_filter.ordered_dict().keys()))
        return self._post(query)['data']['allFiltersList']

    def watch(user):
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
        import time

        def update_music(path):
            for folder in user.folders:
                if path.startswith(folder) and path.endswith(tuple(file.supported_formats)):
                    logger.debug('Creating/modifying DB for: %s', path)
                    f = file.File(path, folder)
                    user.upsert_music(f)
                    return

        class MusicWatcherHandler(PatternMatchingEventHandler):
            patterns = []

            def __init__(self):
                super().__init__()
                MusicWatcherHandler.patterns = ['*.' + f for f in file.supported_formats]

            def on_modified(self, event):
                update_music(event.src_path)

            def on_created(self, event):
                update_music(event.src_path)

            def on_deleted(self, event):
                logger.debug('Deleting entry in DB for: %s %s', event.src_path, event.event_type)
                user.delete_music(event.src_path)

            def on_moved(self, event):
                logger.debug('Moving entry in DB for: %s %s', event.src_path, event.event_type)
                user.delete_music(event.src_path)
                update_music(event.dest_path)

        logger.info('Watching: {}'.format(user.folders))
        event_handler = MusicWatcherHandler()
        observer = Observer()
        for f in user.folders:
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
        response = requests.post(graphql, json={'query': query})
        logger.debug(response)
        if response.status_code != 200:
            raise FailedAuthentication("Cannot create user {}".format(email))
        self = User(graphql, email, password)
        return self

    @helpers.timeit
    def unregister(self):
        query = """
        mutation
        {
            removeUser(input: {})
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
