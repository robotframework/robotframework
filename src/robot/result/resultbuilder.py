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

from typing import Sequence
from xml.etree import ElementTree as ET

from robot.errors import DataError
from robot.utils import ETSource, get_error_message

from .executionresult import CombinedResult, is_json_source, KeywordRemover, Result
from .flattenkeywordmatcher import (
    create_flatten_message, FlattenByNameMatcher, FlattenByTags, FlattenByTypeMatcher
)
from .merger import Merger
from .xmlelementhandlers import XmlElementHandler


def ExecutionResult(
    *sources,
    merge: bool = False,
    include_keywords: bool = True,
    flattened_keywords: Sequence[str] = (),
    rpa: "bool|None" = None,
):
    """Factory method to constructs :class:`~.executionresult.Result` objects.

    :param sources: XML or JSON source(s) containing execution results.
        Can be specified as paths (``pathlib.Path`` or ``str``), opened file
        objects, or strings/bytes containing XML/JSON directly.
    :param merge: When ``True`` and multiple sources are given, results are merged
        instead of combined.
    :param include_keywords: When ``False``, keyword and control structure information
        is not parsed. This can save considerable amount of time and memory.
    :param flattened_keywords: List of patterns controlling what keywords
        and control structures to flatten. See the documentation of
        the ``--flattenkeywords`` option for more details.
    :param rpa: Setting ``rpa`` either to ``True`` (RPA mode) or ``False`` (test
        automation) sets the execution mode explicitly. By default, the mode is got
        from processed output files and conflicting modes cause an error.
    :returns: :class:`~.executionresult.Result` instance.

    A source is considered to be JSON in these cases:
    - It is a path with a ``.json`` suffix.
    - It is an open file that has a ``name`` attribute with a ``.json`` suffix.
    - It is string or bytes starting with ``{`` and ending with ``}``.

    This method should be imported by external code via the :mod:`robot.api`
    package. See the :mod:`robot.result` package for a usage example.
    """
    if not sources:
        raise DataError("One or more data source needed.")
    options = {
        "include_keywords": include_keywords,
        "flattened_keywords": flattened_keywords,
        "rpa": rpa,
    }
    if merge:
        return _merge_results(sources[0], sources[1:], options)
    if len(sources) > 1:
        return _combine_results(sources, options)
    return _single_result(sources[0], options)


def _merge_results(original, merged, options):
    result = ExecutionResult(original, **options)
    merger = Merger(result, rpa=result.rpa)
    for source in merged:
        merged = ExecutionResult(source, **options)
        merger.merge(merged)
    return result


def _combine_results(sources, options):
    return CombinedResult(ExecutionResult(src, **options) for src in sources)


def _single_result(source, options):
    if is_json_source(source):
        return _json_result(source, **options)
    return _xml_result(source, **options)


def _json_result(source, include_keywords, flattened_keywords, rpa):
    try:
        return Result.from_json(source, include_keywords, flattened_keywords, rpa)
    except IOError as err:
        error = err.strerror
    except Exception:
        error = get_error_message()
    raise DataError(f"Reading JSON source '{source}' failed: {error}")


def _xml_result(source, include_keywords, flattened_keywords, rpa):
    ets = ETSource(source)
    builder = ExecutionResultBuilder(ets, include_keywords, flattened_keywords)
    result = Result(source, rpa=rpa)
    try:
        return builder.build(result)
    except IOError as err:
        error = err.strerror
    except Exception:
        error = get_error_message()
    raise DataError(f"Reading XML source '{ets}' failed: {error}")


# TODO:
# - Rename e.g. to XmlExecutionResultBuilder. Probably best done in a major release.
# - Add Result.from_xml as a more convenient API. Could be done in RF 7.4.
class ExecutionResultBuilder:
    """Builds :class:`~.executionresult.Result` objects based on XML output files.

    Instead of using this builder directly, it is recommended to use the
    :func:`ExecutionResult` factory method.
    """

    def __init__(self, source, include_keywords=True, flattened_keywords=()):
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
        self._source = source if isinstance(source, ETSource) else ETSource(source)
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
            result.suite.visit(KeywordRemover())
        return result

    def _parse(self, source, start, end):
        context = ET.iterparse(source, events=("start", "end"))
        if not self._include_keywords:
            context = self._omit_keywords(context)
        elif self._flattened_keywords:
            context = self._flatten_keywords(context, self._flattened_keywords)
        for event, elem in context:
            if event == "start":
                start(elem)
            else:
                end(elem)
                elem.clear()
        # Python 3.15 emits a warning if context is not closed, but `close` is
        # new in Python 3.13.
        try:
            context.close()
        except AttributeError:
            pass

    def _omit_keywords(self, context):
        omitted_elements = {"kw", "for", "while", "if", "try", "group", "variable"}
        omitted = 0
        for event, elem in context:
            # Teardowns cannot be removed yet, because we need to check suite
            # teardown status. They are removed later using KeywordRemover.
            omit = elem.tag in omitted_elements and elem.get("type") != "TEARDOWN"
            start = event == "start"
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
        started = -1  # If 0 or more, we are flattening.
        include_on_top = {"doc", "tag", "timeout", "status"}
        for event, elem in context:
            tag = elem.tag
            if event == "start":
                if started >= 0:
                    started += 1
                elif (
                    by_name
                    and tag == "kw"
                    and name_match(
                        elem.get("name", ""),
                        elem.get("owner") or elem.get("library"),
                        # 'library' is for RF < 7 compatibility
                    )
                ):
                    started = 0
                elif by_type and type_match(tag):
                    started = 0
            elif started == 1 and tag == "status":
                elem.text = create_flatten_message(elem.text)
            if started <= 0 or (started == 1 and tag in include_on_top) or tag == "msg":
                yield event, elem
            else:
                elem.clear()
            if started >= 0 and event == "end":
                started -= 1

    def _get_matcher(self, matcher_class, flattened):
        matcher = matcher_class(flattened)
        return matcher.match, bool(matcher)
