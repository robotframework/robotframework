#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import DataError

try:
    from docutils.core import publish_doctree, publish_from_doctree
    from docutils.parsers.rst.directives import register_directive
    from docutils.parsers.rst.directives.body import CodeBlock
except ImportError:
    raise DataError("Using reStructuredText test data requires having "
                    "'docutils' module version 0.9 or newer installed.")


class CaptureRobotData(CodeBlock):

    def run(self):
        if 'robotframework' in self.arguments:
            store = RobotDataStorage(self.state_machine.document)
            store.add_data(self.content)
        return []


register_directive('code', CaptureRobotData)
register_directive('code-block', CaptureRobotData)
register_directive('sourcecode', CaptureRobotData)


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
