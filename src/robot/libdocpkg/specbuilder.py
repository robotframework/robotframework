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

import os.path

from robot.errors import DataError
from robot.utils import ET, ETSource

from .model import LibraryDoc, KeywordDoc


class SpecDocBuilder(object):

    def build(self, path):
        spec = self._parse_spec(path)
        libdoc = LibraryDoc(name=spec.get('name'),
                            type=spec.get('type').upper(),
                            version=spec.find('version').text or '',
                            doc=spec.find('doc').text or '',
                            scope=self._get_scope(spec),
                            named_args=self._get_named_args(spec),
                            doc_format=spec.get('format', 'ROBOT'),
                            source=spec.get('source'),
                            lineno=int(spec.get('lineno', -1)))
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

    def _get_scope(self, spec):
        # RF >= 3.2 has "scope" attribute w/ value 'GLOBAL', 'SUITE, or 'TEST'.
        if 'scope' in spec.attrib:
            return spec.get('scope')
        # RF < 3.2 has "scope" element. Need to map old values to new.
        scope = spec.find('scope').text
        return {'': 'GLOBAL',          # Was used with resource files.
                'global': 'GLOBAL',
                'test suite': 'SUITE',
                'test case': 'TEST'}[scope]

    def _get_named_args(self, spec):
        # RF >= 3.2 has "namedargs" attribute w/ value 'true' or 'false'.
        namedargs = spec.get('namedargs')
        if namedargs == 'true':
            return True
        if namedargs == 'false':
            return False
        # RF < 3.2 has "namedargs" element with text 'yes' or 'no'.
        namedargs = spec.find('namedargs').text
        return namedargs == 'yes'

    def _create_keywords(self, spec, path):
        return [self._create_keyword(elem) for elem in spec.findall(path)]

    def _create_keyword(self, elem):
        # "deprecated" attribute isn't read because it is read from the doc
        # automatically. That should probably be changed at some point.
        return KeywordDoc(name=elem.get('name', ''),
                          args=[a.text for a in elem.findall('arguments/arg')],
                          doc=elem.find('doc').text or '',
                          tags=[t.text for t in elem.findall('tags/tag')],
                          source=elem.get('source'),
                          lineno=int(elem.get('lineno', -1)))
