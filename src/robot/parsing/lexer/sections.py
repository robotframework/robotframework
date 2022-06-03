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

from robot.utils import normalize_whitespace

from .tokens import Token


class Sections:

    def __init__(self, markers):
        self.markers = markers

    def setting(self, statement):
        return self._handles(statement, self.markers.setting_section)

    def variable(self, statement):
        return self._handles(statement, self.markers.variable_section)

    def test_case(self, statement):
        return False

    def task(self, statement):
        return False

    def keyword(self, statement):
        return self._handles(statement, self.markers.keyword_section)

    def comment(self, statement):
        return self._handles(statement, self.markers.comment_section)

    def _handles(self, statement, validator):
        marker = statement[0].value
        return marker.startswith('*') and validator(self._normalize(marker))

    def _normalize(self, marker):
        return normalize_whitespace(marker).strip('* ').title()

    def lex_invalid(self, statement):
        message, fatal = self._get_invalid_section_error(statement[0].value)
        statement[0].set_error(message, fatal)
        for token in statement[1:]:
            token.type = Token.COMMENT

    def _get_invalid_section_error(self, header):
        raise NotImplementedError


class TestCaseFileSections(Sections):

    def test_case(self, statement):
        return self._handles(statement, self.markers.test_case_section)

    def task(self, statement):
        return self._handles(statement, self.markers.task_section)

    def _get_invalid_section_error(self, header):
        return ("Unrecognized section header '%s'. Valid sections: "
                "'Settings', 'Variables', 'Test Cases', 'Tasks', "
                "'Keywords' and 'Comments'." % header), False


class ResourceFileSections(Sections):

    def _get_invalid_section_error(self, header):
        name = self._normalize(header)
        if self.markers.test_case_section(name) or self.markers.task_section(name):
            message = "Resource file with '%s' section is invalid." % name
            fatal = True
        else:
            message = ("Unrecognized section header '%s'. Valid sections: "
                       "'Settings', 'Variables', 'Keywords' and 'Comments'."
                       % header)
            fatal = False
        return message, fatal


class InitFileSections(Sections):

    def _get_invalid_section_error(self, header):
        name = self._normalize(header)
        if self.markers.test_case_section(name) or self.markers.task_section(name):
            message = ("'%s' section is not allowed in suite initialization "
                       "file." % name)
        else:
            message = ("Unrecognized section header '%s'. Valid sections: "
                       "'Settings', 'Variables', 'Keywords' and 'Comments'."
                       % header)
        return message, False
