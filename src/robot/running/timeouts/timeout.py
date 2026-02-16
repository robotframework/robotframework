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

import time
from collections.abc import Callable, Mapping, Sequence

from robot.errors import DataError, TimeoutExceeded
from robot.utils import secs_to_timestr, Sortable, timestr_to_secs

from .runner import Runner


class Timeout(Sortable):
    kind: str

    def __init__(
        self,
        timeout: "float|str|None" = None,
        variables=None,
        start: bool = False,
    ):
        try:
            self.timeout = self._parse(timeout, variables)
        except (DataError, ValueError) as err:
            self.timeout = 0.000001  # to make timeout active
            self.string = str(timeout)
            self.error = f"Setting {self.kind.lower()} timeout failed: {err}"
        else:
            self.string = secs_to_timestr(self.timeout) if self.timeout else "NONE"
            self.error = None
        if start:
            self.start()
        else:
            self.start_time = -1

    def _parse(self, timeout, variables) -> "float|None":
        if not timeout:
            return None
        if variables:
            timeout = variables.replace_string(timeout)
        else:
            timeout = str(timeout)
        if timeout.upper() in ("NONE", ""):
            return None
        timeout = timestr_to_secs(timeout)
        if timeout <= 0:
            return None
        return timeout

    def start(self):
        if self.timeout is None:
            raise ValueError("Cannot start inactive timeout.")
        self.start_time = time.time()

    def time_left(self) -> float:
        if self.start_time < 0:
            raise ValueError("Timeout is not started.")
        return self.timeout - (time.time() - self.start_time)

    def timed_out(self) -> bool:
        return self.time_left() <= 0

    def get_runner(self) -> Runner:
        """Get a runner that can run code with a timeout."""
        timeout_error = TimeoutExceeded(
            f"{self.kind.title()} timeout {self} exceeded.",
            test_timeout=self.kind != "KEYWORD",
        )
        data_error = DataError(self.error) if self.error else None
        return Runner.for_platform(self.time_left(), timeout_error, data_error)

    def run(
        self,
        runnable: "Callable[..., object]",
        args: "Sequence|None" = None,
        kwargs: "Mapping|None" = None,
    ) -> object:
        """Convenience method to directly run code with a timeout."""
        return self.get_runner().run(runnable, args, kwargs)

    def get_message(self):
        kind = self.kind.title()
        if self.start_time < 0:
            return f"{kind} timeout not active."
        left = self.time_left()
        if left > 0:
            return f"{kind} timeout {self} active. {left:.3f} seconds left."
        return f"{kind} timeout {self} exceeded."

    def __str__(self):
        return self.string

    def __bool__(self):
        return self.timeout is not None

    @property
    def _sort_key(self):
        if self.timeout is None:
            raise ValueError("Cannot compare inactive timeout.")
        return self.time_left()

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


class TestTimeout(Timeout):
    kind = "TEST"
    _keyword_timeout_occurred = False

    def __init__(
        self,
        timeout: "float|str|None" = None,
        variables=None,
        start: bool = False,
        rpa: bool = False,
    ):
        self.kind = "TASK" if rpa else self.kind
        super().__init__(timeout, variables, start)

    def set_keyword_timeout(self, timeout_occurred):
        if timeout_occurred:
            self._keyword_timeout_occurred = True

    def any_timeout_occurred(self):
        return self.timed_out() or self._keyword_timeout_occurred


class KeywordTimeout(Timeout):
    kind = "KEYWORD"
