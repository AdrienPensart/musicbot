import click
from musicbot.helpers import config_string

DEFAULT_ACOUSTID_API_KEY = None
acoustid_api_key_option = [
    click.option(
        '--acoustid-api-key',
        help='AcoustID API Key',
        default=DEFAULT_ACOUSTID_API_KEY,
        callback=config_string,
    )
]
