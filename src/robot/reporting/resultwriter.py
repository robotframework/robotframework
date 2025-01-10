#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.conf import RebotSettings
from robot.errors import DataError
from robot.model import ModelModifier
from robot.output import LOGGER
from robot.result import ExecutionResult, Result

from .jsmodelbuilders import JsModelBuilder
from .logreportwriters import LogWriter, ReportWriter
from .xunitwriter import XUnitWriter


class ResultWriter:
    """A class to create log, report, output XML and xUnit files.

    :param sources: Either one :class:`~robot.result.executionresult.Result`
        object, or one or more paths to existing output XML files.

    By default writes ``report.html`` and ``log.html``, but no output XML
    or xUnit files. Custom file names can be given and results disabled
    or enabled using ``settings`` or ``options`` passed to the
    :meth:`write_results` method. The latter is typically more convenient::

        writer = ResultWriter(result)
        writer.write_results(report='custom.html', log=None, xunit='xunit.xml')
    """

    def __init__(self, *sources):
        self._sources = sources

    def write_results(self, settings=None, **options):
        """Writes results based on the given ``settings``  or ``options``.

        :param settings: :class:`~robot.conf.settings.RebotSettings` object
            to configure result writing.
        :param options: Used to construct new
            :class:`~robot.conf.settings.RebotSettings` object if ``settings``
            are not given.
        """
        settings = settings or RebotSettings(options)
        results = Results(settings, *self._sources)
        if settings.output:
            self._write_output(results.result, settings.output, settings.legacy_output)
        if settings.xunit:
            self._write_xunit(results.result, settings.xunit)
        if settings.log:
            config = dict(settings.log_config,
                          minLevel=results.js_result.min_level)
            self._write_log(results.js_result, settings.log, config)
        if settings.report:
            results.js_result.remove_data_not_needed_in_report()
            self._write_report(results.js_result, settings.report,
                               settings.report_config)
        return results.return_code

    def _write_output(self, result, path, legacy_output=False):
        self._write('Output', result.save, path, legacy_output)

    def _write_xunit(self, result, path):
        self._write('XUnit', XUnitWriter(result).write, path)

    def _write_log(self, js_result, path, config):
        self._write('Log', LogWriter(js_result).write, path, config)

    def _write_report(self, js_result, path, config):
        self._write('Report', ReportWriter(js_result).write, path, config)

    def _write(self, name, writer, path, *args):
        try:
            writer(path, *args)
        except DataError as err:
            LOGGER.error(err.message)
        else:
            LOGGER.result_file(name, path)


class Results:

    def __init__(self, settings, *sources):
        self._settings = settings
        self._sources = sources
        if len(sources) == 1 and isinstance(sources[0], Result):
            self._result = sources[0]
            self._prune = False
            self.return_code = self._result.return_code
        else:
            self._result = None
            self._prune = True
            self.return_code = -1
        self._js_result = None

    @property
    def result(self):
        if self._result is None:
            include_keywords = bool(self._settings.log or self._settings.output)
            flattened = self._settings.flatten_keywords
            self._result = ExecutionResult(include_keywords=include_keywords,
                                           flattened_keywords=flattened,
                                           merge=self._settings.merge,
                                           rpa=self._settings.rpa,
                                           *self._sources)
            if self._settings.rpa is None:
                self._settings.rpa = self._result.rpa
            if self._settings.pre_rebot_modifiers:
                modifier = ModelModifier(self._settings.pre_rebot_modifiers,
                                        self._settings.process_empty_suite,
                                        LOGGER)
                self._result.suite.visit(modifier)
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
                                     expand_keywords=self._settings.expand_keywords,
                                     prune_input_to_save_memory=self._prune)
            self._js_result = builder.build_from(self.result)
            if self._prune:
                self._result = None
        return self._js_result
