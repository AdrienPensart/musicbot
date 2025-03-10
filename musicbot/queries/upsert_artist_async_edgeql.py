# AUTOGENERATED FROM 'musicbot/queries/upsert_artist.edgeql' WITH:
#     $ gel-py --dir musicbot/queries -I musicbot-prod


from __future__ import annotations

import dataclasses
import uuid

import gel


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

        _ = pydantic_dataclass(cls)
        cls.__pydantic_model__.__get_validators__ = lambda: []
        return []


@dataclasses.dataclass
class UpsertArtistResult(NoPydanticValidation):
    id: uuid.UUID


async def upsert_artist(
    executor: gel.AsyncIOExecutor,
    *,
    artist: str,
) -> UpsertArtistResult:
    return await executor.query_single(
        """\
        select (
            insert Artist {
                name := <str>$artist
            }
            unless conflict on (.name) else (select Artist)
        ) {id}\
        """,
        artist=artist,
    )
