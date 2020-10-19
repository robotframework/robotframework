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
from robot.utils import ET, ETSource, unescape
from robot.running.arguments import ArgumentSpec

from .model import LibraryDoc, KeywordDoc


class SpecDocBuilder(object):

    def build(self, path):
        spec = self._parse_spec(path)
        self.name = spec.get('name')
        self.type = spec.get('type').upper()
        libdoc = LibraryDoc(name=self.name,
                            type=self.type,
                            version=spec.find('version').text or '',
                            doc=spec.find('doc').text or '',
                            scope=spec.get('scope'),
                            doc_format=spec.get('format', 'ROBOT'),
                            source=spec.get('source'),
                            lineno=int(spec.get('lineno', -1)))
        libdoc.inits = self._create_keywords(spec, 'inits/init')
        libdoc.keywords = self._create_keywords(spec, 'keywords/kw')
        return libdoc

    def _parse_spec(self, path):
        if not os.path.isfile(path):
            raise DataError("Spec file '%s' does not exist." % path)
        with ETSource(path) as source:
            root = ET.parse(source).getroot()
        if root.tag != 'keywordspec':
            raise DataError("Invalid spec file '%s'." % path)
        version = root.get('specversion')
        if version != '3':
            raise DataError("Invalid spec file version '%s'. "
                            "RF >= 4.0 requires XML specversion 3." % version)
        return root

    def _create_keywords(self, spec, path):
        return [self._create_keyword(elem) for elem in spec.findall(path)]

    def _create_keyword(self, elem):
        # "deprecated" attribute isn't read because it is read from the doc
        # automatically. That should probably be changed at some point.
        return KeywordDoc(name=elem.get('name', ''),
                          args=self._create_arguments(elem),
                          doc=elem.find('doc').text or '',
                          tags=[t.text for t in elem.findall('tags/tag')],
                          source=elem.get('source'),
                          lineno=int(elem.get('lineno', -1)))

    def _create_arguments(self, elem):
        positional_only = []
        positional_or_named = []
        var_positional = None
        named_only = []
        var_named = None
        defaults = {}
        types = {}
        for arg in elem.findall('arguments/arg'):
            name = self._get_name(arg)
            type = self._get_type(arg)
            if type:
                types[name] = type
            default = self._get_default(arg)
            if default:
                defaults[name] = default
            kind = arg.get('kind')
            if kind == 'POSITIONAL_ONLY':
                positional_only.append(name)
            elif kind == 'POSITIONAL_OR_NAMED':
                positional_or_named.append(name)
            elif kind == 'VAR_POSITIONAL':
                var_positional = name
            elif kind == 'NAMED_ONLY':
                named_only.append(name)
            elif kind == 'VAR_NAMED':
                var_named = name

        return ArgumentSpec(positional_only=positional_only,
                            positional_or_named=positional_or_named,
                            var_positional=var_positional,
                            named_only=named_only,
                            var_named=var_named,
                            defaults=defaults,
                            types=types)

    @staticmethod
    def _get_name(arg):
        name_elem = arg.find('name')
        if name_elem is not None:
            return name_elem.text
        else:
            return ''

    @staticmethod
    def _get_type(arg):
        type_elem = arg.find('type')
        if type_elem is not None:
            return type_elem.text

    @staticmethod
    def _get_default(arg):
        default_elem = arg.find('default')
        if default_elem is not None:
            return unescape(default_elem.text)

    @staticmethod
    def _get_required(arg):
        required = arg.get('required')
        if required == 'true':
            return True
        else:
            return False
