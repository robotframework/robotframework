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

import textwrap

from robot.utils import MultiMatcher, encode_output
from robot.errors import DataError


class ConsoleViewer(object):

    def __init__(self, libdoc):
        self._libdoc = libdoc
        self._keywords = KeywordMatcher(libdoc)

    @classmethod
    def handles(cls, command):
        return command.lower() in ['list', 'show', 'version']

    @classmethod
    def validate_command(cls, command, args):
        if not cls.handles(command):
            raise DataError("Unknown command '%s'." % command)
        if command.lower() == 'version' and args:
            raise DataError("Command 'version' does not take arguments.")

    def view(self, command, *args):
        self.validate_command(command, args)
        getattr(self, command.lower())(*args)

    def list(self, *patterns):
        for kw in self._keywords.search('*%s*' % p for p in patterns):
            self._console(kw.name)

    def show(self, *names):
        if MultiMatcher(names, match_if_no_patterns=True).match('intro'):
            self._show_intro(self._libdoc)
            if self._libdoc.inits:
                self._show_inits(self._libdoc)
        for kw in self._keywords.search(names):
            self._show_keyword(kw)

    def version(self):
        self._console(self._libdoc.version or 'N/A')

    def _console(self, msg):
        print encode_output(msg)

    def _show_intro(self, lib):
        self._header(lib.name, underline='=')
        named_args = 'supported' if lib.named_args else 'not supported'
        self._data([('Version', lib.version), ('Scope', lib.scope),
                    ('Named arguments', named_args)])
        self._doc(lib.doc)

    def _show_inits(self, lib):
        self._header('Importing', underline='-')
        for init in lib.inits:
            self._show_keyword(init, show_name=False)

    def _show_keyword(self, kw, show_name=True):
        if show_name:
            self._header(kw.name, underline='-')
        self._data([('Arguments', '[%s]' % ', '.join(kw.args))])
        self._doc(kw.doc)

    def _header(self, name, underline):
        self._console('%s\n%s' % (name, underline * len(name)))

    def _data(self, items):
        ljust = max(len(name) for name, _ in items) + 3
        for name, value in items:
            if value:
                text = '%s%s' % ((name+':').ljust(ljust), value)
                self._console(self._wrap(text, subsequent_indent=' '*ljust))

    def _doc(self, doc):
        self._console('')
        for line in doc.splitlines():
            self._console(self._wrap(line))
        if doc:
            self._console('')

    def _wrap(self, text, width=78, **config):
        return '\n'.join(textwrap.wrap(text, width=width, **config))


class KeywordMatcher(object):

    def __init__(self, libdoc):
        self._keywords = libdoc.keywords

    def search(self, patterns):
        matcher = MultiMatcher(patterns, match_if_no_patterns=True)
        for kw in self._keywords:
            if matcher.match(kw.name):
                yield kw
