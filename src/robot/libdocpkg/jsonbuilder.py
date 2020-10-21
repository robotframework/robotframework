#  Copyright 2020-     Robot Framework Foundation
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
from robot.running.arguments import ArgumentSpec, ArgInfo

from .model import LibraryDoc, KeywordDoc


class JsonDocBuilder(object):

    def build(self, path):
        spec = self._parse_spec_json(path)
        return self.build_from_dict(spec)

    def build_from_dict(self, libdoc_dict):
        libdoc = LibraryDoc(name=libdoc_dict.get('name'),
                            doc=libdoc_dict.get('doc'),
                            version=libdoc_dict.get('version'),
                            type=libdoc_dict.get('type'),
                            scope=libdoc_dict.get('scope'),
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
        return [KeywordDoc(name=kw.get('name'),
                           args=self._create_arguments(kw.get('args')),
                           doc=kw.get('doc'),
                           shortdoc=kw.get('shortdoc'),
                           tags=kw.get('tags'),
                           source=kw.get('source'),
                           lineno=int(kw.get('lineno'))) for kw in keywords]

    def _create_arguments(self, arguments):
        spec = ArgumentSpec()
        setters = {
            ArgInfo.POSITIONAL_ONLY: spec.positional_only.append,
            ArgInfo.POSITIONAL_OR_NAMED: spec.positional_or_named.append,
            ArgInfo.VAR_POSITIONAL: lambda value: setattr(spec, 'var_positional',
                                                          value),
            ArgInfo.NAMED_ONLY: spec.named_only.append,
            ArgInfo.VAR_NAMED: lambda value: setattr(spec, 'var_named', value),
        }
        for arg in arguments:
            name = arg.get('name')
            setters[arg.get('kind')](name)
            default = arg.get('default', None)
            if default:
                spec.defaults[name] = default
            arg_type = arg.get('type')
            if arg_type is not None:
                if not spec.types:
                    spec.types = {}
                spec.types[name] = arg_type
        return spec
