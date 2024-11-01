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
from typing import TypedDict

from ..model import TestCase


class OptionalItems(TypedDict, total=False):
    args: 'Sequence[str]'
    lineno: int


class FixtureDict(OptionalItems):
    """Dictionary containing setup or teardown info.

    :attr:`args` and :attr:`lineno` are optional.
    """
    name: str


class TestDefaults:
    """Represents default values for test related settings set in init files.

    Parsers parsing suite files can read defaults and parsers parsing init
    files can set them. The easiest way to set defaults to a test is using
    the :meth:`set_to` method.

    This class is part of the `public parser API`__. When implementing ``parse``
    or ``parse_init`` method so that they accept two arguments, the second is
    an instance of this class. If the class is needed as a type hint, it can
    be imported via :mod:`robot.running` or :mod:`robot.api.interfaces`.

    __ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#parser-interface
    """

    def __init__(self, parent: 'TestDefaults|None' = None,
                 setup: 'FixtureDict|None' = None,
                 teardown: 'FixtureDict|None' = None,
                 tags: 'Sequence[str]' = (),
                 timeout: 'str|None' = None):
        self.parent = parent
        self.setup = setup
        self.teardown = teardown
        self.tags = tags
        self.timeout = timeout

    @property
    def setup(self) -> 'FixtureDict|None':
        """Default setup as a ``Keyword`` object or ``None`` when not set.

        Can be set also using a dictionary.
        """
        if self._setup:
            return self._setup
        if self.parent:
            return self.parent.setup
        return None

    @setup.setter
    def setup(self, setup: 'FixtureDict|None'):
        self._setup = setup

    @property
    def teardown(self) -> 'FixtureDict|None':
        """Default teardown as a ``Keyword`` object or ``None`` when not set.

        Can be set also using a dictionary.
        """
        if self._teardown:
            return self._teardown
        if self.parent:
            return self.parent.teardown
        return None

    @teardown.setter
    def teardown(self, teardown: 'FixtureDict|None'):
        self._teardown = teardown

    @property
    def tags(self) -> 'tuple[str, ...]':
        """Default tags. Can be set also as a sequence."""
        return self._tags + self.parent.tags if self.parent else self._tags

    @tags.setter
    def tags(self, tags: 'Sequence[str]'):
        self._tags = tuple(tags)

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

    def set_to(self, test: TestCase):
        """Sets defaults to the given test.

        Tags are always added to the test. Setup, teardown and timeout are
        set only if the test does not have them set initially.
        """
        if self.tags:
            test.tags += self.tags
        if self.setup and not test.has_setup:
            test.setup.config(**self.setup)
        if self.teardown and not test.has_teardown:
            test.teardown.config(**self.teardown)
        if self.timeout and not test.timeout:
            test.timeout = self.timeout


class FileSettings:

    def __init__(self, test_defaults: 'TestDefaults|None' = None):
        self.test_defaults = test_defaults or TestDefaults()
        self.test_setup = None
        self.test_teardown = None
        self.test_tags = ()
        self.test_timeout = None
        self.test_template = None
        self.default_tags = ()
        self.keyword_tags = ()

    @property
    def test_setup(self) -> 'FixtureDict|None':
        return self._test_setup or self.test_defaults.setup

    @test_setup.setter
    def test_setup(self, setup: 'FixtureDict|None'):
        self._test_setup = setup

    @property
    def test_teardown(self) -> 'FixtureDict|None':
        return self._test_teardown or self.test_defaults.teardown

    @test_teardown.setter
    def test_teardown(self, teardown: 'FixtureDict|None'):
        self._test_teardown = teardown

    @property
    def test_tags(self) -> 'tuple[str, ...]':
        return self._test_tags + self.test_defaults.tags

    @test_tags.setter
    def test_tags(self, tags: 'Sequence[str]'):
        self._test_tags = tuple(tags)

    @property
    def test_timeout(self) -> 'str|None':
        return self._test_timeout or self.test_defaults.timeout

    @test_timeout.setter
    def test_timeout(self, timeout: 'str|None'):
        self._test_timeout = timeout

    @property
    def test_template(self) -> 'str|None':
        return self._test_template

    @test_template.setter
    def test_template(self, template: 'str|None'):
        self._test_template = template

    @property
    def default_tags(self) -> 'tuple[str, ...]':
        return self._default_tags

    @default_tags.setter
    def default_tags(self, tags: 'Sequence[str]'):
        self._default_tags = tuple(tags)

    @property
    def keyword_tags(self) -> 'tuple[str, ...]':
        return self._keyword_tags

    @keyword_tags.setter
    def keyword_tags(self, tags: 'Sequence[str]'):
        self._keyword_tags = tuple(tags)


class InitFileSettings(FileSettings):

    @FileSettings.test_setup.setter
    def test_setup(self, setup: 'FixtureDict|None'):
        self.test_defaults.setup = setup

    @FileSettings.test_teardown.setter
    def test_teardown(self, teardown: 'FixtureDict|None'):
        self.test_defaults.teardown = teardown

    @FileSettings.test_tags.setter
    def test_tags(self, tags: 'Sequence[str]'):
        self.test_defaults.tags = tags

    @FileSettings.test_timeout.setter
    def test_timeout(self, timeout: 'str|None'):
        self.test_defaults.timeout = timeout
