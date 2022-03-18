from attr import frozen


@frozen
class Music:
    title: str
    links: set[str]
    size: int
    genre: str
    album: str
    artist: str
    keywords: set[str]
    length: int
    track: int
    rating: float
