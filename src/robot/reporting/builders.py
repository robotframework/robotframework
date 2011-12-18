#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from __future__ import with_statement


from robot.errors import DataError
from robot.output import LOGGER
from robot.result.outputwriter import OutputWriter

from .xunitwriter import XUnitWriter
from .logreportwriters import LogWriter, ReportWriter


class OutputBuilder(object):

    def __init__(self, model):
        self._model = model

    def build(self, path):
        try:
            writer = OutputWriter(path)
        except DataError, err:
            LOGGER.error(unicode(err))
        else:
            self._model.visit(writer)
            LOGGER.output_file('Output', path)


class XUnitBuilder(object):

    def __init__(self, model):
        self._model = model

    def build(self, path):
        try:
            writer = XUnitWriter(path)
        except EnvironmentError, err:
            LOGGER.error("Opening XUnit result file '%s' failed: %s"
                         % (path, err.strerror))
        else:
            self._model.visit(writer)
            LOGGER.output_file('XUnit', path)



class LogBuilder(object):

    def __init__(self, js_model):
        self._js_model = js_model

    def build(self, path, config):
        try:
            LogWriter(self._js_model).write(path, config)
        except EnvironmentError, err:
            # Cannot use err.filename due to http://bugs.jython.org/issue1825
            # and thus error has wrong file name if writing split log fails.
            LOGGER.error("Writing log file '%s' failed: %s" % (path, err.strerror))
        else:
            LOGGER.output_file('Log', path)



class ReportBuilder(object):

    def __init__(self, js_model):
        self._js_model = js_model

    def build(self, path, config):
        try:
            ReportWriter(self._js_model).write(path, config)
        except EnvironmentError, err:
            LOGGER.error("Writing report file '%s' failed: %s" % (path, err.strerror))
        else:
            LOGGER.output_file('Report', path)
