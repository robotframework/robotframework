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

import json
import os.path

from robot.errors import DataError

from .model import LibraryDoc, KeywordDoc, ArgumentDoc, DefaultValue


class JsonDocBuilder(object):

    def build(self, path):
        spec = self._parse_spec_json(path)
        return self.build_from_dict(spec)

    def build_from_dict(self, libdoc_dict):
        libdoc = LibraryDoc(name=libdoc_dict.get('name'),
                            type=libdoc_dict.get('type'),
                            version=libdoc_dict.get('version'),
                            doc=libdoc_dict.get('doc'),
                            scope=libdoc_dict.get('scope'),
                            named_args=libdoc_dict.get('named_args'),
                            doc_format=libdoc_dict.get('doc_format'),
                            source=libdoc_dict.get('source'),
                            lineno=int(libdoc_dict.get('lineno')))
        libdoc.inits = self._create_keywords(libdoc_dict.get('inits'))
        libdoc.keywords = self._create_keywords(libdoc_dict.get('keywords'))
        return libdoc

    @staticmethod
    def _parse_spec_json(path):
        if not os.path.isfile(path):
            raise DataError("Spec file '%s' does not exist." % path)
        with open(path) as json_source:
            libdoc_dict = json.load(json_source)
        return libdoc_dict

    def _create_keywords(self, keywords):
        return [self._create_keyword(kw) for kw in keywords]

    def _create_keyword(self, kw):
        # "deprecated" attribute isn't read because it is read from the doc
        # automatically. That should probably be changed at some point.
        return KeywordDoc(name=kw.get('name'),
                          args=self._create_arguments(kw.get('args')),
                          doc=kw.get('doc'),
                          tags=kw.get('tags'),
                          source=kw.get('source'),
                          lineno=int(kw.get('lineno')))

    def _create_arguments(self, arguments):
        return [self._create_argument(arg) for arg in arguments]

    def _create_argument(self, arg):
        return ArgumentDoc(name=arg.get('name'),
                           type=arg.get('type'),
                           default=self._create_default(arg.get('default', None)),
                           argument_type=arg.get('argument_type'),
                           required=arg.get('required'))

    @staticmethod
    def _create_default(default):
        if default:
            return DefaultValue(default)
