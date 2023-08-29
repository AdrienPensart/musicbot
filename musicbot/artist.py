# from dataclasses import dataclass, fields
from dataclasses import dataclass

from beartype import beartype

from musicbot.object import MusicbotObject


@beartype
@dataclass(frozen=True)
class Artist(MusicbotObject):
    name: str
    rating: float
    length: int
    size: int
    albums: int
    musics: int
    keywords: frozenset[str]
    genres: frozenset[str]

    # @classmethod
    # def columns(cls) -> list[str]:
    #     columns = []
    #     for field_attribute in fields(cls):  # pylint: disable=not-an-iterable
    #         columns.append(field_attribute.name.capitalize())
    #     return columns
