# AUTOGENERATED FROM 'musicbot/queries/select_artists.edgeql' WITH:
#     $ edgedb-py -I musicbot-prod --dir musicbot/queries


from __future__ import annotations

import dataclasses
import datetime
import uuid

import edgedb


class NoPydanticValidation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        # Pydantic 2.x
        from pydantic_core.core_schema import any_schema

        return any_schema()

    @classmethod
    def __get_validators__(cls):
        # Pydantic 1.x
        from pydantic.dataclasses import dataclass as pydantic_dataclass

        pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class SelectArtistsResult(NoPydanticValidation):
    id: uuid.UUID
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    size: int
    human_size: str
    all_genres: str
    all_keywords: str
    length: int
    duration: datetime.timedelta
    human_duration: str
    n_albums: int
    n_genres: int
    n_musics: int
    rating: float


async def select_artists(
    executor: edgedb.AsyncIOExecutor,
) -> list[SelectArtistsResult]:
    return await executor.query(
        """\
        select Artist {*} order by .name\
        """,
    )