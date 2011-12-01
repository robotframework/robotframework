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


from robot.errors import DATA_ERROR
from robot.result import ResultFromXml
from robot.result.combiningvisitor import CombiningVisitor, KeywordRemovingVisitor
from robot.result.datamodel import JSModelCreator

from .builders import LogBuilder, ReportBuilder, XUnitBuilder, OutputBuilder


class ResultWriter(object):

    def __init__(self, settings):
        self._settings = settings

    def write_results(self, *data_sources):
        settings = self._settings
        result = Result(settings, data_sources)
        self._write_output(result, settings.output)
        self._write_xunit(result, settings.xunit)
        self._write_log(result, settings.log, settings.log_config)
        self._write_report(result, settings.report, settings.report_config)
        return result.return_code

    def _write_output(self, result, output):
        if output:
            OutputBuilder(result.model).build(output)

    def _write_xunit(self, result, xunit):
        if xunit:
            XUnitBuilder(result.model).build(xunit)

    def _write_log(self, result, log, config):
        if log:
            LogBuilder(result.js_model).build(log, config)

    def _write_report(self, result, report, config):
        if report:
            result.js_model.remove_errors()
            result.js_model.remove_keywords()
            ReportBuilder(result.js_model).build(report, config)


class Result(object):

    def __init__(self, settings, data_sources):
        self._settings = settings
        self._data_sources = data_sources
        self._model = None
        self._js_model = None

    @property
    def return_code(self):
        return self._model.return_code if self._model else DATA_ERROR

    @property
    def model(self):
        if self._model is None:
            self._model = ResultFromXml(*self._data_sources)
            self._model.configure(self._settings.status_rc,
                                  self._settings.suite_config,
                                  self._settings.statistics_config)
        return self._model

    @property
    def js_model(self):
        if self._js_model is None:
            creator = JSModelCreator(log_path=self._settings.log,
                                     split_log=self._settings.split_log)
            self.model.visit(CombiningVisitor(creator, KeywordRemovingVisitor()))
            self._js_model = creator.datamodel
        return self._js_model
