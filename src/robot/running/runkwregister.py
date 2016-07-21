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

import inspect
import warnings

from robot.utils import NormalizedDict, PY3


class _RunKeywordRegister(object):

    def __init__(self):
        self._libs = {}

    def register_run_keyword(self, libname, keyword, args_to_process=None,
                             deprecation_warning=True):
        if deprecation_warning:
            warnings.warn(self._deprecation_warning(), UserWarning)
        if args_to_process is None:
            args_to_process = self._get_args_from_method(keyword)
            keyword = keyword.__name__
        if libname not in self._libs:
            self._libs[libname] = NormalizedDict(ignore=['_'])
        self._libs[libname][keyword] = int(args_to_process)

    def _deprecation_warning(self):
        return ("The API to register run keyword variants and to disable "
                "variable resolving in keyword arguments will change in Robot "
                "Framework 3.1. For more information see issue #2190 <"
                "https://github.com/robotframework/robotframework/issues/2190"
                ">. Use with 'deprecation_warning=False' to avoid related "
                "deprecation warnings.")

    def get_args_to_process(self, libname, kwname):
        if libname in self._libs and kwname in self._libs[libname]:
            return self._libs[libname][kwname]
        return -1

    def is_run_keyword(self, libname, kwname):
        return self.get_args_to_process(libname, kwname) >= 0

    def _get_args_from_method(self, method):
        if PY3:
            raise RuntimeError('Cannot determine arguments to process '
                               'automatically in Python 3.')
        if inspect.ismethod(method):
            return method.__code__.co_argcount - 1
        elif inspect.isfunction(method):
            return method.__code__.co_argcount
        raise ValueError('Needs function or method')


RUN_KW_REGISTER = _RunKeywordRegister()
