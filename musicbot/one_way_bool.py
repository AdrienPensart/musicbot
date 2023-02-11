"""Helper module to secure dry mode"""
import traceback
from typing import Any, List, Optional, Union

from musicbot.exceptions import MusicbotError


class OneWayBool:
    """A bool value that go from False=>True or True=>False but only once"""

    def __init__(self, name: str, default: bool):
        self.name: str = name
        self.mode: Optional[bool] = None
        self.default: bool = default
        self.first_set_trace: List[Any] = []

    def set_mode(self, mode: bool, force: Union["OneWayBool", bool] = False) -> None:
        """Will set a value only once, or many times to same value, else raise error"""
        from musicbot.object import MusicbotObject

        if force:
            MusicbotObject.success(f"SETTING {self.name} MODE TO {mode} (forced)")
            self.mode = mode
            return
        if self.mode is None:
            if mode == self.default:
                return

            self.mode = mode
            if self.mode:
                self.first_set_trace = traceback.format_stack()
                MusicbotObject.success(f"SETTING {self.name} MODE TO {self.mode}")
        elif self.mode == mode:
            MusicbotObject.warn(f"{self.name} has already been initialized once with same value {self.mode}")
        else:
            trace = "".join(self.first_set_trace)
            raise MusicbotError(f"{self.name} has already been initialized once to value {self.mode}, cannot change to {mode}\n{trace}")

    def __repr__(self) -> str:
        return f"Mode {self.name} is {self.mode} | default = {self.default}"

    def __bool__(self) -> bool:
        if self.mode is not None:
            return self.mode
        return self.default
