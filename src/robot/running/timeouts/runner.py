#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from collections.abc import Callable, Mapping, Sequence

from robot.errors import DataError, TimeoutExceeded
from robot.utils import WINDOWS


class Runner:
    runner_implementation: "type[Runner]|None" = None

    def __init__(
        self,
        timeout: float,
        timeout_error: TimeoutExceeded,
        data_error: "DataError|None" = None,
    ):
        self.timeout = round(timeout, 3)
        self.timeout_error = timeout_error
        self.data_error = data_error
        self.exceeded = False
        self.paused = 0

    @classmethod
    def for_platform(
        cls,
        timeout: float,
        timeout_error: TimeoutExceeded,
        data_error: "DataError|None" = None,
    ) -> "Runner":
        runner = cls.runner_implementation
        if not runner:
            runner = cls.runner_implementation = cls._get_runner_implementation()
        return runner(timeout, timeout_error, data_error)

    @classmethod
    def _get_runner_implementation(cls) -> "type[Runner]":
        if WINDOWS:
            from .windows import WindowsRunner

            return WindowsRunner
        try:
            from .posix import PosixRunner

            return PosixRunner
        except ImportError:
            from .nosupport import NoSupportRunner

            return NoSupportRunner

    def run(
        self,
        runnable: "Callable[..., object]",
        args: "Sequence|None" = None,
        kwargs: "Mapping|None" = None,
    ) -> object:
        if self.data_error:
            raise self.data_error
        if self.timeout <= 0:
            raise self.timeout_error
        try:
            return self._run(lambda: runnable(*(args or ()), **(kwargs or {})))
        finally:
            if self.exceeded and not self.paused:
                raise self.timeout_error from None

    def _run(self, runnable: "Callable[[], object]") -> object:
        raise NotImplementedError

    def pause(self):
        self.paused += 1

    def resume(self):
        self.paused -= 1
        if self.exceeded and not self.paused:
            raise self.timeout_error
