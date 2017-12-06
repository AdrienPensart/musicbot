# -*- coding: utf-8 -*-
import click
from lib.filter import Filter


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


db = [
    click.option('--host', envvar='MB_DB_HOST', help='DB host', default='localhost'),
    click.option('--port', envvar='MB_DB_PORT', help='DB port', default=5432),
    click.option('--database', envvar='MB_DB', help='DB name', default='musicbot'),
    click.option('--user', envvar='MB_DB_USER', help='DB user', default='postgres'),
    click.option('--password', envvar='MB_DB_PASSWORD', help='DB password', default='musicbot')
]

default_fields = ['title', 'album', 'artist', 'genre', 'path', 'keywords', 'folder', 'rating', 'number', 'folder', 'youtube', 'duration', 'size']
tag = [
    click.option('--fields', envvar='MB_FIELDS', help='Show only those fields', default=default_fields, multiple=True),
    click.option('--output', envvar='MB_OUTPUT', help='Tags output format'),
]

filters = [
    click.option('--filter', envvar='MB_FILTER', help='Filter file to load', type=click.File('r')),
    click.option('--limit', envvar='MB_LIMIT', help='Fetch a maximum limit of music', default=2147483647),
    click.option('--youtube', envvar='MB_YOUTUBE', help='Select musics with a youtube link', default=None, is_flag=True),
    click.option('--formats', envvar='MB_FORMATS', help='Select musics with file format', default=Filter.formats),
    click.option('--no-formats', envvar='MB_NO_FORMATS', help='Filter musics without format', multiple=True),
    click.option('--keywords', envvar='MB_KEYWORDS', help='Select musics with keywords', multiple=True),
    click.option('--no-keywords', envvar='MB_NO_KEYWORDS', help='Filter musics without keywords', multiple=True),
    click.option('--artists', envvar='MB_ARTISTS', help='Select musics with artists', multiple=True),
    click.option('--no-artists', envvar='MB_NO_ARTISTS', help='Filter musics without artists', multiple=True),
    click.option('--albums', envvar='MB_ALBUMS', help='Select musics with albums', multiple=True),
    click.option('--no-albums', envvar='MB_NO_ALBUMS', help='Filter musics without albums', multiple=True),
    click.option('--titles', envvar='MB_TITLES', help='Select musics with titles', multiple=True),
    click.option('--no-titles', envvar='MB_NO_TITLES', help='Filter musics without titless', multiple=True),
    click.option('--genres', envvar='MB_GENRES', help='Select musics with genres', multiple=True),
    click.option('--no-genres', envvar='MB_NO_GENRES', help='Filter musics without genres', multiple=True),
    click.option('--min-duration', envvar='MB_MIN_DURATION', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', envvar='MB_MAX_DURATION', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size', envvar='MB_MIN_SIZE', help='Minimum file size filter (in bytes)'),
    click.option('--max-size', envvar='MB_MAX_SIZE', help='Maximum file size filter (in bytes)'),
    click.option('--min-rating', envvar='MB_MIN_RATING', help='Minimum rating', default=Filter.min_rating),
    click.option('--max-rating', envvar='MB_MAX_RATING', help='Maximum rating', default=Filter.max_rating),
    click.option('--relative', envvar='MB_RELATIVE', help='Generate relatives paths', is_flag=True),
    click.option('--shuffle', envvar='MB_SHUFFLE', help='Randomize selection', is_flag=True),
]
