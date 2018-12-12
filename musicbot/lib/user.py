import click
import base64
import json
import logging
import requests
from .helpers import timeit
# from . import helpers, lib, file
from . import lib, file, mfilter

MB_TOKEN = 'MB_TOKEN'
DEFAULT_TOKEN = ''
token_argument = [click.argument('token')]
token_option = [click.option('--token', envvar=MB_TOKEN, help='User token', default=DEFAULT_TOKEN, show_default=False)]

MB_SECRET = 'MB_SECRET'
DEFAULT_SECRET = 'my_little_secret'
secret_argument = [click.argument('secret')]
secret_option = [click.option('--secret', envvar=MB_SECRET, help='Secret to sign tokens', default=DEFAULT_SECRET, show_default=False)]

MB_EMAIL = 'MB_EMAIL'
# DEFAULT_EMAIL = 'admin@musicbot.ovh'
DEFAULT_EMAIL = None
email_argument = [click.argument('email')]
email_option = [click.option('--email', envvar=MB_EMAIL, help='User email', default=DEFAULT_EMAIL, show_default=True)]

MB_PASSWORD = 'MB_PASSWORD'
# DEFAULT_PASSWORD = helpers.random_password(size=10)
DEFAULT_PASSWORD = None
password_argument = [click.argument('password')]
password_option = [click.option('--password', envvar=MB_PASSWORD, help='User password', default=DEFAULT_PASSWORD, show_default=False)]

MB_FIRST_NAME = 'MB_FIRST_NAME'
DEFAULT_FIRST_NAME = 'admin'
first_name_option = [click.option('--first-name', envvar=MB_FIRST_NAME, help='User first name', default=DEFAULT_FIRST_NAME, show_default=True)]

MB_LAST_NAME = 'MB_LAST_NAME'
DEFAULT_LAST_NAME = 'admin'
last_name_option = [click.option('--last-name', envvar=MB_LAST_NAME, help='User last name', default=DEFAULT_FIRST_NAME, show_default=True)]

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


class User:
    def __init__(self, graphql=None, email=None, password=None, token=None):
        self.graphql = graphql if graphql is not None else DEFAULT_GRAPHQL
        self.email = email
        self.password = password
        self.token = token
        self.authenticated = False
        self.headers = {"Authorization": "Bearer {}".format(self.token)}

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
                self.headers = {"Authorization": "Bearer {}".format(self.token)}
            else:
                raise FailedAuthentication("Register failed")
        elif self.token is None:
            raise FailedAuthentication("No credentials or token provided")
        self.authenticated = True

    @timeit
    def load_default_filters(self):
        query = """
        mutation
        {
            loadDefaultFilters(input: {})
            {
                clientMutationId
            }
        }"""
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.status_code == 200

    @timeit
    def do_filter(self, mf):
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
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.json()['data']['doFilter']['nodes']

    @timeit
    def upsert_music(self, music):
        query = """
        mutation
        {{
            upsertMusic(input: {{{}}})
            {{
                clientMutationId
            }}
        }}""".format(music.to_graphql())
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.status_code == 200

    @timeit
    def bulk_insert(self, musics):
        j = json.dumps(musics)
        data = base64.b64encode(j.encode('utf-8'))
        query = '''
        mutation
        {
            bulkInsert(input: {data: "''' + data.decode() + '''"})
            {
                clientMutationId
            }
        }'''
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.status_code == 200

    @lib.LazyProperty
    @timeit
    def folders(self):
        query = """
        {
            folders
            {
                nodes
            }
        }"""
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.json()['data']['folders']['nodes']

    @lib.LazyProperty
    @timeit
    def filters(self):
        default_filter = mfilter.Filter()
        query = """
        {{
            allFilters
            {{
                nodes
                {{
                    name,
                    {}
                }}
            }}
        }}""".format(','.join(default_filter.ordered_dict().keys()))
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.json()['data']['allFilters']['nodes']

    def watch(user):
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
        import time

        class MusicWatcherHandler(PatternMatchingEventHandler):
            patterns = []

            def __init__(self):
                super().__init__()
                self.patterns = ['*.' + f for f in file.supported_formats]

            def update(self, path):
                for folder in user.folders:
                    if path.startswith(folder) and path.endswith(tuple(file.supported_formats)):
                        logger.debug('Creating/modifying DB for: %s', path)
                        f = file.File(path, folder)
                        user.upsert_music(f)
                        return

            def on_modified(self, event):
                self.update(event.src_path)

            def on_created(self, event):
                self.update(event.src_path)

            def on_deleted(self, event):
                logger.debug('Deleting entry in DB for: %s %s', event.src_path, event.event_type)
                user.delete_music(event.src_path)

            def on_moved(self, event):
                logger.debug('Moving entry in DB for: %s %s', event.src_path, event.event_type)
                user.delete_music(event.src_path)
                self.update(event.dest_path)

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
    @timeit
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

    @timeit
    def unregister(self):
        query = """
        mutation
        {
            removeUser(input: {})
            {
                clientMutationId
            }
        }"""
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response.status_code)
        if response.status_code != 200:
            raise FailedAuthentication("Cannot delete user {}".format(self.email))
        return response.status_code == 200

    @timeit
    def delete_music(self, path):
        query = """
        mutation
        {{
            deleteMusic(input: {{{}}})
            {{
                clientMutationId
            }}
        }}""".format(path)
        response = requests.post(self.graphql, json={'query': query}, headers=self.headers)
        logger.debug(response.status_code)
        if response.status_code != 200:
            raise FailedRequest("Query failed: {}".format(response.json()))
        return response.status_code == 200
