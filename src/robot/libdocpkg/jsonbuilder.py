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

from robot.running import ArgInfo
from robot.errors import DataError

from .datatypes import EnumMember, TypedDictItem, TypeDoc
from .model import LibraryDoc, KeywordDoc


class JsonDocBuilder:

    def build(self, path):
        spec = self._parse_spec_json(path)
        return self.build_from_dict(spec)

    def build_from_dict(self, spec):
        libdoc = LibraryDoc(name=spec['name'],
                            doc=spec['doc'],
                            version=spec['version'],
                            type=spec['type'],
                            scope=spec['scope'],
                            doc_format=spec['docFormat'],
                            source=spec['source'],
                            lineno=int(spec.get('lineno', -1)))
        libdoc.inits = [self._create_keyword(kw) for kw in spec['inits']]
        libdoc.keywords = [self._create_keyword(kw) for kw in spec['keywords']]
        # RF >= 5 have 'typedocs', RF >= 4 have 'dataTypes', older/custom may have neither.
        if 'typedocs' in spec:
            libdoc.type_docs = self._parse_type_docs(spec['typedocs'])
        elif 'dataTypes' in spec:
            libdoc.type_docs = self._parse_data_types(spec['dataTypes'])
        return libdoc

    def _parse_spec_json(self, path):
        if not os.path.isfile(path):
            raise DataError(f"Spec file '{path}' does not exist.")
        with open(path) as json_source:
            libdoc_dict = json.load(json_source)
        return libdoc_dict

    def _create_keyword(self, data):
        kw = KeywordDoc(name=data.get('name'),
                        doc=data['doc'],
                        shortdoc=data['shortdoc'],
                        tags=data['tags'],
                        private=data.get('private', False),
                        deprecated=data.get('deprecated', False),
                        source=data['source'],
                        lineno=int(data.get('lineno', -1)))
        self._create_arguments(data['args'], kw)
        return kw

    def _create_arguments(self, arguments, kw: KeywordDoc):
        spec = kw.args
        setters = {
            ArgInfo.POSITIONAL_ONLY: spec.positional_only.append,
            ArgInfo.POSITIONAL_ONLY_MARKER: lambda value: None,
            ArgInfo.POSITIONAL_OR_NAMED: spec.positional_or_named.append,
            ArgInfo.VAR_POSITIONAL: lambda value: setattr(spec, 'var_positional', value),
            ArgInfo.NAMED_ONLY_MARKER: lambda value: None,
            ArgInfo.NAMED_ONLY: spec.named_only.append,
            ArgInfo.VAR_NAMED: lambda value: setattr(spec, 'var_named', value),
        }
        for arg in arguments:
            name = arg['name']
            setters[arg['kind']](name)
            default = arg.get('defaultValue')
            if default is not None:
                spec.defaults[name] = default
            if arg.get('type'):
                type_docs = {}
                type_info = self._parse_modern_type_info(arg['type'], type_docs)
            else:    # Compatibility with RF < 6.1.
                type_docs = arg.get('typedocs', {})
                type_info = tuple(arg['types'])
            if type_info:
                if not spec.types:
                    spec.types = {}
                spec.types[name] = type_info
            kw.type_docs[name] = type_docs

    def _parse_modern_type_info(self, data, type_docs):
        if data.get('typedoc'):
            type_docs[data['name']] = data['typedoc']
        return {'name': data['name'],
                'nested': [self._parse_modern_type_info(nested, type_docs)
                           for nested in data.get('nested', ())]}

    def _parse_type_docs(self, type_docs):
        for data in type_docs:
            doc = TypeDoc(data['type'], data['name'], data['doc'], data['accepts'],
                          data['usages'])
            if doc.type == TypeDoc.ENUM:
                doc.members = [EnumMember(d['name'], d['value'])
                               for d in data['members']]
            if doc.type == TypeDoc.TYPED_DICT:
                doc.items = [TypedDictItem(d['key'], d['type'], d['required'])
                             for d in data['items']]
            yield doc

    # Code below used for parsing legacy 'dataTypes'.

    def _parse_data_types(self, data_types):
        for obj in data_types['enums']:
            yield self._create_enum_doc(obj)
        for obj in data_types['typedDicts']:
            yield self._create_typed_dict_doc(obj)

    def _create_enum_doc(self, data):
        return TypeDoc(TypeDoc.ENUM, data['name'], data['doc'],
                       members=[EnumMember(member['name'], member['value'])
                                for member in data['members']])

    def _create_typed_dict_doc(self, data):
        return TypeDoc(TypeDoc.TYPED_DICT, data['name'], data['doc'],
                       items=[TypedDictItem(item['key'], item['type'], item['required'])
                              for item in data['items']])
