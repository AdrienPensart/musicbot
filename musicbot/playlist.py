import codecs
import itertools
import logging
import os
import platform
import random
from pathlib import Path
from typing import Any

from attr import asdict, frozen
from click_skeleton.helpers import PrettyDefaultDict
from click_skeleton.helpers import \
    seconds_to_human as formatted_seconds_to_human
from prompt_toolkit import HTML, Application, print_formatted_text
from prompt_toolkit.application import get_app, run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from rich.table import Column, Table
from rich.text import Text

from musicbot.defaults import DEFAULT_VLC_PARAMS
from musicbot.file import File
from musicbot.helpers import bytes_to_human, precise_seconds_to_human
from musicbot.music import Music
from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject

logging.getLogger("vlc").setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)


@frozen
class Playlist(MusicbotObject):
    musics: list[Music]
    name: str | None = None
    music_filter: MusicFilter | None = None

    @classmethod
    def from_files(cls, files: list[File]) -> "Playlist":
        return cls(
            musics=[file.to_music() for file in files]
        )

    def print(
        self,
        output: str,
        current_title: str | None = None,
        current_album: str | None = None,
        current_artist: str | None = None,
        shuffle: bool = False,
        interleave: bool = False,
    ) -> None:
        musics = self.musics
        if interleave:
            musics_by_artist = PrettyDefaultDict(list)
            for music in self.musics:
                musics_by_artist[music.artist].append(music)
            musics = list(itertools.chain(*itertools.zip_longest(*musics_by_artist.values())))

        if shuffle:
            random.shuffle(musics)

        table = Table(
            Column("T/N", vertical="middle", justify="center", no_wrap=True),
            Column("Artist/Album/Title/Genre", vertical="middle", no_wrap=True),
            Column("Rating", vertical="middle", justify="center", no_wrap=True),
            Column("Keywords", vertical="middle"),
            Column("Links", no_wrap=True),
            Column("Infos", vertical="middle", no_wrap=True),
            show_lines=True,
        )
        links = []
        total_length = 0
        total_size = 0
        for music in musics:
            infos = formatted_seconds_to_human(music.length)
            infos += "\n"
            infos += bytes_to_human(music.size)
            raw_row: list[str] = [
                str(music.track),
                '\n'.join([music.title, music.artist, music.album, music.genre]),
                str(music.rating),
                '\n'.join(sorted(music.keywords)),
                '\n'.join(sorted(music.links)),
                infos,
            ]
            if music.title == current_title and music.album == current_album and music.artist == current_artist:
                colored_row = [Text(elem, style="green") for elem in raw_row]
                table.add_row(*colored_row)
            else:
                table.add_row(*raw_row)

            for link in music.links:
                links.append(link)

            total_length += music.length
            total_size += music.size

        if output == 'm3u' and self.musics:
            p = '#EXTM3U\n'
            p += '\n'.join(links)
            print(p)
        elif output == 'table' and self.musics:
            self.print_table(table)
        elif output == 'json':
            self.print_json([asdict(music) for music in self.musics])
        else:
            self.err(f"unknown output type : {output}")
        self.success(f"Total length: {precise_seconds_to_human(total_length)} | Total size: {bytes_to_human(total_size)}")

    @property
    def links(self) -> frozenset[str]:
        return frozenset(itertools.chain(*[music.links for music in self.musics]))

    @property
    def genres(self) -> frozenset[str]:
        return frozenset(set(music.genre for music in self.musics))

    @property
    def artists(self) -> frozenset[str]:
        return frozenset(set(music.artist for music in self.musics))

    @property
    def keywords(self) -> frozenset[str]:
        return frozenset(itertools.chain(*[music.keywords for music in self.musics]))

    @property
    def ratings(self) -> frozenset[float]:
        return frozenset(set(music.rating for music in self.musics))

    def write(self, filepath: Path) -> None:
        if not self.links:
            return
        content = '#EXTM3U\n' + '\n'.join(self.links)
        if self.dry:
            self.success(f'DRY RUN: Writing playlist to {filepath} with content:\n{content}')
            return
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with codecs.open(str(filepath), 'w', "utf-8-sig") as playlist_file:
                logger.debug(f'Writing playlist to {filepath} with content:\n{content}')
                playlist_file.write(content)
        except (OSError, LookupError, ValueError, UnicodeError) as e:
            logger.warning(f'Unable to write playlist to {filepath} because of {e}')

    def play(self, vlc_params: str = DEFAULT_VLC_PARAMS) -> None:
        if not self.musics:
            self.warn('Empty playlist')
            return

        try:
            if platform.system() == 'Windows':
                vlc_path = r'C:\Program Files\VideoLAN\VLC'
                logger.debug(f"Adding DLL folder {vlc_path}")
                os.add_dll_directory(vlc_path)  # type: ignore
            import vlc  # type: ignore
            instance = vlc.Instance(vlc_params)
            devices = instance.audio_output_enumerate_devices()
            if not devices:
                logger.warning('maybe no audio output detected...')

            if not instance:
                logger.critical('Unable to start VLC instance')
                return

            player = instance.media_list_player_new()
            if not player:
                logger.critical('Unable to create VLC player')
                return

            media_list = instance.media_list_new(list(self.links))
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
                _ = run_in_terminal(play)

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
                _ = run_in_terminal(playlist)

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
                _ = run_in_terminal(_print_help)
                get_app().invalidate()

            def bottom_toolbar() -> Any:
                media_player = player.get_media_player()
                media = media_player.get_media()
                media.parse()
                media_time = formatted_seconds_to_human(round(media_player.get_time() / 1000))
                media_length = formatted_seconds_to_human(round(media_player.get_length() / 1000))
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
