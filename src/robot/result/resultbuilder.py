#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.errors import DataError
from robot.model import SuiteVisitor
from robot.utils import ET, ETSource, get_error_message

from .executionresult import Result, CombinedResult
from .flattenkeywordmatcher import FlattenKeywordMatcher
from .merger import Merger
from .xmlelementhandlers import XmlElementHandler


def ExecutionResult(*sources, **options):
    """Factory method to constructs :class:`~.executionresult.Result` objects.

    :param sources: Path(s) to output XML file(s).
    :param options: Configuration options. `rerun_merge` with True value causes
                    multiple results to be combined so that tests in the latter
                    results replace the ones in the original. Other options
                    are passed further to :py:class:`~ExecutionResultBuilder`.
    :returns: :class:`~.executionresult.Result` instance.

    See :mod:`~robot.result` package for a usage example.
    """
    if not sources:
        raise DataError('One or more data source needed.')
    if options.pop('merge', False):
        return _merge_results(sources[0], sources[1:], options)
    if len(sources) > 1:
        return _combine_results(sources, options)
    return _single_result(sources[0], options)


def _merge_results(original, merged, options):
    result = ExecutionResult(original, **options)
    merger = Merger(result)
    for path in merged:
        merged = ExecutionResult(path, **options)
        merger.merge(merged)
    return result


def _combine_results(sources, options):
    return CombinedResult(ExecutionResult(src, **options) for src in sources)


def _single_result(source, options):
    ets = ETSource(source)
    try:
        return ExecutionResultBuilder(ets, **options).build(Result(source))
    except IOError, err:
        error = err.strerror
    except:
        error = get_error_message()
    raise DataError("Reading XML source '%s' failed: %s" % (unicode(ets), error))


class ExecutionResultBuilder(object):

    def __init__(self, source, include_keywords=True, flattened_keywords=None):
        """Builds :class:`~.executionresult.Result` objects from existing
        output XML files on the file system.

        :param source: Path to output XML file.
        :param include_keywords: Include keyword information to the
            :class:`~.executionresult.Result` objects
        """
        self._source = source \
            if isinstance(source, ETSource) else ETSource(source)
        self._include_keywords = include_keywords
        self._flattened_keywords = flattened_keywords

    def build(self, result):
        # Parsing is performance optimized. Do not change without profiling!
        handler = XmlElementHandler(result)
        with self._source as source:
            self._parse(source, handler.start, handler.end)
        result.handle_suite_teardown_failures()
        if not self._include_keywords:
            result.suite.visit(RemoveKeywords())
        return result

    def _parse(self, source, start, end):
        context = ET.iterparse(source, events=('start', 'end'))
        if not self._include_keywords:
            context = self._omit_keywords(context)
        elif self._flattened_keywords:
            context = self._flatten_keywords(context, self._flattened_keywords)
        for event, elem in context:
            if event == 'start':
                start(elem)
            else:
                end(elem)
                elem.clear()

    def _omit_keywords(self, context):
        omitted_kws = 0
        for event, elem in context:
            # Teardowns aren't omitted to allow checking suite teardown status.
            omit = elem.tag == 'kw' and elem.get('type') != 'teardown'
            start = event == 'start'
            if omit and start:
                omitted_kws += 1
            if not omitted_kws:
                yield event, elem
            elif not start:
                elem.clear()
            if omit and not start:
                omitted_kws -= 1

    def _flatten_keywords(self, context, flattened):
        match = FlattenKeywordMatcher(flattened).match
        started = -1
        for event, elem in context:
            tag = elem.tag
            if event == 'start' and tag == 'kw':
                if started >= 0:
                    started += 1
                elif match(elem.get('name'), elem.get('type')):
                    started = 0
            if started == 0 and event == 'end' and tag == 'doc':
                elem.text = ('%s\n\n_*Keyword content flattened.*_'
                             % (elem.text or '')).strip()
            if started <= 0 or tag == 'msg':
                yield event, elem
            else:
                elem.clear()
            if started >= 0 and event == 'end' and tag == 'kw':
                started -= 1


class RemoveKeywords(SuiteVisitor):

    def start_suite(self, suite):
        suite.keywords = []

    def visit_test(self, test):
        test.keywords = []
