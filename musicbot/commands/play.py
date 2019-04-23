import logging
import click
import vlc
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal, get_app
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import HTML, print_formatted_text as print
from musicbot import helpers, user
from musicbot.lib import seconds_to_human
from musicbot.music import mfilter

logger = logging.getLogger(__name__)
logging.getLogger("vlc").setLevel(logging.NOTSET)


@click.group(cls=helpers.GroupWithHelp, invoke_without_command=True)
@helpers.add_options(user.auth_options)
@helpers.add_options(mfilter.options)
@click.pass_context
def cli(ctx, email, password, token, graphql, **kwargs):
    '''Music player'''
    ctx.obj.u = lambda: user.User.new(email=email, password=password, token=token, graphql=graphql)
    mf = mfilter.Filter(**kwargs)
    p = ctx.obj.u().do_filter(mf)
    if not p:
        logger.warning('Empty playlist')
        return
    instance = vlc.Instance()
    songs = [song['path'] for song in p]
    player = instance.media_list_player_new()
    media_list = instance.media_list_new(songs)
    player.set_media_list(media_list)
    bindings = KeyBindings()

    @bindings.add('p')
    def _play_binding(event):
        def play():
            """Play song"""
            player.play()
        run_in_terminal(play)

    @bindings.add('q')
    def _quit_binding(event):
        player.pause()
        event.app.exit()

    @bindings.add('s')
    def _pause_binding(event):
        player.pause()

    @bindings.add('l')
    def _playlist_binding(event):
        def playlist():
            """List songs"""
            for s in songs:
                print(s)
        run_in_terminal(playlist)

    @bindings.add('right')
    def _next_binding(event):
        player.next()

    @bindings.add('left')
    def _previous_binding(event):
        player.previous()

    def bottom_toolbar():
        media_player = player.get_media_player()
        media = media_player.get_media()
        media.parse()
        media_time = seconds_to_human(round(media_player.get_time() / 1000))
        media_length = seconds_to_human(round(media_player.get_length() / 1000))
        artist = media.get_meta(vlc.Meta.Artist)
        album = media.get_meta(vlc.Meta.Album)
        title = media.get_meta(vlc.Meta.Title)
        current = '({} / {}) {} - {} - {}'.format(media_time, media_length, artist, album, title)
        get_app().invalidate()
        return HTML('Current song: {}'.format(current))

    player.play()
    print(HTML('Bindings: q = quit | p = play | s = pause/continue | right = next song | left = previous song | l = playlist'))

    root_container = HSplit(
        [Window(FormattedTextControl(lambda: bottom_toolbar, style='class:bottom-toolbar.text'), style='class:bottom-toolbar')]
    )
    layout = Layout(root_container)
    app = Application(layout=layout, key_bindings=bindings)
    app.run()
