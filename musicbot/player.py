import logging
import platform
import os
from typing import Any, Iterable, Dict
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal, get_app
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import HTML, print_formatted_text
from click_skeleton.helpers import seconds_to_human
from .playlist import print_playlist

logger = logging.getLogger(__name__)
logging.getLogger("vlc").setLevel(logging.NOTSET)


def play(tracks: Iterable[Dict[str, str]]) -> None:
    if not tracks:
        logger.warning('Empty playlist')
        return

    try:
        if platform.system() == 'Windows':
            os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')  # type: ignore
        import vlc  # type: ignore
        instance = vlc.Instance()
        if not instance:
            logger.critical('Unable to start VLC instance')
            return

        player = instance.media_list_player_new()
        if not player:
            logger.critical('Unable to create VLC player')
            return

        tracks_path = [track['path'] for track in tracks]
        media_list = instance.media_list_new(tracks_path)
        if not media_list:
            logger.critical('Unable to create VLC media list')
            return

        player.set_media_list(media_list)
        bindings = KeyBindings()

        def print_help() -> None:
            print_formatted_text(HTML('<violet>Bindings: q = quit | p = play | s = pause/continue | right = next song | left = previous song | l = playlist</violet>'))

        @bindings.add('p')
        def _play_binding(event: Any) -> None:  # pylint: disable=unused-argument
            def play() -> None:
                """Play song"""
                player.play()
            run_in_terminal(play)

        @bindings.add('q')
        def _quit_binding(event: Any) -> None:
            player.pause()
            event.app.exit()

        @bindings.add('s')
        def _pause_binding(event: Any) -> None:  # pylint: disable=unused-argument
            player.pause()

        @bindings.add('l')
        def _playlist_binding(event: Any) -> None:  # pylint: disable=unused-argument
            def playlist() -> None:
                """List songs"""
                media_player = player.get_media_player()
                media = media_player.get_media()
                media.parse()
                current_artist = media.get_meta(vlc.Meta.Artist)
                current_album = media.get_meta(vlc.Meta.Album)
                current_title = media.get_meta(vlc.Meta.Title)
                print_playlist(tracks, current_artist=current_artist, current_album=current_album, current_title=current_title)
            run_in_terminal(playlist)

        @bindings.add('right')
        def _next_binding(event: Any) -> None:  # pylint: disable=unused-argument
            player.next()

        @bindings.add('left')
        def _previous_binding(event: Any) -> None:  # pylint: disable=unused-argument
            player.previous()

        @bindings.add('h')
        def _help(event: Any) -> None:  # pylint: disable=unused-argument
            def _print_help() -> None:
                print_help()
            run_in_terminal(_print_help)
            get_app().invalidate()

        def bottom_toolbar() -> Any:
            media_player = player.get_media_player()
            media = media_player.get_media()
            media.parse()
            media_time = seconds_to_human(round(media_player.get_time() / 1000))
            media_length = seconds_to_human(round(media_player.get_length() / 1000))
            artist = media.get_meta(vlc.Meta.Artist)
            album = media.get_meta(vlc.Meta.Album)
            title = media.get_meta(vlc.Meta.Title)
            current = f'({media_time} / {media_length}) {artist} - {album} - {title}'
            get_app().invalidate()
            return HTML(f'Current song: {current}')

        print_help()
        player.play()

        root_container = HSplit(
            [Window(FormattedTextControl(lambda: bottom_toolbar, style='class:bottom-toolbar.text'), style='class:bottom-toolbar')]
        )
        layout = Layout(root_container)
        app: Any = Application(layout=layout, key_bindings=bindings)
        app.run()
    except NameError:
        version = vlc.libvlc_get_version()
        logger.critical(f"Your VLC version may be outdated: {version}")
