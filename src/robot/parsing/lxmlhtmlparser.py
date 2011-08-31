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

import os
if os.environ.get('ROBOT_NO_LXML'):
    raise ImportError('Using lxml is disabled')
from lxml import etree


class RobotHtmlParser(object):

    def __init__(self, reader):
        self._reader = reader

    def parse(self, htmlfile):
        parser = etree.HTMLParser(target=self)
        etree.parse(htmlfile, parser)

    def start(self, tag, attrs):
        self._reader.start(tag)

    def end(self, tag):
        self._reader.end(tag)

    def data(self, data):
        self._reader.data(self._normalize_nbsp_and_tilde(data))

    def _normalize_nbsp_and_tilde(self, data):
        return data.replace(u'\xa0', u' ').replace(u'\u02dc', u'~')

    def close(self):
        pass
