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
from xml.etree import ElementTree as ET

from robot.errors import DataError
from robot.running import ArgInfo, TypeInfo
from robot.utils import ETSource

from .datatypes import EnumMember, TypedDictItem, TypeDoc
from .model import KeywordDoc, LibraryDoc


class XmlDocBuilder:

    def build(self, path):
        spec = self._parse_spec(path)
        libdoc = LibraryDoc(
            name=spec.get("name"),
            type=spec.get("type").upper(),
            version=spec.find("version").text or "",
            doc=spec.find("doc").text or "",
            scope=spec.get("scope"),
            doc_format=spec.get("format") or "ROBOT",
            source=spec.get("source"),
            lineno=int(spec.get("lineno")) or -1,
        )
        libdoc.inits = self._create_keywords(spec, "inits/init", libdoc.source)
        libdoc.keywords = self._create_keywords(spec, "keywords/kw", libdoc.source)
        # RF >= 5 have 'typedocs', RF >= 4 have 'datatypes', older/custom may have neither.
        if spec.find("typedocs") is not None:
            libdoc.type_docs = self._parse_type_docs(spec)
        else:
            libdoc.type_docs = self._parse_data_types(spec)
        return libdoc

    def _parse_spec(self, path):
        if not os.path.isfile(path):
            raise DataError(f"Spec file '{path}' does not exist.")
        with ETSource(path) as source:
            root = ET.parse(source).getroot()
        if root.tag != "keywordspec":
            raise DataError(f"Invalid spec file '{path}'.")
        version = root.get("specversion")
        if version not in ("3", "4", "5", "6"):
            raise DataError(
                f"Invalid spec file version '{version}'. "
                f"Supported versions are 3, 4, 5, and 6."
            )
        return root

    def _create_keywords(self, spec, path, lib_source):
        return [self._create_keyword(elem, lib_source) for elem in spec.findall(path)]

    def _create_keyword(self, elem, lib_source):
        kw = KeywordDoc(
            name=elem.get("name", ""),
            doc=elem.find("doc").text or "",
            short_doc=elem.find("shortdoc").text or "",
            tags=[t.text for t in elem.findall("tags/tag")],
            private=elem.get("private", "false") == "true",
            deprecated=elem.get("deprecated", "false") == "true",
            source=elem.get("source") or lib_source,
            lineno=int(elem.get("lineno", -1)),
        )
        self._create_arguments(elem, kw)
        self._add_return_type(elem.find("returntype"), kw)
        return kw

    def _create_arguments(self, elem, kw: KeywordDoc):
        spec = kw.args
        spec = kw.args
        positional_only = []
        positional_or_named = []
        named_only = []
        for arg in elem.findall("arguments/arg"):
            name_elem = arg.find("name")
            if name_elem is None:
                continue
            name = name_elem.text
            kind = arg.get("kind")
            if kind == ArgInfo.POSITIONAL_ONLY:
                positional_only.append(name)
            elif kind == ArgInfo.POSITIONAL_OR_NAMED:
                positional_or_named.append(name)
            elif kind == ArgInfo.VAR_POSITIONAL:
                spec.var_positional = name
            elif kind == ArgInfo.NAMED_ONLY:
                named_only.append(name)
            elif kind == ArgInfo.VAR_NAMED:
                spec.var_named = name
            default_elem = arg.find("default")
            if default_elem is not None:
                spec.defaults[name] = default_elem.text or ""
            if not spec.types:
                spec.types = {}
            type_docs = {}
            type_elems = arg.findall("type")
            if len(type_elems) == 1 and "name" in type_elems[0].attrib:
                type_info = self._parse_type_info(type_elems[0], type_docs)
            else:
                type_info = self._parse_legacy_type_info(type_elems, type_docs)
            if type_info:
                spec.types[name] = type_info
            kw.type_docs[name] = type_docs
        spec.positional_only = positional_only
        spec.positional_or_named = positional_or_named
        spec.named_only = named_only

    def _parse_type_info(self, type_elem, type_docs):
        name = type_elem.get("name")
        if type_elem.get("typedoc"):
            type_docs[name] = type_elem.get("typedoc")
        nested = [
            self._parse_type_info(child, type_docs)
            for child in type_elem.findall("type")
        ]
        return TypeInfo(name, None, nested=nested or None)

    def _parse_legacy_type_info(self, type_elems, type_docs):
        types = []
        for elem in type_elems:
            name = elem.text
            types.append(name)
            if elem.get("typedoc"):
                type_docs[name] = elem.get("typedoc")
        return TypeInfo.from_sequence(types) if types else None

    def _add_return_type(self, elem, kw):
        if elem is not None:
            type_docs = {}
            kw.args.return_type = self._parse_type_info(elem, type_docs)
            kw.type_docs["return"] = type_docs

    def _parse_type_docs(self, spec):
        for elem in spec.findall("typedocs/type"):
            doc = TypeDoc(
                elem.get("type"),
                elem.get("name"),
                elem.find("doc").text,
                [e.text for e in elem.findall("accepts/type")],
                [e.text for e in elem.findall("usages/usage")],
            )
            if doc.type == TypeDoc.ENUM:
                doc.members = self._parse_members(elem)
            if doc.type == TypeDoc.TYPED_DICT:
                doc.items = self._parse_items(elem)
            yield doc

    def _parse_members(self, elem):
        return [
            EnumMember(member.get("name"), member.get("value"))
            for member in elem.findall("members/member")
        ]

    def _parse_items(self, elem):
        def get_required(item):
            required = item.get("required", None)
            return None if required is None else required == "true"

        return [
            TypedDictItem(item.get("key"), item.get("type"), get_required(item))
            for item in elem.findall("items/item")
        ]

    # Code below used for parsing legacy 'datatypes'.

    def _parse_data_types(self, spec):
        for elem in spec.findall("datatypes/enums/enum"):
            yield self._create_enum_doc(elem)
        for elem in spec.findall("datatypes/typeddicts/typeddict"):
            yield self._create_typed_dict_doc(elem)

    def _create_enum_doc(self, elem):
        return TypeDoc(
            TypeDoc.ENUM,
            elem.get("name"),
            elem.find("doc").text,
            members=self._parse_members(elem),
        )

    def _create_typed_dict_doc(self, elem):
        return TypeDoc(
            TypeDoc.TYPED_DICT,
            elem.get("name"),
            elem.find("doc").text,
            items=self._parse_items(elem),
        )
