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

import functools

from robot.errors import DataError
from robot.utils import PY2

try:
    from docutils.core import publish_doctree
    from docutils.parsers.rst import directives
    from docutils.parsers.rst import roles
    from docutils.parsers.rst.directives import register_directive
    from docutils.parsers.rst.directives.body import CodeBlock
    from docutils.parsers.rst.directives.misc import Include
except ImportError:
    raise DataError("Using reStructuredText test data requires having "
                    "'docutils' module version 0.9 or newer installed.")


class RobotDataStorage(object):

    def __init__(self, doctree):
        if not hasattr(doctree, '_robot_data'):
            doctree._robot_data = []
        self._robot_data = doctree._robot_data

    def add_data(self, rows):
        self._robot_data.extend(rows)

    def get_data(self):
        return '\n'.join(self._robot_data)

    def has_data(self):
        return bool(self._robot_data)


class RobotCodeBlock(CodeBlock):

    def run(self):
        if 'robotframework' in self.arguments:
            store = RobotDataStorage(self.state_machine.document)
            store.add_data(self.content)
        return []


register_directive('code', RobotCodeBlock)
register_directive('code-block', RobotCodeBlock)
register_directive('sourcecode', RobotCodeBlock)


relevant_directives = (RobotCodeBlock, Include)


@functools.wraps(directives.directive)
def directive(*args, **kwargs):
    directive_class, messages = directive.__wrapped__(*args, **kwargs)
    if directive_class not in relevant_directives:
        # Skipping unknown or non-relevant directive entirely
        directive_class = (lambda *args, **kwargs: [])
    return directive_class, messages


@functools.wraps(roles.role)
def role(*args, **kwargs):
    role_function = role.__wrapped__(*args, **kwargs)
    if role_function is None:  # role is unknown, ignore
        role_function = (lambda *args, **kwargs: [], [])
    return role_function


if PY2:
    directive.__wrapped__ = directives.directive
    role.__wrapped__ = roles.role


directives.directive = directive
roles.role = role


def read_rest_data(rstfile):
    doctree = publish_doctree(
        rstfile.read(),
        source_path=rstfile.name,
        settings_overrides={
            'input_encoding': 'UTF-8',
        })
    store = RobotDataStorage(doctree)
    return store.get_data()
