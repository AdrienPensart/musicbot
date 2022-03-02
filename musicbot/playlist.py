import codecs
import itertools
import logging
import os
import platform
import textwrap
from pathlib import Path
from typing import Any, Optional

import attr
from click_skeleton.helpers import seconds_to_human
from prompt_toolkit import HTML, Application, print_formatted_text
from prompt_toolkit.application import get_app, run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from rich.table import Table
from rich.text import Text

from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject

logging.getLogger("vlc").setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True, frozen=True)
class Playlist(MusicbotObject):
    musics: list[Music]
    music_filter: Optional[MusicFilter] = None

    def print(
        self,
        output: str,
        current_title: Optional[str] = None,
        current_album: Optional[str] = None,
        current_artist: Optional[str] = None,
    ) -> None:
        if not self.musics:
            return

        table = Table(*attr.fields_dict(Music))
        links = []
        for music in self.musics:
            colored_title: Text | str = Text(music.title, style="green") if music.title == current_title else music.title
            colored_album: Text | str = Text(music.album, style="green") if music.album == current_album else music.album
            colored_artist: Text | str = Text(music.artist, style="green") if music.artist == current_artist else music.artist
            table.add_row(colored_title, colored_album, colored_artist)
            for link in music.links:
                links.append(link)

        if output == 'm3u':
            p = '#EXTM3U\n'
            p += '\n'.join(links)
            print(p)
            return

        if output == 'table':
            self.print_table(table)

        if output == 'json':
            self.print_json([attr.asdict(music) for music in self.musics])
            return

    @property
    def links(self) -> list[str]:
        return list(itertools.chain(*[music.links for music in self.musics]))

    @property
    def genres(self) -> list[str]:
        return list(set(music.genre for music in self.musics))

    @property
    def artists(self) -> list[str]:
        return list(set(music.artist for music in self.musics))

    @property
    def keywords(self) -> list[str]:
        return list(itertools.chain(*[music.keywords for music in self.musics]))

    @property
    def ratings(self) -> list[float]:
        return list(set(music.rating for music in self.musics))

    def write(self, filepath: Path, prefix: Optional[str]) -> None:
        if not self.links:
            return
        content = '\n'.join(self.links)
        if prefix:
            content = textwrap.indent(content, prefix)
        content = ('#EXTM3U\n' + content)
        if MusicbotObject.dry:
            self.success(f'DRY RUN: Writing playlist to {filepath} with content:\n{content}')
            return
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with codecs.open(str(filepath), 'w', "utf-8-sig") as playlist_file:
                logger.debug(f'Writing playlist to {filepath} with content:\n{content}')
                playlist_file.write(content)
        except (OSError, LookupError, ValueError, UnicodeError) as e:
            logger.warning(f'Unable to write playlist to {filepath} because of {e}')

    def play(self) -> None:
        if not self.musics:
            logger.warning('Empty playlist')
            return

        try:
            if platform.system() == 'Windows':
                os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')  # type: ignore
            import vlc  # type: ignore
            instance = vlc.Instance("--vout=dummy --aout=pulse")
            # devices = instance.audio_output_enumerate_devices()
            # if not devices:
            #     logger.error('no audio output')
            #     return

            # if all(device['name'] != b'pulse' for device in devices):
            #     logger.error('pulse audio is not available, available devices : ')
            #     for device in devices:
            #         logger.error(device['name'])
            #     return

            if not instance:
                logger.critical('Unable to start VLC instance')
                return

            player = instance.media_list_player_new()
            if not player:
                logger.critical('Unable to create VLC player')
                return

            links = [music.links for music in self.musics]
            media_list = instance.media_list_new(links)
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
                    self.print(output='table', current_artist=current_artist, current_album=current_album, current_title=current_title)
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
        except Exception as e:  # pylint:disable=broad-except
            logger.exception(e)
