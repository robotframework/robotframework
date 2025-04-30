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

from collections.abc import Iterable, Mapping

from robot.utils import NormalizedDict


class Metadata(NormalizedDict[str]):
    """Free suite metadata as a mapping.

    Keys are case, space, and underscore insensitive.
    """

    def __init__(
        self,
        initial: "Mapping[str, str]|Iterable[tuple[str, str]]|None" = None,
    ):
        super().__init__(initial, ignore="_")

    def __setitem__(self, key: str, value: str):
        if not isinstance(key, str):
            key = str(key)
        if not isinstance(value, str):
            value = str(value)
        super().__setitem__(key, value)

    def __str__(self):
        items = ", ".join(f"{key}: {self[key]}" for key in self)
        return f"{{{items}}}"
