from attr import frozen

from musicbot.defaults import (
    DEFAULT_INTERLEAVE,
    DEFAULT_KINDS,
    DEFAULT_RELATIVE,
    DEFAULT_SHUFFLE
)


@frozen
class PlaylistOptions:
    name: str
    relative: bool = DEFAULT_RELATIVE
    shuffle: bool = DEFAULT_SHUFFLE
    interleave: bool = DEFAULT_INTERLEAVE
    kinds: frozenset[str] = DEFAULT_KINDS
