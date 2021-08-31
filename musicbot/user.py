from typing import Any, Collection, Optional, List
from functools import cached_property
import uuid
import logging
import attr
from musicbot.timing import timeit
from musicbot.object import MusicbotObject
from musicbot.graphql_client import GraphQL
from musicbot.exceptions import MusicbotError, QuerySyntaxError, FilterNotFound, FailedRequest, FailedAuthentication, FailedRegistration
from musicbot.music import file
from musicbot.music.music_filter import MusicFilter, default_filters

logger = logging.getLogger(__name__)

DEFAULT_EMAIL: Optional[str] = None
DEFAULT_PASSWORD: Optional[str] = None
DEFAULT_FIRST_NAME: Optional[str] = None
DEFAULT_LAST_NAME: Optional[str] = None
DEFAULT_TOKEN: Optional[str] = None


@attr.s(auto_attribs=True, frozen=True)
class User(MusicbotObject):
    api: GraphQL
    token: str

    @classmethod
    def from_token(cls, graphql: str, token: str) -> "User":
        api = GraphQL(graphql, authorization=f"Bearer {token}")
        return cls(api=api, token=token)

    @classmethod
    def from_auth(cls, graphql: str, email: str, password: str) -> "User":
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
            api = GraphQL(graphql=graphql)
            response = api.post(query)
            token = response['data']['authenticate']['jwtToken']
            return cls.from_token(graphql=graphql, token=token)
        except MusicbotError as e:
            raise FailedAuthentication(f"Authentication failed for email {email} : {e}") from e
        except KeyError as e:
            raise FailedAuthentication(f"Invalid response received : {response}") from e

    @classmethod
    @timeit
    def register(cls, graphql: str, email: str, password: str, first_name: str, last_name: str) -> "User":
        query = f"""
        mutation
        {{
            registerUser(input: {{firstName: "{first_name}", lastName: "{last_name}", email: "{email}", password: "{password}"}})
            {{
                clientMutationId
            }}
        }}"""

        try:
            api = GraphQL(graphql=graphql)
            api.post(query)
            return cls.from_auth(
                graphql=graphql,
                email=email,
                password=password
            )
        except MusicbotError as e:
            raise FailedRegistration(f"Registration failed for {first_name} | {last_name} | {email} | {password} : {e}") from e

    @timeit
    def unregister(self) -> Any:
        query = """
        mutation
        {
            unregisterUser(input: {})
            {
                clientMutationId
            }
        }"""
        try:
            return self.execute(query)
        except MusicbotError as e:
            raise FailedAuthentication(f"Cannot delete user : {e}") from e

    @cached_property
    def user_id(self):
        query = """{ currentMusicbot }"""
        return self.fetch(query)['currentMusicbot']

    @timeit
    def execute(self, query: str) -> Any:
        return self.api.post(query)

    @timeit
    def execute_many(self, operations: List[Any]) -> Any:
        return self.api.batch(operations)

    @timeit
    def fetch(self, query: str) -> Any:
        logger.debug(query)
        return self.api.post(query)['data']

    @timeit
    def load_default_filters(self) -> Any:
        operations = []
        for music_filter in default_filters:
            try:
                operation = f"filter_{str(uuid.uuid4().hex)}"
                operations.append({
                    "query": music_filter.upsert_mutation(self.user_id, operation),
                    "operation": operation
                })
            except QuerySyntaxError as e:
                MusicbotObject.err(e)
        return self.execute_many(operations)

    @timeit
    def m3u_playlist(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        query = f"""
        {{
            m3UPlaylist({mf.to_graphql()})
        }}"""
        return self.fetch(query)['m3UPlaylist']

    @timeit
    def m3u_bests(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        query = f"""
        {{
            m3UBests({mf.to_graphql()})
            {{
                nodes
                {{
                    name,
                    content
                }}
            }}
        }}"""
        return self.fetch(query)['m3UBests']['nodes']

    @timeit
    def do_filter(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        if mf.name:
            kwargs = self.get_filter(mf.name)
            mf = MusicFilter(**kwargs)

        query = f"""
        {{
            doFilter({mf.to_graphql()})
            {{
                nodes
                {{
                    title
                    album
                    genre
                    artist
                    number
                    rating
                    duration
                    keywords
                    links
                }}
            }}
        }}"""
        return self.fetch(query)['doFilter']['nodes']

    @timeit
    def do_stat(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        query = f"""
        {{
            doStat({mf.to_graphql()})
            {{
              musics
              artists
              albums
              links
              genres
              keywords
              duration
            }}
        }}"""
        return self.fetch(query)['doStat']

    @timeit
    def insert(self, music) -> Any:
        operation = f"music_{str(uuid.uuid4().hex)}"
        return self.execute(music.upsert_mutation(self.user_id, operation))

    @timeit
    def bulk_insert(self, musics: Collection[file.File]) -> Any:
        if not musics:
            logger.info("no musics to insert")
            return None
        if self.config.debug:
            responses = []
            with self.progressbar(max_value=len(musics)) as pbar:
                for music in musics:
                    try:
                        logger.debug(f"inserting {music}")
                        response = self.insert(music)
                        responses.append(response)
                    except (QuerySyntaxError, FailedRequest) as e:
                        MusicbotObject.err(f"{music} : {e}")
                    finally:
                        pbar.value += 1
                        pbar.update()
            return responses

        operations = []
        for music in musics:
            try:
                operation = f"music_{str(uuid.uuid4().hex)}"
                operations.append({
                    "query": music.upsert_mutation(self.user_id, operation),
                    "operationName": operation,
                })
            except QuerySyntaxError as e:
                MusicbotObject.err(f"{music} : {e}")
        return self.execute_many(operations)

    @timeit
    def count_musics(self) -> int:
        query = '''{ musics { totalCount } }'''
        return int(self.fetch(query)['musics']['totalCount'])

    @timeit
    def count_filters(self) -> int:
        query = '''{ filters { totalCount } }'''
        return int(self.fetch(query)['filters']['totalCount'])

    @timeit
    def artists(self) -> Any:
        query = """
        {
          artistsTreeList {
            name
            albums {
              name
              musics {
                name
              }
            }
          }
        }"""
        return self.fetch(query)['artistsTreeList']

    @timeit
    def genres(self) -> Any:
        query = """
        {
          genresTreeList {
            name
          }
        }"""
        return self.fetch(query)['genresTreeList']

    @timeit
    def get_filter(self, name: str) -> Any:
        default_filter = MusicFilter()
        filter_members = ','.join(default_filter.as_dict().keys())
        query = f"""
        {{
            filters(condition: {{name: "{name}"}})
            {{
                nodes {{
                    name,
                    {filter_members}
                }}
            }}
        }}"""
        if not self.fetch(query)['filters']['nodes']:
            raise FilterNotFound(f'{name} : filter not found')
        return self.fetch(query)['filters']['nodes'][0]

    @timeit
    def list_filters(self) -> Any:
        default_filter = MusicFilter()
        filter_members = ','.join(default_filter.as_dict().keys())
        query = f"""
        {{
            filtersList
            {{
                name,
                {filter_members}
            }}
        }}"""
        return self.fetch(query)['filtersList']

    @timeit
    def delete_filter(self, name: str) -> Any:
        query = f"""
        mutation
        {{
            deleteFilter(input: {{name: "{name}"}})
            {{
                clientMutationId
            }}
        }}"""
        return self.execute(query)

    @timeit
    def delete_music(self, path: str) -> Any:
        query = f"""
        mutation
        {{
            deleteMusic(input: {{path: "{path}"}})
            {{
                clientMutationId
            }}
        }}"""
        return self.execute(query)

    @timeit
    def clean_musics(self) -> Any:
        query = """
        mutation
        {
            deleteAllMusic(input: {})
            {
                clientMutationId
            }
        }"""
        return self.execute(query)
