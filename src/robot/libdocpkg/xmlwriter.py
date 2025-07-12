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

from robot.running import TypeInfo
from robot.utils import NOT_SET, XmlWriter

from .output import get_generation_time


class LibdocXmlWriter:

    def write(self, libdoc, outfile):
        writer = XmlWriter(outfile, usage="Libdoc spec")
        self._write_start(libdoc, writer)
        self._write_keywords("inits", "init", libdoc.inits, libdoc.source, writer)
        self._write_keywords("keywords", "kw", libdoc.keywords, libdoc.source, writer)
        self._write_type_docs(libdoc.type_docs, writer)
        self._write_end(writer)

    def _write_start(self, libdoc, writer):
        attrs = {
            "name": libdoc.name,
            "type": libdoc.type,
            "format": libdoc.doc_format,
            "scope": libdoc.scope,
            "generated": get_generation_time(),
            "specversion": "6",
        }
        self._add_source_info(attrs, libdoc)
        writer.start("keywordspec", attrs)
        writer.element("version", libdoc.version)
        writer.element("doc", libdoc.doc)
        self._write_tags(libdoc.all_tags, writer)

    def _add_source_info(self, attrs, item, lib_source=None):
        if item.source and item.source != lib_source:
            attrs["source"] = str(item.source)
        if item.lineno and item.lineno > 0:
            attrs["lineno"] = str(item.lineno)

    def _write_keywords(self, list_name, kw_type, keywords, lib_source, writer):
        writer.start(list_name)
        for kw in keywords:
            attrs = self._get_start_attrs(kw, lib_source)
            writer.start(kw_type, attrs)
            self._write_arguments(kw, writer)
            self._write_return_type(kw, writer)
            writer.element("doc", kw.doc)
            writer.element("shortdoc", kw.short_doc)
            if kw_type == "kw" and kw.tags:
                self._write_tags(kw.tags, writer)
            writer.end(kw_type)
        writer.end(list_name)

    def _write_tags(self, tags, writer):
        writer.start("tags")
        for tag in tags:
            writer.element("tag", tag)
        writer.end("tags")

    def _write_arguments(self, kw, writer):
        writer.start("arguments", {"repr": str(kw.args)})
        for arg in kw.args:
            attrs = {
                "kind": arg.kind,
                "required": "true" if arg.required else "false",
                "repr": str(arg),
            }
            writer.start("arg", attrs)
            if arg.name:
                writer.element("name", arg.name)
            if arg.type:
                self._write_type_info(arg.type, kw.type_docs[arg.name], writer)
            if arg.default is not NOT_SET:
                writer.element("default", arg.default_repr)
            writer.end("arg")
        writer.end("arguments")

    def _write_type_info(
        self,
        type_info: TypeInfo,
        type_docs: dict,
        writer,
        element="type",
    ):
        attrs = {"name": type_info.name}
        if type_info.is_union:
            attrs["union"] = "true"
        if type_info.name in type_docs:
            attrs["typedoc"] = type_docs[type_info.name]
        if type_info.nested:
            writer.start(element, attrs)
            for nested in type_info.nested:
                self._write_type_info(nested, type_docs, writer)
            writer.end(element)
        else:
            writer.element(element, attrs=attrs)

    def _write_return_type(self, kw, writer):
        if kw.args.return_type:
            self._write_type_info(
                kw.args.return_type,
                kw.type_docs["return"],
                writer,
                element="returntype",
            )

    def _get_start_attrs(self, kw, lib_source):
        attrs = {"name": kw.name}
        if kw.private:
            attrs["private"] = "true"
        if kw.deprecated:
            attrs["deprecated"] = "true"
        self._add_source_info(attrs, kw, lib_source)
        return attrs

    def _write_type_docs(self, type_docs, writer):
        writer.start("typedocs")
        for doc in sorted(type_docs):
            writer.start("type", {"name": doc.name, "type": doc.type})
            writer.element("doc", doc.doc)
            writer.start("accepts")
            for typ in doc.accepts:
                writer.element("type", typ)
            writer.end("accepts")
            writer.start("usages")
            for usage in doc.usages:
                writer.element("usage", usage)
            writer.end("usages")
            if doc.type == "Enum":
                self._write_enum_members(doc, writer)
            if doc.type == "TypedDict":
                self._write_typed_dict_items(doc, writer)
            writer.end("type")
        writer.end("typedocs")

    def _write_enum_members(self, enum, writer):
        writer.start("members")
        for member in enum.members:
            writer.element(
                "member",
                attrs={"name": member.name, "value": member.value},
            )
        writer.end("members")

    def _write_typed_dict_items(self, typed_dict, writer):
        writer.start("items")
        for item in typed_dict.items:
            attrs = {"key": item.key, "type": item.type}
            if item.required is not None:
                attrs["required"] = "true" if item.required else "false"
            writer.element("item", attrs=attrs)
        writer.end("items")

    def _write_end(self, writer):
        writer.end("keywordspec")
        writer.close()
