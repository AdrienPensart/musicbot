from typing import Final, Optional

from attr import frozen

from musicbot.helpers import current_user, get_public_ip

DEFAULT_SFTP: Final[bool] = False
DEFAULT_HTTP: Final[bool] = False
DEFAULT_LOCAL: Final[bool] = True
# DEFAULT_SPOTIFY: Final[bool] = False
# DEFAULT_YOUTUBE: Final[bool] = False


@frozen
class LinkOptions:
    sftp: bool = DEFAULT_SFTP
    http: bool = DEFAULT_HTTP
    local: bool = DEFAULT_LOCAL
    http_port: Optional[int] = None
    root: Optional[str] = None
    ssh_user: Optional[str] = current_user()
    public_ip: Optional[str] = get_public_ip()
    # spotify: bool = DEFAULT_SPOTIFY
    # youtube: bool = DEFAULT_YOUTUBE


DEFAULT_LINK_OPTIONS = LinkOptions()
