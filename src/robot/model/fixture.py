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

from collections.abc import Mapping
from typing import Type, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from robot.model import DataDict, Keyword, TestCase, TestSuite
    from robot.running.model import UserKeyword


T = TypeVar("T", bound="Keyword")


def create_fixture(
    fixture_class: Type[T],
    fixture: "T|DataDict|None",
    parent: "TestCase|TestSuite|Keyword|UserKeyword",
    fixture_type: str,
) -> T:
    """Create or configure a `fixture_class` instance."""
    # If a fixture instance has been passed in update the config
    if isinstance(fixture, fixture_class):
        return fixture.config(parent=parent, type=fixture_type)
    # If a Mapping has been passed in, create a fixture instance from it
    if isinstance(fixture, Mapping):
        return fixture_class.from_dict(fixture).config(parent=parent, type=fixture_type)
    # If nothing has been passed in then return a new fixture instance from it
    if fixture is None:
        return fixture_class(None, parent=parent, type=fixture_type)
    raise TypeError(f"Invalid fixture type '{type(fixture).__name__}'.")
