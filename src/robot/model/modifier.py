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
from robot.utils import get_error_details, type_name, Importer

from .visitor import SuiteVisitor


class ModelModifier(SuiteVisitor):

    def __init__(self, visitors, logger):
        self._log_error = logger.error
        self._visitors = list(self._import_visitors(visitors))

    def visit_suite(self, suite):
        for visitor in self._visitors:
            try:
                suite.visit(visitor)
            except:
                message, details = get_error_details()
                self._log_error("Executing model modifier '%s' failed: %s\n%s"
                                % (type_name(visitor), message, details))

    def _import_visitors(self, visitors):
        importer = Importer('model modifier')
        for visitor, args in visitors:
            try:
                yield importer.import_class_or_module(visitor, args)
            except DataError as err:
                self._log_error(unicode(err))
