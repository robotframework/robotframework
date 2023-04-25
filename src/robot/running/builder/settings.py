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

from collections.abc import Sequence
try:
    from typing import TypedDict
except ImportError:
    try:
        from typing_extensions import TypedDict
    except ImportError:
        TypedDict = dict

from robot.model import Tags

from ..model import Keyword


class KeywordDict(TypedDict):
    """Dictionary to create setup or teardown from.

    :attr:`args` and :attr:`lineno` are optional.
    """
    # `args` and `lineno` are not marked optional, because that would be hard
    # until we require Python 3.8 and ugly until Python 3.11.
    name: str
    args: 'Sequence[str]'
    lineno: int


class TestDefaults:
    """Represents default values for test related settings set in init files.

    Parsers parsing suite files can read defaults and parsers parsing init
    files can set them.
    """

    def __init__(self, parent: 'TestDefaults|None' = None):
        self.parent = parent
        self.setup = None
        self.teardown = None
        self.tags = ()
        self.timeout = None

    @property
    def setup(self) -> 'Keyword|None':
        """Default setup as a ``Keyword`` object or ``None`` when not set.

        Can be set also using a dictionary.
        """
        if self._setup:
            return self._setup
        if self.parent:
            return self.parent.setup
        return None

    @setup.setter
    def setup(self, setup: 'Keyword|KeywordDict|None'):
        if isinstance(setup, dict):
            setup = Keyword.from_dict(setup)
        self._setup = setup

    @property
    def teardown(self) -> 'Keyword|None':
        """Default teardown as a ``Keyword`` object or ``None`` when not set.

        Can be set also using a dictionary.
        """
        if self._teardown:
            return self._teardown
        if self.parent:
            return self.parent.teardown
        return None

    @teardown.setter
    def teardown(self, teardown: 'Keyword|KeywordDict|None'):
        if isinstance(teardown, dict):
            teardown = Keyword.from_dict(teardown)
        self._teardown = teardown

    @property
    def tags(self) -> Tags:
        """Default tags. Can be set also as a sequence."""
        return self._tags + self.parent.tags if self.parent else self._tags

    @tags.setter
    def tags(self, tags: 'Sequence[str]'):
        self._tags = Tags(tags)

    @property
    def timeout(self) -> 'str|None':
        """Default timeout."""
        if self._timeout:
            return self._timeout
        if self.parent:
            return self.parent.timeout
        return None

    @timeout.setter
    def timeout(self, timeout: 'str|None'):
        self._timeout = timeout


class FileSettings:

    def __init__(self, test_defaults: 'TestDefaults|None' = None):
        self.test_defaults = test_defaults or TestDefaults()
        self._test_setup = None
        self._test_teardown = None
        self._test_tags = Tags()
        self._test_timeout = None
        self._test_template = None
        self._default_tags = Tags()
        self._keyword_tags = Tags()

    @property
    def test_setup(self) -> 'Keyword|None':
        return self._test_setup or self.test_defaults.setup

    @test_setup.setter
    def test_setup(self, setup: KeywordDict):
        self._test_setup = Keyword.from_dict(setup)

    @property
    def test_teardown(self) -> 'Keyword|None':
        return self._test_teardown or self.test_defaults.teardown

    @test_teardown.setter
    def test_teardown(self, teardown: KeywordDict):
        self._test_teardown = Keyword.from_dict(teardown)

    @property
    def test_tags(self) -> Tags:
        return self._test_tags + self.test_defaults.tags

    @test_tags.setter
    def test_tags(self, tags: 'Sequence[str]'):
        self._test_tags = Tags(tags)

    @property
    def test_timeout(self) -> 'str|None':
        return self._test_timeout or self.test_defaults.timeout

    @test_timeout.setter
    def test_timeout(self, timeout: str):
        self._test_timeout = timeout

    @property
    def test_template(self) -> 'str|None':
        return self._test_template

    @test_template.setter
    def test_template(self, template: str):
        self._test_template = template

    @property
    def default_tags(self) -> Tags:
        return self._default_tags

    @default_tags.setter
    def default_tags(self, tags: 'Sequence[str]'):
        self._default_tags = Tags(tags)

    @property
    def keyword_tags(self) -> Tags:
        return self._keyword_tags

    @keyword_tags.setter
    def keyword_tags(self, tags: 'Sequence[str]'):
        self._keyword_tags = Tags(tags)


class InitFileSettings(FileSettings):

    @FileSettings.test_setup.setter
    def test_setup(self, setup: KeywordDict):
        self.test_defaults.setup = setup

    @FileSettings.test_teardown.setter
    def test_teardown(self, teardown: KeywordDict):
        self.test_defaults.teardown = teardown

    @FileSettings.test_tags.setter
    def test_tags(self, tags: 'Sequence[str]'):
        self.test_defaults.tags = tags

    @FileSettings.test_timeout.setter
    def test_timeout(self, timeout: str):
        self.test_defaults.timeout = timeout
