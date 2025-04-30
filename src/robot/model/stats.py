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

from datetime import timedelta

from robot.utils import elapsed_time_to_string, html_escape, normalize, Sortable

from .tags import TagPattern


class Stat(Sortable):
    """Generic statistic object used for storing all the statistic values."""

    def __init__(self, name):
        #: Human readable identifier of the object these statistics
        #: belong to. `All Tests` for
        #: :class:`~robot.model.totalstatistics.TotalStatistics`,
        #: long name of the suite for
        #: :class:`~robot.model.suitestatistics.SuiteStatistics`
        #: or name of the tag for
        #: :class:`~robot.model.tagstatistics.TagStatistics`
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.elapsed = timedelta()
        self._norm_name = normalize(name, ignore="_")

    def get_attributes(
        self,
        include_label=False,
        include_elapsed=False,
        exclude_empty=True,
        values_as_strings=False,
        html_escape=False,
    ):
        attrs = {
            **({"label": self.name} if include_label else {}),
            **self._get_custom_attrs(),
            "pass": self.passed,
            "fail": self.failed,
            "skip": self.skipped,
        }
        if include_elapsed:
            attrs["elapsed"] = elapsed_time_to_string(
                self.elapsed, include_millis=False
            )
        if exclude_empty:
            attrs = {k: v for k, v in attrs.items() if v not in ("", None)}
        if values_as_strings:
            attrs = {k: str(v if v is not None else "") for k, v in attrs.items()}
        if html_escape:
            attrs = {k: self._html_escape(v) for k, v in attrs.items()}
        return attrs

    def _get_custom_attrs(self):
        return {}

    def _html_escape(self, item):
        return html_escape(item) if isinstance(item, str) else item

    @property
    def total(self):
        return self.passed + self.failed + self.skipped

    def add_test(self, test):
        self._update_stats(test)
        self._update_elapsed(test)

    def _update_stats(self, test):
        if test.passed:
            self.passed += 1
        elif test.skipped:
            self.skipped += 1
        else:
            self.failed += 1

    def _update_elapsed(self, test):
        self.elapsed += test.elapsed_time

    @property
    def _sort_key(self):
        return self._norm_name

    def __bool__(self):
        return not self.failed

    def visit(self, visitor):
        visitor.visit_stat(self)


class TotalStat(Stat):
    """Stores statistic values for a test run."""

    type = "total"


class SuiteStat(Stat):
    """Stores statistics values for a single suite."""

    type = "suite"

    def __init__(self, suite):
        super().__init__(suite.full_name)
        self.id = suite.id
        self.elapsed = suite.elapsed_time
        self._name = suite.name

    def _get_custom_attrs(self):
        return {"name": self._name, "id": self.id}

    def _update_elapsed(self, test):
        pass

    def add_stat(self, other):
        self.passed += other.passed
        self.failed += other.failed
        self.skipped += other.skipped


class TagStat(Stat):
    """Stores statistic values for a single tag."""

    type = "tag"

    def __init__(self, name, doc="", links=None, combined=None):
        super().__init__(name)
        #: Documentation of tag as a string.
        self.doc = doc
        #: List of tuples in which the first value is the link URL and
        #: the second is the link title. An empty list by default.
        self.links = links or []
        #: Pattern as a string if the tag is combined, ``None`` otherwise.
        self.combined = combined

    @property
    def info(self):
        """Returns additional information of the tag statistics
        are about. Either `combined` or an empty string.
        """
        if self.combined:
            return "combined"
        return ""

    def _get_custom_attrs(self):
        return {
            "doc": self.doc,
            "links": self._get_links_as_string(),
            "info": self.info,
            "combined": self.combined,
        }

    def _get_links_as_string(self):
        return ":::".join(f"{title}:{url}" for url, title in self.links)

    @property
    def _sort_key(self):
        return (not self.combined, self._norm_name)


class CombinedTagStat(TagStat):

    def __init__(self, pattern, name=None, doc="", links=None):
        super().__init__(name or pattern, doc, links, combined=pattern)
        self.pattern = TagPattern.from_string(pattern)

    def match(self, tags):
        return self.pattern.match(tags)
