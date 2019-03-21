import click

DEFAULT_ACOUSTID_APIKEY = "WMdZYqSO2I"
acoustid_apikey_option = click.option('--acoustid-apikey', envvar='MB_ACOUSTID_APIKEY', help='AcoustID API Key', default=DEFAULT_ACOUSTID_APIKEY),
