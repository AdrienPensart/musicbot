import click
from musicbot import defaults
from musicbot.helpers import config_string

acoustid_api_key_option = click.option(
    '--acoustid-api-key',
    help='AcoustID API Key',
    default=defaults.DEFAULT_ACOUSTID_API_KEY,
    callback=config_string,
)
