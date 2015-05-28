#  Copyright 2008-2015 Nokia Solutions and Networks
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

import os.path

from robot.errors import DataError
from robot.utils import ET, ETSource

from .model import LibraryDoc, KeywordDoc


class SpecDocBuilder(object):

    def build(self, path):
        spec = self._parse_spec(path)
        libdoc = LibraryDoc(name=spec.get('name'),
                            type=spec.get('type'),
                            version=spec.find('version').text or '',
                            doc=spec.find('doc').text or '',
                            scope=spec.find('scope').text or '',
                            named_args=self._get_named_args(spec),
                            doc_format=spec.get('format', 'ROBOT'))
        libdoc.inits = self._create_keywords(spec, 'init')
        libdoc.keywords = self._create_keywords(spec, 'kw')
        return libdoc

    def _parse_spec(self, path):
        if not os.path.isfile(path):
            raise DataError("Spec file '%s' does not exist." % path)
        with ETSource(path) as source:
            root = ET.parse(source).getroot()
        if root.tag != 'keywordspec':
            raise DataError("Invalid spec file '%s'." % path)
        return root

    def _get_named_args(self, spec):
        elem = spec.find('namedargs')
        if elem is None:
            return False    # Backwards compatiblity with RF < 2.6.2
        return elem.text == 'yes'

    def _create_keywords(self, spec, path):
        return [self._create_keyword(elem) for elem in spec.findall(path)]

    def _create_keyword(self, elem):
        return KeywordDoc(name=elem.get('name', ''),
                          args=[a.text for a in elem.findall('arguments/arg')],
                          doc=elem.find('doc').text or '',
                          tags=[t.text for t in elem.findall('tags/tag')])
