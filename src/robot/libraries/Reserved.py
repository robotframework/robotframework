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

from robot.running import RUN_KW_REGISTER


RESERVED_KEYWORDS = ['for', 'while', 'break', 'continue', 'end',
                     'if', 'else', 'elif', 'else if', 'return']


class Reserved(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        for kw in RESERVED_KEYWORDS:
            self._add_reserved(kw)

    def _add_reserved(self, kw):
        RUN_KW_REGISTER.register_run_keyword('Reserved', kw,
                                             args_to_process=0,
                                             deprecation_warning=False)
        self.__dict__[kw] = lambda *args, **kwargs: self._run_reserved(kw)

    def _run_reserved(self, kw):
        error = "'%s' is a reserved keyword." % kw.title()
        if kw in ('for', 'end', 'if', 'else', 'else if'):
            error += " It must be an upper case '%s'" % kw.upper()
            if kw in ('else', 'else if'):
                error += " and follow an opening 'IF'"
            if kw == 'end':
                error += " and follow an opening 'FOR' or 'IF'"
            error += " when used as a marker."
        if kw == 'elif':
            error += " The marker to use with 'IF' is 'ELSE IF'."
        raise Exception(error)
