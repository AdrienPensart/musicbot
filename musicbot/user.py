import logging
import time
import base64
import json
import functools
from typing import Any, Collection, Optional
import attr
from watchdog.observers import Observer  # type: ignore
from musicbot.graphql import GraphQL
from musicbot.config import config
from musicbot.exceptions import MusicbotError, FailedAuthentication, FailedRegistration
from musicbot.music import file
from musicbot.music.music_filter import MusicFilter

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class User:
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
    @config.timeit
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

    @config.timeit
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

    @config.timeit
    def execute(self, query: str) -> Any:
        return self.api.post(query)

    @config.timeit
    def fetch(self, query: str) -> Any:
        logger.debug(query)
        return self.api.post(query)['data']

    @config.timeit
    def load_default_filters(self) -> Any:
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
        return self.execute(query)

    @config.timeit
    def playlist(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        query = f"""
        {{
            playlist({mf.to_graphql()})
        }}"""
        return self.fetch(query)['playlist']

    @config.timeit
    def bests(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
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
        return self.fetch(query)['bests']['nodes']

    @config.timeit
    def do_filter(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
        if mf.name:
            kwargs = self.get_filter(mf.name)
            print(kwargs)
            mf = MusicFilter(**kwargs)

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
        return self.fetch(query)['doFilter']['nodes']

    @config.timeit
    def do_stat(self, mf: Optional[MusicFilter] = None) -> Any:
        mf = mf if mf is not None else MusicFilter()
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
        return self.fetch(query)['doStat']

    @config.timeit
    def upsert_music(self, music: file.File) -> Any:
        query = f"""
        mutation
        {{
            upsertMusic(input: {{{music.to_graphql()}}})
            {{
                clientMutationId
            }}
        }}"""
        return self.execute(query)

    @config.timeit
    def bulk_insert(self, musics: Collection[file.File]) -> Any:
        if not musics:
            logger.info("no musics to insert")
            return None
        if config.debug:
            with config.progressbar(max_value=len(musics), redirect_stdout=True) as pbar:
                for music in musics:
                    try:
                        logger.debug(f"inserting {music}")
                        self.upsert_music(music)
                    finally:
                        pbar.value += 1
                        pbar.update()
            return None

        j = json.dumps([m.as_dict() for m in musics])
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
        return self.execute(query)

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def folders(self) -> Any:
        query = """
        {
            foldersList
        }"""
        return self.fetch(query)['foldersList']

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def count_musics(self) -> int:
        query = '''
        {
            rawMusics
            {
                totalCount
            }
        }
        '''
        return int(self.fetch(query)['rawMusics']['totalCount'])

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def count_filters(self) -> int:
        query = '''
        {
            filters
            {
                totalCount
            }
        }
        '''
        return int(self.fetch(query)['filters']['totalCount'])

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def artists(self) -> Any:
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
        return self.fetch(query)['artistsTreeList']

    @functools.lru_cache(maxsize=None)
    @config.timeit
    def genres(self) -> Any:
        query = """
        {
          genresTreeList {
            name
          }
        }"""
        return self.fetch(query)['genresTreeList']

    @functools.lru_cache(maxsize=None)
    @config.timeit
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
        return self.fetch(query)['filters']['nodes'][0]

    @functools.lru_cache(maxsize=None)
    @config.timeit
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

    def watch(self) -> None:
        from .watcher import MusicWatcherHandler
        logger.info(f'Watching: {self.folders()}')
        event_handler = MusicWatcherHandler(user=self)
        observer = Observer()
        for f in self.folders():
            observer.schedule(event_handler, f, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(50)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    @config.timeit
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

    @config.timeit
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

    @config.timeit
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
