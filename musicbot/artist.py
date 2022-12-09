from attr import fields, frozen

from musicbot.object import MusicbotObject


@frozen
class Artist(MusicbotObject):
    name: str
    rating: float
    length: int
    size: int
    albums: int
    musics: int
    keywords: frozenset[str]
    genres: frozenset[str]

    @classmethod
    def columns(cls) -> list[str]:
        columns = []
        for field_attribute in fields(cls):  # pylint: disable=not-an-iterable
            columns.append(field_attribute.name.capitalize())
        return columns
