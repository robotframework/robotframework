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
from robot.result.builders import ResultFromXML
from robot.result.combiningvisitor import CombiningVisitor, KeywordRemovingVisitor
from robot.result.datamodel import JSModelCreator

from .builders import LogBuilder, ReportBuilder, XUnitBuilder, OutputBuilder


class ResultWriter(object):

    def __init__(self, settings):
        self._settings = settings

    def write_results(self, *data_sources):
        settings = self._settings
        result = Result(settings, data_sources)
        if settings.output:
            OutputBuilder(result.model).build(settings.output)
        if settings.xunit:
            XUnitBuilder(result.model).build(settings.xunit)
        if settings.log:
            LogBuilder(result.js_model).build(settings.log,
                                              settings.log_configuration())
        if settings.report:
            result.js_model.remove_errors()
            result.js_model.remove_keywords()
            ReportBuilder(result.js_model).build(settings.report,
                                                 settings.report_configuration())
        return result.return_code


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
            self._model = ResultFromXML(*self._data_sources)
            # TODO: configure and configure_statistics really should be combined somehow
            self._model.configure_statistics(*self._settings.statistics_configuration())
            self._model.configure(status_rc=self._settings.status_rc,
                                  **self._settings.result_configuration())
        return self._model

    @property
    def js_model(self):
        if self._js_model is None:
            creator = JSModelCreator(log_path=self._settings.log,
                                     split_log=self._settings.split_log)
            self.model.visit(CombiningVisitor(creator, KeywordRemovingVisitor()))
            self._js_model = creator.datamodel
        return self._js_model
