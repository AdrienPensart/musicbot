# AUTOGENERATED FROM 'musicbot/queries/delete_musics.edgeql' WITH:
#     $ gel-py --dir musicbot/queries -I musicbot-test


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
class DeleteMusicsResult(NoPydanticValidation):
    id: uuid.UUID


async def delete_musics(
    executor: gel.AsyncIOExecutor,
) -> list[DeleteMusicsResult]:
    return await executor.query(
        """\
        delete Artist;\
        """,
    )
