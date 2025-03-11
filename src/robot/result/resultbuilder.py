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

from robot.errors import DataError
from robot.model import SuiteVisitor
from robot.utils import ET, ETSource, get_error_message

from .executionresult import CombinedResult, is_json_source, Result
from .flattenkeywordmatcher import (create_flatten_message, FlattenByNameMatcher,
                                    FlattenByTypeMatcher, FlattenByTags)
from .merger import Merger
from .xmlelementhandlers import XmlElementHandler


def ExecutionResult(*sources, **options):
    """Factory method to constructs :class:`~.executionresult.Result` objects.

    :param sources: XML or JSON source(s) containing execution results.
        Can be specified as paths (``pathlib.Path`` or ``str``), opened file
        objects, or strings/bytes containing XML/JSON directly.
    :param options: Configuration options.
        Using ``merge=True`` causes multiple results to be combined so that
        tests in the latter results replace the ones in the original.
        Setting ``rpa`` either to ``True`` (RPA mode) or ``False`` (test
        automation) sets execution mode explicitly. By default, it is got
        from processed output files and conflicting modes cause an error.
        Other options are passed directly to the
        :class:`ExecutionResultBuilder` object used internally.
    :returns: :class:`~.executionresult.Result` instance.

    A source is considered to be JSON in these cases:
    - It is a path with a ``.json`` suffix.
    - It is an open file that has a ``name`` attribute with a ``.json`` suffix.
    - It is string or bytes starting with ``{`` and ending with ``}``.

    This method should be imported by external code via the :mod:`robot.api`
    package. See the :mod:`robot.result` package for a usage example.
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
    merger = Merger(result, rpa=result.rpa)
    for path in merged:
        merged = ExecutionResult(path, **options)
        merger.merge(merged)
    return result


def _combine_results(sources, options):
    return CombinedResult(ExecutionResult(src, **options) for src in sources)


def _single_result(source, options):
    if is_json_source(source):
        return _json_result(source, options)
    return _xml_result(source, options)


def _json_result(source, options):
    try:
        return Result.from_json(source, rpa=options.get('rpa'))
    except IOError as err:
        error = err.strerror
    except Exception:
        error = get_error_message()
    raise DataError(f"Reading JSON source '{source}' failed: {error}")


def _xml_result(source, options):
    ets = ETSource(source)
    result = Result(source, rpa=options.pop('rpa', None))
    try:
        return ExecutionResultBuilder(ets, **options).build(result)
    except IOError as err:
        error = err.strerror
    except Exception:
        error = get_error_message()
    raise DataError(f"Reading XML source '{ets}' failed: {error}")


class ExecutionResultBuilder:
    """Builds :class:`~.executionresult.Result` objects based on XML output files.

    Instead of using this builder directly, it is recommended to use the
    :func:`ExecutionResult` factory method.
    """

    def __init__(self, source, include_keywords=True, flattened_keywords=None):
        """
        :param source: Path to the XML output file to build
            :class:`~.executionresult.Result` objects from.
        :param include_keywords: Controls whether to include keywords and control
            structures like FOR and IF in the result or not. They are not needed
            when generating only a report.
        :param flattened_keywords: List of patterns controlling what keywords
            and control structures to flatten. See the documentation of
            the ``--flattenkeywords`` option for more details.
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
        if self._flattened_keywords:
            # Tags are nowadays written after keyword content, so we cannot
            # flatten based on them when parsing output.xml.
            result.suite.visit(FlattenByTags(self._flattened_keywords))
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
        omitted_elements = {'kw', 'for', 'while', 'if', 'try'}
        omitted = 0
        for event, elem in context:
            # Teardowns aren't omitted yet to allow checking suite teardown status.
            # They'll be removed later when not needed in `build()`.
            omit = elem.tag in omitted_elements and elem.get('type') != 'TEARDOWN'
            start = event == 'start'
            if omit and start:
                omitted += 1
            if not omitted:
                yield event, elem
            elif not start:
                elem.clear()
            if omit and not start:
                omitted -= 1

    def _flatten_keywords(self, context, flattened):
        # Performance optimized. Do not change without profiling!
        name_match, by_name = self._get_matcher(FlattenByNameMatcher, flattened)
        type_match, by_type = self._get_matcher(FlattenByTypeMatcher, flattened)
        started = -1    # if 0 or more, we are flattening
        containers = {'kw', 'for', 'while', 'iter', 'if', 'try'}
        inside = 0    # to make sure we don't read tags from a test
        for event, elem in context:
            tag = elem.tag
            if event == 'start':
                if tag in containers:
                    inside += 1
                    if started >= 0:
                        started += 1
                    elif by_name and name_match(elem.get('name', ''), elem.get('owner')
                                                or elem.get('library')):
                        started = 0
                    elif by_type and type_match(tag):
                        started = 0
            else:
                if tag in containers:
                    inside -= 1
                elif started == 0 and tag == 'status':
                    elem.text = create_flatten_message(elem.text)
            if started <= 0 or tag == 'msg':
                yield event, elem
            else:
                elem.clear()
            if started >= 0 and event == 'end' and tag in containers:
                started -= 1

    def _get_matcher(self, matcher_class, flattened):
        matcher = matcher_class(flattened)
        return matcher.match, bool(matcher)


class RemoveKeywords(SuiteVisitor):

    def start_suite(self, suite):
        suite.setup = None
        suite.teardown = None

    def visit_test(self, test):
        test.body = []
