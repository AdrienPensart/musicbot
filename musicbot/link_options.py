from typing import Final

from attr import frozen

DEFAULT_SFTP: Final[bool] = False
DEFAULT_HTTP: Final[bool] = False
DEFAULT_LOCAL: Final[bool] = True
DEFAULT_SPOTIFY: Final[bool] = False
DEFAULT_YOUTUBE: Final[bool] = False


@frozen
class LinkOptions:
    sftp: bool = DEFAULT_SFTP
    http: bool = DEFAULT_HTTP
    local: bool = DEFAULT_LOCAL
    spotify: bool = DEFAULT_SPOTIFY
    youtube: bool = DEFAULT_YOUTUBE


DEFAULT_LINK_OPTIONS = LinkOptions()
