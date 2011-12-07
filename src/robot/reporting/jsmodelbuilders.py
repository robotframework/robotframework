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


class JsBuildingContext(object):

    def __init__(self, log_path=None, split_log=False, prune_input=False):
        self._log_dir = os.path.dirname(log_path) \
                if isinstance(log_path, basestring) else None  # isinstance check is unit test hook
        self._split_log = split_log
        self._prune_input = prune_input
        self._strings = self._orig_strings = StringCache()
        self.basemillis = None
        self.split_results = []
        self._msg_links = {}

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

    def create_link_target(self, msg):
        # TODO: Old builder kept id as string. Indexing is better but requires JS changes.
        self._msg_links[self._link_key(msg)] = self.string(msg.parent.id)

    def _link_key(self, msg):
        return (msg.message, msg.level, msg.timestamp)

    def link(self, msg):
        return self._msg_links[self._link_key(msg)]

    @property
    def strings(self):
        return self._strings.dump()

    def start_splitting_if_needed(self, split=False):
        if self._split_log and split:
            self._strings = StringCache()
            return True
        return False

    def end_splitting(self, model):
        self.split_results.append((model, self.strings))
        self._strings = self._orig_strings
        return len(self.split_results)

    @contextmanager
    def prune_input(self, *items):
        yield
        if self._prune_input:
            for item in items:
                item.clear()


# TODO: Change order of items in JS model to be more consistent with "normal" model?

class JsModelBuilder(object):

    def __init__(self, log_path=None, split_log=False,
                 prune_input_to_save_memory=False):
        self._context = JsBuildingContext(log_path, split_log,
                                          prune_input_to_save_memory)

    def build_from(self, result_from_xml):
        return JsExecutionResult(
            suite=SuiteBuilder(self._context).build(result_from_xml.suite),
            statistics=StatisticsBuilder().build(result_from_xml.statistics),
            errors=ErrorsBuilder(self._context).build(result_from_xml.errors),
            strings=self._context.strings,
            basemillis=self._context.basemillis,
            split_results=self._context.split_results
        )


class _Builder(object):
    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}

    def __init__(self, context):
        self._context = context
        self._string = self._context.string
        self._html = self._context.html
        self._timestamp = self._context.timestamp

    def _get_status(self, item):
        model = (self._statuses[item.status],
                 self._timestamp(item.starttime),
                 item.elapsedtime)
        msg = getattr(item, 'message', '')
        return model if not msg else model + (self._string(msg),)

    def _build_keywords(self, kws, split=False):
        splitting = self._context.start_splitting_if_needed(split)
        model = tuple(self._build_keyword(k) for k in kws)
        return model if not splitting else self._context.end_splitting(model)


class SuiteBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_test = TestBuilder(context).build
        self._build_keyword = KeywordBuilder(context).build

    def build(self, suite):
        with self._context.prune_input(suite.keywords):
            return (self._string(suite.name),
                    self._string(suite.source),
                    self._context.relative_source(suite.source),
                    self._html(suite.doc),
                    tuple(self._yield_metadata(suite)),
                    self._get_status(suite),
                    tuple(self.build(s) for s in suite.suites),
                    tuple(self._build_test(t) for t in suite.tests),
                    tuple(self._build_keyword(k, split=True) for k in suite.keywords),
                    self._get_statistics(suite))

    def _yield_metadata(self, suite):
        for name, value in suite.metadata.iteritems():
            yield self._string(name)
            yield self._html(value)

    def _get_statistics(self, suite):
        stats = suite.statistics  # Access property only once
        return (stats.all.total,
                stats.all.passed,
                stats.critical.total,
                stats.critical.passed)


class TestBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_keyword = KeywordBuilder(context).build

    def build(self, test):
        with self._context.prune_input(test.keywords):
            return (self._string(test.name),
                    self._string(test.timeout),
                    int(test.critical == 'yes'),
                    self._html(test.doc),
                    tuple(self._string(t) for t in test.tags),
                    self._get_status(test),
                    self._build_keywords(test.keywords, split=True))


class KeywordBuilder(_Builder):
    _types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_keyword = self.build
        self._build_message = MessageBuilder(context).build

    def build(self, kw, split=False):
        return (self._types[kw.type],
                self._string(kw.name),
                self._string(kw.timeout),
                self._html(kw.doc),
                self._string(', '.join(kw.args)),
                self._get_status(kw),
                self._build_keywords(kw.keywords, split),
                tuple(self._build_message(m) for m in kw.messages))


class MessageBuilder(_Builder):

    def build(self, msg):
        if msg.level == 'WARN':
            self._context.create_link_target(msg)
        return self._build(msg)

    def _build(self, msg):
        return (self._timestamp(msg.timestamp),
                LEVELS[msg.level],
                self._string(msg.html_message))


class StatisticsBuilder(object):

    def build(self, statistics):
        return (self._build_stats(statistics.total),
                self._build_stats(statistics.tags),
                self._build_stats(statistics.suite))

    def _build_stats(self, stats):
        return tuple(stat.get_attributes(include_label=True, exclude_empty=True)
                     for stat in stats)


class ErrorsBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_message = ErrorMessageBuilder(context).build

    def build(self, errors):
        return tuple(self._build_message(msg) for msg in errors)


class ErrorMessageBuilder(MessageBuilder):

    def build(self, msg):
        model = self._build(msg)
        return model if not msg.linkable else model + (self._context.link(msg),)
