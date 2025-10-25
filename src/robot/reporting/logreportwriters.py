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

from pathlib import Path

from robot.htmldata import HtmlFileWriter, LOG, ModelWriter, REPORT
from robot.utils import file_writer

from .jswriter import JsResultWriter, SplitLogWriter


class _LogReportWriter:
    usage = None

    def __init__(self, js_model):
        self._js_model = js_model

    def _write_file(self, path: Path, config, template):
        if isinstance(path, Path):
            outfile = file_writer(path, usage=self.usage)
        else:
            outfile = path  # unit test hook
        with outfile:
            model_writer = RobotModelWriter(outfile, self._js_model, config)
            writer = HtmlFileWriter(outfile, model_writer)
            writer.write(template)


class LogWriter(_LogReportWriter):
    usage = "log"

    def write(self, path: "Path|str", config):
        if isinstance(path, str):
            path = Path(path)
        self._write_file(path, config, LOG)
        if self._js_model.split_results:
            self._write_split_logs(path)

    def _write_split_logs(self, path: Path):
        for index, (kws, strings) in enumerate(self._js_model.split_results, start=1):
            name = f"{path.stem}-{index}.js"
            self._write_split_log(index, kws, strings, path.with_name(name))

    def _write_split_log(self, index, kws, strings, path: Path):
        with file_writer(path, usage=self.usage) as outfile:
            writer = SplitLogWriter(outfile)
            writer.write(kws, strings, index, path.name)


class ReportWriter(_LogReportWriter):
    usage = "report"

    def write(self, path: "Path|str", config):
        if isinstance(path, str):
            path = Path(path)
        self._write_file(path, config, REPORT)


class RobotModelWriter(ModelWriter):

    def __init__(self, output, model, config):
        self._output = output
        self._model = model
        self._config = config

    def write(self, line):
        JsResultWriter(self._output).write(self._model, self._config)
