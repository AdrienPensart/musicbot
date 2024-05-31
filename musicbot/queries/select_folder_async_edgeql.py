# AUTOGENERATED FROM 'musicbot/queries/select_folder.edgeql' WITH:
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
class SelectFolderResult(NoPydanticValidation):
    id: uuid.UUID
    ipv4: str
    name: str
    username: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    size: int
    human_size: str
    all_artists: str
    all_keywords: str
    n_artists: int
    n_albums: int
    n_genres: int
    n_keywords: int
    all_genres: str
    length: int
    duration: datetime.timedelta
    human_duration: str
    n_musics: int


async def select_folder(
    executor: edgedb.AsyncIOExecutor,
) -> list[SelectFolderResult]:
    return await executor.query(
        """\
        select Folder {*} order by .name\
        """,
    )
