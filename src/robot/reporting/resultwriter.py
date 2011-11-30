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

from robot.reporting.jsondatamodel import DataModelWriter
from robot.result.builders import ResultFromXML
from robot.result.combiningvisitor import CombiningVisitor, KeywordRemovingVisitor
from robot.result.datamodel import JSModelCreator

from robot.reporting.builders import LogBuilder, ReportBuilder, XUnitBuilder, OutputBuilder


class _ResultWriter(object):

    def __init__(self, settings):
        self.settings = settings
        self._xml_result = None
        self._data_model = None
        self._data_sources = []

    @property
    def data_model(self):
        if self._data_model is None:
            creator = JSModelCreator(log_path=self.settings['Log'],
                                     split_log=self.settings['SplitLog'])
            self.result_from_xml.visit(CombiningVisitor(creator, KeywordRemovingVisitor()))
            self._data_model = DataModelWriter(creator.datamodel, creator.split_results)
        return self._data_model

    @property
    def result_from_xml(self):
        if self._xml_result is None:
            self._xml_result = ResultFromXML(*self._data_sources)
            # TODO: configure and configure_statistics really should be combined somehow
            self._xml_result.configure_statistics(*self.settings.statistics_configuration())
            self._xml_result.configure(status_rc=not self.settings['NoStatusRC'],
                                       **self.settings.result_configuration())
        return self._xml_result


class RobotResultWriter(_ResultWriter):

    def write_results(self, data_source):
        self._data_sources = [data_source]
        XUnitBuilder(self).build()
        LogBuilder(self).build()
        ReportBuilder(self).build()


class RebotResultWriter(_ResultWriter):

    def write_results(self, *data_sources):
        self._data_sources = data_sources
        OutputBuilder(self).build()
        XUnitBuilder(self).build()
        LogBuilder(self).build()
        ReportBuilder(self).build()
        return self.result_from_xml.return_code
