#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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
from robot.output import LOGGER
from robot.result import ExecutionResult
from robot.utils import unic

from .jsmodelbuilders import JsModelBuilder
from .logreportwriters import LogWriter, ReportWriter
from .xunitwriter import XUnitWriter


class ResultWriter(object):

    def __init__(self, *data_sources):
        self._data_sources = data_sources

    def write_results(self, settings, results=None):
        results = results or Results(self._data_sources, settings)
        if settings.output:
            self._write_output(results.result, settings.output)
        if settings.xunit:
            self._write_xunit(results.result, settings.xunit)
        if settings.log:
            config = dict(settings.log_config, minLevel=results.js_result.min_level)
            self._write_log(results.js_result, settings.log, config)
        if settings.report:
            results.js_result.remove_data_not_needed_in_report()
            self._write_report(results.js_result, settings.report, settings.report_config)
        return results.return_code

    def _write_output(self, result, path):
        self._write('Output', result.save, path)

    def _write_xunit(self, result, path):
        self._write('XUnit', XUnitWriter(result).write, path)

    def _write_log(self, js_result, path, config):
        self._write('Log', LogWriter(js_result).write, path, config)

    def _write_report(self, js_result, path, config):
        self._write('Report', ReportWriter(js_result).write, path, config)

    def _write(self, name, writer, path, *args):
        try:
            writer(path, *args)
        except DataError, err:
            LOGGER.error(unicode(err))
        except EnvironmentError, err:
            # `err.filename` can be different than `path` at least if reading
            # log/report templates or writing split log fails.
            # `unic` is needed due to http://bugs.jython.org/issue1825.
            LOGGER.error("Writing %s file '%s' failed: %s: %s" %
                         (name.lower(), path, err.strerror, unic(err.filename)))
        else:
            LOGGER.output_file(name, path)


class Results(object):

    def __init__(self, data_sources, settings):
        self._data_sources = data_sources \
            if not isinstance(data_sources, basestring) else [data_sources]
        self._settings = settings
        self._result = None
        self._js_result = None
        self.return_code = -1

    @property
    def result(self):
        if self._result is None:
            include_keywords = bool(self._settings.log or
                                    self._settings.output or
                                    self._settings.xunit)
            self._result = ExecutionResult(include_keywords=include_keywords,
                                           *self._data_sources)
            self._result.configure(self._settings.status_rc,
                                   self._settings.suite_config,
                                   self._settings.statistics_config)
            self.return_code = self._result.return_code
        return self._result

    @property
    def js_result(self):
        if self._js_result is None:
            builder = JsModelBuilder(log_path=self._settings.log,
                                     split_log=self._settings.split_log,
                                     prune_input_to_save_memory=True)
            self._js_result = builder.build_from(self.result)
            self._result = None
        return self._js_result
