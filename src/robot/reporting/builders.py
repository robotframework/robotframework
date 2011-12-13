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
import os
import os.path
import codecs

from robot.errors import DataError
from robot.output import LOGGER
from robot.result.serializer import RebotXMLWriter
from robot import utils

from .jswriter import SplitLogWriter
from .xunitwriter import XUnitWriter
from .htmlfilewriter import HtmlFileWriter


class OutputBuilder(object):

    def __init__(self, model):
        self._model = model

    def build(self, path):
        writer = RebotXMLWriter(path)
        self._model.visit(writer)
        LOGGER.output_file('Output', path)


class XUnitBuilder(object):

    def __init__(self, model):
        self._model = model

    def build(self, path):
        writer = XUnitWriter(path) # TODO: handle (with atests) error in opening output file
        try:
            self._model.visit(writer)
        except:
            raise DataError("Writing XUnit result file '%s' failed: %s" %
                            (path, utils.get_error_message()))
        finally:
            writer.close()
        LOGGER.output_file('XUnit', path)


class _HTMLFileBuilder(object):

    def __init__(self, js_model):
        self._js_model = js_model

    def _write_file(self, output, config, template):
        outfile = codecs.open(output, 'wb', encoding='UTF-8') \
            if isinstance(output, basestring) else output  # isinstance is unit test hook
        with outfile:
            writer = HtmlFileWriter(outfile, self._js_model, config)
            writer.write(template)


class LogBuilder(_HTMLFileBuilder):

    def build(self, output, config):
        try:
            self._write_file(output, config, 'log.html')
            self._write_split_logs_if_needed(output)
        except EnvironmentError, err:
            # Cannot use err.filename due to http://bugs.jython.org/issue1825
            # and thus error has wrong file name if writing split log fails.
            LOGGER.error("Writing log file '%s' failed: %s" % (output, err.strerror))
        else:
            LOGGER.output_file('Log', output)

    def _write_split_logs_if_needed(self, output):
        base = os.path.splitext(output)[0] if isinstance(output, basestring) else ''
        for index, (keywords, strings) in enumerate(self._js_model.split_results):
            index += 1  # enumerate accepts start index only in Py 2.6+
            self._write_split_log(index, keywords, strings, '%s-%d.js' % (base, index))

    def _write_split_log(self, index, keywords, strings, path):
        with codecs.open(path, 'wb', encoding='UTF-8') as outfile:
            writer = SplitLogWriter(outfile)
            writer.write(keywords, strings, index, os.path.basename(path))


class ReportBuilder(_HTMLFileBuilder):

    def build(self, path, config):
        try:
            self._write_file(path, config, 'report.html')
        except EnvironmentError, err:
            LOGGER.error("Writing report file '%s' failed: %s" % (path, err.strerror))
        else:
            LOGGER.output_file('Report', path)
