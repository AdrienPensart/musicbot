import click

MB_CLIENT_ID='MB_CLIENT_ID'
MB_CLIENT_SECRET='MB_CLIENT_SECRET'
MB_TOKEN='MB_TOKEN'

options = [
    click.option('--client-id', help='Spotify client ID', envvar=MB_CLIENT_ID, default=None),
    click.option('--client-secret', help='Spotify client secret', envvar=MB_CLIENT_SECRET, default=None),
    click.option('--token', help='Spotify token', envvar=MB_TOKEN, default=None)
]
