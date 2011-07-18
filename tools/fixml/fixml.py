#!/usr/bin/env python

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

"""fixml.py -- A tool to fix broken Robot Framework output files

Usage:  fixml.py inpath outpath

This tool can fix Robot Framework output files that are not properly finished
or are missing elements from the middle. It should be possible to generate
reports and logs from the fixed output afterwards with the `rebot` tool.

The tool uses BeautifulSoup module which must be installed separately.
See http://www.crummy.com/software/BeautifulSoup for more information.
Additionally, the tool is only compatible with Robot Framework 2.1.3 or newer.
"""

from __future__ import with_statement
import sys
import os
try:
    from BeautifulSoup import BeautifulStoneSoup
except ImportError:
    raise ImportError('fixml.py requires BeautifulSoup to be installed: '
                      'http://www.crummy.com/software/BeautifulSoup/')


class Fixxxer(BeautifulStoneSoup):
    NESTABLE_TAGS = {'suite': ['robot','suite', 'statistics'],
                     'doc': ['suite', 'test', 'kw'],
                     'metadata': ['suite'],
                     'item': ['metadata'],
                     'status': ['suite', 'test', 'kw'],
                     'test': ['suite'],
                     'tags': ['test'],
                     'tag': ['tags'],
                     'kw': ['suite', 'test', 'kw'],
                     'msg': ['kw', 'errors'],
                     'arguments': ['kw'],
                     'arg': ['arguments'],
                     'statistics': ['robot'],
                     'errors': ['robot']}
    __close_on_open = None

    def unknown_starttag(self, name, attrs, selfClosing=0):
        if name == 'robot':
            attrs = [(key, value if key != 'generator' else 'fixml.py')
                     for key, value in attrs]
        if name == 'kw' and ('type', 'teardown') in attrs:
            while self.tagStack[-1].name not in ['test', 'suite']:
                self._popToTag(self.tagStack[-1].name)
        if self.__close_on_open:
            self._popToTag(self.__close_on_open)
            self.__close_on_open = None
        BeautifulStoneSoup.unknown_starttag(self, name, attrs, selfClosing)

    def unknown_endtag(self, name):
        BeautifulStoneSoup.unknown_endtag(self, name)
        if name == 'status':
            self.__close_on_open = self.tagStack[-1].name
        else:
            self.__close_on_open = None


def main(inpath, outpath):
    with open(inpath) as infile:
        with open(outpath, 'w') as outfile:
            outfile.write(str(Fixxxer(infile)))
    return outpath


if __name__ == '__main__':
    try:
        outpath = main(*sys.argv[1:])
    except TypeError:
        print __doc__
    else:
        print os.path.abspath(outpath)
