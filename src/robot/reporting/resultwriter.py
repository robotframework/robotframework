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

from robot.errors import DataError
from robot.output import LOGGER
from robot.reporting.jsondatamodel import DataModelWriter
from robot.result.builders import ResultFromXML as RFX
from robot.result.combiningvisitor import CombiningVisitor, KeywordRemovingVisitor
from robot.result.datamodel import JSModelCreator
from robot.result.serializer import RebotXMLWriter
from robot import utils

from robot.reporting.xunitwriter import XUnitWriter
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
            self.result.visit(CombiningVisitor(creator, KeywordRemovingVisitor()))
            self._data_model = DataModelWriter(creator.datamodel, creator.split_results)
        return self._data_model

    @property
    def result_from_xml(self):
        if self._xml_result is None:
            #TODO: RFX and ResultFromXML name conflict
            execution_result = RFX(*self._data_sources)
            execution_result.configure(status_rc=not self.settings['NoStatusRC'],
                                       **self.settings.result_configuration())
            self._xml_result = ResultFromXML(execution_result, self.settings)
        return self._xml_result

    @property
    def result(self):
        return self.result_from_xml.result


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
        return self.result_from_xml.result


class ResultFromXML(object):

    def __init__(self, execution_result, settings=None):
        self.result = execution_result
        self._settings = settings
        self._generator = 'Robot'

    def serialize_output(self, path, log=True):
        if path == 'NONE':
            return
        if self._settings:
            settings = self._settings
            params = (settings['SuiteStatLevel'], settings['TagStatInclude'],
                      settings['TagStatExclude'], settings['TagStatCombine'],
                      settings['TagDoc'], settings['TagStatLink'])
        else:
            params = ()
        self.result.configure_statistics(*params)
        serializer = RebotXMLWriter(path)
        self.result.visit(serializer)
        if log:
            LOGGER.output_file('Output', path)

    def serialize_xunit(self, path):
        if path == 'NONE':
            return
        serializer = XUnitWriter(path)
        try:
            self.result.suite.visit(serializer)
        except:
            raise DataError("Writing XUnit result file '%s' failed: %s" %
                            (path, utils.get_error_message()))
        finally:
            serializer.close()
        LOGGER.output_file('XUnit', path)

