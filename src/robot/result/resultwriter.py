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

from robot.common import Statistics
from robot.output import LOGGER, process_outputs

from outputwriter import OutputWriter
from xunitwriter import XUnitWriter
from builders import LogBuilder, ReportBuilder, XUnitBuilder, OutputBuilder
import jsparser


class ResultWriter(object):

    def __init__(self, settings):
        self._xml_result = None
        self._suite = None
        self._settings = settings
        self._data_sources = None

    def write_robot_results(self, data_source):
        self._data_sources = [data_source]
        self._data_model = None
        LogBuilder(self).build()
        ReportBuilder(self).build()
        XUnitBuilder(self).build()

    @property
    def data_model(self):
        if self._data_model is None:
            self._data_model = jsparser.create_datamodel_from(self._data_sources[0], self._settings['SplitLog'])
        return self._data_model

    @property
    def settings(self):
        return self._settings

    @property
    def result_from_xml(self):
        if self._xml_result is None:
            self._suite, errs = process_outputs(self._data_sources, self._settings)
            self._suite.set_options(self._settings)
            self._xml_result = ResultFromXML(self._suite, errs, self._settings)
        return self._xml_result

    def write_rebot_results(self, *data_sources):
        self._data_sources = data_sources
        builder = OutputBuilder(self)
        self.write_robot_results(builder.build())
        builder.finalize()
        return self._suite


class ResultFromXML(object):

    def __init__(self, suite, exec_errors, settings=None):
        self.suite = suite
        self.exec_errors = exec_errors
        if settings:
            params = (settings['SuiteStatLevel'], settings['TagStatInclude'],
                      settings['TagStatExclude'], settings['TagStatCombine'],
                      settings['TagDoc'], settings['TagStatLink'])
        else:
            params = ()
        self.statistics = Statistics(suite, *params)
        self._generator = 'Robot'

    def serialize_output(self, path, log=True):
        if path == 'NONE':
            return
        serializer = OutputWriter(path)
        self.suite.serialize(serializer)
        self.statistics.serialize(serializer)
        self.exec_errors.serialize(serializer)
        serializer.close()
        if log:
            LOGGER.output_file('Output', path)

    def serialize_xunit(self, path):
        if path == 'NONE':
            return
        serializer = XUnitWriter(path)
        try:
            self.suite.serialize(serializer)
        finally:
            serializer.close()
        LOGGER.output_file('XUnit', path)

