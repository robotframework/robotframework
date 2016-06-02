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

from robot.errors import DataError
from robot.utils import (get_error_details, is_string,
                         split_args_from_name_or_path, type_name, Importer)

from .visitor import SuiteVisitor


class ModelModifier(SuiteVisitor):

    def __init__(self, visitors, empty_suite_ok, logger):
        self._log_error = logger.error
        self._empty_suite_ok = empty_suite_ok
        self._visitors = list(self._yield_visitors(visitors))

    def visit_suite(self, suite):
        for visitor in self._visitors:
            try:
                suite.visit(visitor)
            except:
                message, details = get_error_details()
                self._log_error("Executing model modifier '%s' failed: %s\n%s"
                                % (type_name(visitor), message, details))
        if not (suite.test_count or self._empty_suite_ok):
            raise DataError("Suite '%s' contains no tests after model "
                            "modifiers." % suite.name)

    def _yield_visitors(self, visitors):
        importer = Importer('model modifier')
        for visitor in visitors:
            try:
                if not is_string(visitor):
                    yield visitor
                else:
                    name, args = split_args_from_name_or_path(visitor)
                    yield importer.import_class_or_module(name, args)
            except DataError as err:
                self._log_error(err.message)
