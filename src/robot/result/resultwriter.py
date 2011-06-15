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
from robot.output import LOGGER, process_outputs

from outputwriter import OutputWriter
from xunitwriter import XUnitWriter
from writer import serialize_log, serialize_report
import jsparser


class ResultWriter(object):

    def __init__(self, settings):
        self._xml_result = None
        self._suite = None
        self._settings = settings

    def write_robot_results(self, data_source):
        data_model = jsparser.create_datamodel_from(data_source)
        data_model.set_generated(time.localtime())
        LogBuilder(data_model, self._settings).create()
        data_model.remove_keywords()
        ReportBuilder(data_model, self._settings).create()
        XUnitBuilder(self._result_from_xml([data_source]),
                     self._settings).create()

    def _result_from_xml(self, data_sources):
        if not self._xml_result:
            self._suite, errs = process_outputs(data_sources, self._settings)
            self._suite.set_options(self._settings)
            self._xml_result = ResultFromXML(self._suite, errs, self._settings)
        return self._xml_result

    def write_rebot_results(self, *data_sources):
        builder = OutputBuilder(self._result_from_xml(data_sources),
                                self._settings)
        self.write_robot_results(builder.create())
        builder.finalize()
        return self._suite


class _Builder(object):

    def __init__(self, data_model, settings):
        self._settings = settings
        self._path = self._parse_file(self._type)
        self._data_model = data_model

    def create(self):
        if self._path:
            self._data_model.set_settings(self._get_settings())
            self._create()
            LOGGER.output_file(self._type, self._path)

    def _parse_file(self, name):
        value = self._settings[name]
        return value if value != 'NONE' else None

    def _url_from_path(self, source, dest):
        if not dest:
            return None
        return utils.get_link_path(dest, os.path.dirname(source))


class LogBuilder(_Builder):
    _type = 'Log'

    def _create(self):
        serialize_log(self._data_model, self._path)

    def _get_settings(self):
        return {
            'title': self._settings['LogTitle'],
            'reportURL': self._url_from_path(self._path,
                                             self._parse_file('Report'))
        }


class ReportBuilder(_Builder):
    _type = 'Report'

    def _create(self):
        serialize_report(self._data_model, self._path)

    def _get_settings(self):
        return {
            'title': self._settings['ReportTitle'],
            'background' : self._resolve_background_colors(),
            'logURL': self._url_from_path(self._path,
                                          self._parse_file('Log'))
        }

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


class OutputBuilder(_Builder):
    _type = 'Output'
    _temp_file = None

    def create(self):
        output_file = self._output_file()
        self._data_model.serialize_output(output_file, log=not self._temp_file)
        return output_file

    def _output_file(self):
        if self._path:
            return self._path
        handle, output_file = tempfile.mkstemp(suffix='.xml', prefix='rebot-')
        os.close(handle)
        self._temp_file = output_file
        return output_file

    def finalize(self):
        if self._temp_file:
            os.remove(self._temp_file)


class XUnitBuilder(_Builder):
    _type = 'XUnitFile'

    def create(self):
        if self._path:
            self._data_model.serialize_xunit(self._path)


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

