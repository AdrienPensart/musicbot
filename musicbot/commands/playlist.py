import click
import logging
import codecs
import os
from textwrap import indent
from tqdm import tqdm
from musicbot.lib import helpers, mfilter, user
from musicbot.lib.config import config

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(user.auth_options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Playlist management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(mfilter.options)
@click.argument('path', type=click.File('w'), default='-')
def new(ctx, path, **kwargs):
    '''Generate a new playlist'''
    mf = mfilter.Filter(**kwargs)
    p = ctx.obj.u().playlist(mf)
    if not config.dry:
        print(p, file=path)
    else:
        logger.info('DRY RUN: Writing playlist to %s with content:\n%s', path, p)


@cli.command()
@click.pass_context
@helpers.add_options(mfilter.options)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
def bests(ctx, path, prefix, suffix, **kwargs):
    '''Generate bests playlists with some rules'''
    mf = mfilter.Filter(**kwargs)
    if prefix:
        ctx.obj.mf.relative = True
    playlists = ctx.obj.u().bests(mf)
    print(playlists)
    with tqdm(total=len(playlists), desc="Bests playlists", disable=config.quiet) as pbar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'] + suffix + '.m3u')
            content = indent(p['content'], prefix, lambda line: line != '#EXTM3U')
            if not config.dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        logger.debug('Writing playlist to %s with content:\n%s', playlist_filepath, content)
                        playlist_file.write(content)
                except Exception as e:
                    logger.info('Unable to write playlist to %s because of %s', playlist_filepath, e)
            else:
                logger.info('DRY RUN: Writing playlist to %s with content:\n%s', playlist_filepath, content)
            pbar.update(1)
