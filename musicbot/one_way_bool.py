"""Helper module to secure dry mode"""
import logging
import os
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Self

from beartype import beartype

logger = logging.getLogger(__name__)


@beartype
@dataclass
class OneWayBool:
    """A bool value that go from False=>True or True=>False but only once"""

    name: str
    default: bool
    mode: bool | None = None
    first_set_trace: list[Any] | None = None

    def set_mode(self, mode: bool, force: Self | bool = False) -> None:
        """Will set a value only once, or many times to same value, else raise error"""
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "")
        if test_name:
            test_name = f" in test {test_name}"
        if force:
            logger.info(f"SETTING {self.name} MODE TO {mode} (forced){test_name}")
            self.mode = mode
            return
        if self.mode is None:
            if mode == self.default:
                return

            self.mode = mode
            if self.mode:
                self.first_set_trace = traceback.format_stack()
                logger.info(f"SETTING {self.name} MODE TO {self.mode}{test_name}")
        elif self.mode == mode:
            logger.warning(f"{self.name} has already been initialized once with same value {self.mode}{test_name}")
        else:
            trace = "".join(self.first_set_trace or [])
            logger.critical(f"{self.name} has already been initialized once to value {self.mode}, cannot change to {mode}{test_name}\n{trace}")
            sys.exit(-1)

    def __repr__(self) -> str:
        return f"Mode {self.name} is {self.mode} | default = {self.default}"

    def __bool__(self) -> bool:
        if self.mode is not None:
            return self.mode
        return self.default
