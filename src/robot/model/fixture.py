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

from .keyword import Keyword


def create_fixture(fixture, parent, fixture_type) -> Keyword:
    # TestCase and TestSuite have 'fixture_class', Keyword doesn't.
    fixture_class = getattr(parent, 'fixture_class', parent.__class__)
    if isinstance(fixture, fixture_class):
        return fixture.config(parent=parent, type=fixture_type)
    if isinstance(fixture, Mapping):
        return fixture_class.from_dict(fixture).config(parent=parent, type=fixture_type)
    if fixture is None:
        return fixture_class(None, parent=parent, type=fixture_type)
    raise TypeError(f"Invalid fixture type '{type(fixture).__name__}'.")
