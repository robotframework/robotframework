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



# TODO: Most (all?) of this class is dead code
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

    def serialize(self, settings, generator='Robot', output=None):
        self._generator = generator
        self.serialize_output(settings['Output'], settings['SplitOutputs'])
        self.serialize_summary(settings['Summary'], settings['SummaryTitle'],
                               settings['ReportBackground'])
        datamodel = jsparser.create_datamodel_from(output)
        serialize_report(datamodel, settings['Report'], settings['ReportTitle'], settings['Log'])
        LOGGER.output_file('Report', settings['Report'])
        serialize_log(datamodel, settings['Log'], settings['LogTitle'])
        LOGGER.output_file('Log', settings['Log'])
        self.serialize_xunit(settings['XUnitFile'])

    def serialize_output(self, path, split=-1, log=True):
        if path == 'NONE':
            return
        serializer = OutputSerializer(path, split)
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

    def serialize_summary(self, path, title=None, background=None):
        outfile = self._get_outfile(path, 'summary')
        if not outfile:
            return
        self._use_template(outfile, templates.REPORT,
                           title or '%s Summary Report' % self.suite.name,
                           self._get_background_color(background))
        self.statistics.serialize(SummaryStatSerializer(outfile))
        outfile.write('</body>\n</html>\n')
        outfile.close()
        LOGGER.output_file('Summary', path)

    def _get_background_color(self, colors):
        all_passed, critical_passed, failures \
                = self._resolve_background_colors(colors)
        if self.suite.all_stats:
            return all_passed
        if self.suite.critical_stats:
            return critical_passed
        return failures

    def _resolve_background_colors(self, color_str):
        if color_str and color_str.count(':') not in [1, 2]:
            LOGGER.error("Invalid background color '%s'." % color_str)
            color_str = None
        if not color_str:
            color_str = '#99FF66:#FF3333'
        colors = color_str.split(':', 2)
        return colors if len(colors) == 3 else [colors[0], colors[0], colors[1]]

    def serialize_report(self, path, title=None, background=None,
                         logpath=None, split=-1):
        outfile = self._get_outfile(path, 'report')
        if not outfile:
            return
        self._use_template(outfile, templates.REPORT,
                           title or '%s Test Report' % self.suite.name,
                           self._get_background_color(background))
        self.statistics.serialize(ReportStatSerializer(outfile))
        logpath = logpath if logpath != 'NONE' else None
        if split > 0 and logpath:
            self.suite.serialize(SplitReportSerializer(outfile, logpath, split))
        else:
            self.suite.serialize(ReportSerializer(outfile, logpath))
        self.statistics.tags.serialize(TagDetailsSerializer(outfile))
        outfile.write('</body>\n</html>\n')
        outfile.close()
        LOGGER.output_file('Report', path)

    def serialize_log(self, path, title=None, split=-1):
        outfile = self._get_outfile(path, 'log')
        if not outfile:
            return
        self._use_template(outfile, templates.LOG,
                           title or '%s Test Log' % self.suite.name)
        if split > 0:
            self._serialize_split_log(outfile, split)
        else:
            self._serialize_log(outfile)
        outfile.write('</body>\n</html>\n')
        outfile.close()
        LOGGER.output_file('Log', path)

    def _serialize_log(self, outfile):
        self.statistics.serialize(LogStatSerializer(outfile))
        self.exec_errors.serialize(ErrorSerializer(outfile))
        self.suite.serialize(LogSerializer(outfile))

    def _serialize_split_log(self, outfile, level):
        self.statistics.serialize(SplitLogStatSerializer(outfile, level))
        self.exec_errors.serialize(ErrorSerializer(outfile))
        self.suite.serialize(SplitLogSerializer(outfile, level))
        self._create_split_sub_logs(self.suite, level)

    def _create_split_sub_logs(self, suite, level):
        # Overridden by RebotTestOutput
        pass

    def _use_template(self, outfile, template, title, background=None):
        ttuple = time.localtime()
        str_time = utils.format_time(ttuple, daytimesep='&nbsp;', gmtsep='&nbsp;')
        int_time = long(time.mktime(ttuple))
        elapsed_time = utils.elapsed_time_to_string(self.suite.elapsedtime)
        namespace = Namespace(gentime_str=str_time,
                              gentime_int=int_time,
                              elapsed_time=elapsed_time,
                              version=get_full_version(self._generator),
                              suite=self.suite,
                              title=title,
                              background=background)
        Template(template=template).generate(namespace, outfile)

    def _get_outfile(self, outpath, outtype):
        if outpath != 'NONE':
            try:
                return open(outpath, 'wb')
            except:
                LOGGER.error("Opening %s file '%s' for writing failed: %s"
                             % (outtype, outpath, utils.get_error_message()))
        return None


class RebotTestOutput(RobotTestOutput):

    def __init__(self, datasources, settings):
        suite, exec_errors = process_outputs(datasources, settings)
        suite.set_options(settings)
        RobotTestOutput.__init__(self, suite, exec_errors, settings)
        self._namegen = utils.FileNameGenerator(settings['Log'])

    def _create_split_sub_logs(self, suite, split_level, suite_level=0):
        if suite_level < split_level:
            for sub in suite.suites:
                self._create_split_sub_logs(sub, split_level, suite_level+1)
        elif suite_level == split_level:
            self._create_split_sub_log(suite, split_level)

    def _create_split_sub_log(self, suite, split_level):
        outfile = self._get_outfile(self._namegen.get_name(), 'log')
        if not outfile:
            return
        self._use_template(outfile, templates.LOG, '%s Test Log' % suite.name)
        Statistics(suite).serialize(LogStatSerializer(outfile, split_level))
        suite.serialize(LogSerializer(outfile, split_level))
        outfile.write('</body>\n</html>\n')
        outfile.close()


class SplitSubTestOutput(RobotTestOutput):

    def __init__(self, path, settings):
        suite, exec_errors = process_output(path)
        suite.set_critical_tags(settings['Critical'], settings['NonCritical'])
        RobotTestOutput.__init__(self, suite, exec_errors)


class SplitIndexTestOutput(RobotTestOutput):

    def __init__(self, runsuite, path, settings):
        # 'runsuite' is the one got when running tests and 'outsuite' is read
        # from xml. The former contains information (incl. stats) about all
        # tests but no messages. The latter contains messages but no info
        # about tests in splitted outputs.
        outsuite, exec_errors = process_output(path, settings['SplitOutputs'])
        self._update_stats(outsuite, runsuite)
        RobotTestOutput.__init__(self, runsuite, exec_errors, settings)
        self._outsuite = outsuite

    def _update_stats(self, outsuite, runsuite):
        outsuite.critical_stats = runsuite.critical_stats
        outsuite.all_stats = runsuite.all_stats
        outsuite.status = runsuite.status
        for outsub, runsub in zip(outsuite.suites, runsuite.suites):
            self._update_stats(outsub, runsub)

    def _serialize_split_log(self, outfile, level):
        self.statistics.serialize(SplitLogStatSerializer(outfile, level))
        self.exec_errors.serialize(ErrorSerializer(outfile))
        self._outsuite.serialize(SplitLogSerializer(outfile, level))
