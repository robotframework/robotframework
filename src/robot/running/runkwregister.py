#  Copyright 2008-2014 Nokia Solutions and Networks
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

import inspect

from robot.utils import NormalizedDict


class _RunKeywordRegister:

    def __init__(self):
        self._libs = {}

    def register_run_keyword(self, libname, keyword, args_to_process=None):
        if args_to_process is None:
            args_to_process = self._get_args_from_method(keyword)
            keyword = keyword.__name__
        if libname not in self._libs:
            self._libs[libname] = NormalizedDict(ignore=['_'])
        self._libs[libname][keyword] = int(args_to_process)

    def get_args_to_process(self, libname, kwname):
        if libname in self._libs and kwname in self._libs[libname]:
            return self._libs[libname][kwname]
        return -1

    def is_run_keyword(self, libname, kwname):
        return self.get_args_to_process(libname, kwname) >= 0

    def _get_args_from_method(self, method):
        if inspect.ismethod(method):
            return method.im_func.func_code.co_argcount - 1
        elif inspect.isfunction(method):
            return method.func_code.co_argcount
        raise ValueError('Needs function or method')


RUN_KW_REGISTER = _RunKeywordRegister()
