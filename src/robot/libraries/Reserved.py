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

RESERVED_KEYWORDS = ['for', 'while', 'break', 'continue', 'end',
                     'if', 'else', 'elif', 'else if', 'return']


class Reserved(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def get_keyword_names(self):
        return RESERVED_KEYWORDS

    def run_keyword(self, name, args):
        error = "'%s' is a reserved keyword." % name.title()
        if name in ('else', 'else if'):
            error += (" It must be in uppercase (%s) when used as a marker"
                      " with 'Run Keyword If'." % name.upper())
        raise Exception(error)
