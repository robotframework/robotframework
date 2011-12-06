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

from __future__ import with_statement
from contextlib import contextmanager
import os.path

from robot.utils import timestamp_to_secs, get_link_path, html_format
from robot.output import LEVELS

from robot.result.jsexecutionresult import JsExecutionResult
from .parsingcontext import TextCache as StringCache


class NewParsingContext(object):

    def __init__(self, log_path=None):
        self._log_dir = os.path.dirname(log_path) if log_path else None
        self._strings = self._orig_strings = StringCache()
        self.basemillis = None

    def string(self, string):
        return self._strings.add(string)

    def html(self, string):
        return self.string(html_format(string))

    def relative_source(self, source):
        rel_source = get_link_path(source, self._log_dir) \
            if self._log_dir and source and os.path.exists(source) else ''
        return self.string(rel_source)

    def timestamp(self, time):
        if time == 'N/A':   # TODO: Should definitely use None in model!
            return None
        # Must use `long` due to http://ironpython.codeplex.com/workitem/31549
        millis = long(round(timestamp_to_secs(time) * 1000))
        if self.basemillis is None:
            self.basemillis = millis
        return millis - self.basemillis

    @property
    def strings(self):
        return self._strings.dump()

    @property
    @contextmanager
    def splitting(self):
        self._strings = StringCache()
        yield
        self._strings = self._orig_strings


# TODO: Change order of items in JS model to be more consistent with "normal" model?

class JsModelBuilder(object):
    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}
    _kw_types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self, log_path=None, split_log=False):
        self._split_log = split_log
        self._context = NewParsingContext(log_path)
        self._string = self._context.string
        self._html = self._context.html
        self._timestamp = self._context.timestamp
        self._relative_source = self._context.relative_source
        self._split_results = []

    def build_from(self, result_from_xml):
        return JsExecutionResult(
            suite=self._build_suite(result_from_xml.suite),
            statistics=self._build_statistics(result_from_xml.statistics),
            errors=self._build_errors(result_from_xml.errors),
            strings=self._context.strings,
            basemillis=self._context.basemillis,
            split_results=self._split_results
        )

    def _build_suite(self, suite):
        return (self._string(suite.name),
                self._string(suite.source),
                self._relative_source(suite.source),
                self._html(suite.doc),
                tuple(self._yield_metadata(suite)),
                self._get_status(suite),
                tuple(self._build_suite(s) for s in suite.suites),
                tuple(self._build_test(t) for t in suite.tests),
                tuple(self._build_keyword(k, split=True) for k in suite.keywords),
                self._get_statistics(suite))

    def _yield_metadata(self, suite):
        for name, value in suite.metadata.iteritems():
            yield self._string(name)
            yield self._html(value)

    def _get_status(self, item):
        model = (self._statuses[item.status],
                 self._timestamp(item.starttime),
                 item.elapsedtime)
        msg = getattr(item, 'message', '')
        return model if not msg else model + (self._string(msg),)

    def _get_statistics(self, suite):
        stats = suite.statistics  # Access property only once
        return (stats.all.total,
                stats.all.passed,
                stats.critical.total,
                stats.critical.passed)

    def _build_test(self, test):
        return (self._string(test.name),
                self._string(test.timeout),
                int(test.critical == 'yes'),
                self._html(test.doc),
                tuple(self._string(t) for t in test.tags),
                self._get_status(test),
                self._build_keywords(test.keywords, split=True))

    def _build_keywords(self, kws, split=False):
        if not (split and self._split_log):
            return tuple(self._build_keyword(k) for k in kws)
        with self._context.splitting:
            model = self._build_keywords(kws)
            self._split_results.append((model, self._context.strings))
        return len(self._split_results)

    def _build_keyword(self, kw, split=False):
        return (self._kw_types[kw.type],
                self._string(kw.name),
                self._string(kw.timeout),
                self._html(kw.doc),
                self._string(', '.join(kw.args)),
                self._get_status(kw),
                self._build_keywords(kw.keywords, split),
                tuple(self._build_message(m) for m in kw.messages))

    def _build_message(self, msg):
        # TODO: linking
        return (self._timestamp(msg.timestamp),
                LEVELS[msg.level],
                self._string(msg.html_message))

    def _build_statistics(self, statistics):
        return (self._build_stats(statistics.total),
                self._build_stats(statistics.tags),
                self._build_stats(statistics.suite))

    def _build_stats(self, stats):
        return tuple(stat.get_attributes(include_label=True, exclude_empty=True)
                     for stat in stats)
