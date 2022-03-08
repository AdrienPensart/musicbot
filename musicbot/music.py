from attr import frozen


@frozen
class Music:
    title: str
    links: list[str]
    size: int
    genre: str
    album: str
    artist: str
    keywords: list[str]
    length: int
    track: int
    rating: float
