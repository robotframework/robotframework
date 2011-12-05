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

from robot.utils import timestamp_to_secs
from robot.output import LEVELS

from .parsingcontext import TextCache as StringCache

# TODO: Replace old context with this one
class NewParsingContext(object):

    def __init__(self):
        self._strings = StringCache()
        self.basemillis = None

    def string(self, string):
        return self._strings.add(string)

    def dump_strings(self):
        return self._strings.dump()

    def timestamp(self, time):
        if time == 'N/A':   # TODO: Should we use None in model?
            return None
        # Must use `long` and not `int` below due to this IronPython bug:
        # http://ironpython.codeplex.com/workitem/31549
        millis = long(round(timestamp_to_secs(time) * 1000))
        if self.basemillis is None:
            self.basemillis = millis
        return millis - self.basemillis


# TODO: Change order of items in JS model to be more consistent with "normal" model?

class JsModelBuilder(object):
    _statuses = {'FAIL': 0, 'PASS': 1, 'NOT_RUN': 2}
    _kw_types = {'kw': 0, 'setup': 1, 'teardown': 2, 'for': 3, 'foritem': 4}

    def __init__(self):
        self._context = NewParsingContext()
        self._string = self._context.string
        self._timestamp = self._context.timestamp

    def dump_strings(self):
        return self._context.dump_strings()

    def build_from(self, result_from_xml):
        return self._build_suite(result_from_xml.suite)

    def _build_suite(self, suite):
        return (self._string(suite.name),
                self._string(suite.source),
                self._string(''),   # TODO: relative source
                self._string(suite.doc),
                tuple(self._yield_metadata(suite)),
                self._get_status(suite),
                tuple(self._build_suite(s) for s in suite.suites),
                tuple(self._build_test(t) for t in suite.tests),
                tuple(self._build_keyword(k) for k in suite.keywords),
                self._get_statistics(suite))

    def _yield_metadata(self, suite):
        for name, value in suite.metadata.iteritems():
            yield self._string(name)
            yield self._string(value)

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
                self._string(test.doc),
                tuple(self._string(t) for t in test.tags),
                self._get_status(test),
                tuple(self._build_keyword(k) for k in test.keywords))

    def _build_keyword(self, kw):
        return (self._kw_types[kw.type],
                self._string(kw.name),
                self._string(kw.timeout),
                self._string(kw.doc),
                self._string(', '.join(kw.args)),
                self._get_status(kw),
                tuple(self._build_keyword(k) for k in kw.keywords),
                tuple(self._build_message(m) for m in kw.messages))

    def _build_message(self, msg):
        # TODO: linking
        return (self._timestamp(msg.timestamp),
                LEVELS[msg.level],
                self._string(msg.html_message))
