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

import os
import tempfile
import time

from robot import utils
from robot.common import Statistics
from robot.output import LOGGER, process_outputs, process_output
from robot.version import get_full_version

from templating import Namespace, Template
from outputserializers import OutputSerializer
from xunitserializers import XUnitSerializer
from robot.serializing.serialize_log import serialize_log, serialize_report
from robot.serializing import jsparser


class Reporter(object):

    def __init__(self, settings):
        self._robot_test_output_cached = None
        self._temp_file = None
        self._suite = None
        self._settings = settings

    def _make_report(self, report_path, data_model):
        if report_path:
            data_model.set_settings(self._get_report_settings())
            serialize_report(data_model, report_path)
            LOGGER.output_file('Report', report_path)

    def _get_report_settings(self):
        return {
            'title': self._settings['ReportTitle'],
            'background' : self._resolve_background_colors(),
            'logURL': self._url_from_path(self._parse_file('Report'),
                                          self._parse_file('Log'))
        }

    def _url_from_path(self, source, dest):
        if not dest:
            return None
        return utils.get_link_path(dest, os.path.dirname(source))

    def _resolve_background_colors(self):
        color_str = self._settings['ReportBackground']
        if color_str and color_str.count(':') not in [1, 2]:
            LOGGER.error("Invalid background color '%s'." % color_str)
            color_str = None
        if not color_str:
            color_str = '#99FF66:#FF3333'
        colors = color_str.split(':', 2)
        if len(colors) == 2:
            colors.insert(1, colors[0])
        return {'pass': colors[0], 'nonCriticalFail': colors[1], 'fail': colors[2]}

    def _make_log(self, log_path, data_model):
        if log_path:
            data_model.set_settings(self._get_log_settings())
            serialize_log(data_model, log_path)
            LOGGER.output_file('Log', log_path)

    def _get_log_settings(self):
        return {
            'title': self._settings['ReportTitle'],
            'reportURL': self._url_from_path(self._parse_file('Log'),
                                             self._parse_file('Report'))
        }

    def _make_xunit(self, xunit_path, data_source):
        if xunit_path:
            self._robot_test_output([data_source]).serialize_xunit(xunit_path)

    def _robot_test_output(self, data_sources):
        if self._robot_test_output_cached is None:
            self._suite, exec_errors = process_outputs(data_sources, self._settings)
            self._suite.set_options(self._settings)
            self._robot_test_output_cached = RobotTestOutput(self._suite, exec_errors, self._settings)
        return self._robot_test_output_cached

    def _combine_outputs(self, data_sources):
        output_file = self._parse_file('Output')
        if output_file is None:
            handle, output_file = tempfile.mkstemp(suffix='.xml', prefix='rebot-')
            os.close(handle)
            self._temp_file = output_file
        self._robot_test_output(data_sources).serialize_output(output_file, log=not self._temp_file)
        return output_file

    def execute_rebot(self, *data_sources):
        combined = self._combine_outputs(data_sources)
        self.execute(combined)
        if self._temp_file:
            os.remove(self._temp_file)
        return self._suite

    def execute(self, data_source):
        data_model = jsparser.create_datamodel_from(data_source)
        data_model.set_generated(time.localtime())
        log_path = self._parse_file('Log')
        report_path = self._parse_file('Report')
        self._make_log(log_path, data_model)
        data_model.remove_keywords()
        self._make_report(report_path, data_model)
        xunit_path = self._parse_file('XUnitFile')
        self._make_xunit(xunit_path, data_source)

    def _parse_file(self, name):
        value = self._settings[name]
        return value if value != 'NONE' else None


class RobotTestOutput:

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
        serializer = OutputSerializer(path)
        self.suite.serialize(serializer)
        self.statistics.serialize(serializer)
        self.exec_errors.serialize(serializer)
        serializer.close()
        if log:
            LOGGER.output_file('Output', path)

    def serialize_xunit(self, path):
        if path == 'NONE':
            return
        serializer = XUnitSerializer(path)
        try:
            self.suite.serialize(serializer)
        finally:
            serializer.close()
        LOGGER.output_file('XUnit', path)

