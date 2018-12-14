import click

MB_SECRET = 'MB_SECRET'
DEFAULT_SECRET = 'my_little_secret'
secret_argument = [click.argument('secret')]
secret_option = [click.option('--secret', envvar=MB_SECRET, help='Secret to sign tokens', default=DEFAULT_SECRET, show_default=False)]
