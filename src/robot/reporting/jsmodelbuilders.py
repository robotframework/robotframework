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

from robot.output import LEVELS

from .jsbuildingcontext import JsBuildingContext
from .jsexecutionresult import JsExecutionResult


STATUSES = {'FAIL': 0, 'PASS': 1, 'SKIP': 2, 'NOT RUN': 3}
KEYWORD_TYPES = {'KEYWORD': 0, 'SETUP': 1, 'TEARDOWN': 2,
                 'FOR': 3, 'ITERATION': 4, 'IF': 5, 'ELSE IF': 6, 'ELSE': 7,
                 'RETURN': 8, 'TRY': 9, 'EXCEPT': 10, 'FINALLY': 11, 'WHILE': 12,
                 'CONTINUE': 13, 'BREAK': 14, 'ERROR': 15}


class JsModelBuilder:

    def __init__(self, log_path=None, split_log=False, expand_keywords=None,
                 prune_input_to_save_memory=False):
        self._context = JsBuildingContext(log_path, split_log, expand_keywords,
                                          prune_input_to_save_memory)

    def build_from(self, result_from_xml):
        # Statistics must be build first because building suite may prune input.
        return JsExecutionResult(
            statistics=StatisticsBuilder().build(result_from_xml.statistics),
            suite=SuiteBuilder(self._context).build(result_from_xml.suite),
            errors=ErrorsBuilder(self._context).build(result_from_xml.errors),
            strings=self._context.strings,
            basemillis=self._context.basemillis,
            split_results=self._context.split_results,
            min_level=self._context.min_level,
            expand_keywords=self._context.expand_keywords
        )


class _Builder:

    def __init__(self, context):
        self._context = context
        self._string = self._context.string
        self._html = self._context.html
        self._timestamp = self._context.timestamp

    def _get_status(self, item):
        model = (STATUSES[item.status],
                 self._timestamp(item.starttime),
                 item.elapsedtime)
        msg = getattr(item, 'message', '')
        if not msg:
            return model
        elif msg.startswith('*HTML*'):
            msg = self._string(msg[6:].lstrip(), escape=False)
        else:
            msg = self._string(msg)
        return model + (msg,)

    def _build_keywords(self, steps, split=False):
        splitting = self._context.start_splitting_if_needed(split)
        # tuple([<listcomp>>]) is faster than tuple(<genex>) with short lists.
        model = tuple([self._build_keyword(step) for step in steps])
        return model if not splitting else self._context.end_splitting(model)

    def _build_keyword(self, step):
        raise NotImplementedError


class SuiteBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_suite = self.build
        self._build_test = TestBuilder(context).build
        self._build_keyword = KeywordBuilder(context).build

    def build(self, suite):
        with self._context.prune_input(suite.tests, suite.suites):
            stats = self._get_statistics(suite)  # Must be done before pruning
            kws = [kw for kw in (suite.setup, suite.teardown) if kw]
            return (self._string(suite.name, attr=True),
                    self._string(suite.source),
                    self._context.relative_source(suite.source),
                    self._html(suite.doc),
                    tuple(self._yield_metadata(suite)),
                    self._get_status(suite),
                    tuple(self._build_suite(s) for s in suite.suites),
                    tuple(self._build_test(t) for t in suite.tests),
                    tuple(self._build_keyword(k, split=True) for k in kws),
                    stats)

    def _yield_metadata(self, suite):
        for name, value in suite.metadata.items():
            yield self._string(name)
            yield self._html(value)

    def _get_statistics(self, suite):
        stats = suite.statistics  # Access property only once
        return (stats.total, stats.passed, stats.failed, stats.skipped)


class TestBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_keyword = KeywordBuilder(context).build

    def build(self, test):
        kws = self._get_keywords(test)
        with self._context.prune_input(test.body):
            return (self._string(test.name, attr=True),
                    self._string(test.timeout),
                    self._html(test.doc),
                    tuple(self._string(t) for t in test.tags),
                    self._get_status(test),
                    self._build_keywords(kws, split=True))

    def _get_keywords(self, test):
        kws = []
        if test.setup:
            kws.append(test.setup)
        kws.extend(test.body.flatten())
        if test.teardown:
            kws.append(test.teardown)
        return kws


class KeywordBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_keyword = self.build
        self._build_message = MessageBuilder(context).build

    def build(self, item, split=False):
        if item.type == item.MESSAGE:
            return self._build_message(item)
        return self.build_keyword(item, split)

    def build_keyword(self, kw, split=False):
        self._context.check_expansion(kw)
        items = kw.body.flatten()
        if getattr(kw, 'has_teardown', False):
            items.append(kw.teardown)
        with self._context.prune_input(kw.body):
            return (KEYWORD_TYPES[kw.type],
                    self._string(kw.kwname, attr=True),
                    self._string(kw.libname, attr=True),
                    self._string(kw.timeout),
                    self._html(kw.doc),
                    self._string(', '.join(kw.args)),
                    self._string(', '.join(kw.assign)),
                    self._string(', '.join(kw.tags)),
                    self._get_status(kw),
                    self._build_keywords(items, split))


class MessageBuilder(_Builder):

    def build(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._context.create_link_target(msg)
        self._context.message_level(msg.level)
        return self._build(msg)

    def _build(self, msg):
        return (self._timestamp(msg.timestamp),
                LEVELS[msg.level],
                self._string(msg.html_message, escape=False))


class StatisticsBuilder:

    def build(self, statistics):
        return (self._build_stats(statistics.total),
                self._build_stats(statistics.tags),
                self._build_stats(statistics.suite, exclude_empty=False))

    def _build_stats(self, stats, exclude_empty=True):
        return tuple(stat.get_attributes(include_label=True,
                                         include_elapsed=True,
                                         exclude_empty=exclude_empty,
                                         html_escape=True)
                     for stat in stats)


class ErrorsBuilder(_Builder):

    def __init__(self, context):
        _Builder.__init__(self, context)
        self._build_message = ErrorMessageBuilder(context).build

    def build(self, errors):
        with self._context.prune_input(errors.messages):
            return tuple(self._build_message(msg) for msg in errors)


class ErrorMessageBuilder(MessageBuilder):

    def build(self, msg):
        model = self._build(msg)
        link = self._context.link(msg)
        return model if link is None else model + (link,)
